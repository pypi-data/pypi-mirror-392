"""
Validators for DSL Pipeline - Phase 4: Memory Validation.

Simple validation functions that return lists of issues found.
These are called by the Phase 4 validator which raises exceptions if needed.

Validation Functions:
- validate_parsed_memory(): Validate complete ParsedMemory against TemplateSpec
- validate_field(): Validate a single field value against FieldSpec
- validate_section(): Validate a section against SectionSpec
- validate_field_format(): Check field format constraints (date, int, float, enum)
- validate_field_pattern(): Check field pattern (regex) matching
- validate_field_enum(): Check field enum value

Pattern: All functions return list[str] of issues found, empty list = valid
"""

import re
from datetime import datetime
from typing import Any

from ..service.dsl.phase1_specs import FieldSpec, SectionSpec, TemplateSpec
from ..service.dsl.phase2_parser import ParsedMemory, ParsedSection


def validate_parsed_memory(memory: ParsedMemory, spec: TemplateSpec) -> list[str]:
    """
    Validate a ParsedMemory object against a TemplateSpec.

    Checks:
    - All required fields are present and non-empty
    - All required sections are present and non-empty
    - Field values match their specs (format, pattern, enum)
    - Section items match their specs

    Args:
        memory: Parsed memory to validate
        spec: Template specification with requirements

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    # Validate all fields
    for field_id, field_spec in spec.fields.items():
        field_issues = validate_field_in_memory(field_id, memory, field_spec)
        issues.extend(field_issues)

    # Validate all sections
    for section_id, section_spec in spec.sections.items():
        section_issues = validate_section_in_memory(section_id, memory, section_spec)
        issues.extend(section_issues)

    return issues


def validate_field_in_memory(
    field_id: str,
    memory: ParsedMemory,
    field_spec: FieldSpec,
) -> list[str]:
    """
    Validate a field in ParsedMemory against its FieldSpec.

    Args:
        field_id: Field identifier
        memory: Parsed memory containing the field
        field_spec: Field specification with requirements

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    # Check if field exists in memory
    parsed_field = memory.fields.get(field_id)

    # Required field missing
    if field_spec.required and parsed_field is None:
        issues.append(f"[ERROR] Required field '{field_id}' is missing")
        return issues  # Can't validate further without the field

    # Optional field missing is OK
    if parsed_field is None:
        return issues

    # Field exists, validate its value
    field_value = parsed_field.value

    # Required field with empty value
    if field_spec.required and (field_value is None or not str(field_value).strip()):
        issues.append(f"[ERROR] Required field '{field_id}' is empty")
        return issues

    # If field is empty and optional, nothing more to validate
    if field_value is None or not str(field_value).strip():
        return issues

    # Validate field value against spec
    value_issues = validate_field(field_value, field_spec)
    # Prefix issues with field_id for context
    issues.extend([f"Field '{field_id}': {issue}" for issue in value_issues])

    return issues


def validate_field(value: Any, field_spec: FieldSpec) -> list[str]:
    """
    Validate a field value against its FieldSpec.

    Args:
        value: Field value to validate
        field_spec: Field specification with requirements

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    # Convert value to string for validation
    str_value = str(value) if value is not None else ""

    # Validate format if specified
    if field_spec.format:
        format_issues = validate_field_format(str_value, field_spec.format)
        issues.extend(format_issues)

    # Validate pattern if specified
    if field_spec.pattern:
        pattern_issues = validate_field_pattern(str_value, field_spec.pattern)
        issues.extend(pattern_issues)

    # Validate enum if specified
    if field_spec.enum:
        enum_issues = validate_field_enum(str_value, field_spec.enum)
        issues.extend(enum_issues)

    return issues


def validate_field_format(value: str, format_type: str) -> list[str]:
    """
    Validate field value format.

    Supported formats:
    - date: ISO date format (YYYY-MM-DD)
    - iso8601: Full ISO8601 datetime
    - int: Integer number
    - float: Floating point number
    - lower: Lowercase string
    - upper: Uppercase string

    Args:
        value: Value to validate
        format_type: Expected format type

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    if format_type == "date":
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            issues.append(f"[ERROR] Value '{value}' is not a valid date (expected YYYY-MM-DD)")

    elif format_type == "iso8601":
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            issues.append(f"[ERROR] Value '{value}' is not a valid ISO8601 datetime")

    elif format_type == "int":
        try:
            int(value)
        except ValueError:
            issues.append(f"[ERROR] Value '{value}' is not a valid integer")

    elif format_type == "float":
        try:
            float(value)
        except ValueError:
            issues.append(f"[ERROR] Value '{value}' is not a valid float")

    elif format_type == "lower":
        if value != value.lower():
            issues.append(f"[ERROR] Value '{value}' is not lowercase")

    elif format_type == "upper":
        if value != value.upper():
            issues.append(f"[ERROR] Value '{value}' is not uppercase")

    else:
        issues.append(f"[WARNING] Unknown format type '{format_type}'")

    return issues


def validate_field_pattern(value: str, pattern: re.Pattern[str]) -> list[str]:
    """
    Validate field value matches regex pattern.

    Args:
        value: Value to validate
        pattern: Compiled regex pattern

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    if not pattern.match(value):
        issues.append(f"[ERROR] Value '{value}' does not match required pattern {pattern.pattern}")

    return issues


def validate_field_enum(value: str, enum_values: list[str]) -> list[str]:
    """
    Validate field value is in allowed enum values.

    Args:
        value: Value to validate
        enum_values: List of allowed values

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    if value not in enum_values:
        allowed = ", ".join(f"'{v}'" for v in enum_values)
        issues.append(f"[ERROR] Value '{value}' not in allowed values: {allowed}")

    return issues


def validate_section_in_memory(
    section_id: str,
    memory: ParsedMemory,
    section_spec: SectionSpec,
) -> list[str]:
    """
    Validate a section in ParsedMemory against its SectionSpec.

    Args:
        section_id: Section identifier
        memory: Parsed memory containing the section
        section_spec: Section specification with requirements

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    # Check if section exists in memory
    parsed_section = memory.sections.get(section_id)

    # Required section missing
    if section_spec.required and parsed_section is None:
        issues.append(f"[ERROR] Required section '{section_id}' is missing")
        return issues

    # Optional section missing is OK
    if parsed_section is None:
        return issues

    # Section exists, validate it
    section_issues = validate_section(parsed_section, section_spec)
    # Prefix issues with section_id for context
    issues.extend([f"Section '{section_id}': {issue}" for issue in section_issues])

    return issues


def validate_section(section: ParsedSection, section_spec: SectionSpec) -> list[str]:
    """
    Validate a ParsedSection against its SectionSpec.

    Args:
        section: Parsed section to validate
        section_spec: Section specification with requirements

    Returns:
        List of validation issues found (empty if valid)
    """
    issues: list[str] = []

    # Required section with no items
    if section_spec.required and not section.items:
        issues.append("[ERROR] Required section is empty")

    # Additional section-level validations can be added here
    # For example: validate item patterns, checkbox requirements, etc.

    return issues
