# Template DSL Reference

Concise reference for the Template DSL v1.0 — bidirectional Markdown ↔ Memory transformation system based on the actual implementation.

---

## Overview

The DSL pipeline transforms structured markdown documents:

```text
Phase 1: Template → TemplateSpec (annotation parsing)
Phase 2: Markdown + TemplateSpec → ParsedMemory (extraction)
Phase 4: ParsedMemory + TemplateSpec → Validation (checking)
Phase 3: ParsedMemory + Template → Markdown (rendering)
```

**Implementation Status:**

| Phase | Component              | Status      | Module                           |
| ----- | ---------------------- | ----------- | -------------------------------- |
| 1     | Template Specification | ✅ Complete | `phase1_specs.py`                |
| 2     | Markdown Parser        | ✅ Complete | `phase2_parser.py`               |
| 3     | Template Renderer      | ✅ Complete | `phase3_renderer.py`             |
| 4     | Memory Validator       | ✅ Complete | `phase4_validator.py`            |
| —     | Memory Manager         | ✅ Complete | `memory_manager.py`              |
| —     | Pipeline Orchestration | ✅ Complete | `pipeline.py`                    |
| —     | Field Validators       | ✅ Complete | `validators/validate_dsl.py`     |
| —     | In-Place Editor        | ✅ Complete | `inplace_edit.py`                |

**Design Principles:**

- AST-first: markdown-it-py for parsing, never regex on raw text
- Offset tracking: character positions preserved for future surgical updates
- Error aggregation: issues collected with `[ERROR]`/`[WARNING]` prefixes
- Fail-fast mode: `Phase1Error` raised on template errors, blocking invalid specs
- Truth-file integrity: invalid templates cannot create corrupted output

---

## Annotation Syntax

Annotations are Jinja2 comments parsed with regex: `{# @(\w+):(\w+)\s*(.*?)\s*#}`

```jinja
{# @TYPE:IDENTIFIER attr1="value" attr2=bare attr3='other' #}
```

**Structure:**

| Element      | Pattern                          | Description                                          |
| ------------ | -------------------------------- | ---------------------------------------------------- |
| `TYPE`       | `field` \| `section` \| `meta`   | Annotation type                                      |
| `IDENTIFIER` | `\w+`                            | Key in parsed memory (e.g., `name`, `tasks`)         |
| Attributes   | `key=value` or `key="value"`     | Space-separated; quotes for strings with spaces      |
| Value types  | `true`/`false`, numbers, strings | Bare: booleans/numbers; Quoted: strings              |

**Attribute Parsing:** Regex `(\w+)=(?:"([^"]*)"|'([^']*)'|([^\s]+))`

**Example:**

```jinja
{# @meta:dsl_version value="1.0" #}

## {{ milestone_name }} {# @field:name type=inline required=true #}

{{ milestone_description }} {# @field:description type=paragraph #}

**Status:** {{ status }} {# @field:status type=line enum='["planned","in-progress","completed"]' required=true #}

### Tasks {# @section:tasks title_like="^Tasks$" level=3 checkbox='^\[([ xX])\]\s*(?P<text>.*)$' #}
- [ ] Task one
- [x] Task two (@alice)
```

---

## Data Structures

### Phase 1: TemplateSpec

```python
@dataclass
class FieldSpec:
    field_id: str
    type: str = "inline"                 # "inline" | "paragraph" | "line"
    required: bool = False
    pattern: re.Pattern[str] | None = None
    capture: str | None = None
    format: str | None = None            # "date" | "iso8601" | "int" | "float" | "lower" | "upper"
    enum: list[str] | None = None
    default: str | None = None
    level: int | None = None

@dataclass
class SectionSpec:
    section_id: str
    title_like: re.Pattern[str] | None = None
    level: int | None = None
    checkbox: re.Pattern[str] | None = None
    item_pattern: re.Pattern[str] | None = None
    item_selector: str | None = None     # Conceptual hint (not yet used)
    required: bool = False

@dataclass
class TemplateSpec:
    fields: dict[str, FieldSpec] = field(default_factory=dict)
    sections: dict[str, SectionSpec] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)  # [ERROR]/[WARNING] strings
    
    def has_errors(self) -> bool:       # Check for [ERROR] issues
    def has_warnings(self) -> bool:     # Check for [WARNING] issues
```

### Phase 2: ParsedMemory

