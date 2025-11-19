"""
DSL Pipeline - Phase 1: Template Specification.

Defines the data structures for template annotations and specifications.
This is the foundation phase of the bidirectional Markdown ↔ Memory transformation.

Key Classes:
- FieldSpec: Specification for a field annotation (@field:...)
- SectionSpec: Specification for a section annotation (@section:...)
- TemplateSpec: Complete specification of a parsed template

Annotations are parsed from Jinja2 template comments to define the structure
of markdown documents. These specs are used by:
- Phase 2 (Parser): Extract structured data from markdown
- Phase 4 (Validator): Validate extracted data against requirements

Example Annotations:
    {# @field:name type=inline required=true #}
    {# @section:tasks title_like="### Tasks" checkbox=true required=false #}
    {# @meta:version value="1.0" #}

This phase includes the annotation parser that extracts these specs from templates.
"""

import json
import re
from dataclasses import dataclass, field
from typing import Any

from reerelease.errors import Phase1Error


@dataclass
class FieldSpec:
    """Specification for a field annotation (@field:...)."""

    field_id: str
    type: str = "inline"  # "inline" | "paragraph" | "line"
    required: bool = False
    pattern: re.Pattern[str] | None = None
    capture: str | None = None
    format: str | None = None  # "date" | "iso8601" | "int" | "float" | "lower" | "upper"
    enum: list[str] | None = None
    default: str | None = None
    level: int | None = None


@dataclass
class SectionSpec:
    """Specification for a section annotation (@section:...)."""

    section_id: str
    title_like: re.Pattern[str] | None = None
    level: int | None = None
    checkbox: re.Pattern[str] | None = None
    item_pattern: re.Pattern[str] | None = None
    item_selector: str | None = None
    required: bool = False


