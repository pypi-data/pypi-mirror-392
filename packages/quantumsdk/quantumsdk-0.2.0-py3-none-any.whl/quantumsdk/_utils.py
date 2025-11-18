from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional


def unwrap_api_payload(payload: Any) -> Any:
    """
    Normalize API payloads to the underlying data structure.
    """
    if isinstance(payload, Mapping):
        if "data" in payload:
            return payload["data"]
        if "results" in payload:
            return payload["results"]
    return payload


def ensure_iterable_of_dicts(items: Any) -> List[Dict[str, Any]]:
    if items is None:
        return []

    if isinstance(items, Mapping):
        return [dict(items)]

    if isinstance(items, Iterable) and not isinstance(items, (str, bytes)):
        normalized: List[Dict[str, Any]] = []
        for item in items:
            if not isinstance(item, Mapping):
                raise ValueError(
                    "Unexpected item type; expected a mapping but received "
                    f"{type(item)!r}."
                )
            normalized.append(dict(item))
        return normalized

    raise ValueError(
        "Unexpected payload structure; expected an iterable of mappings but "
        f"received {type(items)!r}."
    )


def normalize_numbered_mapping(
    data: Any, *, default_start: int = 1
) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Normalize machine config sections expected to be dicts keyed by string numbers.

    Accepts:
        - None
        - dict-like objects mapping string/int keys to dict payloads
        - iterables (list/tuple) of dicts where a "number" field may be present

    Returns a dict keyed by stringified integers. The "number" field is removed
    from the nested payloads to match the backend contract (the key determines
    the sequence number).
    """
    if data is None:
        return None

    if isinstance(data, Mapping):
        normalized: Dict[str, Dict[str, Any]] = {}
        for key, value in data.items():
            if not isinstance(value, Mapping):
                raise ValueError(
                    "Expected mapping values in machine_config section, but "
                    f"found {type(value)!r}."
                )
            normalized[str(key)] = {k: v for k, v in value.items() if k != "number"}
        return normalized

    if isinstance(data, Iterable) and not isinstance(data, (str, bytes)):
        normalized_list = ensure_iterable_of_dicts(data)
        normalized_dict: Dict[str, Dict[str, Any]] = {}
        counter = default_start
        for item in normalized_list:
            number = item.get("number")
            if number is None:
                number = counter
                counter += 1
            normalized_dict[str(number)] = {
                k: v for k, v in item.items() if k != "number"
            }
        return normalized_dict

    raise ValueError(
        "Unsupported machine_config section format: "
        f"{type(data)!r}. Expected dict or iterable."
    )
