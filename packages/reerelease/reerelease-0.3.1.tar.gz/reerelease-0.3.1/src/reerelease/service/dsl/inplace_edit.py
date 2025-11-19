"""In-Place Memory Editor.

This module implements surgical updates to markdown memory files, preserving
unchanged content and minimizing git diffs. Uses character-precise offset
information from Phase 2 parser to perform targeted replacements.

Architecture:
    1. Diff Detection: Compare old vs new parsed memory to identify changes
    2. Offset-Based Replacement: Use OffsetInfo to replace only changed elements
    3. Fallback: If offsets invalid, fall back to full reconstruction

Key Features:
    - Preserves formatting, whitespace, comments outside changed sections
    - Maintains document structure for minimal git diffs
    - Safe fallback ensures correctness even with stale offsets
"""

# TODO: Big doubts that this is a good approach overall, the inline edit seems very difficult to understand by the app
# And a bounded char placement strategy seems a better agnostic approach

import logging
from dataclasses import dataclass
from typing import Any

from reerelease.service.dsl.phase2_parser import OffsetInfo, ParsedMemory

logger = logging.getLogger("dslipe")


def _reconstruct_memory(memory: ParsedMemory) -> str:
    """Reconstruct memory as markdown (fallback when surgical updates fail).

    This is a simple reconstruction that preserves basic structure.
    For more sophisticated rendering, use Phase 3 with templates.

    Args:
        memory: Parsed memory to reconstruct

    Returns:
        Markdown representation of the memory
    """
    lines = []

    # Render fields using simple line format
    for field_id, field in memory.fields.items():
        value = field.value
        if not value:
            continue

        # Always use line format for consistency
        if "\n" in value:
            # Multi-line value
            lines.append(f"**{field_id}:**")
            lines.append(value)
        else:
            # Single-line value
            lines.append(f"**{field_id}:** {value}")

        lines.append("")  # Blank line after field

    # Render sections
    for section_id, section in memory.sections.items():
        if not section.items:
            continue

        section_title = section_id.replace("_", " ").title()
        lines.append(f"### {section_title}")
        lines.append("")

        for item in section.items:
            checkbox = "[x]" if getattr(item, "complete", False) else "[ ]"
            lines.append(f"- {checkbox} {item.text}")

        lines.append("")  # Blank line after section

    return "\n".join(lines).rstrip() + "\n"


@dataclass
class MemoryUpdate:
    """Represents a single update to a memory element.

    Attributes:
        element_type: Type of element to update ('field' or 'section')
        element_id: ID of the field or section to update
        new_value: New value for the element (str for fields, list of items for sections)
        old_offset: OffsetInfo from the original parse (for validation)
    """

    element_type: str  # 'field' or 'section'
    element_id: str
    new_value: Any  # str for fields, list[ParsedItem] for sections
    old_offset: OffsetInfo | None

    def __post_init__(self) -> None:
        """Validate the update."""
        if self.element_type not in ("field", "section"):
            raise ValueError(f"Invalid element_type: {self.element_type}")
        if not self.element_id:
            raise ValueError("element_id cannot be empty")
        if self.new_value is None:
            raise ValueError("new_value cannot be None")


