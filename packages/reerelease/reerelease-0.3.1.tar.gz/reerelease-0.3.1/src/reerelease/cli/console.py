"""Console output utilities."""

from functools import singledispatch
from typing import Any, NoReturn

import typer
from rich import print as rprint

from reerelease.cli.error_codes import GENERAL_ERROR, OK, USAGE_ERROR
from reerelease.errors import (
    AppError,
    ContextAlreadyExists,
    ContextCreationError,
    ContextDeletionError,
    ContextDiscoveryError,
    ContextError,
    DocumentReconstructionError,
    DSLError,
    InvalidContextName,
    InvalidTargetPath,
    MilestoneError,
    NoContextFound,
    Phase1Error,
    Phase3Error,
    TemplateCreationError,
    TemplateError,
)

from ..config import get_config


def quiet_print(*args: Any, **kwargs: Any) -> None:
    """Print only if not in quiet mode."""
    cfg = get_config()
    if not cfg.quiet:
        rprint(*args, **kwargs)


def exit_with(code: int) -> NoReturn:
    """Exit using Typer's mechanism from the CLI layer.

    Keep this function in the CLI package so core code never needs to import
    typer directly.
    """
    raise typer.Exit(code=code)


# ---- Exception printing and exit code handling ---- #
def print_exception(root_exception: AppError) -> int:
    """Print exception tree with causes and issues, return appropriate exit code.

    Prints a hierarchical tree showing the exception, its issues, and any nested causes.
    Exit code is determined by the root exception type.
    """
    _print_exception_tree(root_exception, indent=0)
    return _get_exit_code(root_exception)


def _print_exception_tree(exc: Exception, indent: int = 0) -> None:
    """Recursively print exception tree with proper indentation.

    Args:
        exc: The exception to print (can be AppError or any Exception)
        indent: Current indentation level (0 = root)
    """
    prefix = "  " * indent

    # Format and print the exception header
    exc_name = type(exc).__name__
    exc_message = _format_exception_message(exc)
    quiet_print(f"{prefix}{exc_name}: {exc_message}")

    # Print extra context for specific exception types
    _print_exception_context(exc, prefix)

    # Print issues if this is an AppError with issues
    if isinstance(exc, AppError) and exc.issues:
        for issue in exc.issues:
            quiet_print(f"{prefix}  - {issue}")

    # Recursively print nested causes
    if isinstance(exc, AppError) and exc.causes:
        for cause in exc.causes:
            _print_exception_tree(cause, indent + 1)


@singledispatch
def _format_exception_message(exc: Exception) -> str:
    """Format the message for an exception. Override for specific types.

    This uses singledispatch for extensibility - register new formatters
    for custom exception types without modifying this function.
    """
    # Default: use the exception's message attribute or basic str if no message
    if isinstance(exc, AppError):
        # For AppError, return just the message, not the full __str__ representation
        return f"[red]{exc.message or type(exc).__name__}[/red]"
    return str(exc)


@_format_exception_message.register(NoContextFound)
def _format_no_context_found(exc: NoContextFound) -> str:
    """Format NoContextFound with yellow styling."""
    message = exc.message or "No context found"
    return f"[yellow]{message}[/yellow]"


@_format_exception_message.register(InvalidContextName)
def _format_invalid_context_name(exc: InvalidContextName) -> str:
    """Format InvalidContextName with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(InvalidTargetPath)
def _format_invalid_target_path(exc: InvalidTargetPath) -> str:
    """Format InvalidTargetPath with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(ContextAlreadyExists)
def _format_context_already_exists(exc: ContextAlreadyExists) -> str:
    """Format ContextAlreadyExists with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red], use [--force] to override"


@_format_exception_message.register(ContextCreationError)
def _format_context_creation_error(exc: ContextCreationError) -> str:
    """Format ContextCreationError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(ContextDeletionError)
def _format_context_deletion_error(exc: ContextDeletionError) -> str:
    """Format ContextDeletionError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(ContextDiscoveryError)
def _format_context_discovery_error(exc: ContextDiscoveryError) -> str:
    """Format ContextDiscoveryError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(ContextError)
