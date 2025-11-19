from importlib.metadata import version as _pkg_version

from .types import Config, SdkMetric, Env
from .middleware import (
    ObservifyASGIMiddleware,
    ObservifyDjangoMiddleware,
    django_middleware_factory,
    fastapi_integration,
)
from .batching import get_manager

try:
    __version__ = _pkg_version("observify")
except Exception:
    __version__ = "0.0.0"

__all__ = [
    "Config",
    "SdkMetric",
    "Env",
    "ObservifyASGIMiddleware",
    "ObservifyDjangoMiddleware",
    "django_middleware_factory",
    "fastapi_integration",
    "get_manager",
    "__version__",
]