def detect_changes(
    old_memory: ParsedMemory,
    new_memory: ParsedMemory,
) -> list[MemoryUpdate]:
    """Detect changes between old and new memory.

    Args:
        old_memory: Original parsed memory with offset information
        new_memory: New memory state (may not have offsets)

    Returns:
        List of MemoryUpdate objects representing the changes
    """
    updates: list[MemoryUpdate] = []

    # Detect field changes
    all_field_ids = set(old_memory.fields.keys()) | set(new_memory.fields.keys())
    for field_id in all_field_ids:
        old_field = old_memory.fields.get(field_id)
        new_field = new_memory.fields.get(field_id)

        # Field added
        if old_field is None and new_field is not None:
            updates.append(
                MemoryUpdate(
                    element_type="field",
                    element_id=field_id,
                    new_value=new_field.value,
                    old_offset=None,
                )
            )
        # Field removed
        elif old_field is not None and new_field is None:
            updates.append(
                MemoryUpdate(
                    element_type="field",
                    element_id=field_id,
                    new_value="",  # Empty value means removal
                    old_offset=old_field.offset,
                )
            )
        # Field changed
        elif old_field is not None and new_field is not None and old_field.value != new_field.value:
            updates.append(
                MemoryUpdate(
                    element_type="field",
                    element_id=field_id,
                    new_value=new_field.value,
                    old_offset=old_field.offset,
                )
            )

    # Detect section changes
    all_section_ids = set(old_memory.sections.keys()) | set(new_memory.sections.keys())
    for section_id in all_section_ids:
        old_section = old_memory.sections.get(section_id)
        new_section = new_memory.sections.get(section_id)

        # Section added
        if old_section is None and new_section is not None:
            updates.append(
                MemoryUpdate(
                    element_type="section",
                    element_id=section_id,
                    new_value=new_section.items,
                    old_offset=None,
                )
            )
        # Section removed
        elif old_section is not None and new_section is None:
            # When removing a section, we need to remove the header AND all items
            # The section offset only covers the header, so extend to last item
            old_offset = old_section.offset
            if old_offset and old_section.items and old_section.items[-1].offset:
                # Extend offset to include all items
                old_offset = OffsetInfo(
                    start_line=old_offset.start_line,
                    end_line=old_section.items[-1].offset.end_line,
                    start_char=old_offset.start_char,
                    end_char=old_section.items[-1].offset.end_char,
                )

            updates.append(
                MemoryUpdate(
                    element_type="section",
                    element_id=section_id,
                    new_value=[],  # Empty list means removal
                    old_offset=old_offset,
                )
            )
        # Section changed (compare item values)
        elif old_section is not None and new_section is not None:
            old_items = [item.text for item in old_section.items]
            new_items = [item.text for item in new_section.items]
            if old_items != new_items:
                # When updating a section, also extend to cover all old items
                old_offset = old_section.offset
                if old_offset and old_section.items and old_section.items[-1].offset:
                    old_offset = OffsetInfo(
                        start_line=old_offset.start_line,
                        end_line=old_section.items[-1].offset.end_line,
                        start_char=old_offset.start_char,
                        end_char=old_section.items[-1].offset.end_char,
                    )

                updates.append(
                    MemoryUpdate(
                        element_type="section",
                        element_id=section_id,
                        new_value=new_section.items,
                        old_offset=old_offset,
                    )
                )

    return updates


def apply_memory_updates(
    original_text: str,
    old_memory: ParsedMemory,
    new_memory: ParsedMemory,
) -> str:
    """Apply minimal-churn updates to memory file.

    Strategy:
        1. Detect changes between old and new memory
        2. If no changes, return original text unchanged
        3. If changes detected, attempt surgical replacement using offsets
        4. If offset-based replacement fails, fall back to full reconstruction

    Args:
        original_text: Original markdown content
        old_memory: Parsed memory from original text (with offsets)
        new_memory: New memory state to write

    Returns:
        Updated markdown content with minimal changes

    Raises:
        ValueError: If inputs are invalid
    """
    logger.debug("apply_memory_updates: Starting update process")

    if not original_text:
        # Empty file, just reconstruct
        logger.debug("apply_memory_updates: Empty original text, using reconstruction")
        return _reconstruct_memory(new_memory)

    # Detect changes
    updates = detect_changes(old_memory, new_memory)
    logger.info(f"apply_memory_updates: Detected {len(updates)} change(s)")

    for update in updates:
        logger.debug(
            f"  - {update.element_type} '{update.element_id}': "
            f"{'added' if update.old_offset is None else 'modified/removed'}"
        )

    if not updates:
        # No changes, return original
        logger.debug("apply_memory_updates: No changes detected, returning original text")
        return original_text

    # Try surgical replacement
    try:
        logger.info("apply_memory_updates: Attempting surgical updates")
        result = _apply_surgical_updates(original_text, updates, new_memory)
        logger.info("apply_memory_updates: Surgical updates successful")
        return result
    except (ValueError, IndexError, AttributeError) as e:
        # Offset-based replacement failed, fall back to reconstruction
        # This can happen if:
        # - File was manually edited between parse and update
        # - Offsets are stale or invalid
        # - Structure changed unexpectedly
        logger.warning(
            f"apply_memory_updates: Surgical updates failed ({e.__class__.__name__}: {e}), "
            "falling back to reconstruction"
        )
        return _reconstruct_memory(new_memory)


