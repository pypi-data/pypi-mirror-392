# REErelease Architecture

High-level overview of REErelease's structure and how different components interact.

---

## Overview

REErelease follows an **MVC-inspired architecture** with clear separation of concerns:

``` text
┌─────────────────────────────────────────────────────┐
│ CLI Layer (Typer)                                   │
│ ├─ context_app (list, add, remove, check)           │
│ ├─ milestone_app (list, add, update, remove, check) │
│ └─ task_app, problem_app (skeleton/planned)         │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│ Service Layer                                       │
│ ├─ ContextManager (discovery, creation, deletion)   │
│ ├─ MilestoneManager (parsing, CRUD operations)      │
│ ├─ TemplateManager (rendering, file handling)       │
│ └─ Global config & logging                          │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│ Core Layer (Data Models & Validators)               │
│ ├─ Context, Milestone, Task, Problem (dataclasses)  │
│ ├─ Validators (context, milestone, DSL)             │
│ └─ Errors (AppError hierarchy)                      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│ File I/O & Templates                                │
│ ├─ DSL Pipeline (phase 1-4: parse → render)         │
│ ├─ Template files (Jinja2)                          │
│ └─ Markdown file reading/writing                    │
└─────────────────────────────────────────────────────┘
```

---

## Layer Details

### CLI Layer (`src/reerelease/cli/`)

**Responsibility:** Parse user input, call service layer, display output.

**Structure:**

- `reerelease.py` — Root CLI app (Typer), entry point, global options
- `commands/` — Command groups
  - `context.py` — Context commands (`context_app`)
  - `milestone.py` — Milestone commands (`milestone_app`)
  - `task.py`, `problem.py` — Skeleton commands (planned in v0.4.0+)

**Characteristics:**

