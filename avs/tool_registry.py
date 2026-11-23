"""Single-source-of-truth tool registry, permission gate, and alias resolver (v6.3)."""
import difflib
from typing import Callable, Any
from avs.contracts import ToolSpec, ToolResult


class ToolRegistry:
    """Bounded registry of tools with trust-tier gating and typo/alias resolution."""

    def __init__(self, max_tools: int = 128):
        self.max_tools = max(8, int(max_tools))
        self._specs: dict[str, ToolSpec] = {}
        self._handlers: dict[str, Callable[..., Any]] = {}
        self._alias_to_name: dict[str, str] = {}

    def register(self, spec: ToolSpec, handler: Callable[..., Any]) -> bool:
        if not spec or not spec.name or not callable(handler):
            return False
        key = spec.name.strip().lower()
        if key not in self._specs and len(self._specs) >= self.max_tools:
            return False
        self._specs[key] = spec
        self._handlers[key] = handler
        self._alias_to_name[key] = key
        for al in (spec.aliases or ()):
            a_low = str(al).strip().lower()
            if a_low:
                self._alias_to_name[a_low] = key
        return True

    def resolve_name(self, name_or_alias: str) -> str:
        low = (name_or_alias or "").strip().lower()
        return self._alias_to_name.get(low, low)

    def suggest_names(self, name_or_alias: str, n: int = 4) -> list[str]:
        low = (name_or_alias or "").strip().lower()
        candidates = sorted(set(self._specs.keys()) | set(self._alias_to_name.keys()))
        return difflib.get_close_matches(low, candidates, n=max(1, int(n)), cutoff=0.45)

    def get_spec(self, name_or_alias: str) -> ToolSpec | None:
        resolved = self.resolve_name(name_or_alias)
        return self._specs.get(resolved)

    def list_specs(self) -> list[ToolSpec]:
        return list(self._specs.values())

    def invoke(self, name_or_alias: str, args: dict | None = None, trust_level: str = "safe_auto") -> ToolResult:
        resolved = self.resolve_name(name_or_alias)
        spec = self._specs.get(resolved)
        handler = self._handlers.get(resolved)
        if spec is None or handler is None:
            near = self.suggest_names(name_or_alias)
            hint = f" Closest tools: {', '.join(near)}." if near else ""
            return ToolResult(ok=False, error=f"Unknown tool '{name_or_alias}'.{hint}")

        trust_norm = (trust_level or "safe_auto").strip().lower()
        if spec.trust_tier == "full_pc" and trust_norm != "full_pc":
            return ToolResult(
                ok=False,
                error=f"Tool '{spec.name}' requires Full PC trust tier (currently '{trust_norm}')."
            )

        safe_args = args if isinstance(args, dict) else {}
        try:
            raw_out = handler(**safe_args)
            if isinstance(raw_out, ToolResult):
                return raw_out
            if isinstance(raw_out, dict):
                ok_val = bool(raw_out.get("ok", True))
                summ = str(raw_out.get("result") or raw_out.get("summary") or raw_out.get("error") or "")
                return ToolResult(ok=ok_val, summary=summ, data=raw_out, error=raw_out.get("error"))
            return ToolResult(ok=True, summary=str(raw_out if raw_out is not None else ""), data=raw_out)
        except Exception as exc:
            return ToolResult(ok=False, error=f"{type(exc).__name__}: {exc}")