def _apply_surgical_updates(
    original_text: str,
    updates: list[MemoryUpdate],
    new_memory: ParsedMemory,
) -> str:
    """Apply updates using character-precise offsets.

    Args:
        original_text: Original markdown content
        updates: List of updates to apply
        new_memory: New memory state (for reconstructing updated elements)

    Returns:
        Updated markdown with surgical replacements

    Raises:
        ValueError: If offsets are invalid
        IndexError: If offset ranges are out of bounds
    """
    logger.debug(f"_apply_surgical_updates: Processing {len(updates)} update(s)")

    # Sort updates by offset (reverse order, so we can apply from end to start)
    # This prevents earlier replacements from invalidating later offsets
    sorted_updates = sorted(
        [u for u in updates if u.old_offset is not None],
        key=lambda u: u.old_offset.start_char if u.old_offset else 0,
        reverse=True,
    )

    logger.debug(f"_apply_surgical_updates: {len(sorted_updates)} have offsets for surgical update")

    result = original_text

    for update in sorted_updates:
        if update.old_offset is None:
            # New element, can't do surgical replacement
            # Fall back to reconstruction
            logger.debug(
                f"_apply_surgical_updates: Cannot add new {update.element_type} '{update.element_id}' surgically"
            )
            raise ValueError("Cannot surgically add new elements")

        offset = update.old_offset

        # Validate offset
        if offset.start_char < 0 or offset.end_char > len(result):
            logger.error(
                f"_apply_surgical_updates: Invalid offset for {update.element_type} '{update.element_id}': "
                f"[{offset.start_char}:{offset.end_char}] exceeds text length {len(result)}"
            )
            raise ValueError(f"Invalid offset range: {offset}")

        if offset.start_char >= offset.end_char:
            logger.error(
                f"_apply_surgical_updates: Invalid offset ordering for {update.element_type} '{update.element_id}': "
                f"start ({offset.start_char}) >= end ({offset.end_char})"
            )
            raise ValueError(f"Invalid offset ordering: {offset}")

        # Generate replacement text
        if update.element_type == "field":
            replacement = _render_field_update(update, new_memory, result, offset)
        else:  # section
            replacement = _render_section_update(update, new_memory)

        logger.debug(
            f"_apply_surgical_updates: Replacing {update.element_type} '{update.element_id}' "
            f"at [{offset.start_char}:{offset.end_char}] with {len(replacement)} chars"
        )

        # Apply replacement
        result = result[: offset.start_char] + replacement + result[offset.end_char :]

    # Handle additions (elements without old_offset)
    additions = [u for u in updates if u.old_offset is None]
    if additions:
        # For now, fall back to reconstruction for additions
        # TODO: Future enhancement - smart insertion based on field/section order
        raise ValueError("Cannot surgically add new elements")

    return result


def _render_field_update(
    update: MemoryUpdate, new_memory: ParsedMemory, original_text: str, offset: OffsetInfo
) -> str:
    """Render the updated field value preserving original markdown format.

    Args:
        update: MemoryUpdate for the field
        new_memory: New memory state
        original_text: Original markdown text
        offset: Offset of the field in original text

    Returns:
        Markdown-formatted field content preserving original format
    """
    field = new_memory.fields.get(update.element_id)
    if field is None:
        # Field removed
        return ""

    # Extract the original text to determine the format
    original_field_text = original_text[offset.start_char : offset.end_char]

    # Get the new value
    new_value = field.value

    # Detect the original format and preserve it
    # For inline fields (headings), preserve the heading structure
    if original_field_text.startswith("#"):
        # Count the leading # characters to preserve heading level
        heading_level = len(original_field_text) - len(original_field_text.lstrip("#"))
        heading_marker = "#" * heading_level
        # Check if original had a newline at the end
        has_trailing_newline = original_field_text.endswith("\n")
        # Return new value with the same heading format
        result = f"{heading_marker} {new_value}"
        if has_trailing_newline:
            result += "\n"
        return result

    # For line fields with **label:** format
    if "**" in original_field_text and ":**" in original_field_text:
        # Preserve the label format
        if "\n" in new_value:
            return f"**{update.element_id}:**\n{new_value}"
        else:
            return f"**{update.element_id}:** {new_value}"

    # Default: just return the new value (for simple text replacements)
    return new_value


def _render_section_update(update: MemoryUpdate, new_memory: ParsedMemory) -> str:
    """Render the updated section in markdown format.

    Args:
        update: MemoryUpdate for the section
        new_memory: New memory state

    Returns:
        Markdown-formatted section content
    """
    section = new_memory.sections.get(update.element_id)
    if section is None:
        # Section removed
        return ""

    # Format section as markdown list
    lines = []
    section_title = update.element_id.replace("_", " ").title()
    lines.append(f"### {section_title}")
    lines.append("")

    for item in section.items:
        checkbox = "[x]" if getattr(item, "complete", False) else "[ ]"
        lines.append(f"- {checkbox} {item.text}")

    return "\n".join(lines)
