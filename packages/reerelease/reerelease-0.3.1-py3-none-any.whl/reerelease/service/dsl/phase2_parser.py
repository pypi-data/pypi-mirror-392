"""
DSL Pipeline - Phase 2: Markdown Parser.

Parses markdown documents into structured ParsedMemory objects.

Uses markdown-it-py AST parsing to extract fields and sections defined in Phase 1 specs.
Supports field extraction (inline, line, paragraph), section extraction with checkboxes,
offset tracking for minimal-churn updates, and required field validation.

Input: Markdown text + TemplateSpec
Output: ParsedMemory with extracted fields and sections
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

from markdown_it import MarkdownIt

from .phase1_specs import FieldSpec, SectionSpec, TemplateSpec

logger = logging.getLogger("dslp2")

# =============================================================================
# Offset Tracking
# =============================================================================


@dataclass
class OffsetInfo:
    """
    Character-precise location tracking with line and character positions.

    Provides byte-level precision for surgical document updates while
    maintaining line-based information for diagnostics.

    Attributes:
        start_line: 1-based line number where element starts
        end_line: 1-based line number where element ends (inclusive)
        start_char: Character offset from document start (0-based)
        end_char: Character offset from document end (0-based, exclusive)
    """

    start_line: int
    end_line: int
    start_char: int
    end_char: int

    def to_dict(self) -> dict[str, int]:
        """Serialize to dictionary for JSON export."""
        return {
            "start_line": self.start_line,
            "end_line": self.end_line,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }

    def __post_init__(self) -> None:
        """Validate offset values."""
        if self.start_char < 0 or self.end_char < 0:
            msg = f"Character positions must be non-negative: start={self.start_char}, end={self.end_char}"
            raise ValueError(msg)
        if self.start_char > self.end_char:
            msg = f"start_char must be <= end_char: start={self.start_char}, end={self.end_char}"
            raise ValueError(msg)
        if self.start_line < 1 or self.end_line < 1:
            msg = (
                f"Line numbers must be >= 1: start_line={self.start_line}, end_line={self.end_line}"
            )
            raise ValueError(msg)
        if self.start_line > self.end_line:
            msg = f"start_line must be <= end_line: start_line={self.start_line}, end_line={self.end_line}"
            raise ValueError(msg)


def build_line_offset_map(text: str) -> list[int]:
    """
    Build array mapping line numbers to character offsets.

    Args:
        text: Source text to analyze

    Returns:
        List where index=line_number (0-based), value=character_offset
    """
    offsets = [0]
    for i, char in enumerate(text):
        if char == "\n":
            offsets.append(i + 1)
    return offsets


def token_to_offset_info(token: Any, line_offset_map: list[int], source_text: str) -> OffsetInfo:
    """
    Convert markdown-it token.map to OffsetInfo.

    Args:
        token: Token with .map attribute [start_line, end_line)
        line_offset_map: Pre-computed line offset mapping
        source_text: Original markdown source

    Returns:
        OffsetInfo with line and character positions
    """
    if not token.map:
        msg = "Token has no map"
        raise ValueError(msg)

    start_line, end_line = token.map  # 0-based, end exclusive

    start_char = line_offset_map[start_line]
    end_char = line_offset_map[end_line] if end_line < len(line_offset_map) else len(source_text)

    return OffsetInfo(
        start_line=start_line + 1,  # Convert to 1-based
        end_line=end_line,  # 0-based + exclusive = 1-based inclusive
        start_char=start_char,
        end_char=end_char,
    )


@dataclass
class ParsedField:
    """Represents a parsed field value with metadata."""

    field_id: str
    value: str
    captures: dict[str, str] = field(default_factory=dict)
    offset: OffsetInfo | None = None  # Character-precise offset  # Character offset in source


@dataclass
class ParsedItem:
    """Represents a parsed list item from a section."""

    text: str
    complete: bool | None = None  # For checkbox items
    metadata: dict[str, str] = field(default_factory=dict)  # Extracted from item_pattern
    offset: OffsetInfo | None = None  # Character-precise offset


@dataclass
class ParsedSection:
    """Represents a parsed section with its items."""

    section_id: str
    items: list[ParsedItem] = field(default_factory=list)
    offset: OffsetInfo | None = None  # Character-precise offset


@dataclass
class ParsedMemory:
    """Complete parsed document memory."""

    fields: dict[str, ParsedField] = field(default_factory=dict)
    sections: dict[str, ParsedSection] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)

    def has_errors(self) -> bool:
        """Check if any issue is an error (vs warning)."""
        return any(issue.startswith("[ERROR]") for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if any issue is a warning."""
        return any(issue.startswith("[WARNING]") for issue in self.issues)


