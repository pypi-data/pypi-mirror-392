# Reerelease supported metadata

This file describes all metadata used and understood by reerelease.  
More can be added, and at some point there will be a way to inject custom ones through config files or similar methods.

---

## Context

### Context Name

The name identifying a context within a project structure.

**Format:** Alphanumeric with hyphens and underscores  
**Examples:** `my-project`, `api_gateway`, `frontend`  
**Notes:**

- Names can be duplicated; path serves as differentiator
- Lowercase with hyphens recommended for consistency
- Altough they are supported, avoiding spaces and special characters is suggested to ensure filesystem doesn't complain

### Context Files

Each context consists of three markdown files:

- **readme.md** — Project overview, guidelines, and documentation
- **roadmap.md** — Planned milestones, tasks, and timeline
- **release.md** — Release history and version notes

---

## Readme

### Structure

Standard markdown document with project information.

**Common sections:**

- Overview/Description
- Installation/Getting Started
- Documentation links (roadmap, releases)
- Contributing guidelines
- License information

**Template variables:**

- `{{ context_name }}` — Context identifier

---

## Roadmap

### Ignored H2 sections

In a roadmap file, H2 headers determine different milestones. Specific titles are ignored and **not** considered milestones:

- `Backlog` — Tasks not assigned to a specific milestone
- `Unassigned` — Similar to Backlog
- `Note` — Generic notes section for additional details

### Milestone

A milestone represents a planned release or development phase.

#### Milestone Name

The identifier for a milestone within a context.

**Format:** Alphanumeric with dots, hyphens, underscores  
**Examples:**

- Version numbers: `0.1.0`, `1.2.3`, `v2.0`
- Named phases: `Phase1`, `Alpha`, `Beta`
- Date-based: `Q1-2025`, `2025-11`

**Notes:**

- Must be unique within a context
- Recommended to use semantic versioning for release versions
- Consistency within a project improves readability

#### Milestone Description

Brief text describing the milestone's purpose or goals.

**Format:** Plain text, typically 1-2 sentences  
**Examples:**

- "Initial MVP release"
- "Performance optimization and bug fixes"
- "Advanced template system implementation"

#### Milestone Target Date

Optional deadline for milestone completion.

**Format:** [ISO8601] date (`YYYY-MM-DD`)  
**Examples:** `2025-12-31`, `2026-03-15`  
**Notes:**

- Purely informational; no automatic enforcement
- Used for planning and timeline visualization

#### Milestone Status

Current state of the milestone.

**Values:**

- `planned` — Not yet started
- `in-progress` — Currently being worked on
- `completed` — Finished but not released
- `released` — Completed and published
- `canceled` — Abandoned or deprioritized
- `invalid` — Unknown or unrecognized status

**Default:** `planned`  
**Notes:** Status transitions typically follow: `planned` → `in-progress` → `completed` → `released`

#### Milestone Tasks

List of work items within a milestone.

**Format:** Markdown checkbox list items  
**Examples:**

``` markdown
- [ ] Incomplete task
- [x] Complete task
- [ ] Task with assignee (@alice)
```

**Task states:**

- `[ ]` — Not started or incomplete
- `[x]` or `[X]` — Complete

**Assignee format:** `(@username)` at end of task text (current implementation)  
**Future enhancements:** Due dates, priorities, links, subtasks (see [roadmap](/roadmap.md))

#### Milestone Problems

List of known issues or problems associated with a milestone.

**Format:** Markdown list items  
**Status:** Planned feature (see [roadmap](/roadmap.md))  
**Future capabilities:**

- Problem tracking within milestones
- Automatic resolution task creation
- Severity levels

---

## Release

### Release Structure

Release history organized by version/milestone.

**Common sections per release:**

- Release name (matches milestone)
- Release date
- Release artifacts
- Summary/description
  - Changes, features, fixes
  - Breaking changes (if any)
  - Upgrade notes

### Release name

Version identifier for a release.

**Format:** Matches milestone name  
**Examples:** `0.1.0`, `1.2.3`, `Phase1`  
**Notes:**

- Corresponds to milestone that was released
- Used for cross-referencing between roadmap and release files

### Release date

Date when a milestone was released.

**Format:** [ISO8601] date (`YYYY-MM-DD`)  
**Examples:** `2025-10-31`, `2026-01-15`  
**Notes:**

- Automatically set during `milestone release` command
- Should match git tag date for consistency

### Release artifacts

> TODO

### Summary / description

> TODO

#### Changes / features / fixes

#### Breaking changes

#### Upgrade notes

---

## Template Variables

Variables used in Jinja2 templates for file generation.

### Common Variables

- `{{ context_name }}` — Name of the context
- `{{ milestone_name }}` — Milestone identifier
- `{{ milestone_description }}` — Milestone summary
- `{{ milestone_target_date }}` — Target completion date
- `{{ milestone_status }}` — Current milestone status
- `{{ milestone_tasks }}` — List of tasks
- `{{ milestone_problems }}` — List of problems

### Template Files

Located in `src/reerelease/templates/`:

- `context/readme.md.j2` — README template
- `context/roadmap.md.j2` — Roadmap template
- `context/release.md.j2` — Release template
- `milestone/milestone_section.j2` — Milestone section template
- `section/file_links.j2` — Common file link for md substitution linking

---

## DSL Annotations

Special Jinja2 comments used for bidirectional markdown parsing.

**Format:** `{# @TYPE:IDENTIFIER attributes #}`

**Types:**

- `@field` — Single-value field (inline, paragraph, line)
- `@section` — Repeating sections (tasks, milestones)
- `@meta` — Metadata (DSL version, config)

**Reference:** See [DSL documentation](/docs/dsl.md) for complete specification

---

## Exit Codes

Standard Unix exit codes used by commands.

**Common codes:**

- `0` — Success
- `1` — Error (not found, permission denied, validation failed)
- `2` — Invalid arguments or configuration

**Reference:** See [commands documentation](/docs/commands.md) for command-specific codes

---

## Future Metadata

Planned metadata support (see [roadmap](/roadmap.md)):

- Task labels and priorities
- Developer/contributor assignments
- Domain-specific templates
- Custom metadata through configuration
- Subtask relationships
- Problem severity levels
- Cross-context dependencies

<!-- links -->
[ISO8601]: https://en.wikipedia.org/wiki/ISO_8601