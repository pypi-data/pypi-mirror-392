"""
Memory Management for Template DSL v1.0 - Phase 3+4+5.

This module provides:
- MemoryBlock: structured representation of parsed document blocks
- SectionMeta: offset tracking for sections
- UnmanagedRegion: tracking of non-DSL markdown content
- ParsedDocument: complete document parse result with managed + unmanaged content
- Transformation operations: update, add, remove, reorder
- Serialization: to_dict/from_dict for persistence
- Pretty-printing: for debugging and development
- Multi-block support: for documents with multiple top-level sections

The memory schema is generic and reusable across different use cases:
- Milestones and tasks
- Project descriptions
- Work domains (PCB design, firmware, software)
- Any other structured markdown content
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SectionMeta:
    """Metadata for a parsed section, including location tracking."""

    start_char: int
    end_char: int
    start_line: int | None = None
    end_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "start_char": self.start_char,
            "end_char": self.end_char,
        }
        if self.start_line is not None:
            result["start_line"] = self.start_line
        if self.end_line is not None:
            result["end_line"] = self.end_line
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SectionMeta:
        """Create from dictionary representation."""
        return cls(
            start_char=data["start_char"],
            end_char=data["end_char"],
            start_line=data.get("start_line"),
            end_line=data.get("end_line"),
        )


@dataclass
class UnmanagedRegion:
    """
    Tracks markdown content not managed by DSL annotations.

    Unmanaged content includes:
    - Document headers (before first block)
    - Content between blocks (inter-block)
    - Document footers (after last block)
    - Content within blocks but not annotated (intra-block)

    Character-level offset tracking enables precise preservation during rendering.

    Attributes:
        content: Raw markdown text of this region
        start_char: Character position in original document
        end_char: Character position in original document
        location_type: Classification of where this region appears
        block_index: Associated block index (None for header/footer)
        annotations: Parsed template variables (e.g., {"project_name": str} for "# {project_name} Roadmap")
    """

    content: str
    start_char: int
    end_char: int
    location_type: str  # "document_header" | "inter_block" | "document_footer" | "intra_block"
    block_index: int | None = None
    annotations: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "content": self.content,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "location_type": self.location_type,
            "block_index": self.block_index,
            "annotations": self.annotations.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UnmanagedRegion:
        """Create from dictionary representation."""
        return cls(
            content=data["content"],
            start_char=data["start_char"],
            end_char=data["end_char"],
            location_type=data["location_type"],
            block_index=data.get("block_index"),
            annotations=data.get("annotations", {}),
        )

    def pretty_print(self, indent: int = 0) -> str:
        """Format for debugging output."""
        prefix = "  " * indent
        lines = [
            f"{prefix}UnmanagedRegion(",
            f"{prefix}  location_type='{self.location_type}',",
            f"{prefix}  chars=[{self.start_char}, {self.end_char}),",
            f"{prefix}  length={len(self.content)},",
        ]
        if self.block_index is not None:
            lines.append(f"{prefix}  block_index={self.block_index},")
        if self.annotations:
            lines.append(f"{prefix}  annotations={self.annotations},")

        # Preview content (first 50 chars)
        preview = self.content[:50].replace("\n", "\\n")
        if len(self.content) > 50:
            preview += "..."
        lines.append(f'{prefix}  content="{preview}"')
        lines.append(f"{prefix})")
        return "\n".join(lines)


@dataclass
class MemoryBlock:
    """
    Structured memory representation of a parsed document block.

    A block typically corresponds to a top-level section (e.g., one milestone).
    Documents can contain multiple blocks.

    Attributes:
        fields: Scalar values extracted from the block (name, status, date, etc.)
        sections: Lists of items for each section (tasks, problems, notes, etc.)
        sections_meta: Location tracking for each section (for minimal-churn updates)
        start_char: Character position where this block starts in source document
        end_char: Character position where this block ends in source document
        start_line: Line number where block starts (optional)
        end_line: Line number where block ends (optional)
        diagnostics: Validation errors/warnings for this block
    """

    fields: dict[str, Any]
    sections: dict[str, list[str]]
    sections_meta: dict[str, SectionMeta]
    start_char: int
    end_char: int
    start_line: int | None = None
    end_line: int | None = None
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert memory block to dictionary representation.

        Returns:
            Dictionary with all block data, suitable for JSON serialization.
        """
        return {
            "fields": self.fields.copy(),
            "sections": {k: list(v) for k, v in self.sections.items()},
            "sections_meta": {k: v.to_dict() for k, v in self.sections_meta.items()},
            "start_char": self.start_char,
            "end_char": self.end_char,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "diagnostics": list(self.diagnostics),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryBlock:
        """
        Create memory block from dictionary representation.

        Args:
            data: Dictionary containing block data

        Returns:
            MemoryBlock instance
        """
        sections_meta_data = data.get("sections_meta", {})
        sections_meta = {k: SectionMeta.from_dict(v) for k, v in sections_meta_data.items()}

        return cls(
            fields=data.get("fields", {}),
            sections=data.get("sections", {}),
            sections_meta=sections_meta,
            start_char=data["start_char"],
            end_char=data["end_char"],
            start_line=data.get("start_line"),
            end_line=data.get("end_line"),
            diagnostics=data.get("diagnostics", []),
        )

    # ---- Field Operations ----

    def update_field(self, field_id: str, value: Any) -> None:
        """
        Update or add a field value.

        Args:
            field_id: Field identifier
            value: New value (can be any type)
        """
        self.fields[field_id] = value

    def get_field(self, field_id: str, default: Any = None) -> Any:
        """
        Get a field value with optional default.

        Args:
            field_id: Field identifier
            default: Default value if field not found

        Returns:
            Field value or default
        """
        return self.fields.get(field_id, default)

    # ---- Section Operations ----

    def add_section_item(self, section_id: str, item: str) -> None:
        """
        Add an item to a section. Creates section if it doesn't exist.

        Args:
            section_id: Section identifier
            item: Item text to add
        """
        if section_id not in self.sections:
            self.sections[section_id] = []
        self.sections[section_id].append(item)

    def remove_section_item(self, section_id: str, item: str) -> None:
        """
        Remove an item from a section.

        Args:
            section_id: Section identifier
            item: Item text to remove

        Raises:
            ValueError: If section doesn't exist or item not found
        """
        if section_id not in self.sections:
            raise ValueError(f"Section '{section_id}' not found")

        if item not in self.sections[section_id]:
            raise ValueError(f"Item '{item}' not found in section '{section_id}'")

        self.sections[section_id].remove(item)

    def reorder_section_items(self, section_id: str, new_order: list[int]) -> None:
        """
        Reorder items in a section using index mapping.

        Args:
            section_id: Section identifier
            new_order: List of indices representing new order

        Raises:
            ValueError: If indices are invalid
        """
        if section_id not in self.sections:
            raise ValueError(f"Section '{section_id}' not found")

        items = self.sections[section_id]

        # Validate indices
        if len(new_order) != len(items):
            raise ValueError(
                f"Invalid indices: expected {len(items)} indices, got {len(new_order)}"
            )

        if set(new_order) != set(range(len(items))):
            raise ValueError(f"Invalid indices: must be permutation of 0..{len(items) - 1}")

        # Reorder
        self.sections[section_id] = [items[i] for i in new_order]

    def clear_section(self, section_id: str) -> None:
        """
        Remove all items from a section.

        Args:
            section_id: Section identifier
        """
        if section_id in self.sections:
            self.sections[section_id] = []

    def has_section(self, section_id: str) -> bool:
        """
        Check if a section exists.

        Args:
            section_id: Section identifier

        Returns:
            True if section exists
        """
        return section_id in self.sections

    def get_section_items(self, section_id: str) -> list[str]:
        """
        Get items from a section, returning empty list if not found.

        Args:
            section_id: Section identifier

        Returns:
            List of section items (empty if section doesn't exist)
        """
        return self.sections.get(section_id, [])

    def pretty_print(self, indent: int = 0) -> str:
        """
        Format memory block for debugging output.

        Args:
            indent: Indentation level

        Returns:
            Formatted string representation
        """
        prefix = "  " * indent
        lines = [f"{prefix}MemoryBlock("]

        # Fields
        lines.append(f"{prefix}  fields={{")
        for key, value in self.fields.items():
            value_str = str(value)[:50]
            if len(str(value)) > 50:
                value_str += "..."
            lines.append(f"{prefix}    '{key}': {value_str!r},")
        lines.append(f"{prefix}  }},")

        # Sections
        lines.append(f"{prefix}  sections={{")
        for key, items in self.sections.items():
            lines.append(f"{prefix}    '{key}': [{len(items)} items],")
        lines.append(f"{prefix}  }},")

        # Character positions
        lines.append(f"{prefix}  chars=[{self.start_char}, {self.end_char}),")

        # Diagnostics
        if self.diagnostics:
            lines.append(f"{prefix}  diagnostics={len(self.diagnostics)},")

        lines.append(f"{prefix})")
        return "\n".join(lines)


@dataclass
class ParsedDocument:
    """
    Complete document parse result with managed and unmanaged content.

    This is the enhanced Phase 2 output that includes both:
    - Managed blocks (extracted via DSL annotations)
    - Unmanaged regions (preserved non-DSL markdown)

    Attributes:
        blocks: List of managed MemoryBlock instances
        unmanaged_regions: List of UnmanagedRegion instances
        template_spec: Compiled template specification used for parsing
        source_text: Original markdown text (for Phase 6 diffs)
        source_path: Path to source file (for error reporting)
        issues: Collected issues from parsing (warnings, errors)
    """

    blocks: list[MemoryBlock]
    unmanaged_regions: list[UnmanagedRegion]
    template_spec: Any  # CompiledTemplateSpec (avoid circular import)
    source_text: str
    source_path: Path | None = None
    issues: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if any issue is an error (vs warning)."""
        return any(issue.startswith("[ERROR]") for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if any issue is a warning."""
        return any(issue.startswith("[WARNING]") for issue in self.issues)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation (excluding template_spec)."""
        return {
            "blocks": [b.to_dict() for b in self.blocks],
            "unmanaged_regions": [r.to_dict() for r in self.unmanaged_regions],
            "source_text": self.source_text,
            "source_path": str(self.source_path) if self.source_path else None,
            "issues": self.issues,
        }

    def pretty_print(self, include_source: bool = False) -> str:
        """
        Format parsed document for debugging.

        Args:
            include_source: If True, include source_text preview

        Returns:
            Formatted string representation
        """
        lines = ["ParsedDocument("]

        # Blocks summary
        lines.append(f"  blocks={len(self.blocks)} [")
        for i, block in enumerate(self.blocks):
            name = block.fields.get("name", f"Block {i}")
            chars = f"[{block.start_char}, {block.end_char})"
            lines.append(f"    {i}: '{name}' {chars}")
        lines.append("  ],")

        # Unmanaged regions summary
        lines.append(f"  unmanaged_regions={len(self.unmanaged_regions)} [")
        for i, region in enumerate(self.unmanaged_regions):
            chars = f"[{region.start_char}, {region.end_char})"
            lines.append(f"    {i}: {region.location_type} {chars}")
        lines.append("  ],")

        # Source info
        if self.source_path:
            lines.append(f"  source_path={self.source_path},")
        lines.append(f"  source_length={len(self.source_text)}")

        if include_source:
            preview = self.source_text[:200].replace("\n", "\\n")
            if len(self.source_text) > 200:
                preview += "..."
            lines.append(f'  source_preview="{preview}"')

        lines.append(")")
        return "\n".join(lines)

    def to_debug_dict(self) -> dict[str, Any]:
        """
        Get structured debug data for JSON serialization.

        Useful for:
        - Saving parse results to file
        - Inspecting in debugger
        - Logging complex state
        """
        return {
            "summary": {
                "blocks_count": len(self.blocks),
                "unmanaged_regions_count": len(self.unmanaged_regions),
                "source_length": len(self.source_text),
                "source_path": str(self.source_path) if self.source_path else None,
                "issues_count": len(self.issues),
                "has_errors": self.has_errors(),
                "has_warnings": self.has_warnings(),
            },
            "blocks": [
                {
                    "index": i,
                    "name": block.fields.get("name", f"Block {i}"),
                    "chars": [block.start_char, block.end_char],
                    "fields": list(block.fields.keys()),
                    "sections": {k: len(v) for k, v in block.sections.items()},
                    "diagnostics_count": len(block.diagnostics),
                }
                for i, block in enumerate(self.blocks)
            ],
            "unmanaged_regions": [
                {
                    "index": i,
                    "location_type": region.location_type,
                    "chars": [region.start_char, region.end_char],
                    "length": len(region.content),
                    "block_index": region.block_index,
                    "annotations": region.annotations,
                }
                for i, region in enumerate(self.unmanaged_regions)
            ],
        }


# ---- Multi-Block Operations ----


def create_memory_blocks(parsed_data: list[dict[str, Any]]) -> list[MemoryBlock]:
    """
    Create memory blocks from parsed data.

    Args:
        parsed_data: List of dictionaries from parser (Phase 2 output)

    Returns:
        List of MemoryBlock instances
    """
    return [MemoryBlock.from_dict(data) for data in parsed_data]


def merge_memory_blocks(blocks: list[MemoryBlock]) -> list[MemoryBlock]:
    """
    Merge multiple memory blocks (currently a pass-through).

    This function exists for future enhancements like:
    - Deduplication
    - Conflict resolution
    - Block aggregation

    Args:
        blocks: List of memory blocks

    Returns:
        Merged/processed list of memory blocks
    """
    return blocks
