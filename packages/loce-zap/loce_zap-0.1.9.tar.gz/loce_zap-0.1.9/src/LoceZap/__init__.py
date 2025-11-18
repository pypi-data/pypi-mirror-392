from __future__ import annotations

import sys
import types
from typing import Any

from loce_zap import *  # type: ignore[F403]  # noqa: F401,F403
from loce_zap import AsyncLoceZap as _AsyncLoceZap, LoceZap as _LoceZap
from loce_zap import __all__ as _loce_all

__all__ = _loce_all


class _LoceZapModule(types.ModuleType):
    """Permite `import LoceZap; LoceZap(...)` direto."""

    def __call__(self, *args: Any, **kwargs: Any) -> _LoceZap:
        return _LoceZap(*args, **kwargs)


_module = sys.modules[__name__]
if not isinstance(_module, _LoceZapModule):
    _module.__class__ = _LoceZapModule
