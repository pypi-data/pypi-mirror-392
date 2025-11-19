"""
DSL Pipeline - High-Level Orchestration API.

Provides a unified interface for the complete DSL pipeline workflow.

Pipeline Phases:
  Phase 1: Template Specification
    - Parse @field and @section annotations from Jinja2 templates
    - Create TemplateSpec defining document structure

  Phase 2: Markdown Parsing
    - Extract structured data from markdown using TemplateSpec
    - Create ParsedMemory with fields and sections

  Phase 4: Memory Validation
    - Validate ParsedMemory against TemplateSpec requirements
    - Check required fields, formats, patterns, enums

  Phase 3: Template Rendering
    - Render ParsedMemory back to markdown using Jinja2 templates
    - Apply custom templates with context data

The DSLPipeline class wraps these phases into convenient methods:
- parse(): Markdown → ParsedMemory (Phase 2)
- validate(): ParsedMemory validation (Phase 4)
- render(): ParsedMemory → Markdown (Phase 3)
- parse_and_validate(): Combined parse + validate
- validate_and_render(): Combined validate + render

Example:
    # Create pipeline with specs and template directory
    pipeline = DSLPipeline(template_spec, template_dir)

    # Parse markdown into memory
    memory = pipeline.parse(markdown_text)

    # Validate memory
    pipeline.validate(memory, fail_fast=True)

    # Render memory to markdown
    result = pipeline.render("template.j2", memory.to_context())

    # Or combined: parse + validate
    memory = pipeline.parse_and_validate(markdown_text)
"""

import logging
from pathlib import Path
from typing import Any

from .inplace_edit import apply_memory_updates
from .phase1_specs import TemplateSpec, parse_template_annotations
from .phase2_parser import ParsedField, ParsedItem, ParsedMemory, ParsedSection, parse_markdown
from .phase3_renderer import MemoryRenderer
from .phase4_validator import MemoryValidator


