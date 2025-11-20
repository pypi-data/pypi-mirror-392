"""Internal prompt context for Jinja template rendering."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, TypeAdapter

from .permissions import Permission


@dataclass
class PromptContext:
    """Internal helper for prompt rendering.

    Wraps request state and provides @property methods for Jinja templates.
    Users never see this - it's only used internally by invoke.py/structured.py.

    Templates can use:
        {% if ctx.is_retry %}
        {% if ctx.has_schema %}
    """

    # === Core State (from Request) ===
    user_prompt: str
    permissions: Permission
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None

    # === Structured Output ===
    attempt: int = 1
    validation_errors: list[str] = field(default_factory=list)

    # === Config ===
    compact_schema: bool = True
    terse_instructions: bool = False

    # === Internal (computed once) ===
    _slimschema_yaml: str | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Compute SlimSchema YAML once at init."""
        if self.response_format is not None:
            from .structured import _to_slimschema_yaml

            self._slimschema_yaml = _to_slimschema_yaml(self.response_format)

    # ============================================================
    # Computed Properties - Used directly in Jinja templates
    # ============================================================

    @property
    def is_retry(self) -> bool:
        """True if this is a retry attempt (attempt > 1)."""
        return self.attempt > 1

    @property
    def has_schema(self) -> bool:
        """True if structured output is requested."""
        return self.response_format is not None

    @property
    def is_default_permissions(self) -> bool:
        """True if permissions are default (edit=ALLOW, bash=DENY, webfetch=DENY)."""
        return (
            self.permissions.edit == Permission.ALLOW
            and self.permissions.bash == Permission.DENY
            and self.permissions.webfetch == Permission.DENY
        )

    @property
    def allowed_tools(self) -> list[str]:
        """List of allowed tool names."""
        tools = []
        if self.permissions.edit == Permission.ALLOW:
            tools.append("edit")
        if self.permissions.bash == Permission.ALLOW:
            tools.append("bash")
        if self.permissions.webfetch == Permission.ALLOW:
            tools.append("webfetch")
        return tools

    @property
    def denied_tools(self) -> list[str]:
        """List of denied tool names."""
        tools = []
        if self.permissions.edit == Permission.DENY:
            tools.append("edit")
        if self.permissions.bash == Permission.DENY:
            tools.append("bash")
        if self.permissions.webfetch == Permission.DENY:
            tools.append("webfetch")
        return tools

    @property
    def has_allowed_tools(self) -> bool:
        """True if any tools are allowed."""
        return len(self.allowed_tools) > 0

    @property
    def schema_yaml(self) -> str:
        """SlimSchema YAML string for prompts."""
        return self._slimschema_yaml or ""

    @property
    def error_list(self) -> str:
        """Formatted validation errors for retry prompts."""
        if not self.validation_errors:
            return ""
        errors = self.validation_errors[:5]  # Max 5 errors
        formatted = "\n".join(f"  - {err}" for err in errors)
        if len(self.validation_errors) > 5:
            formatted += (
                f"\n  ... and {len(self.validation_errors) - 5} more errors"
            )
        return formatted

    # ============================================================
    # Tool Descriptions (static, used by template)
    # ============================================================

    TOOL_DESCRIPTIONS = {
        "bash": "Execute shell commands",
        "webfetch": "Fetch content from URLs via HTTP/HTTPS",
        "edit": "Read, write, and modify files",
    }

    TOOL_AVOID_TEXT = {
        "bash": "Do not attempt shell commands, scripts, or command-line utilities",
        "webfetch": "Do not attempt to fetch web content or make HTTP requests",
        "edit": "Do not attempt file operations (read, write, create, or edit files)",
    }
