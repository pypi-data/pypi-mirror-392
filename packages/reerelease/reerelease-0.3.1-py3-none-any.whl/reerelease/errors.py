from __future__ import annotations

from collections.abc import Sequence


class AppError(Exception):
    """Base class for all custom exceptions in the application."""

    """Base class for all context-related exceptions.

    Supports two types of error aggregation:
    - `issues`: List of validation error messages (strings) from low-level validators
    - `causes`: List of sub-exceptions that caused this error (for aggregating multiple failures)
    """

    def __init__(
        self,
        message: str | None = None,
        issues: Sequence[str] | None = None,
        causes: Sequence[Exception] | None = None,
    ) -> None:
        """Create a ContextError with an optional message, issues, and/or causes.

        Args:
            message: Human-readable error description
            issues: Validation error strings from low-level validators
            causes: Sub-exceptions that caused this error (for aggregation)
        """
        super().__init__(message)
        self.message = message
        # Make copies so callers can mutate their original lists without affecting us
        self.issues: list[str] = list(issues) if issues else []
        self.causes: list[Exception] = list(causes) if causes else []

    def add_issue(self, issue: str) -> None:
        """Append an issue to the stored issues list."""
        self.issues.append(issue)

    def add_cause(self, cause: AppError) -> None:
        """Append a sub-exception to the stored causes list."""
        self.causes.append(cause)

    def get_all_issues(self) -> list[str]:
        """Get all issues including those from nested causes.

        Returns:
            Flattened list of all issue strings from this exception and all causes.
        """
        all_issues = list(self.issues)
        for cause in self.causes:
            # Be defensive: causes may not always be AppError instances at
            # runtime (some callers cast or forward raw Exceptions). If a
            # cause implements `get_all_issues()` use it; otherwise include
            # the stringified exception so we don't raise AttributeError.
            if isinstance(cause, AppError):
                all_issues.extend(cause.get_all_issues())
            else:
                all_issues.append(str(cause))
        return all_issues

    def __str__(self) -> str:
        base = self.message or self.__class__.__name__
        parts = [base]

        if self.issues:
            parts.append(f"issues: {', '.join(self.issues)}")

        if self.causes:
            cause_summary = [type(c).__name__ for c in self.causes]
            parts.append(f"causes: {', '.join(cause_summary)}")

        return " | ".join(parts) if len(parts) > 1 else parts[0]


# ---- context ---- #
class ContextError(AppError):
    """Base class for all context-related exceptions."""

    pass


class ContextDiscoveryError(ContextError):
    """Raised when context discovery fails."""

    pass


class ContextCreationError(ContextError):
    """Raised when context creation fails.

    Inherits issues/message behavior from `ContextError` so callers can inspect
    `exc.issues` or use `str(exc)` for a human-friendly summary.
    """

    pass


class ContextDeletionError(ContextError):
    """Raised when a context cannot be deleted (e.g., non-leaf or confirmation required)."""

    pass


class ContextUpdateError(ContextError):
    """Raised when a context cannot be updated/renamed."""

    pass


