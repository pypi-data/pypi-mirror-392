from __future__ import annotations

from typing import Mapping, Optional

from loce_zap import *  # type: ignore[F403]
from loce_zap import (
    AsyncLoceZap as AsyncLoceZap,
    LoceZap as _LoceZap,
    DEFAULT_BACKOFF_FACTOR,
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)

def __call__(
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    default_headers: Optional[Mapping[str, str]] = ...,
) -> _LoceZap: ...

__all__: list[str]
