from .config import SDKOptions, RetryConfig
from .errors import AmeideRpcError, RpcErrorCategory, normalize_error

def __getattr__(name: str):
    if name == "AmeideClient":
        from .client import AmeideClient
        return AmeideClient
    raise AttributeError(name)


__all__ = [
    "AmeideClient",
    "SDKOptions",
    "RetryConfig",
    "AmeideRpcError",
    "RpcErrorCategory",
    "normalize_error",
]
