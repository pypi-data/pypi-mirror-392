"""
DSL Pipeline - Phase 3: Template Renderer.

Renders ParsedMemory objects back to markdown using Jinja2 templates.

Uses custom FileSystemLoader for user-specified template directories (distinct from
TemplateManager which uses packaged templates for CLI). Supports template composition
(includes, extends) and proper error handling with Phase3Error.

Input: ParsedMemory + Jinja2 template
Output: Rendered markdown string
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateError, TemplateNotFound

from reerelease.errors import Phase3Error


class MemoryRenderer:
    """
    Renders ParsedMemory objects to markdown using Jinja2 templates.

    This is Phase 3 of the DSL pipeline:
    - Takes ParsedMemory (output of Phase 2)
    - Renders it using Jinja2 templates
    - Returns rendered markdown string

    Supports:
    - Template composition (includes, extends, imports)
    - Error collection with fail-fast mode
    - Offset tracking for Phase 6 (future)
    """

    def __init__(self, template_dir: Path | str):
        """
        Initialize renderer with template directory.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = Path(template_dir)
        self.log = logging.getLogger("dslp3")
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=False,  # We're generating markdown, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,  # Preserve trailing newlines in templates
        )

    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        fail_fast: bool = True,
    ) -> str:
        """
        Render a template with the given context.

        Args:
            template_name: Name of template file (e.g., "milestone_base.j2")
            context: Variables to pass to template
            fail_fast: If True, raise on first error. If False, collect errors.
                      (Currently only affects validation, not Jinja2 errors)

        Returns:
            Rendered markdown string

        Raises:
            Phase3Error: If rendering fails (Jinja2 errors wrapped in causes)
        """
        self.log.debug(f"Loading template: {template_name}")
        # Jinja2 errors are irrecoverable at THIS layer - use causes only (no issues duplication)
        try:
            template = self.env.get_template(template_name)
            self.log.debug(f"Template loaded: {template_name}")
        except TemplateNotFound as e:
            self.log.error(f"Template not found: {template_name}")
            raise Phase3Error(
                message=f"Template not found: {template_name}",
                template_name=template_name,
                causes=[e],
            ) from e
        except TemplateError as e:
            self.log.error(f"Failed to load template '{template_name}': {e}")
            raise Phase3Error(
                message=f"Failed to load template: {template_name}",
                template_name=template_name,
                causes=[e],
            ) from e

        try:
            self.log.debug(f"Rendering template '{template_name}' with {len(context)} context keys")
            rendered = template.render(**context)
            self.log.info(f"Rendered template '{template_name}': {len(rendered)} chars")
            return rendered
        except TemplateError as e:
            self.log.error(f"Rendering failed for '{template_name}': {e}")
            raise Phase3Error(
                message=f"Rendering failed: {template_name}",
                template_name=template_name,
                causes=[e],
            ) from e
        except Exception as e:
            self.log.error(f"Unexpected rendering error for '{template_name}': {e}")
            raise Phase3Error(
                message=f"Unexpected rendering error: {template_name}",
                template_name=template_name,
                causes=[e],
            ) from e

    def render_field(
        self,
        field_id: str,
        field_value: Any,
        field_spec: Any,
        fail_fast: bool = True,
    ) -> str:
        """
        Render a single field to markdown text.

        Args:
            field_id: Field identifier
            field_value: Value to render
            field_spec: FieldSpec defining the field
            fail_fast: If True, raise on first error

        Returns:
            Rendered field content

        Raises:
            Phase3Error: If rendering fails
        """
        issues: list[str] = []

        try:
            # For now, simple string conversion
            # In Phase 6, we might need more sophisticated rendering
            if field_value is None:
                if field_spec.required:
                    issue = f"[ERROR] Required field '{field_id}' is None"
                    issues.append(issue)
                    if fail_fast:
                        raise Phase3Error(
                            message=f"Required field is None: {field_id}",
                            block_index=0,  # Field rendering doesn't have block context
                            issues=issues,
                        )
                return ""

            return str(field_value)

        except Phase3Error:
            # Re-raise Phase3Error without wrapping
            raise
        except Exception as e:
            issue = f"[ERROR] Failed to render field '{field_id}': {e}"
            issues.append(issue)
            raise Phase3Error(
                message=f"Field rendering failed: {field_id}",
                block_index=0,  # Field rendering doesn't have block context
                issues=issues,
                causes=[e],
            ) from e

    def render_section(
        self,
        section_id: str,
        section_items: list[Any],
        section_spec: Any,
        fail_fast: bool = True,
    ) -> str:
        """
        Render a section (e.g., task list, file links) to markdown.

        Args:
            section_id: Section identifier
            section_items: List of items in the section
            section_spec: SectionSpec defining the section
            fail_fast: If True, raise on first error

        Returns:
            Rendered section content

        Raises:
            Phase3Error: If rendering fails
        """
        issues: list[str] = []

        try:
            # For now, simple list rendering
            # In Phase 6, we might use templates for sections
            if not section_items:
                return ""

            lines = []
            for item in section_items:
                if isinstance(item, dict):
                    # Render dict items (e.g., {"text": "...", "done": True})
                    text = item.get("text", str(item))
                    lines.append(f"- {text}")
                else:
                    # Render simple items
                    lines.append(f"- {item}")

            return "\n".join(lines)

        except Phase3Error:
            # Re-raise Phase3Error without wrapping
            raise
        except Exception as e:
            issue = f"[ERROR] Failed to render section '{section_id}': {e}"
            issues.append(issue)
            raise Phase3Error(
                message=f"Section rendering failed: {section_id}",
                block_name=section_id,  # Section ID maps to block name
                issues=issues,
                causes=[e],
            ) from e