```python
@dataclass
class ParsedField:
    field_id: str
    value: str
    captures: dict[str, str] = field(default_factory=dict)  # Named groups from pattern
    offset: int | None = None                               # Character offset in source

@dataclass
class ParsedItem:
    text: str
    complete: bool | None = None                            # For checkbox items
    metadata: dict[str, str] = field(default_factory=dict)  # From item_pattern
    offset: int | None = None

@dataclass
class ParsedSection:
    section_id: str
    items: list[ParsedItem] = field(default_factory=list)
    offset: int | None = None

@dataclass
class ParsedMemory:
    fields: dict[str, ParsedField] = field(default_factory=dict)
    sections: dict[str, ParsedSection] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    
    def has_errors(self) -> bool
    def has_warnings(self) -> bool
```

### Memory Manager: MemoryBlock

```python
@dataclass
class SectionMeta:
    start_offset: int
    end_offset: int
    start_line: int | None = None
    end_line: int | None = None

@dataclass
class MemoryBlock:
    fields: dict[str, Any]
    sections: dict[str, list[str]]
    sections_meta: dict[str, SectionMeta]
    start_offset: int
    end_offset: int
    start_line: int | None = None
    end_line: int | None = None
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    
    # Field operations
    def update_field(self, field_id: str, value: Any) -> None
    def get_field(self, field_id: str, default: Any = None) -> Any
    
    # Section operations
    def add_section_item(self, section_id: str, item: str) -> None
    def remove_section_item(self, section_id: str, item: str) -> None
    def reorder_section_items(self, section_id: str, new_order: list[int]) -> None
    def clear_section(self, section_id: str) -> None
    def has_section(self, section_id: str) -> bool
    def get_section_items(self, section_id: str) -> list[str]
    
    # Serialization
    def to_dict(self) -> dict[str, Any]
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryBlock
    def pretty_print(self, indent: int = 0) -> str

@dataclass
class UnmanagedRegion:
    """Content not managed by DSL annotations."""
    content: str
    start_offset: int
    end_offset: int
    location_type: str  # "document_header" | "inter_block" | "document_footer" | "intra_block"
    block_index: int | None = None
    annotations: dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedDocument:
    """Complete parse result with managed and unmanaged content."""
    blocks: list[MemoryBlock]
    unmanaged_regions: list[UnmanagedRegion]
    template_spec: Any                  # CompiledTemplateSpec
    source_text: str
    source_path: Path | None = None
    issues: list[str] = field(default_factory=list)
```

---

## Attribute Reference

### Common Attributes (all types)

| Attribute  | Type | Default  | Description                        | Coercion                                                                   |
| ---------- | ---- | -------- | ---------------------------------- | -------------------------------------------------------------------------- |
| `required` | bool | `false`  | Emit error if extraction fails     | `_coerce_bool()`: true/1/yes → True; false/0/no → False; fallback to False |
| `level`    | int  | inferred | Heading level (e.g., `2` for `##`) | `_coerce_int()`: parse int, fallback to 0                                  |

### Field Attributes (`@field:...`)

| Attribute | Type       | Default           | Description                                      | Parsing/Coercion                                          |
| --------- | ---------- | ----------------- | ------------------------------------------------ | --------------------------------------------------------- |
| `type`    | enum       | `inline`          | `inline` \| `paragraph` \| `line`                | Direct string assignment                                  |
| `pattern` | regex      | none              | Regex for extraction (prefer named groups)       | `_compile_regex()`: emit [WARNING] on re.error            |
| `capture` | str        | first named group | Group name to extract                            | Direct string assignment                                  |
| `format`  | enum       | none              | `date` \| `iso8601` \| `int` \| `float` \| ...   | Direct string assignment                                  |
| `enum`    | JSON array | none              | Allowed values `'["a","b"]'`                     | `_parse_json_array()`: emit [WARNING] on JSONDecodeError  |
| `default` | str        | `null`            | Default if extraction fails (non-required only)  | Direct string assignment                                  |

**Field Extraction Types:**

- `inline`: Extract from heading content or adjacent inline token
  - Searches for `heading_open` → `inline` token pairs
  - Returns first non-empty `token.content.strip()`
  - Pattern applies to extracted text
  
- `line`: Extract from single line (typically `**Label:** value` format)
  - Searches lines with `:` delimiter
  - Extracts value after colon, strips markdown formatting
  - Pattern applies to extracted value
  - Skips lines already used by other fields
  