def _format_context_error(exc: ContextError) -> str:
    """Format ContextError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(MilestoneError)
def _format_milestone_error(exc: MilestoneError) -> str:
    """Format MilestoneError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(TemplateError)
def _format_template_error(exc: TemplateError) -> str:
    """Format TemplateError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(TemplateCreationError)
def _format_template_creation_error(exc: TemplateCreationError) -> str:
    """Format TemplateCreationError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(DSLError)
def _format_dsl_error(exc: DSLError) -> str:
    """Format DSLError with red styling."""
    message = exc.message or type(exc).__name__
    return f"[red]{message}[/red]"


@_format_exception_message.register(Phase1Error)
def _format_phase1_error(exc: Phase1Error) -> str:
    """Format Phase1Error with red styling and file context."""
    message = exc.message or "Phase 1 error"
    return f"[red]{message}[/red]"


@_format_exception_message.register(Phase3Error)
def _format_phase3_error(exc: Phase3Error) -> str:
    """Format Phase3Error with red styling and template context."""
    message = exc.message or "Phase 3 error"
    if exc.template_name:
        return f"[red]{message}[/red] in template [yellow]{exc.template_name}[/yellow]"
    return f"[red]{message}[/red]"


@_format_exception_message.register(DocumentReconstructionError)
def _format_document_reconstruction_error(exc: DocumentReconstructionError) -> str:
    """Format DocumentReconstructionError with red styling."""
    message = exc.message or "Document reconstruction error"
    return f"[red]{message}[/red]"


def _print_exception_context(exc: Exception, prefix: str) -> None:
    """Print additional contextual information for specific exception types.

    Args:
        exc: The exception to print context for
        prefix: Current indentation prefix
    """
    if isinstance(exc, InvalidContextName) and exc.name:
        quiet_print(f"{prefix}  name: {exc.name}")
    elif isinstance(exc, InvalidTargetPath) and exc.path:
        quiet_print(f"{prefix}  path: {exc.path}")
    elif isinstance(exc, ContextAlreadyExists) and exc.existing_path:
        quiet_print(f"{prefix}  existing_path: {exc.existing_path}")
    elif isinstance(exc, NoContextFound) and exc.search_path:
        quiet_print(f"{prefix}  searched_path: {exc.search_path}")
    elif isinstance(exc, Phase1Error):
        if exc.source_path:
            quiet_print(f"{prefix}  source: {exc.source_path}")
        if exc.location:
            offsets = exc.location
            if "start_offset" in offsets and "end_offset" in offsets:
                quiet_print(
                    f"{prefix}  location: [{offsets['start_offset']}, {offsets['end_offset']})"
                )
    elif isinstance(exc, Phase3Error):
        if exc.template_name:
            quiet_print(f"{prefix}  template: {exc.template_name}")
        if exc.block_index is not None:
            quiet_print(f"{prefix}  block_index: {exc.block_index}")
        if exc.block_name:
            quiet_print(f"{prefix}  block_name: {exc.block_name}")
    elif isinstance(exc, DocumentReconstructionError):
        if exc.managed_blocks_count is not None:
            quiet_print(f"{prefix}  managed_blocks: {exc.managed_blocks_count}")
        if exc.unmanaged_regions_count is not None:
            quiet_print(f"{prefix}  unmanaged_regions: {exc.unmanaged_regions_count}")


@singledispatch
def _get_exit_code(exc: AppError) -> int:
    """Get the appropriate exit code for an exception type.

    This uses singledispatch for clean, extensible exit code mapping.
    Register new exception types without modifying this function.
    """
    return GENERAL_ERROR


# Register exit codes for specific exception types
_get_exit_code.register(NoContextFound)(lambda exc: OK)
_get_exit_code.register(InvalidContextName)(lambda exc: USAGE_ERROR)
_get_exit_code.register(InvalidTargetPath)(lambda exc: USAGE_ERROR)
_get_exit_code.register(ContextAlreadyExists)(lambda exc: USAGE_ERROR)
