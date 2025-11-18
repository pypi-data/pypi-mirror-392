from __future__ import annotations

from typing import Any, Iterable, Set


class APIResponse(dict):
    """Dict que permite acesso por atributos (ex: resp.qrCode)."""

    def __getattr__(self, item: str) -> Any:
        try:
            return self[item]
        except KeyError as exc:
            camelized = _snake_to_camel(item)
            if camelized in self:
                return self[camelized]
            raise AttributeError(item) from exc

    def __dir__(self) -> Any:
        return sorted(_dir_with_aliases(super().__dir__(), self.keys()))


def wrap_response_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return APIResponse({k: wrap_response_payload(v) for k, v in value.items()})
    if isinstance(value, list):
        return [wrap_response_payload(v) for v in value]
    if isinstance(value, tuple):
        return tuple(wrap_response_payload(v) for v in value)
    return value


def _snake_to_camel(name: str) -> str:
    if not name or "_" not in name.strip("_"):
        return name

    prefix = ""
    while name.startswith("_"):
        prefix += "_"
        name = name[1:]
    if not name:
        return prefix

    parts = name.split("_")
    first, rest = parts[0], parts[1:]
    camel_rest = "".join(part.capitalize() for part in rest if part)
    return f"{prefix}{first}{camel_rest}"


def _camel_to_snake(name: str) -> str:
    if not name:
        return name
    prefix = ""
    while name.startswith("_"):
        prefix += "_"
        name = name[1:]
    if not name:
        return prefix

    chars = []
    for ch in name:
        if ch.isupper() and chars:
            chars.append("_")
        chars.append(ch.lower())
    return prefix + "".join(chars)


def _dir_with_aliases(base: Iterable[str], keys: Iterable[str]) -> Set[str]:
    result: Set[str] = set(base)
    for key in keys:
        result.add(key)
        alias = _camel_to_snake(key)
        result.add(alias)
    return result