- `paragraph`: Extract from first paragraph block
  - Searches for `paragraph_open` → `inline` → `paragraph_close`
  - Stops at first subsequent heading (after initial section heading)
  - Filters out field-like lines (containing `:`)
  - Pattern applies to paragraph content

### Section Attributes (`@section:...`)

| Attribute       | Type  | Default                        | Description                                   | Implementation                                        |
| --------------- | ----- | ------------------------------ | --------------------------------------------- | ----------------------------------------------------- |
| `title_like`    | regex | none                           | Regex to match subsection heading             | `_compile_regex()`: emit [WARNING] on error           |
| `level`         | int   | none                           | Heading level to match                        | `_coerce_int()`                                       |
| `checkbox`      | regex | `^\[([ xX])\]\s*(?P<text>.*)$` | Parse checkbox items (must have `text` group) | Applied to each list item; extracts `complete` state  |
| `item_pattern`  | regex | none                           | Extract named groups from item text           | Applied after checkbox extraction; populates metadata |
| `item_selector` | hint  | `ul>li`                        | Conceptual hint (currently unused)            | Reserved for future use                               |

**Section Extraction Logic:**

1. Find heading matching `title_like` pattern or `level`
2. Search for `bullet_list_open` token after heading
3. Extract items until `bullet_list_close` (matching level)
4. Stop at next heading of same/higher level
5. For each item:
   - Extract `inline` token content
   - Apply `checkbox` pattern if specified (extracts `complete` bool)
   - Apply `item_pattern` for metadata extraction
   - Store offsets from `token.map[0]`

### Meta Attributes (`@meta:...`)

| Attribute | Type | Default | Description                             | Storage                              |
| --------- | ---- | ------- | --------------------------------------- | ------------------------------------ |
| any key   | any  | none    | Arbitrary metadata for tooling          | `spec.meta[identifier] = attributes` |

**Common Meta Keys:**

- `dsl_version`: DSL version (e.g., `"1.0"`)
- `schema_id`: Custom schema identifier
- `last_updated`: Timestamp or version info

---

## Validation Rules

Implemented in `validators/validate_dsl.py`:

```python
def validate_parsed_memory(memory: ParsedMemory, spec: TemplateSpec) -> list[str]
def validate_field_in_memory(field_id: str, memory: ParsedMemory, field_spec: FieldSpec) -> list[str]
def validate_section_in_memory(section_id: str, memory: ParsedMemory, section_spec: SectionSpec) -> list[str]
```

| Rule                 | Code                       | Level       | Check                                                                 |
| -------------------- | -------------------------- | ----------- | --------------------------------------------------------------------- |
| Required field       | `required_field_missing`   | `[ERROR]`   | `field_spec.required=True` and field not in memory                    |
| Field format         | varies                     | varies      | `validate_field_format()`: date/int/float/iso8601 parsing             |
| Field pattern        | `pattern_mismatch`         | varies      | `validate_field_pattern()`: regex match on field value                |
| Field enum           | `enum_mismatch`            | varies      | `validate_field_enum()`: value in allowed list (case-insensitive)     |
| Required section     | `required_section_missing` | `[ERROR]`   | `section_spec.required=True` and (section not in memory or empty)     |
| Malformed annotation | `malformed_annotation`     | `[WARNING]` | Annotation parsing fails (Phase 1), continues without that annotation |
| Invalid regex        | `invalid_regex`            | `[WARNING]` | `re.compile()` fails on pattern/checkbox/item_pattern                 |
| Invalid JSON array   | varies                     | `[WARNING]` | `json.loads()` fails on enum attribute                                |

**Phase 1 Error Handling:**

- `[WARNING]` issues collected in `spec.issues`
- `[ERROR]` issues raise `Phase1Error` (truth-file integrity protection)
- Template with errors cannot proceed to Phase 2

**Phase 4 Validation:**

- All validators return `list[str]` of issues
- `fail_fast=True`: raise `Phase4Error` on first issue
- `fail_fast=False`: collect all issues, then raise `Phase4Error`

---

## Error Hierarchy

```python
AppError(Exception)
└── DSLError(AppError)
    ├── Phase1Error    # Template annotation parsing
    │   Attributes: source_path, location, issues, causes
    ├── Phase2Error    # Markdown document parsing
    │   Attributes: source_path, location, issues, causes
    ├── Phase3Error    # Template rendering
    │   Attributes: template_name, block_index, block_name, issues, causes
    ├── Phase4Error    # Memory validation
    │   Attributes: issues, causes
    └── DocumentReconstructionError  # Merge failures (Phase 6, future)
        Attributes: managed_blocks_count, unmanaged_regions_count, issues
```

