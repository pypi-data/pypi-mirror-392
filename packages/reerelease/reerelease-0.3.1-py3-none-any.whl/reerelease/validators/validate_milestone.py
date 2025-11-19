"""Validators for Milestone objects and related data."""

import datetime
import unicodedata

from ..config import DEFAULTS, get_config
from ..core.milestone import Milestone


def validate_milestone_name(name: str) -> list[str]:
    """Validate a milestone name.

    Return a list of issues found.

    Verification is based on:
    - non-empty name
    - no leading/trailing whitespace
    - no path separators
    - length within limits
    - no control characters
    - printable characters only (after normalization)
    """
    issues: list[str] = []

    assert name is not None, "name is None"

    if not name or not name.strip():
        issues.append("Milestone name is empty")
        return issues

    if name != name.strip():
        issues.append(f"Milestone name '{name}' has leading or trailing whitespace")

    # Check for path separators
    if "/" in name or "\\" in name:
        issues.append(f"Milestone name '{name}' contains path separators")

    # Check length
    if len(name) > DEFAULTS.max_name_length:
        issues.append(
            f"Milestone name '{name}' exceeds maximum length of {DEFAULTS.max_name_length} characters"
        )

    # Normalize unicode (NFC) so accents/emoji are handled consistently
    try:
        name_normalized = unicodedata.normalize("NFC", name)
    except Exception:
        name_normalized = name

    # Reject control characters and nulls explicitly
    # Control characters are in categories Cc (Other, control)
    for ch in name_normalized:
        if unicodedata.category(ch) == "Cc":
            issues.append("Milestone name contains control characters or nulls")
            break

    # After normalization, allow any printable characters except path separators
    # and a small set of disallowed control-like characters. We already checked for
    # path separators earlier. We also disallow ASCII DEL (0x7F) as non-printable.
    if any(ord(ch) == 0x7F for ch in name_normalized):
        issues.append("Milestone name contains non-printable characters")

    # Final sanity: ensure name is still within allowed length after normalization
    if len(name_normalized) > DEFAULTS.max_name_length:
        issues.append(
            f"Milestone name '{name}' exceeds maximum length of {DEFAULTS.max_name_length} characters"
        )

    return issues


def validate_milestone_status(status: str) -> list[str]:
    """Validate a milestone status string format.

    Validates that the status is a non-empty string and matches
    one of the configured valid milestone statuses.

    Return a list of issues found.

    Args:
        status: The status string to validate
    """
    issues: list[str] = []

    assert status is not None, "Status is None"

    if not isinstance(status, str):
        issues.append(f"Milestone status must be a string, not {type(status).__name__}")  # type: ignore
        return issues

    if not status or not status.strip():
        issues.append("Milestone status cannot be empty")
        return issues

    # Validate against configured statuses
    cfg = get_config()
    valid_statuses = cfg.milestone_statuses
    if valid_statuses:
        valid_status_values: list[str] = [s.desc for s in valid_statuses]
        if status not in valid_status_values:
            valid_status_names = ", ".join(valid_status_values)
            issues.append(f"Invalid status: {status}, must be one of: {valid_status_names}")

    return issues


def validate_milestone_date(target_date: datetime.date | str) -> list[str]:
    """Validate a milestone target date.

    Return a list of issues found.

    Verification is based on:
    - date is a valid datetime.date or can be parsed
    """
    issues: list[str] = []

    assert target_date is not None, "Target date is None"

    # If it's a string, try to parse it
    if isinstance(target_date, str):
        try:
            parsed_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
            target_date = parsed_date
        except ValueError:
            issues.append(
                f"Milestone target date '{target_date}' is not a valid date format. "
                "Expected YYYY-MM-DD"
            )

    # If it's not a datetime.date at this point, it's invalid
    if not isinstance(target_date, datetime.date):
        issues.append(f"Milestone target date '{target_date}' is not a datetime.date object")
        return issues

    return issues


def validate_milestone_description(description: str) -> list[str]:
    """Validate a milestone description.

    Return a list of issues found.

    Verification is based on:
    - description is not None
    - description is not empty or just whitespace
    - length within limits
    """
    issues: list[str] = []

    assert description is not None, "Description is None"

    if not description.strip():
        issues.append("Milestone description is empty or just whitespace")

    if len(description) > DEFAULTS.max_description_length:
        issues.append(
            f"Milestone description exceeds maximum length of {DEFAULTS.max_description_length} characters"
        )

    return issues


def validate_milestone(milestone: Milestone) -> list[str]:
    """Validate a complete Milestone object.

    This aggregator function validates all aspects of a milestone:
    - name
    - status
    - target_date

    Updates the milestone's `issues` attributes.

    Returns:
        List of all validation issues found.
    """
    all_issues: list[str] = []

    assert milestone is not None, "Milestone is None"

    # Validate name
    name_issues = validate_milestone_name(milestone.name)
    all_issues.extend(name_issues)

    # Validate status
    status_issues = validate_milestone_status(str(milestone.status))
    all_issues.extend(status_issues)

    # Validate target date
    date_issues = validate_milestone_date(milestone.target_date)
    all_issues.extend(date_issues)

    # Additional validations
    desc_issues = validate_milestone_description(milestone.description)
    all_issues.extend(desc_issues)

    # TODO: revise this when tasks are implemented, may need to explore a tree
    # # Check for task consistency
    # if milestone.status == "completed" and milestone.tasks:
    #     incomplete_tasks = [t for t in milestone.tasks if not t.completed]
    #     if incomplete_tasks:
    #         all_issues.append(
    #             f"Milestone '{milestone.name}' is marked completed but has "
    #             f"{len(incomplete_tasks)} incomplete tasks"
    #         )

    # attach issues to milestone
    milestone.issues = all_issues

    return all_issues