class DSLPipeline:
    """
    High-level orchestration for DSL pipeline operations.

    Provides a unified API for all 4 phases of the DSL pipeline.

    Phase 1: Template Specification - parse template annotations
    Phase 2: Markdown Parsing - extract structured data
    Phase 3: Template Rendering - render back to markdown
    Phase 4: Memory Validation - validate against spec
    """

    log = logging.getLogger("dslpipe")

    def __init__(self, spec: TemplateSpec, template_dir: Path | str):
        """
        Initialize DSL pipeline with template spec and template directory.

        Args:
            spec: Template specification (from Phase 1)
            template_dir: Directory containing Jinja2 templates for rendering
        """
        self.log = self.__class__.log
        self.spec = spec
        self.template_dir = Path(template_dir) if isinstance(template_dir, str) else template_dir

        # Initialize phase components
        self.validator = MemoryValidator(spec)
        self.renderer = MemoryRenderer(template_dir)

    @classmethod
    def from_template(
        cls,
        template_path: Path | str,
        template_dir: Path | str,
    ) -> "DSLPipeline":
        """
        Create pipeline by parsing template file (Phase 1).

        Args:
            template_path: Path to template file with @field/@section annotations
            template_dir: Directory containing Jinja2 templates for rendering

        Returns:
            DSLPipeline instance with parsed template spec

        Example:
            pipeline = DSLPipeline.from_template(
                "templates/milestone.j2",
                "templates"
            )
        """
        cls.log.debug(f"Creating pipeline from template: {template_path}")
        template_path = Path(template_path) if isinstance(template_path, str) else template_path
        template_source = template_path.read_text(encoding="utf-8")
        spec = parse_template_annotations(template_source, str(template_path))
        cls.log.info(
            f"Parsed template spec: {len(spec.fields)} fields, {len(spec.sections)} sections"
        )
        return cls(spec, template_dir)

    def parse_template(self, template_path: Path | str) -> TemplateSpec:
        """
        Phase 1: Parse template annotations to create TemplateSpec.

        Args:
            template_path: Path to template file with @field/@section annotations

        Returns:
            TemplateSpec defining document structure

        Note:
            This updates self.spec and reinitializes the validator.
        """
        self.log.debug(f"Parsing template: {template_path}")
        template_path = Path(template_path) if isinstance(template_path, str) else template_path
        template_source = template_path.read_text(encoding="utf-8")
        self.spec = parse_template_annotations(template_source, str(template_path))
        self.log.info(
            f"Updated spec: {len(self.spec.fields)} fields, {len(self.spec.sections)} sections"
        )
        # Reinitialize validator with new spec
        self.validator = MemoryValidator(self.spec)
        return self.spec

    def parse(self, markdown: str) -> ParsedMemory:
        """
        Phase 2: Parse markdown into structured memory.

        Args:
            markdown: Markdown text to parse

        Returns:
            ParsedMemory with extracted fields and sections

        Note:
            This does NOT validate the memory. Use parse_and_validate() for that.
        """
        self.log.debug(f"Parsing markdown ({len(markdown)} chars)")
        memory = parse_markdown(markdown, self.spec)
        self.log.info(
            f"Parsed memory: {len(memory.fields)} fields, {len(memory.sections)} sections"
        )
        return memory

    def validate(self, memory: ParsedMemory, fail_fast: bool = True) -> None:
        """
        Phase 4: Validate memory against template spec.

        Args:
            memory: Parsed memory to validate
            fail_fast: If True, raise on first error. If False, collect all errors.

        Raises:
            Phase4Error: If validation fails

        Note:
            Following "no news = good news" pattern: returns silently if valid,
            raises Phase4Error if invalid.
        """
        self.log.debug(f"Validating memory (fail_fast={fail_fast})")
        try:
            self.validator.validate(memory, fail_fast=fail_fast)
            self.log.info("Memory validation passed")
        except Exception as e:
            self.log.error(f"Memory validation failed: {e}")
            raise

    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        fail_fast: bool = True,
    ) -> str:
        """
        Phase 3: Render context to markdown using template.

        Args:
            template_name: Name of Jinja2 template file
            context: Context variables for template rendering
            fail_fast: If True, raise on first error (for future validation)

        Returns:
            Rendered markdown string

        Raises:
            Phase3Error: If rendering fails
        """
        self.log.debug(f"Rendering template: {template_name}")
        try:
            result = self.renderer.render(template_name, context, fail_fast=fail_fast)
            self.log.info(f"Rendered {len(result)} chars from template '{template_name}'")
            return result
        except Exception as e:
            self.log.error(f"Rendering failed for '{template_name}': {e}")
            raise

    def parse_and_validate(
        self,
        markdown: str,
        fail_fast: bool = True,
    ) -> ParsedMemory:
        """
        Combined: Parse markdown and validate result.

        Args:
            markdown: Markdown text to parse
            fail_fast: If True, raise on first validation error

        Returns:
            Validated ParsedMemory

        Raises:
            Phase2Error: If parsing fails
            Phase4Error: If validation fails
        """
        self.log.debug("Starting parse_and_validate")
        memory = self.parse(markdown)
        self.validate(memory, fail_fast=fail_fast)
        self.log.info("Parse and validation completed successfully")
        return memory

    def parse_to_dict(self, markdown: str) -> dict[str, Any]:
        """
        Parse markdown into a flat dictionary.

        Convenience method that parses markdown and converts ParsedMemory
        to a flat dictionary structure suitable for domain object creation.

        Args:
            markdown: Markdown text to parse

        Returns:
            Dictionary with fields as values and sections as lists

        Note:
            - Fields are returned as their string values
            - Checkbox sections return lists of dicts: {"text": str, "done": bool}
            - Simple sections return lists of strings
            - Does NOT validate the memory
        """
        memory = self.parse(markdown)
        return self._memory_to_context(memory)

    def validate_and_render(
        self,
        memory: ParsedMemory,
        template_name: str,
        fail_fast: bool = True,
    ) -> str:
        """
        Combined: Validate memory and render to markdown.

        Args:
            memory: ParsedMemory to validate and render
            template_name: Name of Jinja2 template file
            fail_fast: If True, raise on first error

        Returns:
            Rendered markdown string

        Raises:
            Phase4Error: If validation fails
            Phase3Error: If rendering fails
        """
        self.log.debug(f"Starting validate_and_render for template '{template_name}'")
        self.validate(memory, fail_fast=fail_fast)

        # Convert memory to context dict for rendering
        context = self._memory_to_context(memory)

        result = self.render(template_name, context, fail_fast=fail_fast)
        self.log.info("Validate and render completed successfully")
        return result

    def update_memory_file(
        self,
        filepath: Path,
        updates: dict[str, Any],
        *,
        fail_fast: bool = False,
    ) -> str:
        """Update a memory file with minimal changes using surgical edits.

        This method performs in-place updates to preserve formatting and minimize
        git diffs. It parses the existing file, applies updates to the memory,
        and uses offset-based replacement to change only the modified sections.

        Args:
            filepath: Path to the memory markdown file to update
            updates: Dictionary of field/section updates (field_id -> new_value)
            fail_fast: Whether to stop on first validation error

        Returns:
            Updated markdown content

        Raises:
            FileNotFoundError: If file doesn't exist
            MemoryValidationError: If updated memory is invalid
            DSLError: If update fails

        Example:
            >>> pipeline = DSLPipeline.from_template("milestone", template_dir)
            >>> updated = pipeline.update_memory_file(
            ...     Path("milestone.md"),
            ...     {"status": "completed", "progress": "100%"}
            ... )
        """
        self.log.debug(f"Updating memory file: {filepath}")
        self.log.debug(f"Updates: {list(updates.keys())}")

        # Read original file
        if not filepath.exists():
            msg = f"Memory file not found: {filepath}"
            self.log.error(msg)
            raise FileNotFoundError(msg)

        original_text = filepath.read_text(encoding="utf-8")
        self.log.debug(f"Read {len(original_text)} chars from {filepath}")

        # Parse original memory (with offsets)
        old_memory = self.parse(original_text)

        # Apply updates to create new memory
        new_memory = self._apply_updates_to_memory(old_memory, updates)

        # Validate updated memory
        try:
            self.validate(new_memory, fail_fast=fail_fast)
            self.log.info("Updated memory validated successfully")
        except Exception as e:
            self.log.error(f"Updated memory validation failed: {e}")
            raise

        # Apply minimal-churn updates using offset-based replacement
        updated_text = apply_memory_updates(original_text, old_memory, new_memory)
        self.log.info(f"Generated updated text ({len(updated_text)} chars)")

        return updated_text

    def _apply_updates_to_memory(
        self, memory: ParsedMemory, updates: dict[str, Any]
    ) -> ParsedMemory:
        """Apply updates to a ParsedMemory, creating a new instance.

        Args:
            memory: Original parsed memory
            updates: Dictionary of field/section updates

        Returns:
            New ParsedMemory with updates applied
        """

        # Start with copies of all existing fields and sections
        new_fields = {
            fid: ParsedField(field_id=field.field_id, value=field.value, offset=None)
            for fid, field in memory.fields.items()
        }
        new_sections = {
            sid: ParsedSection(
                section_id=section.section_id, items=list(section.items), offset=None
            )
            for sid, section in memory.sections.items()
        }

        # Apply updates
        for key, value in updates.items():
            # Check if it's a field or section update
            if key in memory.fields or key not in memory.sections:
                # Update or add field (clear offset for updated fields)
                new_fields[key] = ParsedField(field_id=key, value=str(value), offset=None)
            else:
                # Update section
                if isinstance(value, list):
                    # If empty list, remove the section entirely
                    if not value:
                        new_sections.pop(key, None)
                    else:
                        items = []
                        for item in value:
                            if isinstance(item, dict):
                                # Checkbox item with 'text' and 'done'
                                items.append(
                                    ParsedItem(
                                        text=item.get("text", ""),
                                        complete=item.get("done", False),
                                        offset=None,
                                    )
                                )
                            else:
                                # Simple text item
                                items.append(ParsedItem(text=str(item), complete=None, offset=None))
                        new_sections[key] = ParsedSection(section_id=key, items=items, offset=None)

        return ParsedMemory(fields=new_fields, sections=new_sections, issues=memory.issues.copy())

    def _memory_to_context(self, memory: ParsedMemory) -> dict[str, Any]:
        """
        Convert ParsedMemory to context dict for template rendering.

        Args:
            memory: Parsed memory to convert

        Returns:
            Context dictionary with fields and sections
        """
        context: dict[str, Any] = {}

        # Add fields to context
        for field_id, parsed_field in memory.fields.items():
            context[field_id] = parsed_field.value

        # Add sections to context
        for section_id, parsed_section in memory.sections.items():
            # Convert ParsedItems to simple dicts or strings
            items: list[dict[str, Any] | str] = []
            for item in parsed_section.items:
                if item.complete is not None:
                    # Checkbox item
                    items.append({"text": item.text, "done": item.complete})
                else:
                    # Simple item
                    items.append(item.text)
            context[section_id] = items

        return context