**Error Aggregation:**

All error classes support:

```python
def __init__(self, message, *, issues=None, causes=None)
def add_issue(self, issue: str) -> None
def add_cause(self, cause: AppError) -> None
def get_all_issues(self) -> list[str]  # Flatten issues from nested causes
```

---

## API Reference

### Phase 1: Template Specification

```python
from reerelease.service.dsl.phase1_specs import parse_template_annotations

def parse_template_annotations(
    template_source: str,
    template_path: str | None = None
) -> TemplateSpec:
    """
    Parse Jinja template and extract DSL annotations.
    
    Raises:
        Phase1Error: If any [ERROR] issues found (blocks processing)
    
    Returns:
        TemplateSpec with fields/sections/meta and issues list
    """
```

**Annotation Parsing:**

1. Regex scan: `ANNOTATION_PATTERN.finditer(template_source)`
2. Parse attributes: `_parse_attributes(attributes_str)`
3. Create specs:
   - `_create_field_spec()`: coerce types, compile patterns
   - `_create_section_spec()`: coerce types, compile patterns
   - Meta: store in `spec.meta[identifier]`
4. Validate: raise `Phase1Error` if `spec.has_errors()`

### Phase 2: Markdown Parsing

```python
from reerelease.service.dsl.phase2_parser import parse_markdown

def parse_markdown(markdown_source: str, spec: TemplateSpec) -> ParsedMemory:
    """
    Parse markdown document using TemplateSpec.
    
    Returns:
        ParsedMemory with extracted fields/sections and validation issues
    """
```

**Parsing Process:**

1. Parse markdown: `md = MarkdownIt(); tokens = md.parse(markdown_source)`
2. Extract fields: `_extract_fields(source, tokens, spec, memory)`
   - `_extract_inline_field()`: search heading tokens
   - `_extract_line_field()`: parse lines with `:` delimiter
   - `_extract_paragraph_field()`: extract paragraph content
3. Extract sections: `_extract_sections(source, tokens, spec, memory)`
   - `_extract_section()`: find heading, extract list items
   - `_extract_list_item()`: parse checkbox, apply item_pattern
4. Validate required fields: `_validate_required_fields(spec, memory)`

### Phase 3: Template Rendering

```python
from reerelease.service.dsl.phase3_renderer import MemoryRenderer

class MemoryRenderer:
    def __init__(self, template_dir: Path | str):
        """Initialize with Jinja2 FileSystemLoader."""
        
    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        fail_fast: bool = True,
    ) -> str:
        """
        Render template with context.
        
        Raises:
            Phase3Error: If rendering fails (wraps Jinja2 errors in causes)
        """
    
    def render_field(self, field_id, field_value, field_spec, fail_fast=True) -> str:
        """Render single field to markdown text."""
    
    def render_section(self, section_id, section_items, section_spec, fail_fast=True) -> str:
        """Render section to markdown list."""
```

**Jinja2 Environment:**

- `FileSystemLoader(template_dir)`
- `autoescape=False` (generating markdown, not HTML)
- `trim_blocks=True`, `lstrip_blocks=True`
- `keep_trailing_newline=True`

### Phase 4: Memory Validation

```python
from reerelease.service.dsl.phase4_validator import MemoryValidator

class MemoryValidator:
    def __init__(self, spec: TemplateSpec):
        """Initialize validator with template specification."""
    
    def validate(self, memory: ParsedMemory, fail_fast: bool = True) -> None:
        """
        Validate ParsedMemory against TemplateSpec.
        
        Raises:
            Phase4Error: If validation finds issues
        
        Note:
            "No news = good news" pattern: returns silently if valid
        """
```

**Validation Delegation:**

- Calls `validators.validate_dsl.validate_parsed_memory(memory, spec)`
- Collects all issues (or first if `fail_fast=True`)
- Raises `Phase4Error` with collected issues

### Pipeline Orchestration