def parse_markdown(markdown: str, spec: TemplateSpec) -> ParsedMemory:
    """
    Parse markdown into structured memory using template spec.

    Args:
        markdown: Markdown text to parse
        spec: Template specification defining fields and sections

    Returns:
        ParsedMemory with extracted fields and sections
    """
    logger.debug(f"Starting markdown parse ({len(markdown)} chars)")

    # Parse markdown to tokens
    md = MarkdownIt()
    tokens = md.parse(markdown)

    # Build line offset map for precise offset tracking
    line_offset_map = build_line_offset_map(markdown)

    # Create empty memory
    memory = ParsedMemory(fields={}, sections={}, issues=spec.issues.copy())

    # Extract fields
    _extract_fields(markdown, tokens, spec, memory, line_offset_map)
    logger.debug(f"Extracted {len(memory.fields)} fields")

    # Extract sections
    _extract_sections(markdown, tokens, spec, memory, line_offset_map)
    logger.debug(f"Extracted {len(memory.sections)} sections")

    # Validate required fields
    _validate_required_fields(spec, memory)
    logger.info(f"Parsed markdown: {len(memory.fields)} fields, {len(memory.sections)} sections")

    return memory


def _extract_fields(
    source: str,
    tokens: list[Any],
    spec: TemplateSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract field values from the parsed tokens."""
    for _field_id, field_spec in spec.fields.items():
        if field_spec.type == "inline":
            _extract_inline_field(source, tokens, field_spec, memory, line_offset_map)
        elif field_spec.type == "line":
            _extract_line_field(source, tokens, field_spec, memory, line_offset_map)
        elif field_spec.type == "paragraph":
            _extract_paragraph_field(source, tokens, field_spec, memory, line_offset_map)


def _extract_inline_field(
    source: str,
    tokens: list[Any],
    field_spec: FieldSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract an inline field (typically from heading text)."""
    # Look for heading tokens
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            # Next token should be inline content
            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                content_token = tokens[i + 1]
                text = content_token.content.strip()

                if text:  # Found non-empty heading
                    offset_info = (
                        token_to_offset_info(content_token, line_offset_map, source)
                        if content_token.map
                        else None
                    )
                    parsed_field = ParsedField(
                        field_id=field_spec.field_id, value=text, offset=offset_info
                    )

                    # Apply pattern if specified
                    if field_spec.pattern:
                        match = field_spec.pattern.search(text)
                        if match:
                            parsed_field.captures = match.groupdict()

                    memory.fields[field_spec.field_id] = parsed_field
                    return  # Take first heading found  # Take first heading found


def _extract_line_field(
    source: str,
    tokens: list[Any],
    field_spec: FieldSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract a line field (single line value, possibly after a label)."""
    lines = source.splitlines()

    # Skip lines already used by other fields to avoid conflicts
    used_line_numbers = {
        f.offset.start_line for f in memory.fields.values() if f.offset is not None
    }

    for line_idx, line in enumerate(lines):
        line_number = line_idx + 1  # Convert to 1-based
        if line_number in used_line_numbers:
            continue

        # Look for common patterns like "**Label:** value" or "Label: value"
        # Try to extract value after colon
        if ":" in line:
            value_part = line.split(":", 1)[1].strip()
            # Remove any markdown formatting
            value_part = _strip_markdown_formatting(value_part)

            if value_part:
                # Calculate character offsets for this line
                start_char = line_offset_map[line_idx]
                end_char = (
                    line_offset_map[line_idx + 1] - 1
                    if line_idx + 1 < len(line_offset_map)
                    else len(source)
                )

                offset_info = OffsetInfo(
                    start_line=line_number,
                    end_line=line_number,
                    start_char=start_char,
                    end_char=end_char,
                )

                parsed_field = ParsedField(
                    field_id=field_spec.field_id, value=value_part, offset=offset_info
                )

                # Apply pattern if specified
                if field_spec.pattern:
                    match = field_spec.pattern.search(value_part)
                    if match:
                        parsed_field.captures = match.groupdict()
                        # If pattern has captures, use the main value
                        if "d" in match.groupdict():
                            parsed_field.value = match.group("d")
                        elif "email" in match.groupdict():
                            parsed_field.value = match.group("email")

                memory.fields[field_spec.field_id] = parsed_field
                return  # Take first match  # Take first match


def _extract_paragraph_field(
    source: str,
    tokens: list[Any],
    field_spec: FieldSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract a paragraph field (multi-line text block).

    Paragraphs should not include lines that look like field definitions
    (e.g., **Label:** value). If a paragraph contains field-like lines,
    extract only the text before them. Skip paragraphs that are entirely
    field definitions.

    Stops at any heading that appears AFTER the first heading, to avoid
    capturing paragraphs from subsequent sections (e.g., Tasks, Problems).
    Skips the first heading (the section/milestone heading itself).
    """
    # Track whether we've seen the first heading
    seen_first_heading = False

    # Look for paragraph tokens, stop at subsequent headings
    for token in tokens:
        # Handle heading boundaries
        if token.type == "heading_open":
            if seen_first_heading:
                # Stop at any subsequent heading
                break
            else:
                # Skip the first heading (the section heading itself)
                seen_first_heading = True
                continue

        if token.type == "paragraph_open":
            # Find corresponding inline content
            idx = tokens.index(token)
            if idx + 1 < len(tokens) and tokens[idx + 1].type == "inline":
                content_token = tokens[idx + 1]
                text = content_token.content.strip()

                if not text:
                    continue

                # Get the offset info of this paragraph
                offset_info = (
                    token_to_offset_info(content_token, line_offset_map, source)
                    if content_token.map
                    else None
                )

                # If the paragraph text contains field-like patterns, extract only the part before them
                # This handles cases where markdown parses paragraph + field lines as one paragraph
                if "**" in text and ":**" in text:
                    # Split by lines and take only lines before the first field line
                    text_lines = text.split("\n")
                    paragraph_lines = []
                    for line in text_lines:
                        if line.strip().startswith("**") and ":**" in line:
                            # Stop at the first field line
                            break
                        paragraph_lines.append(line)

                    text = "\n".join(paragraph_lines).strip()

                    # If nothing left after filtering, skip this paragraph
                    if not text:
                        continue

                parsed_field = ParsedField(
                    field_id=field_spec.field_id, value=text, offset=offset_info
                )

                # Apply pattern if specified
                if field_spec.pattern:
                    match = field_spec.pattern.search(text)
                    if match:
                        parsed_field.captures = match.groupdict()

                memory.fields[field_spec.field_id] = parsed_field
                return  # Take first valid paragraph

    # If no paragraph found, add empty field
    if field_spec.field_id not in memory.fields:
        memory.fields[field_spec.field_id] = ParsedField(
            field_id=field_spec.field_id, value="", offset=None
        )


def _extract_sections(
    source: str,
    tokens: list[Any],
    spec: TemplateSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract sections with list items."""
    for _section_id, section_spec in spec.sections.items():
        _extract_section(source, tokens, section_spec, memory, line_offset_map)


def _extract_section(
    source: str,
    tokens: list[Any],
    section_spec: SectionSpec,
    memory: ParsedMemory,
    line_offset_map: list[int],
) -> None:
    """Extract a single section with its items."""
    # Find the section by matching heading against title_like pattern or by level
    section_heading_idx = None
    section_heading_token = None

    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            # Check level if specified
            if section_spec.level is not None:
                # Extract level from tag (e.g., "h3" -> 3)
                tag_level = int(token.tag[1:]) if len(token.tag) > 1 else 0
                if tag_level != section_spec.level:
                    continue

            if i + 1 < len(tokens) and tokens[i + 1].type == "inline":
                heading_text = tokens[i + 1].content

                # Check if this matches our section
                if section_spec.title_like:
                    if section_spec.title_like.search(heading_text):
                        section_heading_idx = i
                        section_heading_token = token
                        break
                else:
                    # No title_like means match any heading (at specified level)
                    section_heading_idx = i
                    section_heading_token = token
                    break

    if section_heading_idx is None:
        return  # Section not found in document

    # Extract list items following this heading
    parsed_section = ParsedSection(section_id=section_spec.section_id)

    # Set section offset if heading token has map
    if section_heading_token and section_heading_token.map:
        parsed_section.offset = token_to_offset_info(section_heading_token, line_offset_map, source)

    # Find list items after this heading
    for i in range(section_heading_idx, len(tokens)):
        token = tokens[i]

        if token.type == "bullet_list_open":
            # Track the level of the main list to know when it ends
            main_list_level = token.level

            # Process list items
            for j in range(i + 1, len(tokens)):
                item_token = tokens[j]

                if item_token.type == "list_item_open":
                    # Only process top-level items (level == main_list_level + 1)
                    # Skip nested items (level > main_list_level + 1)
                    if item_token.level == main_list_level + 1:
                        # Extract item content
                        item = _extract_list_item(tokens, j, section_spec, line_offset_map, source)
                        if item:
                            parsed_section.items.append(item)

                elif item_token.type == "bullet_list_close" and item_token.level == main_list_level:
                    # End of the main list (not a nested list)
                    break

            break  # Found and processed the list

        # Stop if we hit another heading (entering next section)
        if token.type == "heading_open" and i > section_heading_idx:
            break

    memory.sections[section_spec.section_id] = parsed_section


def _extract_list_item(
    tokens: list[Any],
    start_idx: int,
    section_spec: SectionSpec,
    line_offset_map: list[int],
    source: str,
) -> ParsedItem | None:
    """Extract a single list item with checkbox and metadata."""
    # Find the inline content of this list item
    for i in range(start_idx, len(tokens)):
        token = tokens[i]

        if token.type == "inline":
            text = token.content
            offset_info = (
                token_to_offset_info(token, line_offset_map, source) if token.map else None
            )

            item = ParsedItem(text=text, offset=offset_info)

            # Check for checkbox pattern
            if section_spec.checkbox:
                match = section_spec.checkbox.match(text)
                if match:
                    # Extract checkbox state
                    last_idx = match.lastindex if match.lastindex is not None else 0
                    state = match.group(1) if last_idx >= 1 else " "
                    item.complete = state.lower() in ("x", "X")

                    # Extract text after checkbox
                    if "text" in match.groupdict():
                        item.text = match.group("text")

                    # Extract metadata from checkbox pattern groupdict
                    # Skip 'text' as it's already handled
                    for key, value in match.groupdict().items():
                        if key != "text" and value is not None:
                            item.metadata[key] = value

            # Extract metadata using item_pattern (additional metadata extraction)
            if section_spec.item_pattern:
                match = section_spec.item_pattern.search(text)
                if match:
                    item.metadata.update(match.groupdict())

            return item

        elif token.type == "list_item_close":
            break  # End of this item without finding content

    return None


def _strip_markdown_formatting(text: str) -> str:
    """Remove common Markdown formatting from text."""
    # Remove bold/italic markers (greedy to handle nested)
    text = re.sub(r"\*\*", "", text)  # Remove ** markers
    text = re.sub(r"__", "", text)  # Remove __ markers
    text = re.sub(r"\*", "", text)  # Remove * markers
    text = re.sub(r"_", "", text)  # Remove _ markers

    # Remove inline code markers
    text = re.sub(r"`", "", text)  # Remove ` markers

    return text.strip()


def _validate_required_fields(spec: TemplateSpec, memory: ParsedMemory) -> None:
    """Validate that all required fields are present."""
    for field_id, field_spec in spec.fields.items():
        if field_spec.required and field_id not in memory.fields:
            issue = f"[ERROR] Required field '{field_id}' is missing"
            memory.issues.append(issue)
