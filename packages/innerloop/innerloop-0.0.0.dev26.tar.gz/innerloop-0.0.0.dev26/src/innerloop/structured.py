from __future__ import annotations

from typing import Any

from pydantic import BaseModel, TypeAdapter
from slimschema import to_data, to_schema  # type: ignore[import-untyped]

from .events import ErrorEvent, StreamEvent, TimeInfo
from .helper import unix_ms
from .logging_config import get_logger
from .request import Request
from .response import Response
from .usage import compute_usage

logger = get_logger("structured")


def _to_slimschema_yaml(
    response_format: str | type[BaseModel] | TypeAdapter[Any],
) -> str:
    """Convert a response format into token-efficient SlimSchema YAML."""

    if isinstance(response_format, str):
        return response_format

    schema = to_schema(response_format)
    return str(schema)


def _extract_and_parse_json(
    text: str, validation_format: str | type[BaseModel] | TypeAdapter[Any]
) -> Any:
    """Extract and validate JSON using SlimSchema's parser/validator."""

    data, error = to_data(text, validation_format)
    if error is not None:
        raise ValueError(error)
    return data


async def _attempt(
    request: Request,
    *,
    prompt: str,
    validation_format: str | type[BaseModel] | TypeAdapter[Any],
    session: str | None,
    timeout: float | None = None,
) -> tuple[Response[Any], Any | None, str | None]:
    from .invoke import async_invoke  # local import to avoid cycles

    resp = await async_invoke(
        Request(
            model=request.model,
            prompt=prompt,
            permission=request.permission,
            providers=request.providers,
            mcp=request.mcp,
            response_format=None,
            session=session,
        ),
        timeout=timeout,
    )

    try:
        out = _extract_and_parse_json(str(resp.output), validation_format)
    except ValueError as exc:
        return resp, None, str(exc)

    return resp, out, None


async def invoke_structured(
    request: Request,
    *,
    max_retries: int = 3,
    timeout: float | None = None,
) -> Response[Any]:
    """Structured output invocation with SlimSchema validation and retry."""
    from slimschema import to_prompt  # import slimschema's to_prompt

    if request.response_format is None:
        from .invoke import async_invoke  # local import

        return await async_invoke(request, timeout=timeout)

    schema_yaml = _to_slimschema_yaml(request.response_format)
    validation_format: str | type[BaseModel] | TypeAdapter[Any]
    if isinstance(request.response_format, TypeAdapter):
        validation_format = schema_yaml
    else:
        validation_format = request.response_format

    logger.info(
        "Starting structured invocation (max_retries=%s, model=%s)",
        max_retries,
        request.model,
    )
    logger.debug(
        "Response format: %s",
        getattr(request.response_format, "__name__", "SlimSchema"),
    )

    attempts = 0
    total_events: list[StreamEvent] = []
    final_session: str | None = request.session
    final_output: BaseModel | dict[str, Any] | None = None
    wall_start = unix_ms()
    last_err: str | None = None

    while attempts < max_retries:
        attempts += 1
        logger.info("Attempt %s/%s", attempts, max_retries)

        # Build prompt using slimschema.to_prompt()
        schema_instructions = to_prompt(
            schema_yaml,
            errors=last_err if attempts > 1 else None,
            xml_tag="output",
            fence_language="json",
        )

        # Combine user prompt + schema instructions
        prompt = f"{request.prompt}\n\n---\n\n{schema_instructions}"

        if attempts > 1:
            logger.warning(
                "Retrying structured output validation (attempt %s/%s) - Previous validation error: %s",
                attempts,
                max_retries,
                last_err,
            )

        resp, out, err = await _attempt(
            request,
            prompt=prompt,
            validation_format=validation_format,
            session=final_session,
            timeout=timeout,
        )
        total_events.extend(resp.events)
        final_session = resp.session_id

        if out is not None:
            final_output = out
            logger.info(
                "Structured output validation successful on attempt %s",
                attempts,
            )
            break

        last_err = err or "Validation failed"
        logger.warning(
            "Validation failed on attempt %s: %s", attempts, last_err
        )

        total_events.append(
            ErrorEvent(
                timestamp=unix_ms(),
                sessionID=final_session or "",
                type="error",
                message=last_err,
                code=None,
                severity="error",
            )
        )

    if final_output is None:
        logger.error(
            "Structured output validation failed after %s attempts. Final error: %s",
            attempts,
            last_err,
        )
        raise RuntimeError(
            "Structured output validation failed after "
            f"{attempts} attempts. Error: {last_err}"
        )

    wall_end = unix_ms()
    logger.info(
        "Structured invocation completed successfully after %s attempt(s)",
        attempts,
    )
    logger.debug(
        "Total events: %s, Session: %s", len(total_events), final_session
    )

    out_resp = Response(
        session_id=final_session or "",
        input=request.prompt,
        output=final_output,
        events=total_events,
        attempts=attempts,
        time=TimeInfo(start=wall_start, end=wall_end),
    )
    out_resp.usage = compute_usage(total_events)
    return out_resp
