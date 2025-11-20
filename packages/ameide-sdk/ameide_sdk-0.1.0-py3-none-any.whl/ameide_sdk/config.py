from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping, MutableMapping, Optional, Sequence

DEFAULT_ENDPOINT = "api.ameide.io:443"


TokenProvider = Callable[[], Optional[str]]
MetadataProvider = Mapping[str, str] | MutableMapping[str, str]


@dataclass
class RetryConfig:
    max_attempts: int = 3
    initial_backoff: float = 0.2  # seconds
    max_backoff: float = 5.0
    backoff_multiplier: float = 2.0
    retryable_codes: Sequence[str] = (
        "UNAVAILABLE",
        "DEADLINE_EXCEEDED",
        "RESOURCE_EXHAUSTED",
        "ABORTED",
    )


@dataclass
class SDKOptions:
    endpoint: str = DEFAULT_ENDPOINT
    secure: bool = True
    auth: Optional[TokenProvider] = None
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: MetadataProvider = field(default_factory=dict)
    timeout: float = 5.0
    retry: RetryConfig = field(default_factory=RetryConfig)
    request_id_provider: Optional[Callable[[], str]] = None
    interceptors: Sequence[object] = field(default_factory=tuple)
