try:
    import kumoai.kumolib  # noqa: F401
except Exception as e:
    import platform

    _msg = f"""RFM is not supported in your environment.

💻 Your Environment:
Python version: {platform.python_version()}
Operating system: {platform.system()}
CPU architecture: {platform.machine()}
glibc version: {platform.libc_ver()[1]}

✅ Supported Environments:
* Python versions: 3.10, 3.11, 3.12, 3.13
* Operating systems and CPU architectures:
  * Linux (x86_64)
  * macOS (arm64)
  * Windows (x86_64)
* glibc versions: >=2.28

❌ Unsupported Environments:
* Python versions: 3.8, 3.9, 3.14
* Operating systems and CPU architectures:
  * Linux (arm64)
  * macOS (x86_64)
  * Windows (arm64)
* glibc versions: <2.28

Please create a feature request at 'https://github.com/kumo-ai/kumo-rfm'."""

    raise RuntimeError(_msg) from e

from dataclasses import dataclass
from enum import Enum
import ipaddress
import logging
import re
import socket
import threading
from typing import Optional, Dict, Tuple
import os
from urllib.parse import urlparse
import kumoai
from kumoai.client.client import KumoClient
from .sagemaker import (KumoClient_SageMakerAdapter,
                        KumoClient_SageMakerProxy_Local)
from .local_table import LocalTable
from .local_graph import LocalGraph
from .rfm import ExplainConfig, Explanation, KumoRFM
from .authenticate import authenticate

logger = logging.getLogger('kumoai_rfm')


def _is_local_address(host: str | None) -> bool:
    """Return True if the hostname/IP refers to the local machine."""
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
        for _, _, _, _, sockaddr in infos:
            ip = sockaddr[0]
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_loopback or ip_obj.is_unspecified:
                return True
        return False
    except Exception:
        return False


class InferenceBackend(str, Enum):
    REST = "REST"
    LOCAL_SAGEMAKER = "LOCAL_SAGEMAKER"
    AWS_SAGEMAKER = "AWS_SAGEMAKER"
    UNKNOWN = "UNKNOWN"


def _detect_backend(
        url: str) -> Tuple[InferenceBackend, Optional[str], Optional[str]]:
    parsed = urlparse(url)

    # Remote SageMaker
    if ("runtime.sagemaker" in parsed.netloc
            and parsed.path.endswith("/invocations")):
        # Example: https://runtime.sagemaker.us-west-2.amazonaws.com/
        # endpoints/Name/invocations
        match = re.search(r"runtime\.sagemaker\.([a-z0-9-]+)\.amazonaws\.com",
                          parsed.netloc)
        region = match.group(1) if match else None
        m = re.search(r"/endpoints/([^/]+)/invocations", parsed.path)
        endpoint_name = m.group(1) if m else None
        return InferenceBackend.AWS_SAGEMAKER, region, endpoint_name

    # Local SageMaker
    if parsed.port == 8080 and parsed.path.endswith(
            "/invocations") and _is_local_address(parsed.hostname):
        return InferenceBackend.LOCAL_SAGEMAKER, None, None

    # Default: regular REST
    return InferenceBackend.REST, None, None


@dataclass
class RfmGlobalState:
    _url: str = '__url_not_provided__'
    _backend: InferenceBackend = InferenceBackend.UNKNOWN
    _region: Optional[str] = None
    _endpoint_name: Optional[str] = None
    _thread_local = threading.local()

    # Thread-safe init-once.
    _initialized: bool = False
    _lock: threading.Lock = threading.Lock()

    @property
    def client(self) -> KumoClient:
        if self._backend == InferenceBackend.REST:
            return kumoai.global_state.client

        if hasattr(self._thread_local, '_sagemaker'):
            # Set the spcs token in the client to ensure it has the latest.
            return self._thread_local._sagemaker

        sagemaker_client: KumoClient
        if self._backend == InferenceBackend.LOCAL_SAGEMAKER:
            sagemaker_client = KumoClient_SageMakerProxy_Local(self._url)
        else:
            assert self._backend == InferenceBackend.AWS_SAGEMAKER
            assert self._region
            assert self._endpoint_name
            sagemaker_client = KumoClient_SageMakerAdapter(
                self._region, self._endpoint_name)

        self._thread_local._sagemaker = sagemaker_client
        return sagemaker_client

    def reset(self) -> None:  # For testing only.
        with self._lock:
            self._initialized = False
            self._url = '__url_not_provided__'
            self._backend = InferenceBackend.UNKNOWN
            self._region = None
            self._endpoint_name = None
            self._thread_local = threading.local()


global_state = RfmGlobalState()


def init(
    url: Optional[str] = None,
    api_key: Optional[str] = None,
    snowflake_credentials: Optional[Dict[str, str]] = None,
    snowflake_application: Optional[str] = None,
    log_level: str = "INFO",
) -> None:
    with global_state._lock:
        if global_state._initialized:
            if url != global_state._url:
                raise ValueError(
                    "Kumo RFM has already been initialized with a different "
                    "URL. Re-initialization with a different URL is not "
                    "supported.")
            return

        if url is None:
            url = os.getenv("RFM_API_URL", "https://kumorfm.ai/api")

        backend, region, endpoint_name = _detect_backend(url)
        if backend == InferenceBackend.REST:
            # Initialize kumoai.global_state
            if (kumoai.global_state.initialized
                    and kumoai.global_state._url != url):
                raise ValueError(
                    "Kumo AI SDK has already been initialized with different "
                    "API URL. Please restart Python interpreter and "
                    "initialize via kumoai.rfm.init()")
            kumoai.init(url=url, api_key=api_key,
                        snowflake_credentials=snowflake_credentials,
                        snowflake_application=snowflake_application,
                        log_level=log_level)
        elif backend == InferenceBackend.AWS_SAGEMAKER:
            assert region
            assert endpoint_name
            KumoClient_SageMakerAdapter(region, endpoint_name).authenticate()
        else:
            assert backend == InferenceBackend.LOCAL_SAGEMAKER
            KumoClient_SageMakerProxy_Local(url).authenticate()

        global_state._url = url
        global_state._backend = backend
        global_state._region = region
        global_state._endpoint_name = endpoint_name
        global_state._initialized = True
        logger.info("Kumo RFM initialized with backend: %s, url: %s", backend,
                    url)


__all__ = [
    'LocalTable',
    'LocalGraph',
    'KumoRFM',
    'ExplainConfig',
    'Explanation',
    'authenticate',
    'init',
]