class InvalidContextName(ContextError):
    """Raised when the provided context name is invalid (format/characters)."""

    def __init__(
        self,
        message: str | None = None,
        *,
        name: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.name = name


class InvalidTargetPath(ContextError):
    """Raised when the target path for context creation is invalid or not usable."""

    def __init__(
        self,
        message: str | None = None,
        *,
        path: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.path = path


class ContextAlreadyExists(ContextError):
    """Raised when the target location already contains a context and --force was not provided."""

    def __init__(
        self,
        message: str | None = None,
        *,
        existing_path: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.existing_path = existing_path


class NoContextFound(ContextError):
    """Raised when no context could be found in the specified path."""

    def __init__(
        self,
        message: str | None = None,
        *,
        search_path: str | None = None,
    ) -> None:
        super().__init__(message)
        self.search_path = search_path


# ---- template ---- #
class TemplateError(AppError):
    """Base class for all template-related exceptions."""

    pass


class TemplateCreationError(TemplateError):
    """Raised when template creation fails."""

    pass


# ---- milestone ---- #
class MilestoneError(AppError):
    """Base class for all milestone-related exceptions."""

    pass


class MilestoneDiscoveryError(MilestoneError):
    """Raised when milestone discovery fails."""

    pass


class MilestoneCreationError(MilestoneError):
    """Raised when milestone creation fails.

    Inherits issues/message behavior from `MilestoneError` so callers can inspect
    `exc.issues` or use `str(exc)` for a human-friendly summary.
    """

    pass


class MilestoneDeletionError(MilestoneError):
    """Raised when a milestone cannot be deleted."""

    pass


class MilestoneUpdateError(MilestoneError):
    """Raised when a milestone cannot be updated."""

    pass


class InvalidMilestoneName(MilestoneError):
    """Raised when the provided milestone name is invalid (format/characters)."""

    def __init__(
        self,
        message: str | None = None,
        *,
        name: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.name = name


class InvalidMilestoneStatus(MilestoneError):
    """Raised when the provided milestone status is invalid."""

    def __init__(
        self,
        message: str | None = None,
        *,
        status: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.status = status


class InvalidMilestoneDate(MilestoneError):
    """Raised when the provided milestone date is invalid."""

    def __init__(
        self,
        message: str | None = None,
        *,
        date: str | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.date = date


class NoMilestoneFound(MilestoneError):
    """Raised when no milestone could be found."""

    def __init__(
        self,
        message: str | None = None,
        *,
        milestone_name: str | None = None,
        context_filepath: str | None = None,
    ) -> None:
        super().__init__(message)
        self.milestone_name = milestone_name
        self.context_filepath = context_filepath


class DuplicateMilestone(MilestoneError):
    """Raised when trying to create a milestone with a name that already exists."""

    def __init__(
        self,
        message: str | None = None,
        *,
        milestone_name: str | None = None,
        context_filepath: str | None = None,
    ) -> None:
        super().__init__(message)
        self.milestone_name = milestone_name
        self.context_filepath = context_filepath


# ---- task ---- #


# ---- problem ---- #


# ---- domain ---- #


# ---- DSL (Template DSL Pipeline) ---- #
class DSLError(AppError):
    """Base class for all Template DSL-related exceptions."""

    pass


class Phase1Error(DSLError):
    """Raised when template annotation parsing fails (Phase 1).

    Phase 1 parses template files to extract @field, @section, and other
    annotations to build the TemplateSpec. Issues include malformed annotations,
    invalid field types, duplicate definitions, etc.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        source_path: str | None = None,
        location: dict[str, int] | None = None,
        issues: Sequence[str] | None = None,
        causes: Sequence[Exception] | None = None,
    ) -> None:
        super().__init__(message, issues=issues, causes=causes)
        self.source_path = source_path  # Template file being parsed
        self.location = location  # {"start_offset": int, "end_offset": int, ...}


class Phase2Error(DSLError):
    """Raised when markdown document parsing fails (Phase 2).

    Phase 2 parses markdown documents against a TemplateSpec to extract
    structured memory. Issues include missing required fields, malformed
    sections, invalid field values, etc.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        source_path: str | None = None,
        location: dict[str, int] | None = None,
        issues: Sequence[str] | None = None,
        causes: Sequence[Exception] | None = None,
    ) -> None:
        super().__init__(message, issues=issues, causes=causes)
        self.source_path = source_path  # Markdown file being parsed
        self.location = location  # {"start_offset": int, "end_offset": int, ...}


class Phase3Error(DSLError):
    """Raised when template rendering fails (Phase 3).

    Phase 3 renders ParsedMemory back to markdown using Jinja2 templates.
    Issues include template syntax errors, undefined variables, rendering failures.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        template_name: str | None = None,
        block_index: int | None = None,
        block_name: str | None = None,
        issues: Sequence[str] | None = None,
        causes: Sequence[Exception] | None = None,
    ) -> None:
        super().__init__(message, issues=issues, causes=causes)
        self.template_name = template_name
        self.block_index = block_index
        self.block_name = block_name


class Phase4Error(DSLError):
    """Raised when memory validation fails (Phase 4).

    Phase 4 validates ParsedMemory against TemplateSpec requirements.
    Issues include missing required fields, format violations, pattern mismatches.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        issues: Sequence[str] | None = None,
        causes: Sequence[Exception] | None = None,
    ) -> None:
        super().__init__(message, issues=issues, causes=causes)


class DocumentReconstructionError(DSLError):
    """Raised when merging managed/unmanaged content fails (Phase 3).

    This indicates a bug in the reconstruction algorithm or invalid state.
    """

    def __init__(
        self,
        message: str | None = None,
        *,
        managed_blocks_count: int | None = None,
        unmanaged_regions_count: int | None = None,
        issues: Sequence[str] | None = None,
    ) -> None:
        super().__init__(message, issues=issues)
        self.managed_blocks_count = managed_blocks_count
        self.unmanaged_regions_count = unmanaged_regions_count
