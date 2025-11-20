from __future__ import annotations

import os
import time


def safe_debug_log(category: str, message: str) -> None:
    """Best-effort debug logger to an opt-in file.

    - Only logs when `INNERLOOP_LOG_FILE` env var is set to a writable path.
    - Never raises; failures to write are silently ignored.
    - Callers must avoid writing sensitive contents (API keys, prompts, etc.).
    """
    path = os.getenv("INNERLOOP_LOG_FILE")
    if not path:
        return
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{category}] {message}\n")
            f.flush()
        # Best-effort tighten perms on first write
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass
    except Exception:
        # Never let debug logging impact main code paths
        pass


def to_session_id(item: str | object | None) -> str | None:
    """Return a session id string from a Response or string.

    - If ``item`` is a Response, returns ``item.session_id``.
    - If ``item`` is a string, returns it unchanged.
    - If ``item`` is None, returns None.
    """
    # Avoid importing Response to prevent circular import; duck-type on attribute.
    if item is None or isinstance(item, str):
        return item
    sid = getattr(item, "session_id", None)
    return sid if isinstance(sid, str) else None


def unix_ms() -> int:
    """Current wall-clock time in Unix milliseconds as an int."""
    return int(time.time() * 1000)
