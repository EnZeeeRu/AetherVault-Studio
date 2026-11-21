"""
avs/toolbox.py — Single-Source Tool Registry & Structured ToolResult Envelope.
Register each tool once with @toolbox.register(...); auto-generates:
  - Fuzzy alias resolution
  - vault.help() cheatsheet
  - OpenAI-compatible JSON tool schemas
  - MCP tools/list definitions
"""
import difflib
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional


@dataclass
class ToolResult:
    ok: bool
    summary: str = ""
    data: Any = None
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class ToolSpec:
    def __init__(
        self,
        name: str,
        fn: Callable,
        description: str,
        parameters: dict,
        trust: str = "safe_auto",
        aliases: Optional[List[str]] = None,
        mcp_exposed: bool = False,
    ):
        self.name = name
        self.fn = fn
        self.description = description
        self.parameters = parameters or {"type": "object", "properties": {}, "required": []}
        self.trust = trust
        self.aliases = [a.lower() for a in (aliases or [])]
        self.mcp_exposed = mcp_exposed


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSpec] = {}
        self._alias_map: Dict[str, str] = {}

    def register(
        self,
        name: str,
        description: str = "",
        parameters: Optional[dict] = None,
        trust: str = "safe_auto",
        aliases: Optional[List[str]] = None,
        mcp_exposed: bool = False,
    ):
        def decorator(fn: Callable):
            spec = ToolSpec(
                name=name,
                fn=fn,
                description=description or ((fn.__doc__ or "").strip().splitlines()[0] if fn.__doc__ else name),
                parameters=parameters or {"type": "object", "properties": {}, "required": []},
                trust=trust,
                aliases=aliases,
                mcp_exposed=mcp_exposed,
            )
            self._tools[name] = spec
            for a in spec.aliases:
                self._alias_map[a] = name
            return fn
        return decorator

    def resolve_name(self, name: str) -> Optional[str]:
        low = (name or "").strip().lower()
        if low in self._tools:
            return low
        if low in self._alias_map:
            return self._alias_map[low]
        return None

    def call(self, name: str, args: Optional[dict] = None, trust_level: str = "safe_auto") -> ToolResult:
        resolved = self.resolve_name(name)
        if not resolved:
            candidates = list(self._tools.keys()) + list(self._alias_map.keys())
            close = difflib.get_close_matches((name or "").lower(), candidates, n=3, cutoff=0.45)
            hint = f" Did you mean: {', '.join(close)}?" if close else ""
            return ToolResult(ok=False, error=f"Unknown tool '{name}'.{hint}")

        spec = self._tools[resolved]
        if spec.trust == "full_pc" and trust_level != "full_pc":
            return ToolResult(
                ok=False,
                error=f"Safety Gate: '{spec.name}' requires workbench_trust='full_pc' (currently '{trust_level}')."
            )
        try:
            res = spec.fn(**(args or {}))
            if isinstance(res, ToolResult):
                return res
            return ToolResult(ok=True, summary=str(res), data=res)
        except Exception as e:
            return ToolResult(ok=False, error=f"{type(e).__name__}: {e}")

    def help_text(self, topic: str = "") -> str:
        t = (topic or "").strip().lower()
        lines = []
        for name, spec in sorted(self._tools.items()):
            if t and (t not in name.lower() and t not in spec.description.lower()):
                continue
            al = f" (aliases: {', '.join(spec.aliases)})" if spec.aliases else ""
            lines.append(f"- vault.{name}(): {spec.description}{al}")
        return "\n".join(lines) if lines else "No matching tools found."

    def openai_schemas(self) -> List[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": spec.parameters,
                },
            }
            for spec in self._tools.values()
        ]

    def mcp_tools(self) -> List[dict]:
        return [
            {
                "name": spec.name,
                "description": spec.description,
                "inputSchema": spec.parameters,
            }
            for spec in self._tools.values()
            if spec.mcp_exposed
        ]


toolbox = ToolRegistry()
