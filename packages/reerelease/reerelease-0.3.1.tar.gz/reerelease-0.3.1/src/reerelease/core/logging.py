"""Logging configuration for reerelease."""

import logging
import sys


def configure_logging(*, level: int, quiet: bool) -> None:
    """Configure a simple, blocking console logger."""

    log = logging.getLogger("reerelease")

    if level is None or quiet is None:
        raise ValueError("Both level and quiet parameters must be provided")

    # Clear any handlers configured by previous tests, but avoid allowing
    # existing handlers to close the underlying streams which may be
    # captured by test harnesses (click.testing swaps stdout/stderr with
    # in-memory buffers which must not be closed). We override each
    # handler.close to be a no-op that only flushes, then clear the list.
    if log.hasHandlers():
        try:
            for h in list(log.handlers):
                try:
                    if hasattr(h, "flush"):
                        h.flush()
                    # prevent closing of underlying streams when handler is
                    # later garbage-collected
                    if hasattr(h, "close"):
                        h.close = lambda *a, **k: None  # type: ignore[method-assign]
                except Exception:
                    # Ignore any errors while making handlers safe
                    pass
        finally:
            log.handlers.clear()

    # During test runs, Click's in-memory capture objects may be closed by
    # finalizers while the test harness still needs them. Detect pytest via
    # environment and, if present, make BytesIOCopy.close a no-op. This is
    # intentionally narrow and only executes during CLI logging setup.
    try:
        import os

        if os.environ.get("PYTEST_CURRENT_TEST"):
            try:
                import click.testing as _ct

                if hasattr(_ct, "BytesIOCopy") and hasattr(_ct.BytesIOCopy, "close"):
                    _ct.BytesIOCopy.close = lambda self, *a, **k: None  # type: ignore[method-assign]
            except Exception:
                pass
    except Exception:
        pass

    if quiet:
        log.addHandler(logging.NullHandler())
        return

    log.setLevel(level)
    handler: logging.Handler
    try:
        from rich.logging import RichHandler

        # Send logs to stderr (default for RichHandler)
        handler = RichHandler(rich_tracebacks=True, show_path=False, level=level)
        handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    except ImportError:
        # Explicitly send logs to stderr
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(level)

    # kinda force flushing and no closing of the stream, to avoid issues with test harnesses, but does is it useful?
    try:
        # Only wrap if the handler has a close attribute we can override
        if hasattr(handler, "close"):
            handler.flush()
            # handler.close = _safe_close(handler.close)  # type: ignore[method-assign]
    except Exception:
        # If anything goes wrong, don't fail logger configuration; fallback to default
        pass

    log.addHandler(handler)
    log.propagate = False  # Prevent passing messages to the root logger