```python
from reerelease.service.dsl import DSLPipeline

class DSLPipeline:
    def __init__(self, spec: TemplateSpec, template_dir: Path | str):
        """Initialize pipeline with spec and template directory."""
    
    @classmethod
    def from_template(
        cls,
        template_path: Path | str,
        template_dir: Path | str,
    ) -> "DSLPipeline":
        """Create pipeline by parsing template file (Phase 1)."""
    
    def parse_template(self, template_path: Path | str) -> TemplateSpec:
        """Phase 1: Parse template annotations."""
    
    def parse(self, markdown: str) -> ParsedMemory:
        """Phase 2: Parse markdown into memory (no validation)."""
    
    def validate(self, memory: ParsedMemory, fail_fast: bool = True) -> None:
        """Phase 4: Validate memory against spec."""
    
    def render(
        self,
        template_name: str,
        context: dict[str, Any],
        fail_fast: bool = True,
    ) -> str:
        """Phase 3: Render context to markdown."""
    
    # --- Combined operations ---
    
    def parse_and_validate(
        self,
        markdown: str,
        fail_fast: bool = True,
    ) -> ParsedMemory:
        """Parse and validate markdown."""
    
    def parse_to_dict(self, markdown: str) -> dict[str, Any]:
        """Parse markdown to flat dict (fields + sections)."""
    
    def validate_and_render(
        self,
        memory: ParsedMemory,
        template_name: str,
        fail_fast: bool = True,
    ) -> str:
        """Validate memory and render to markdown."""
    
    # --- Internal ---
    
    def _memory_to_context(self, memory: ParsedMemory) -> dict[str, Any]:
        """Convert ParsedMemory to context dict for template rendering."""
```

**Context Conversion:**

- Fields: `context[field_id] = parsed_field.value`
- Sections:
  - Checkbox items: `{"text": str, "done": bool}`
  - Simple items: `str`

---

## Common Patterns

### Date Field with Pattern

```jinja
**Date:** {{ date }} {# @field:date type=line pattern="(?P<d>\\d{4}-\\d{2}-\\d{2})" format=date #}
```

Extracts: `field.value = "2025-10-15"`, `field.captures = {"d": "2025-10-15"}`

### Status Enum Field

```jinja
**Status:** {{ status }} {# @field:status type=line enum='["planned","in-progress","completed","cancelled"]' required=true #}
```

Validates: value must be in enum list (case-insensitive)

### Checkbox Section with User Mentions

```jinja
### Tasks {# @section:tasks title_like="^Tasks$" checkbox='^\[([ xX])\]\s*(?P<text>.*)$' item_pattern='@(?P<user>\\w+)' #}
- [ ] Implement feature @alice
- [x] Write tests @bob
```

Extracts:

- `item.text = "Implement feature @alice"`
- `item.complete = False`
- `item.metadata = {"user": "alice"}`

### Version Pattern with Multiple Groups

```jinja
## Release {{ version }} {# @field:version type=inline pattern="v?(?P<major>\\d+)\\.(?P<minor>\\d+)\\.(?P<patch>\\d+)" #}
```

Extracts: `field.captures = {"major": "1", "minor": "2", "patch": "3"}`

### Paragraph with Email Extraction

```jinja
{{ description }} {# @field:description type=paragraph pattern="(?P<email>\\S+@\\S+\\.\\S+)" #}
```

Content:

``` markdown
This is a multi-line description.
Contact: admin@example.com for support.
```

Extracts:

- `field.value = "This is a multi-line description.\nContact: admin@example.com for support."`
- `field.captures = {"email": "admin@example.com"}`

---

## Usage Examples

### Basic Workflow

```python
from pathlib import Path
from reerelease.service.dsl import DSLPipeline

# 1. Create pipeline from template
pipeline = DSLPipeline.from_template(
    template_path="templates/milestone.j2",
    template_dir="templates"
)

# 2. Parse markdown document
markdown = Path("roadmap.md").read_text()
memory = pipeline.parse_and_validate(markdown, fail_fast=True)

# 3. Modify memory
memory.fields["status"].value = "completed"
memory.sections["tasks"].items.append(
    ParsedItem(text="New task", complete=False)
)

# 4. Render back to markdown
context = pipeline._memory_to_context(memory)
result = pipeline.render("milestone.j2", context)

# 5. Write output
Path("roadmap_updated.md").write_text(result)
```

### Error Handling

```python
from reerelease.errors import Phase1Error, Phase2Error, Phase4Error

try:
    pipeline = DSLPipeline.from_template("template.j2", "templates")
except Phase1Error as e:
    print(f"Template has errors: {e.get_all_issues()}")
    # [ERROR] issues prevent processing

try:
    memory = pipeline.parse("roadmap.md")
    pipeline.validate(memory, fail_fast=False)  # Collect all errors
except Phase4Error as e:
    for issue in e.issues:
        print(issue)  # [ERROR] Required field 'name' is missing
```