- Thin command handlers (no business logic)
- Interactive prompts via [questionary](https://github.com/tmbo/questionary)
- Confirmation dialogs for destructive operations
- Delegate all operations to service layer

**Example flow:**

``` python
# User: reerelease context add my-project
# → context.py handles argument parsing
# → calls ContextManager.create_context()
# → displays result
```

### Service Layer (`src/reerelease/service/`)

**Responsibility:** Business logic, state management, orchestration.

**Core classes:**

#### ContextManager

Manages context discovery, creation, and deletion.

**Key methods:**

- `discover_contexts(path, depth)` — Find all contexts recursively
- `create_context(name, path, inplace, force)` — Create new context with templates
- `delete_context(name, path, force)` — Remove context and validate
- `validate_context(context)` — Check file integrity

**Interactions:**

- Calls `TemplateManager` to generate files
- Creates `Context` objects from discovered directories
- Raises `ContextError` subclasses on failure

#### MilestoneManager

Manages milestone parsing, creation, and updates.

**Key methods:**

- `discover_milestones(context)` — Parse roadmap file, extract milestones
- `create_milestone(context, name, desc, date, status)` — Add milestone to roadmap
- `update_milestone(context, name, updates)` — Modify milestone properties
- `delete_milestone(context, name)` — Remove milestone from roadmap
- `validate_milestone(milestone)` — Check validity

**Interactions:**

- Uses DSL pipeline to parse/render markdown
- Creates `Milestone` and `Task` objects
- Calls validators for integrity checks

#### TemplateManager

Handles template rendering and file operations.

**Key methods:**

- `render_template(template_path, context_data)` — Jinja2 rendering
- `create_context_files(path, context_name)` — Generate readme/roadmap/release
- `read_file(path)` — Safe file reading with encoding
- `write_file(path, content)` — Safe file writing with backups

**Interactions:**

- Uses Jinja2 for template rendering
- Calls DSL memory manager for bidirectional sync
- Handles file permissions and encoding

#### GlobalConfig

Manages runtime configuration and logging.

**Properties:**

- `verbosity` — Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `quiet` — Suppress output
- `logger` — Configured Python logger

**Lifecycle:**

- Initialized in `main()` callback (before any command runs)
- Accessed globally via `GLOBAL_CONFIG`

### Core Layer (`src/reerelease/core/`)

**Responsibility:** Data structures, validation rules, error definitions.

**Data Models:**

#### Context

Represents a project context.

**Fields:**

- `name` — Context identifier
- `path` — Directory path containing readme/roadmap/release
- `readme_path`, `roadmap_path`, `release_path` — File locations
- `children` — Nested contexts (monorepo support)

#### Milestone

Represents a release or development phase.

**Fields:**

- `name` — Milestone identifier (e.g., `0.1.0`)
- `description` — Brief summary
- `target_date` — Optional deadline (ISO 8601)
- `status` — Current state (planned, in-progress, completed, released, canceled)
- `tasks` — List of `Task` objects
- `problems` — List of `Problem` objects (planned)

#### Task

Represents a work item.

**Fields:**

- `text` — Task description
- `complete` — Completion state (true/false)
- `assignee` — Assigned user (optional, MVP: `@username` format)
- `metadata` — Future: due date, priority, etc.

#### Problem

Planned data model for tracking known issues.

**Planned fields:**

- `text` — Problem description
- `severity` — Level (low, medium, high, critical)
- `resolution_task` — Linked task ID
- `milestone` — Associated milestone

**Validators:**

Located in `src/reerelease/validators/`:

- `validate_context_*` — File existence, permissions, structure
- `validate_milestone_*` — Name format, status values, dates
- `validate_dsl.py` — DSL parsing validation (phase 4)

**Errors:**

Hierarchy in `src/reerelease/errors.py`:

``` text
AppError (base)
├─ ContextError
│  ├─ ContextDiscoveryError
│  ├─ ContextCreationError
│  ├─ ContextDeletionError
│  └─ NoContextFound
├─ TemplateError
│  └─ TemplateCreationError
├─ MilestoneError
│  ├─ MilestoneDiscoveryError
│  ├─ MilestoneCreationError
│  ├─ MilestoneDeletionError
│  ├─ MilestoneUpdateError
│  ├─ InvalidMilestoneName
│  ├─ InvalidMilestoneStatus
│  └─ ...
└─ DSLError
```

### File I/O & Templates

**DSL Pipeline** (`src/reerelease/service/dsl/`)

Bidirectional markdown ↔ memory transformation:

``` text
Phase 1: Template Specification
  └─ Parse Jinja2 comments for DSL annotations
  └─ Extract field/section metadata

Phase 2: Markdown Parsing
  └─ Parse roadmap/readme/release markdown
  └─ Extract values based on spec
  └─ Create ParsedMemory objects

Phase 3: Rendering
  └─ Apply ParsedMemory to template
  └─ Generate updated markdown
  └─ Preserve unmanaged blocks

Phase 4: Validation
  └─ Check required fields
  └─ Validate formats and enums
  └─ Report issues
```

**Components:**

- `phase1_specs.py` — Parse DSL annotations → TemplateSpec
- `phase2_parser.py` — Parse markdown → ParsedMemory
- `phase3_renderer.py` — Render template + memory → markdown
- `phase4_validator.py` — Validate ParsedMemory
- `pipeline.py` — Orchestrate all phases
- `memory_manager.py` — Memory block management
- `inplace_edit.py` — Surgical edits with minimal churn

**Template Files** (`src/reerelease/templates/`)

Jinja2 templates with DSL annotations:

- `context/readme.md.j2` — README template
- `context/roadmap.md.j2` — Roadmap template (with milestone sections)
- `context/release.md.j2` — Release template
- `milestone/milestone_section.j2` — Reusable milestone block
- `section/file_links.j2` — File references section
- `common/` — Shared partials

---

## Data Flow Examples

### Creating a Context

``` text
User: reerelease context add my-project
  ↓
CLI (context.py)
  ├─ Parse arguments
  ├─ Call ContextManager.create_context()
  │   ├─ Validate name & path
  │   ├─ Check no overwrite (unless --force)
  │   ├─ Call TemplateManager.create_context_files()
  │   │   └─ Render templates with Jinja2
  │   │   └─ Write readme/roadmap/release
  │   ├─ Create Context object
  │   └─ Return success
  ├─ Display result to user
  └─ Exit with code 0
```

### Listing Milestones

``` text
User: reerelease milestone list --context my-project
  ↓
CLI (milestone.py)
  ├─ Parse arguments
  ├─ Call ContextManager.discover_contexts()
  │   └─ Find context by name
  ├─ Call MilestoneManager.discover_milestones(context)
  │   ├─ Read roadmap.md file
  │   ├─ Run DSL pipeline (phase 1-2)
  │   ├─ Extract Milestone objects
  │   └─ Return list
  ├─ Format & display milestones
  └─ Exit with code 0
```

### Adding a Milestone

``` text
User: reerelease milestone add 0.1.0 --desc "First release" --date 2025-12-31
  ↓
CLI (milestone.py)
  ├─ Parse arguments
  ├─ Validate inputs (validators)
  ├─ Call MilestoneManager.create_milestone()
  │   ├─ Read roadmap.md
  │   ├─ Run DSL pipeline phase 2 (parse existing)
  │   ├─ Create new Milestone object
  │   ├─ Add to ParsedMemory
  │   ├─ Run DSL pipeline phase 3 (render)
  │   ├─ Write updated roadmap.md
  │   └─ Return Milestone
  ├─ Display result
  └─ Exit with code 0
```

---

## Key Design Decisions

### MVC Separation

- **Model** (Core) — Data structures, validation rules
- **View** (CLI) — User interface, command parsing
- **Controller** (Service) — Business logic, orchestration

Benefits:

- Easy to test each layer independently
- CLI can be replaced without touching core logic
- Service layer reusable for different interfaces (API, GUI, etc.)

### DSL for Bidirectional Sync

- Parse markdown → Extract structured data (Phase 2)
- Modify structured data → Regenerate markdown (Phase 3)
- Preserve unmanaged blocks (custom content by users)
- Minimal churn edits (only changed sections updated)

Benefits:

- Users can edit files directly
- Tool can still parse and understand them
- No merge conflicts between automated updates and manual edits

### Error Hierarchy

- Specific error types for different failures
- Rich error context (file, line, reason)
- Enables targeted error handling in CLI
- Clear error messages to users

### Global Config

- Single source of truth for logging, verbosity, quiet mode
- Initialized before any command runs
- Accessible throughout application

---

## Testing Strategy

**Unit tests:**

- `tests/core/` — Test dataclass validation, error handling
- `tests/service/` — Test manager logic, edge cases
- `tests/validators/` — Test validation rules
- `tests/cli/` — Test command parsing, arg handling

**Integration tests:**

- `tests/dsl/` — Test DSL pipeline end-to-end
- `tests/integration/` — Test workflows (create context → add milestone → update)

**Coverage:**

- Target: >90% code coverage
- Run via: `hatch run coverage` or `hatch run reports`
- Reports in: `docs/coverage-report/`

---

## Dependencies

**Core dependencies:**

- **typer** — CLI framework with Click backend
- **jinja2** — Template rendering
- **questionary** — Interactive prompts
- **markdown-it-py** — Markdown parsing (AST-based, not regex)
- **anytree** — Tree structures for nested contexts

**Development dependencies:**

- **pytest**, **pytest-cov** — Testing & coverage
- **mypy** — Static type checking (strict mode)
- **ruff** — Linting & formatting
- **hatch** — Environment management & scripts

---

## Configuration

**Entry point:**

- `pyproject.toml` → `scripts.reerelease = "reerelease.reerelease:cli_hook"`

**Development scripts:**

- `hatch run test` — Run tests
- `hatch run quality` — Lint, type-check, test
- `hatch run format` — Auto-format code
- See `pyproject.toml` for full list

**Global options:**

- `--verbosity` — Set log level
- `--quiet` — Suppress output
- `--version` — Show version
- `--help` — Show help

---

## Future Enhancements

**Planned (see roadmap):**

- Task/Problem commands (v0.4.0) with automatic IDs
- Release functionality (v0.5.0) with git integration
- Template domains and marketplace (v0.7.0)
- Subtask relationships, priority, due dates (v0.6.0+)

**Architectural impact:**

- New command groups will follow existing CLI pattern
- Service managers will extend existing managers
- New validators for new field types
- Extended DSL for new metadata
