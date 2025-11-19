"""
DSL Pipeline - Bidirectional Markdown ↔ Memory Transformation.

This package provides a complete DSL (Domain-Specific Language) pipeline for working
with structured markdown documents.

Pipeline Phases:
  Phase 1: Template Specification (phase1_specs.py)
    - Define document structure with FieldSpec and SectionSpec annotations
    - Parse @field and @section annotations from Jinja2 templates

  Phase 2: Markdown Parsing (phase2_parser.py)
    - Extract structured data from markdown using template specs
    - Parse fields (inline, line, paragraph) and sections (with checkboxes)
    - Track offsets for minimal-churn updates

  Phase 3: Template Rendering (phase3_renderer.py)
    - Render ParsedMemory back to markdown using Jinja2 templates
    - Support custom template directories with FileSystemLoader
    - Proper error handling with Phase3Error

  Phase 4: Memory Validation (phase4_validator.py)
    - Validate ParsedMemory against TemplateSpec requirements
    - Check required fields/sections, formats, patterns, enums
    - Collect validation issues before rendering

Usage:
    # Low-level API (direct phase access)
    from reerelease.service.dsl import (
        FieldSpec, SectionSpec, TemplateSpec,
        MarkdownParser, ParsedMemory,
        MemoryValidator,
        MemoryRenderer,
    )

    spec = TemplateSpec(...)
    parser = MarkdownParser(spec)
    memory = parser.parse(markdown_text)

    validator = MemoryValidator(spec)
    issues = validator.validate(memory)

    renderer = MemoryRenderer(template_dir)
    result = renderer.render("template.j2", context)

    # High-level API (pipeline orchestration)
    from reerelease.service.dsl import DSLPipeline

    pipeline = DSLPipeline(spec, template_dir)
    memory = pipeline.parse_and_validate(markdown_text)
    result = pipeline.render("template.j2", memory)
"""

# Phase 1: Template Specification
# Memory Manager (part of DSL pipeline)
from .memory_manager import (
    MemoryBlock,
    ParsedDocument,
    SectionMeta,
    UnmanagedRegion,
    create_memory_blocks,
    merge_memory_blocks,
)
from .phase1_specs import (
    ANNOTATION_PATTERN,
    ATTRIBUTE_PATTERN,
    FieldSpec,
    SectionSpec,
    TemplateSpec,
    parse_template_annotations,
)

# Phase 2: Markdown Parser
from .phase2_parser import (
    ParsedField,
    ParsedItem,
    ParsedMemory,
    ParsedSection,
    parse_markdown,
)

# Phase 3: Template Renderer
from .phase3_renderer import MemoryRenderer

# Phase 4: Memory Validator
from .phase4_validator import MemoryValidator

# High-level Pipeline API
from .pipeline import DSLPipeline

__all__ = [
    # Phase 1: Specs
    "FieldSpec",
    "SectionSpec",
    "TemplateSpec",
    "parse_template_annotations",
    "ANNOTATION_PATTERN",
    "ATTRIBUTE_PATTERN",
    # Phase 2: Parser
    "ParsedMemory",
    "ParsedField",
    "ParsedSection",
    "ParsedItem",
    "parse_markdown",
    # Phase 3: Renderer
    "MemoryRenderer",
    # Phase 4: Validator
    "MemoryValidator",
    # Pipeline
    "DSLPipeline",
    # Memory Manager
    "MemoryBlock",
    "ParsedDocument",
    "SectionMeta",
    "UnmanagedRegion",
    "create_memory_blocks",
    "merge_memory_blocks",
]
