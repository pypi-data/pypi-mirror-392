from __future__ import annotations

from typing import Any, TypeVar, cast

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from .mcp import LocalMcpServer, McpServer, RemoteMcpServer, normalize_mcp
from .permissions import Permission
from .providers import ProviderConfig

P = TypeVar("P", bound=BaseModel)


class Request(BaseModel):
    """A single, stateless invocation request (internal).

    Fields:
      - model: provider/model identifier
      - prompt: instruction text
      - permission/providers/mcp: config to forward to CLI
      - response_format: optional structured output schema (SlimSchema YAML, Pydantic class, or TypeAdapter)
      - session: optional session id to resume
      - timeout: optional runtime hints
    """

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    model: str
    prompt: str
    permission: Permission = Field(default_factory=Permission)
    providers: dict[str, ProviderConfig] | None = None
    mcp: (
        dict[str, LocalMcpServer | RemoteMcpServer] | list[McpServer] | None
    ) = None
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None
    session: str | None = None

    @field_validator("mcp", mode="before")
    @classmethod
    def _normalize_mcp(
        cls, v: list[McpServer] | dict[str, McpServer] | None
    ) -> dict[str, LocalMcpServer | RemoteMcpServer] | None:
        out = normalize_mcp(v)
        return cast(dict[str, LocalMcpServer | RemoteMcpServer] | None, out)