@dataclass
class TemplateSpec:
    """Complete specification of a parsed template with annotations."""

    fields: dict[str, FieldSpec] = field(default_factory=dict)
    sections: dict[str, SectionSpec] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)  # Unified issue propagation

    def has_errors(self) -> bool:
        """Check if any issue is an error (vs warning)."""
        return any(issue.startswith("[ERROR]") for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if any issue is a warning."""
        return any(issue.startswith("[WARNING]") for issue in self.issues)


# Regex for parsing annotations: {# @TYPE:IDENTIFIER attr1="value" attr2=bare #}
ANNOTATION_PATTERN = re.compile(r"\{#\s*@(\w+):(\w+)\s*(.*?)\s*#\}", re.DOTALL)

# Regex for parsing attributes within annotation
ATTRIBUTE_PATTERN = re.compile(r'(\w+)=(?:"([^"]*)"|\'([^\']*)\'|([^\s]+))')


def parse_template_annotations(
    template_source: str, template_path: str | None = None
) -> TemplateSpec:
    """
    Parse a Jinja template and extract all DSL annotations.

    Args:
        template_source: The Jinja template source code with annotations
        template_path: Optional path to template file (for error reporting)

    Returns:
        TemplateSpec containing parsed field/section/meta annotations and issues
        (Only returns if no [ERROR] level issues exist)

    Raises:
        Phase1Error: If any [ERROR] level issues are encountered
            (protects truth-file integrity by preventing processing of invalid templates)
    """
    spec = TemplateSpec()

    # Find all annotations in the template
    for match in ANNOTATION_PATTERN.finditer(template_source):
        annotation_type = match.group(1)  # "field" | "section" | "meta"
        identifier = match.group(2)  # The ID (e.g., "name", "tasks")
        attributes_str = match.group(3)  # The attributes string

        # Parse attributes
        try:
            attributes = _parse_attributes(attributes_str)
        except Exception as e:
            spec.issues.append(
                f"[WARNING] Malformed annotation @{annotation_type}:{identifier}: {e!s}"
            )
            continue

        # Process based on annotation type
        if annotation_type == "field":
            field_spec = _create_field_spec(identifier, attributes, spec.issues)
            spec.fields[identifier] = field_spec
        elif annotation_type == "section":
            section_spec = _create_section_spec(identifier, attributes, spec.issues)
            spec.sections[identifier] = section_spec
        elif annotation_type == "meta":
            # Meta annotations store arbitrary key-value pairs
            spec.meta[identifier] = attributes.get("value", attributes)

    # Truth-file integrity: If any errors exist, raise exception
    # Errors indicate structural problems that would corrupt output
    # Warnings are non-blocking issues that can be tolerated
    if spec.has_errors():
        raise Phase1Error(
            message="Cannot process template with errors - truth-file integrity",
            source_path=template_path,
            issues=spec.issues,
        )

    return spec


def _parse_attributes(attributes_str: str) -> dict[str, Any]:
    """
    Parse attribute string into dict of key-value pairs.

    Examples:
        'type=inline required=true' -> {'type': 'inline', 'required': 'true'}
        'enum=\'["a","b"]\' pattern="test"' -> {'enum': '["a","b"]', 'pattern': 'test'}
    """
    attributes: dict[str, Any] = {}

    for match in ATTRIBUTE_PATTERN.finditer(attributes_str):
        key = match.group(1)
        # Value can be in double quotes (group 2), single quotes (group 3), or bare (group 4)
        value = match.group(2) or match.group(3) or match.group(4)
        attributes[key] = value

    return attributes


def _create_field_spec(field_id: str, attributes: dict[str, Any], issues: list[str]) -> FieldSpec:
    """Create a FieldSpec from parsed attributes, with type coercion."""
    spec = FieldSpec(field_id=field_id)

    # Process each attribute with appropriate coercion
    if "type" in attributes:
        spec.type = attributes["type"]

    if "required" in attributes:
        spec.required = _coerce_bool(attributes["required"])

    if "level" in attributes:
        spec.level = _coerce_int(attributes["level"])

    if "pattern" in attributes:
        spec.pattern = _compile_regex(attributes["pattern"], f"field:{field_id}", issues)

    if "capture" in attributes:
        spec.capture = attributes["capture"]

    if "format" in attributes:
        spec.format = attributes["format"]

    if "enum" in attributes:
        spec.enum = _parse_json_array(attributes["enum"], f"field:{field_id}", issues)

    if "default" in attributes:
        spec.default = attributes["default"]

    return spec


def _create_section_spec(
    section_id: str, attributes: dict[str, Any], issues: list[str]
) -> SectionSpec:
    """Create a SectionSpec from parsed attributes, with type coercion."""
    spec = SectionSpec(section_id=section_id)

    if "title_like" in attributes:
        spec.title_like = _compile_regex(attributes["title_like"], f"section:{section_id}", issues)

    if "level" in attributes:
        spec.level = _coerce_int(attributes["level"])

    if "checkbox" in attributes:
        spec.checkbox = _compile_regex(attributes["checkbox"], f"section:{section_id}", issues)

    if "item_pattern" in attributes:
        spec.item_pattern = _compile_regex(
            attributes["item_pattern"], f"section:{section_id}", issues
        )

    if "item_selector" in attributes:
        spec.item_selector = attributes["item_selector"]

    if "required" in attributes:
        spec.required = _coerce_bool(attributes["required"])

    return spec


def _coerce_bool(value: Any) -> bool:
    """Coerce a value to boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ("false", "0", "no"):
            return False
        elif value.lower() in ("true", "1", "yes"):
            return True
        else:
            return False

    return bool(value)


def _coerce_int(value: Any) -> int:
    """Coerce a value to integer."""
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 0
    else:
        return 0


def _compile_regex(pattern: str, source: str, issues: list[str]) -> re.Pattern[str] | None:
    """
    Compile a regex pattern string, emitting issue on failure.

    Args:
        pattern: The regex pattern string
        source: Source identifier for issue (e.g., "field:name")
        issues: List to append issue string to on error

    Returns:
        Compiled regex or None if compilation failed
    """
    try:
        return re.compile(pattern)
    except re.error as e:
        issues.append(f"[WARNING] Invalid regex pattern in @{source}: {e!s}")
        return None


def _parse_json_array(json_str: str, source: str, issues: list[str]) -> list[str] | None:
    """
    Parse a JSON array string, emitting issue on failure.

    Args:
        json_str: The JSON array string
        source: Source identifier for issue
        issues: List to append issue string to on error

    Returns:
        Parsed list or None if parsing failed
    """
    try:
        result = json.loads(json_str)
        if not isinstance(result, list):
            raise ValueError("Expected JSON array")
        return result
    except (json.JSONDecodeError, ValueError) as e:
        issues.append(f"[WARNING] Invalid JSON array in @{source}: {e!s}")
        return None