### Validation with Custom Logic

```python
from reerelease.validators.validate_dsl import (
    validate_parsed_memory,
    validate_field_in_memory,
)

# Validate specific field
issues = validate_field_in_memory("status", memory, spec.fields["status"])
if issues:
    print(f"Status field issues: {issues}")

# Full validation
all_issues = validate_parsed_memory(memory, spec)
errors = [i for i in all_issues if i.startswith("[ERROR]")]
warnings = [i for i in all_issues if i.startswith("[WARNING]")]
```

### Memory Block Operations

```python
from reerelease.service.dsl.memory_manager import MemoryBlock, SectionMeta

# Create memory block
block = MemoryBlock(
    fields={"name": "Milestone 1.0", "status": "in-progress"},
    sections={"tasks": ["Task 1", "Task 2"]},
    sections_meta={"tasks": SectionMeta(100, 200)},
    start_offset=0,
    end_offset=300,
)

# Update field
block.update_field("status", "completed")

# Modify section
block.add_section_item("tasks", "Task 3")
block.remove_section_item("tasks", "Task 1")

# Serialize
data = block.to_dict()
restored = MemoryBlock.from_dict(data)

# Debug output
print(block.pretty_print())
```

---

## Testing Patterns

From `tests/service/dsl/`:

### Fixture-Based Testing (Phase 2)

```python
# Use pre-built specs to decouple from Phase 1
from tests.service.dsl.test_phase_fixtures import (
    create_simple_inline_field_spec,
    create_checkbox_section_spec,
    SIMPLE_INLINE_FIELD_DOC,
)

def test_parse_inline_field():
    spec = create_simple_inline_field_spec()
    result = parse_markdown(SIMPLE_INLINE_FIELD_DOC, spec)
    assert "name" in result.fields
    assert result.fields["name"].value == "My Project"
```

### Parametrized Validation Tests

```python
@pytest.mark.parametrize(
    "template,field_id,test_input,should_match,expected_groups",
    [
        (
            '{# @field:date pattern="(?P<d>\\d{4}-\\d{2}-\\d{2})" #}',
            "date",
            "2025-10-15",
            True,
            {"d": "2025-10-15"},
        ),
        (
            '{# @field:email pattern="(?P<email>[\\w.-]+@[\\w.-]+\\.\\w+)" #}',
            "email",
            "test@example.com",
            True,
            {"email": "test@example.com"},
        ),
    ],
)
def test_field_pattern_compilation(template, field_id, test_input, should_match, expected_groups):
    result = parse_template_annotations(template)
    field = result.fields[field_id]
    match = field.pattern.search(test_input)
    assert match is not None if should_match else match is None
```

### Integration Tests (Pipeline)

```python
def test_full_pipeline_integration():
    """End-to-end: parse template → parse markdown → validate → render."""
    pipeline = DSLPipeline.from_template("test.j2", "templates")
    memory = pipeline.parse_and_validate("# Test\n**Status:** active")
    result = pipeline.validate_and_render(memory, "test.j2")
    assert "Status" in result
```

---



---

## Versioning

### Version Declaration

```jinja
{# @meta:dsl_version value="1.0" #}
```

### Version Semantics

| Version | Type                | Changes                               | Status      |
| ------- | ------------------- | ------------------------------------- | ----------- |
| `1.0`   | Initial stable      | Core features (Phases 1-4)            | ✅ Complete |
| `1.x`   | Minor               | New attributes, backward-compatible   | 🚧 Future   |
| `2.0`   | Major (breaking)    | API changes, removed features         | 🚧 Future   |

### Compatibility

- Parser should check `meta["dsl_version"]` and warn on unknown versions
- Default to `1.0` if unspecified
- Provide migration tools for major version upgrades

---

## AST Token Reference (markdown-it-py)

Key token types used in Phase 2:

| Token Type           | Description          | Attributes                                   | Usage                                |
| -------------------- | -------------------- | -------------------------------------------- | ------------------------------------ |
| `heading_open`       | Start heading        | `.tag` (`h2`, `h3`), `.map` (line range)     | Field extraction (inline type)       |
| `heading_close`      | End heading          |                                              | Boundary detection                   |
| `inline`             | Inline content       | `.content` (text), `.children`               | Field/section text extraction        |
| `paragraph_open`     | Start paragraph      | `.map`                                       | Field extraction (paragraph type)    |
| `paragraph_close`    | End paragraph        |                                              | Paragraph boundary                   |
| `bullet_list_open`   | Start unordered list | `.map`, `.level`                             | Section extraction                   |
| `bullet_list_close`  | End unordered list   | `.level`                                     | Section boundary                     |
| `list_item_open`     | Start list item      | `.map`                                       | Item extraction                      |
| `list_item_close`    | End list item        |                                              | Item boundary                        |

**Token Navigation:**

- `.map`: `[start_line, end_line)` (0-indexed, end exclusive)
- `.level`: Nesting depth (for list hierarchy)
- `.content`: Text content for inline tokens

**Offset Conversion:**

```python
def token_map_to_offsets(token, line_offsets):
    """Convert token.map to character offsets."""
    if token.map:
        start_line, end_line = token.map
        return line_offsets[start_line], line_offsets[end_line]
    return None, None
```

---

## In-Place Editing (`inplace_edit.py`)

The in-place editor enables **surgical updates** to markdown memory files, preserving unchanged content and minimizing git diffs. It uses character-precise offset information from Phase 2 to perform targeted replacements.

### Architecture

```text
1. Diff Detection: Compare old vs new ParsedMemory → MemoryUpdate[]
2. Surgical Updates: Use OffsetInfo to replace only changed elements
3. Fallback: If offsets invalid → full reconstruction
```

**Key Components:**

| Function                    | Purpose                           | Strategy                    |
| --------------------------- | --------------------------------- | --------------------------- |
| `detect_changes()`          | Identify modified fields/sections | Diff old vs new memory      |
| `apply_memory_updates()`    | Apply changes to original text    | Surgical or fallback        |
| `_apply_surgical_updates()` | Character-precise replacements    | Reverse-order offset-based  |
| `_reconstruct_memory()`     | Full markdown regeneration        | Fallback when offsets stale |

### MemoryUpdate Dataclass

```python
@dataclass
class MemoryUpdate:
    element_type: str              # 'field' or 'section'
    element_id: str                # Field/section identifier
    new_value: Any                 # str for fields, list[ParsedItem] for sections
    old_offset: OffsetInfo | None  # Character positions (None for additions)
```

**Validation:**

- `element_type` must be `"field"` or `"section"`
- `element_id` cannot be empty
- `new_value` cannot be `None` (use `""` or `[]` for removal)

### Change Detection

The `detect_changes()` function compares old and new memory states:

**Field Changes:**

- **Added:** `old_field is None and new_field is not None` → `old_offset=None`
- **Removed:** `old_field is not None and new_field is None` → `new_value=""`
- **Modified:** `old_field.value != new_field.value` → `old_offset` from old field

**Section Changes:**

- **Added:** `old_section is None` → `old_offset=None`
- **Removed:** `old_section is not None and new_section is None` → `new_value=[]`
- **Modified:** Compare item texts: `[item.text for item in items]`

**Example:**

```python
old_memory = ParsedMemory(
    fields={"status": ParsedField(field_id="status", value="in_progress", offset=...)},
    sections={}
)
new_memory = ParsedMemory(
    fields={"status": ParsedField(field_id="status", value="completed", offset=None)},
    sections={}
)

updates = detect_changes(old_memory, new_memory)
# → [MemoryUpdate(element_type="field", element_id="status", 
#                  new_value="completed", old_offset=OffsetInfo(...))]
```

### Surgical Update Strategy

The `_apply_surgical_updates()` function applies changes using character offsets:

**Algorithm:**

1. **Sort updates:** Reverse order by `start_char` (end → start)
2. **For each update:**
   - Validate offset bounds: `0 <= start_char < end_char <= len(text)`
   - Render replacement: `_render_field_update()` or `_render_section_update()`
   - Replace substring: `text[:start] + replacement + text[end:]`
3. **Check for additions:** If any `old_offset is None` → raise `ValueError`

**Why reverse order?**

- Prevents earlier replacements from invalidating later offsets
- Example: Replacing at char 100, then char 50 → both offsets stay valid

**Offset Validation:**

```python
if offset.start_char < 0 or offset.end_char > len(result):
    raise ValueError(f"Invalid offset range: {offset}")

if offset.start_char >= offset.end_char:
    raise ValueError(f"Invalid offset ordering: {offset}")
```

