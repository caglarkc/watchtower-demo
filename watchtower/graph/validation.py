"""Node output validation and safe halt."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from watchtower.graph.state import GraphState

T = TypeVar("T", bound=BaseModel)


def validate_output(model: type[T], data: dict[str, Any]) -> T:
    return model.model_validate(data)


def audit_patch(node_name: str, output: dict[str, Any]) -> dict[str, Any]:
    return {
        "audit_trail": [
            {
                "node": node_name,
                "output_keys": sorted(output.keys()),
            }
        ]
    }


def halt_state(error: str) -> dict[str, Any]:
    return {
        "halted": True,
        "error": error,
        "status": "failed",
    }


def safe_node(
    node_name: str,
    output_model: type[BaseModel] | None = None,
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
    """Wrap a node: validate output schema; halt graph on failure."""

    def decorator(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        def wrapper(state: GraphState, deps: Any) -> dict[str, Any]:
            if state.get("halted"):
                return {}
            try:
                if state.get("candidate", {}).get("attributes", {}).get(
                    "_force_validation_error"
                ) and node_name == "resolve_identity":
                    raise ValidationError.from_exception_data(
                        "IdentityOutput",
                        [{"type": "missing", "loc": ("user_id",), "msg": "forced"}],
                    )
                result = fn(state, deps)
                if output_model is not None and result:
                    payload = {k: v for k, v in result.items() if k != "audit_trail"}
                    key = next(
                        (k for k in payload if k not in ("halted", "error", "status")),
                        None,
                    )
                    if key and isinstance(payload.get(key), dict):
                        nested = payload[key]
                        validate_output(output_model, nested)
                    elif output_model.__name__ in (
                        "RouteOutput",
                        "FinalizeOutput",
                    ):
                        validate_output(output_model, payload)
                patch = audit_patch(node_name, result)
                result.update(patch)
                return result
            except ValidationError as exc:
                out = halt_state(f"{node_name} validation failed: {exc}")
                out.update(audit_patch(node_name, out))
                return out
            except Exception as exc:  # noqa: BLE001 — graph must halt safely
                out = halt_state(f"{node_name} error: {exc}")
                out.update(audit_patch(node_name, out))
                return out

        wrapper.__name__ = fn.__name__
        return wrapper

    return decorator
