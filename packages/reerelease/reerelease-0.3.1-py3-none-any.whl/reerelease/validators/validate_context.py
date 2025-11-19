"""Validators for Context objects and related data."""

import os
import pathlib

from ..config import DEFAULTS
from ..core.context import Context
from ..service.template_manager import TemplateManager


def validate_context_file(path: pathlib.Path) -> list[str]:
    """Check if a directory contains a valid context.
    Return a list of issues found, empty if valid.

    Verification is based on presence of:
    - required files from templates
    - nominal content of required files (validated via DSL pipeline)
    - readability of required files
    - Corrected typing of arguments
    """
    issues: list[str] = []

    # Get required files from templates
    # TODO: this should be cached, or passed from outside, also should not simply be an "issue", should raise
    templates = TemplateManager().get_templates("context")
    required_files = [output_name for _, output_name in templates]
    if not required_files:  # no templates found
        issues.append("No template files found")
        return issues

    # Check for presence of each required file
    assert path is not None, "Path is None"
    assert isinstance(path, pathlib.Path), f"Context path is not a pathlib.Path but {type(path)}"

    # Build a mapping of output filename to template filename
    template_map = {output_name: template_name for template_name, output_name in templates}

    # Check for presence of each required file and validate content
    for file in required_files:
        file_path = path / file
        try:
            # Check file can be read
            _file_content = file_path.read_text(encoding="utf-8")

            # Validate file content using DSL pipeline
            template_name = template_map.get(file)
            if template_name:
                dsl_issues = _validate_file_with_dsl(file_path, template_name)
                issues.extend(dsl_issues)

        # File missing
        except FileNotFoundError:
            issues.append(f"Missing required {file} in '{path}'")
        # Reading errors
        except PermissionError:
            issues.append(f"Permission error accessing '{path} / {file}'")

    return issues


def _validate_file_with_dsl(file_path: pathlib.Path, template_name: str) -> list[str]:
    """Validate a file using the DSL pipeline.

    Args:
        file_path: Path to the file to validate
        template_name: Name of the template file (e.g., "context/roadmap.md.j2")

    Returns:
        List of validation issues found, empty if valid
    """
    from ..errors import DSLError
    from ..service.dsl.pipeline import DSLPipeline

    issues: list[str] = []

    try:
        # Get template directory and construct template path
        template_manager = TemplateManager()
        templates_base_dir = template_manager.get_templates_dir()
        template_path = templates_base_dir / template_name

        if not template_path.exists():
            # If template doesn't exist, skip DSL validation
            return issues

        # Get the parent directory for Jinja2 template includes
        template_dir = templates_base_dir

        # Read file content
        file_content = file_path.read_text(encoding="utf-8")

        # Create pipeline from template and validate
        pipeline = DSLPipeline.from_template(template_path, template_dir)
        pipeline.parse_and_validate(file_content, fail_fast=False)

    except DSLError as e:
        # Extract all issues from the DSL error
        all_issues = e.get_all_issues()
        for issue in all_issues:
            issues.append(f"{file_path.name}: {issue}")
    except Exception as e:
        # Catch unexpected errors during validation
        issues.append(f"{file_path.name}: Validation error - {str(e)}")

    return issues


def validate_context_name(name: str) -> list[str]:
    """Validate a context name
    Return a list of issues found

    Verification is based on:
    - non-empty name
    - no spaces
    - no path separators
    - length within limits"""
    issues: list[str] = []
    assert name is not None, "name is None"

    if not name or not name.strip():
        issues.append("Context name is empty")

    if " " in name:
        issues.append(f"Context name '{name}' contains spaces")

    if "/" in name or "\\" in name:
        issues.append(f"Context name '{name}' contains path separators")

    if len(name) > DEFAULTS.max_name_length:
        issues.append(
            f"Context name '{name}' exceeds maximum length of {DEFAULTS.max_name_length} characters"
        )

    return issues


def validate_context_path(path: pathlib.Path, mode: str = "existing") -> list[str]:
    """Validate a context path
    Args:
        path: Path to validate.
        mode: Validation mode:
            - "existing": path must exist and be a directory. (default)
            - "creation": path may not exist; parent must exist and be writable.

    Returns:
        List of issue strings. Empty list means valid.

    Verification is based on:
    - correct typing of path
    - path is a directory
    - path exist and is writable (in "existing" mode) OR parent exist and is writable (in "creation" mode)
    - path does not contain invalid characters
    - path is not a symlink
    """

    issues: list[str] = []

    assert path is not None, "Path is None"

    assert isinstance(path, pathlib.Path), f"Context path is not a pathlib.Path but {type(path)}"

    # Check for invalid characters in path
    present_invalid = {c for c in set(DEFAULTS.invalid_path_chars) if c in str(path)}
    if present_invalid:
        issues.append(f"Context path '{path}' contains invalid character(s): {present_invalid}")

    if path.is_symlink():
        issues.append(f"Context path '{path}' is a symbolic link")

    if mode == "existing":
        # Must exist, must be directory, must be readable
        if not path.exists():
            issues.append(f"Context path '{path}' does not exist")
        elif not path.is_dir():
            issues.append(f"Context path '{path}' is not a directory")
        elif not os.access(path, os.R_OK):
            issues.append(f"Context path '{path}' is not readable")
        elif not os.access(path, os.W_OK):
            issues.append(f"Context path '{path}' is not writable")

    elif mode == "creation":
        if (path.exists() and not path.is_dir()) or not path.exists():
            found_existing_parent = None
            for p in path.parents:
                if p.exists() and p.is_dir():  # Find the nearest existing parent directory
                    found_existing_parent = p
                    if not os.access(p, os.W_OK):  # Then check if it's writable
                        issues.append(f"Parent directory '{p}' is not writable")
                    break

            # If we didn't find any existing parent directory at all
            if found_existing_parent is None:
                issues.append(f"No existing parent directory found for '{path}'")

    else:
        raise ValueError(f"Invalid validation mode '{mode}'")

    return issues


def validate_context(context: Context) -> list[str]:
    """Validate a Context object
    Return a list of issues found, and update context.healthy accordingly.

    Verification is uses the individual validation functions for:
    - context name
    - context path
    - context files
    """
    issues: list[str] = []
    assert context is not None, "Context is None"

    issues.extend(validate_context_name(context.name))
    issues.extend(validate_context_path(context.filepath, mode="existing"))
    issues.extend(validate_context_file(context.filepath))

    context.issues = issues

    if not issues:
        context.healthy = True
    else:
        context.healthy = False

    return issues


# -- helpers -- #
def path_contains_context(path: pathlib.Path) -> bool:
    """Check if a given path contains a valid context."""
    issues = validate_context_file(path)
    return not issues