**Note:** These defensive checks are redundant because `OffsetInfo.__post_init__()` validates earlier, but provide defense-in-depth.

### Fallback Reconstruction

When surgical updates fail, the system falls back to `_reconstruct_memory()`:

**Triggers:**

- File manually edited between parse and update (stale offsets)
- Offsets out of bounds (`IndexError`)
- New elements added (`old_offset is None`)
- Structural changes (`AttributeError`)

**Reconstruction Format:**

```markdown
**field_id:** single-line value

**field_id:**
multi-line value
line 2

### Section Title

- [ ] Item 1
- [x] Item 2
```

**Limitations:**

- Comments outside fields/sections are lost
- Whitespace normalized to standard format
- Original formatting not preserved

### Rendering Functions

**Field Rendering** (`_render_field_update()`):

```python
if "\n" in value:
    return f"**{field_id}:**\n{value}"  # Multi-line
else:
    return f"**{field_id}:** {value}"    # Single-line
```

**Section Rendering** (`_render_section_update()`):

```python
lines = [
    f"### {section_id.title()}",
    "",
    *[f"- [{'x' if item.complete else ' '}] {item.text}" 
      for item in items]
]
return "\n".join(lines)
```

### Usage Example

```python
from reerelease.service.dsl.pipeline import DSLPipeline

# Parse original file
pipeline = DSLPipeline.from_template(template_path, template_dir)
original_text = Path("milestone.md").read_text()
old_memory = pipeline.parse(original_text)

# Create updated memory
new_memory = old_memory.copy()
new_memory.fields["status"].value = "completed"

# Apply surgical update
from reerelease.service.dsl.inplace_edit import apply_memory_updates
updated_text = apply_memory_updates(original_text, old_memory, new_memory)

# Or use pipeline convenience method
updated_text = pipeline.update_memory_file(
    Path("milestone.md"),
    {"status": "completed", "progress": "100%"}
)
```

### Coverage & Testing

**Test Coverage:** 99.42% (113/113 statements, 59/60 branches)

**Test Categories:**

- **Unit Tests (34 tests):** MemoryUpdate validation, change detection, rendering
- **Integration Tests (8 tests):** End-to-end workflows, formatting preservation, fallback behavior

**Key Test Patterns:**

- **Exact assertions:** Use `assert result == "expected"` not `"substring" in result`
- **Offset precision:** Character positions must be exact (off-by-one catches bugs)
- **Mock objects:** Use `MockOffset` classes to bypass `OffsetInfo` validation for defensive code tests

**Example Strong Test:**

```python
def test_apply_memory_updates_preserves_surrounding_content():
    original = "# Header\n\n**status:** in_progress\n\n## Footer\n"
    old_memory = ParsedMemory(
        fields={"status": ParsedField(
            field_id="status", value="in_progress",
            offset=OffsetInfo(start_line=3, end_line=3, start_char=10, end_char=33)
        )},
        sections={}
    )
    new_memory = ParsedMemory(
        fields={"status": ParsedField(field_id="status", value="completed", offset=None)},
        sections={}
    )
    
    result = apply_memory_updates(original, old_memory, new_memory)
    
    # Exact assertion catches offset errors
    assert result == "# Header\n\n**status:** completed\n\n## Footer\n"
```

### Design Decisions

**Why character offsets instead of line numbers?**

- Precise substring replacement without parsing
- Handles inline fields and multi-line values uniformly
- Single replacement operation: `text[start:end]`

**Why reverse-order application?**

- Prevents offset invalidation
- Simpler than recalculating offsets after each edit

**Why fall back instead of failing?**

- Ensures updates always succeed (correctness > optimization)
- Handles manual edits gracefully
- Reconstruction is fast enough (<1ms for typical files)

**Future Enhancements:**

- Smart insertion for additions (currently triggers fallback)
- Whitespace-aware rendering to match original style
- Incremental offset recalculation for multiple edits

---

## Performance Considerations

- **Regex compilation:** Patterns compiled once in Phase 1, reused in Phase 2
- **Token traversal:** Single-pass AST walk for field/section extraction
- **Memory allocation:** Dataclasses with `default_factory` for efficient dict/list creation
- **Issue aggregation:** Lists reused across phases (no re-allocation)

**Optimization Tips:**

- Use specific `level` constraints to reduce heading search space
- Apply `title_like` patterns for precise section matching
- Prefer named capture groups over full-text extraction
- Avoid overlapping field definitions (causes line skipping)
