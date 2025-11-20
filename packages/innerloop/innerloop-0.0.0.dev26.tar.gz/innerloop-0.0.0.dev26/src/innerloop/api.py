"""Public API: Loop class + convenience helpers.

Surface:
- Loop: run/arun, session/asession
- Functional wrappers: run/arun
- Helpers: allow (permissions), mcp (servers)
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, TypeAdapter

from .errors import CliTimeoutError
from .events import (
    ErrorEvent,
    OpenCodeEvent,
    PromptRenderedEvent,
    RetryEvent,
    StreamEvent,
    TimeInfo,
    TimeoutEvent,
    ValidationErrorEvent,
    ValidationSuccessEvent,
    parse_event,
)
from .helper import safe_debug_log, to_session_id, unix_ms
from .invoke import run_opencode_jsonl
from .mcp import LocalMcpServer, RemoteMcpServer
from .output import assemble_output
from .permissions import Permission, PermissionLevel
from .providers import ProviderConfig
from .response import Response
from .usage import compute_usage


def allow(
    *tools: str,
    read: bool = True,
    write: bool = True,
    bash: bool | dict[str, PermissionLevel] = False,
    webfetch: bool = False,
) -> Permission:
    """Convenience builder for Permission.

    Semantics:
    - tools may contain "bash" or "webfetch" to allow them quickly
    - edit is ALLOW only when both read=True and write=True; otherwise DENY
    - passing a dict for `bash` enables fine‑grained tool policies
    """
    edit_level = Permission.ALLOW if write and read else Permission.DENY
    bash_level = (
        Permission.ALLOW
        if (bash is True or "bash" in tools)
        else Permission.DENY
    )
    web_level = (
        Permission.ALLOW
        if (webfetch or "webfetch" in tools)
        else Permission.DENY
    )
    return Permission(
        edit=edit_level,
        bash=bash if isinstance(bash, dict) else bash_level,
        webfetch=web_level,
    )


def mcp(**servers: str) -> dict[str, LocalMcpServer | RemoteMcpServer]:
    """Build MCP server definitions.

    - Remote: pass a URL string (http/https)
    - Local: pass a command string; optional "ENV=VALUE" tokens allowed before cmd

    Examples:
      mcp(context7="https://mcp.context7.com/mcp")
      mcp(biomcp="uvx --from biomcp-python biomcp run")
    """
    out: dict[str, LocalMcpServer | RemoteMcpServer] = {}
    for name, spec in servers.items():
        s = spec.strip()
        if s.startswith(("http://", "https://")):
            out[name] = RemoteMcpServer(name=name, url=s)  # type: ignore[arg-type]
            continue
        env: dict[str, str] = {}
        cmd: list[str] = []
        for tok in s.split():
            if "=" in tok and not cmd:
                k, _, v = tok.partition("=")
                env[k] = v
            else:
                cmd.append(tok)
        out[name] = LocalMcpServer(
            name=name, command=cmd, environment=env or None
        )
    return out


# providers(...) helper removed; prefer innerloop.providers.provider(name, **options)


class Loop:
    """Reusable loop that hides config and exposes simple methods."""

    def __init__(
        self,
        *,
        model: str,
        perms: Permission | None = None,
        providers: dict[str, ProviderConfig] | None = None,
        mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
        timeout: float | None = None,
    ) -> None:
        self.model = model
        self.perms = perms or Permission()
        self.providers = providers
        self.mcp = mcp
        self.default_response_format: (
            type[BaseModel] | TypeAdapter[Any] | None
        ) = None
        self._last_session_id: str | None = None
        self.default_timeout: float | None = timeout

    def run(
        self,
        prompt: str,
        *,
        response_format: (
            str | type[BaseModel] | TypeAdapter[Any] | None
        ) = None,
        session: str | Response[Any] | None = None,
        max_retries: int = 3,
        # Single timeout (idle inactivity)
        timeout: float | None = None,
    ) -> Response[Any]:
        # Avoid creating coroutine objects when running inside an event loop;
        # raising early prevents un-awaited coroutine warnings in async tests.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop → safe to proceed with asyncio.run
            pass
        else:
            # Avoid creating coroutine objects that would trigger "never awaited"
            # warnings when raising from within an active event loop.
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )

        # Collect all events from streaming
        all_events: list[StreamEvent] = []
        validation_events: list[
            ValidationSuccessEvent | ValidationErrorEvent
        ] = []
        wall_start = unix_ms()
        final_session: str | None = None
        structured_output: Any = None

        for event in self.stream(
            prompt,
            response_format=response_format,
            session=session,
            max_retries=max_retries,
            timeout=timeout,
        ):
            if isinstance(
                event, (ValidationSuccessEvent, ValidationErrorEvent)
            ):
                validation_events.append(event)
                if isinstance(event, ValidationSuccessEvent):
                    structured_output = event.output
                elif isinstance(event, ValidationErrorEvent):
                    # Add ErrorEvent for backward compatibility
                    all_events.append(
                        ErrorEvent(
                            timestamp=event.timestamp,
                            sessionID=event.sessionID,
                            type="error",
                            message=event.error_message,
                            code=None,
                            severity="error",
                        )
                    )
            elif isinstance(event, RetryEvent):
                pass  # Don't include retry events in the event list
            else:
                # StreamEvent (includes OpenCodeEvent + PromptRenderedEvent + validation events)
                all_events.append(event)
                if final_session is None:
                    final_session = getattr(event, "sessionID", None) or None

        wall_end = unix_ms()

        # Determine final output
        # Check if timeout occurred
        timed_out = any(isinstance(e, TimeoutEvent) for e in all_events)

        if structured_output is not None:
            output = structured_output
        else:
            # If response_format was requested but validation failed, raise error (unless timed out)
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            if eff_format is not None and not timed_out:
                # Find the last validation error
                last_error = next(
                    (
                        e.error_message
                        for e in reversed(validation_events)
                        if isinstance(e, ValidationErrorEvent)
                    ),
                    "Validation failed",
                )
                raise RuntimeError(
                    f"Structured output validation failed after {max_retries} attempts. Error: {last_error}"
                )
            # Assemble text output from events
            output = assemble_output(
                all_events, reset_on_tool=True, fallback_to_tool=True
            )

        # Count attempts from validation events
        attempts = max(
            (
                max(e.attempt for e in validation_events)
                if validation_events
                else 1
            ),
            1,
        )

        # Build response
        resp: Response[Any] = Response(
            session_id=final_session or self._last_session_id or "",
            input=prompt,
            output=output,
            events=all_events,
            attempts=attempts,
            timed_out=timed_out,
            time=TimeInfo(start=wall_start, end=wall_end),
        )
        resp.usage = compute_usage(all_events)

        if final_session:
            self._last_session_id = final_session

        return resp

    async def arun(
        self,
        prompt: str,
        *,
        response_format: (
            str | type[BaseModel] | TypeAdapter[Any] | None
        ) = None,
        session: str | Response[Any] | None = None,
        max_retries: int = 3,
        timeout: float | None = None,
    ) -> Response[Any]:
        # Collect all events from streaming
        all_events: list[StreamEvent] = []
        validation_events: list[
            ValidationSuccessEvent | ValidationErrorEvent
        ] = []
        wall_start = unix_ms()
        final_session: str | None = None
        structured_output: Any = None

        async for event in self.astream(
            prompt,
            response_format=response_format,
            session=session,
            max_retries=max_retries,
            timeout=timeout,
        ):
            if isinstance(
                event, (ValidationSuccessEvent, ValidationErrorEvent)
            ):
                validation_events.append(event)
                if isinstance(event, ValidationSuccessEvent):
                    structured_output = event.output
                elif isinstance(event, ValidationErrorEvent):
                    # Add ErrorEvent for backward compatibility
                    all_events.append(
                        ErrorEvent(
                            timestamp=event.timestamp,
                            sessionID=event.sessionID,
                            type="error",
                            message=event.error_message,
                            code=None,
                            severity="error",
                        )
                    )
            elif isinstance(event, RetryEvent):
                pass  # Don't include retry events in the event list
            else:
                # StreamEvent (includes OpenCodeEvent + PromptRenderedEvent + validation events)
                all_events.append(event)
                if final_session is None:
                    final_session = getattr(event, "sessionID", None) or None

        wall_end = unix_ms()

        # Determine final output
        # Check if timeout occurred
        timed_out = any(isinstance(e, TimeoutEvent) for e in all_events)

        if structured_output is not None:
            output = structured_output
        else:
            # If response_format was requested but validation failed, raise error (unless timed out)
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            if eff_format is not None and not timed_out:
                # Find the last validation error
                last_error = next(
                    (
                        e.error_message
                        for e in reversed(validation_events)
                        if isinstance(e, ValidationErrorEvent)
                    ),
                    "Validation failed",
                )
                raise RuntimeError(
                    f"Structured output validation failed after {max_retries} attempts. Error: {last_error}"
                )
            # Assemble text output from events
            output = assemble_output(
                all_events, reset_on_tool=True, fallback_to_tool=True
            )

        # Count attempts from validation events
        attempts = max(
            (
                max(e.attempt for e in validation_events)
                if validation_events
                else 1
            ),
            1,
        )

        # Build response
        resp: Response[Any] = Response(
            session_id=final_session or self._last_session_id or "",
            input=prompt,
            output=output,
            events=all_events,
            attempts=attempts,
            timed_out=timed_out,
            time=TimeInfo(start=wall_start, end=wall_end),
        )
        resp.usage = compute_usage(all_events)

        if final_session:
            self._last_session_id = final_session

        return resp

    def stream(
        self,
        prompt: str,
        *,
        response_format: (
            str | type[BaseModel] | TypeAdapter[Any] | None
        ) = None,
        session: str | Response[Any] | None = None,
        max_retries: int = 3,
        timeout: float | None = None,
    ) -> Iterator[StreamEvent]:
        """Stream events from the LLM, including structured output validation (sync wrapper).

        This is a synchronous wrapper around astream(). For truly asynchronous streaming,
        use astream() instead.

        See astream() for full documentation.
        """
        # Check for running event loop to avoid issues
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            pass  # No running loop, safe to proceed
        else:
            raise RuntimeError(
                "stream() cannot be called from a running event loop. Use astream() instead."
            )

        # Helper async function to collect all events
        async def _collect_events() -> list[StreamEvent]:
            events: list[StreamEvent] = []
            async for event in self.astream(
                prompt,
                response_format=response_format,
                session=session,
                max_retries=max_retries,
                timeout=timeout,
            ):
                events.append(event)
            return events

        # Run async generator to completion and yield results
        events = asyncio.run(_collect_events())
        yield from events

    async def astream(
        self,
        prompt: str,
        *,
        response_format: (
            str | type[BaseModel] | TypeAdapter[Any] | None
        ) = None,
        session: str | Response[Any] | None = None,
        max_retries: int = 3,
        timeout: float | None = None,
    ) -> AsyncIterator[StreamEvent]:
        """Stream events from the LLM in real-time, including structured output validation.

        This method streams all events as they occur, including:
        - OpenCode events (step_start, text, tool_use, step_finish, error)
        - Structured output validation events (validation_error, validation_success, retry)

        When response_format is provided, the method will:
        1. Stream all OpenCode events from each attempt
        2. Validate the output against the response_format
        3. Yield ValidationSuccessEvent if validation passes
        4. Yield ValidationErrorEvent and RetryEvent if validation fails (and retries remain)

        Args:
            prompt: The user prompt to send to the LLM
            response_format: Optional Pydantic model or TypeAdapter for structured output
            session: Optional session ID or Response object for multi-turn conversations
            max_retries: Maximum number of validation retry attempts (default: 3)
            timeout: Idle timeout in seconds (how long to wait for next event)

        Yields:
            StreamEvent: OpenCodeEvent, ValidationErrorEvent, ValidationSuccessEvent, or RetryEvent

        Example:
            >>> loop = Loop(model="opencode/big-pickle")
            >>> async for event in loop.astream("What is 2 + 2?"):
            ...     if event.type == "text":
            ...         print(event.text, end="", flush=True)
            ...     elif event.type == "validation_success":
            ...         print(f"\\nParsed output: {event.output}")
        """
        sid = to_session_id(session)
        if sid is None:
            sid = self._last_session_id
        eff_format = (
            response_format
            if response_format is not None
            else self.default_response_format
        )
        eff_timeout = timeout if timeout is not None else self.default_timeout

        # If no structured output requested, just stream events
        if eff_format is None:
            # Yield prompt rendered event
            yield PromptRenderedEvent(
                timestamp=unix_ms(),
                sessionID=sid or "",
                type="prompt_rendered",
                prompt=prompt,
                attempt=1,
                schema_yaml=None,
            )

            try:
                async for raw_event in run_opencode_jsonl(
                    prompt,
                    model=self.model,
                    permission=self.perms,
                    providers=self.providers,
                    mcp_servers=self.mcp,  # type: ignore[arg-type]
                    session_id=sid,
                    timeout=eff_timeout,
                ):
                    event = parse_event(raw_event)
                    yield event
                    if self._last_session_id is None:
                        self._last_session_id = (
                            getattr(event, "sessionID", None) or None
                        )
            except CliTimeoutError as exc:
                # Timeout occurred, yield timeout event instead of raising
                yield TimeoutEvent(
                    timestamp=unix_ms(),
                    sessionID=sid or self._last_session_id or "",
                    type="timeout",
                    timeout_seconds=exc.timeout,
                    message=str(exc),
                )
            return

        # Structured output path: handle validation and retries
        from slimschema import to_prompt  # type: ignore[import-untyped]

        from .structured import _extract_and_parse_json, _to_slimschema_yaml

        schema_yaml = _to_slimschema_yaml(eff_format)
        validation_format: str | type[BaseModel] | TypeAdapter[Any]
        if isinstance(eff_format, TypeAdapter):
            validation_format = schema_yaml
        else:
            validation_format = eff_format

        attempts = 0
        last_err: str | None = None
        final_session = sid

        while attempts < max_retries:
            attempts += 1

            # Build prompt using slimschema.to_prompt()
            schema_instructions = to_prompt(
                schema_yaml,
                errors=last_err if attempts > 1 else None,
                xml_tag="output",
                fence_language="json",
            )
            rendered_prompt = f"{prompt}\n\n---\n\n{schema_instructions}"

            # Yield prompt rendered event
            yield PromptRenderedEvent(
                timestamp=unix_ms(),
                sessionID=final_session or "",
                type="prompt_rendered",
                prompt=rendered_prompt,
                attempt=attempts,
                schema_yaml=schema_yaml,
            )

            # Stream all events from this attempt
            events: list[OpenCodeEvent] = []
            try:
                async for raw_event in run_opencode_jsonl(
                    rendered_prompt,
                    model=self.model,
                    permission=self.perms,
                    providers=self.providers,
                    mcp_servers=self.mcp,  # type: ignore[arg-type]
                    session_id=final_session,
                    timeout=eff_timeout,
                ):
                    event = parse_event(raw_event)
                    events.append(event)
                    yield event
                    if final_session is None:
                        final_session = (
                            getattr(event, "sessionID", None) or None
                        )
            except CliTimeoutError as exc:
                # Timeout occurred, yield timeout event and exit retry loop
                yield TimeoutEvent(
                    timestamp=unix_ms(),
                    sessionID=final_session or "",
                    type="timeout",
                    timeout_seconds=exc.timeout,
                    message=str(exc),
                )
                break

            # Update session tracking
            if self._last_session_id is None and final_session:
                self._last_session_id = final_session

            # Try to parse and validate the output
            output_text = assemble_output(
                events, reset_on_tool=True, fallback_to_tool=True
            )
            try:
                parsed_output = _extract_and_parse_json(
                    str(output_text), validation_format
                )
                # Validation succeeded!
                yield ValidationSuccessEvent(
                    timestamp=unix_ms(),
                    sessionID=final_session or "",
                    type="validation_success",
                    output=parsed_output,
                    attempt=attempts,
                )
                break
            except ValueError as exc:
                # Validation failed
                last_err = str(exc)
                will_retry = attempts < max_retries
                yield ValidationErrorEvent(
                    timestamp=unix_ms(),
                    sessionID=final_session or "",
                    type="validation_error",
                    error_message=last_err,
                    attempt=attempts,
                    will_retry=will_retry,
                )

                if will_retry:
                    yield RetryEvent(
                        timestamp=unix_ms(),
                        sessionID=final_session or "",
                        type="retry",
                        attempt=attempts + 1,
                        previous_error=last_err,
                    )

    @runtime_checkable
    class AskSync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | TypeAdapter[Any] | None = None,
        ) -> Response[Any]: ...

    @runtime_checkable
    class AskAsync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | TypeAdapter[Any] | None = None,
        ) -> Awaitable[Response[Any]]: ...

    @contextmanager
    def session(self) -> Iterator[AskSync]:
        sid: str | None = None

        def ask(
            prompt: str,
            response_format: type[BaseModel] | TypeAdapter[Any] | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = self.run(
                prompt,
                response_format=eff_format,
                session=sid,
            )
            sid = resp.session_id or sid
            return resp

        yield ask

    @asynccontextmanager
    async def asession(self) -> AsyncIterator[AskAsync]:
        sid: str | None = None

        async def ask(
            prompt: str,
            response_format: type[BaseModel] | TypeAdapter[Any] | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = await self.arun(
                prompt,
                response_format=eff_format,
                session=sid,
            )
            sid = resp.session_id or sid
            return resp

        yield ask


def run(
    prompt: str,
    *,
    model: str,
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None,
    session: str | Response[Any] | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    timeout: float | None = None,
) -> Response[Any]:
    safe_debug_log("API", f"run() START: model={model}, timeout={timeout}")
    try:
        result = Loop(
            model=model, perms=perms, providers=providers, mcp=mcp
        ).run(
            prompt,
            response_format=response_format,
            session=session,
            timeout=timeout,
        )
        safe_debug_log("API", "run() SUCCESS")
        return result
    except Exception as e:
        safe_debug_log("API", f"run() EXCEPTION: {type(e).__name__}: {e}")
        raise


def stream(
    prompt: str,
    *,
    model: str,
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None,
    session: str | Response[Any] | None = None,
    max_retries: int = 3,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    timeout: float | None = None,
) -> Iterator[StreamEvent]:
    """Stream events from the LLM, including structured output validation (sync wrapper).

    This is a synchronous wrapper around astream(). For truly asynchronous streaming,
    use astream() instead.

    See astream() for full documentation.

    Example:
        >>> for event in stream("What is 2 + 2?", model="opencode/big-pickle"):
        ...     if event.type == "text":
        ...         print(event.text, end="", flush=True)
        ...     elif event.type == "validation_success":
        ...         print(f"\\nParsed output: {event.output}")
    """
    loop_inst = Loop(model=model, perms=perms, providers=providers, mcp=mcp)
    yield from loop_inst.stream(
        prompt,
        response_format=response_format,
        session=session,
        max_retries=max_retries,
        timeout=timeout,
    )


async def arun(
    prompt: str,
    *,
    model: str,
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None,
    session: str | Response[Any] | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    timeout: float | None = None,
) -> Response[Any]:
    return await Loop(
        model=model, perms=perms, providers=providers, mcp=mcp
    ).arun(
        prompt,
        response_format=response_format,
        session=session,
        timeout=timeout,
    )


async def astream(
    prompt: str,
    *,
    model: str,
    response_format: str | type[BaseModel] | TypeAdapter[Any] | None = None,
    session: str | Response[Any] | None = None,
    max_retries: int = 3,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    timeout: float | None = None,
) -> AsyncIterator[StreamEvent]:
    """Stream events from the LLM in real-time, including structured output validation.

    This function streams all events as they occur, including:
    - OpenCode events (step_start, text, tool_use, step_finish, error)
    - Structured output validation events (validation_error, validation_success, retry)

    When response_format is provided, the function will:
    1. Stream all OpenCode events from each attempt
    2. Validate the output against the response_format
    3. Yield ValidationSuccessEvent if validation passes
    4. Yield ValidationErrorEvent and RetryEvent if validation fails (and retries remain)

    Args:
        prompt: The user prompt to send to the LLM
        model: Model ID (e.g., "opencode/big-pickle")
        response_format: Optional Pydantic model or TypeAdapter for structured output
        session: Optional session ID or Response object for multi-turn conversations
        max_retries: Maximum number of validation retry attempts (default: 3)
        perms: Permission settings controlling what tools the LLM can use
        providers: Optional provider configurations
        mcp: Optional MCP (Model Context Protocol) servers
        timeout: Idle timeout in seconds (how long to wait for next event)

    Yields:
        StreamEvent: OpenCodeEvent, ValidationErrorEvent, ValidationSuccessEvent, or RetryEvent

    Example:
        >>> async for event in astream("What is 2 + 2?", model="opencode/big-pickle"):
        ...     if event.type == "text":
        ...         print(event.text, end="", flush=True)
        ...     elif event.type == "validation_success":
        ...         print(f"\\nParsed output: {event.output}")
    """
    loop = Loop(model=model, perms=perms, providers=providers, mcp=mcp)
    async for event in loop.astream(
        prompt,
        response_format=response_format,
        session=session,
        max_retries=max_retries,
        timeout=timeout,
    ):
        yield event


__all__ = [
    "Loop",
    "run",
    "arun",
    "stream",
    "astream",
    "allow",
    "mcp",
]
