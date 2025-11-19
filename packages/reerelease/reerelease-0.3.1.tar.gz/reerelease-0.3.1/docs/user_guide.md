# REErelease User Guide

Quick reference guide for using REErelease to manage your project documentation through markdown files.

> NOTE: *This guide covers REErelease **v0.3.x** and later. For older versions, some commands may differ.*

- [REErelease User Guide](#reerelease-user-guide)
  - [What is REErelease?](#what-is-reerelease)
  - [Installation](#installation)
  - [Core Concepts](#core-concepts)
    - [Context](#context)
    - [Milestone](#milestone)
    - [Task](#task)
    - [Problems](#problems)
  - [Quick Start](#quick-start)
    - [Create Your First Context](#create-your-first-context)
    - [View Existing Contexts](#view-existing-contexts)
    - [Remove a Context](#remove-a-context)
  - [Working with Milestones](#working-with-milestones)
    - [List Milestones](#list-milestones)
    - [Add a Milestone](#add-a-milestone)
    - [Update a Milestone](#update-a-milestone)
    - [Remove a Milestone](#remove-a-milestone)
  - [Working with Tasks](#working-with-tasks)
    - [Manual Task Management](#manual-task-management)
    - [Backlog Section](#backlog-section)
  - [Context Organization](#context-organization)
    - [Monorepo Example](#monorepo-example)
    - [Single Project Example](#single-project-example)
  - [Command Reference](#command-reference)
  - [Best Practices](#best-practices)
    - [Naming Conventions](#naming-conventions)
    - [Workflow Tips](#workflow-tips)
    - [File Management](#file-management)
  - [Troubleshooting](#troubleshooting)
    - [Context Not Found](#context-not-found)
    - [Cannot Create Context](#cannot-create-context)
    - [Invalid Milestone Name](#invalid-milestone-name)
    - [Permission Denied](#permission-denied)
  - [Advanced Usage](#advanced-usage)
    - [Context Discovery Depth](#context-discovery-depth)
    - [Batch Operations](#batch-operations)
    - [Integration with Git](#integration-with-git)
  - [Getting Help](#getting-help)
    - [Command Help](#command-help)
    - [Resources](#resources)
  - [Quick Command Cheatsheet](#quick-command-cheatsheet)

---

## What is REErelease?

REErelease manages your project through **3 markdown files**:

- **readme.md** — Project overview and guidelines
- **roadmap.md** — Planned work organized by milestones
- **release.md** — Release history and notes

It works with **contexts** (projects/subprojects) organized hierarchically, making it ideal for monorepos.  
It is structured as an automatic tool to help and supplement manual project management,  
do not feel forced to use this tool for all it's capabilities, it is here to help automate part of **your** workflow.

---

## Installation

```sh
pip install reerelease
```

Verify installation:

```sh
reerelease --version
```

---

## Core Concepts

### Context

A **context** is a project or subproject with its own set of readme, roadmap, and release files.

- Contexts can be nested (e.g., monorepo with multiple packages)
- Each context has a name (can be duplicated, will use the path as differentiator)
- Files can be automatically generated from templates and read following a specific [DSL](/docs/dsl.md)

### Milestone

A **milestone** is a planned release or development phase in your roadmap within a [context](#context)

- Has a name (e.g., `0.1.0`, `Phase1`, `Q1-2025`)
- A description (ie: *First MVP release*)
- Contains a list of tasks to complete and known problems
- Tracks status: `planned`, `in-progress`, `completed`, `released`
- Has an optional target date

### Task

A **task** is a checkbox item within a [milestone](#milestone) representing work to be done.

- Appears as `- [ ]` (incomplete) or `- [x]` (complete) in markdown
- Tasks can have assignees: `- [ ] Fix bug (@alice)` (MVP implementation for now)
- They will be able to have metadata like due-date, priority, linked tasks/problem, etc in future release (see [roadmap](/roadmap.md))

### Problems

A **problem** is a list item within a [milestone](#milestone) describing a known problem of a milestone.

- Implementation will be done in the short future, see [roadmap](/roadmap.md)

---

## Quick Start

### Create Your First Context

```sh
# Create a new project context
reerelease context add my-project

# Or create in current directory without subfolder
reerelease context add my-project --inplace
```

This generates:

- `readme.md` — Basic project documentation
- `roadmap.md` — Empty roadmap with Backlog section
- `release.md` — Empty release history

### View Existing Contexts

```sh
# List all contexts in current directory
reerelease context list

# List contexts in specific path
reerelease context list --path /path/to/project

# Limit search depth
reerelease context list --depth 5
```

### Remove a Context

```sh
# Remove a context (prompts for confirmation)
reerelease context remove my-project

# Force removal without confirmation
reerelease context remove my-project --force
```

---

## Working with Milestones

### List Milestones

```sh
# List milestones in current (or first found) context
reerelease milestone list

# List milestones in specific context
reerelease milestone list --context my-project --path /path/to/search
```

### Add a Milestone

```sh
# Add milestone with all details provided
reerelease milestone add 0.1.0 \
  --context my-project \
  --desc "Initial release" \
  --date 2025-12-31 \
  --status planned

# Interactive mode (prompts for missing info)
reerelease milestone add 0.1.0
```

**Milestone name formats:** Any alphanumeric identifier (e.g., `0.1.0`, `Phase1`, `Q1-2025`)

**Valid statuses:** See [milestone status reference](/docs/metadata.md#milestone---status)

### Update a Milestone

```sh
# Update milestone properties
reerelease milestone update 0.1.0 \
  --name 0.2.0 \
  --desc "Updated description" \
  --status in-progress

# Interactive mode
reerelease milestone update 0.1.0
```

### Remove a Milestone

```sh
# Remove milestone (prompts for confirmation)
reerelease milestone remove 0.1.0

# Force removal
reerelease milestone remove 0.1.0 --force
```

---

## Working with Tasks

### Manual Task Management

For now they are only written manually, but a basic form is understandable by the app.  
A `task` command is coming in version [0.4.0](/roadmap.md#040) with automatic capabilities.  
Tasks are managed directly in the `roadmap.md` file under each milestone section:

```markdown
## 0.1.0

Initial release  
**Target date:** 2025-12-31  
**Status:** in-progress

- [ ] Set up project structure
- [x] Create documentation
- [ ] Write tests (@alice)
- [ ] Deploy to production
```

**Task format:**

- `- [ ]` — Incomplete task
- `- [x]` — Complete task
- `- [ ] Task text (@user)` — Task assigned to user

### Backlog Section

The **Backlog** (or **Unassigned**) section contains tasks not yet assigned to a milestone.  
See [ignored H2 sections](/docs/metadata.md#ignored-h2-sections) for special roadmap sections.

```markdown
## Backlog

- [ ] Future feature idea
- [ ] Technical debt cleanup
- [ ] Performance optimization
```

---

## Context Organization

### Monorepo Example

``` sh
my-company/
├── readme.md          # Root context
├── roadmap.md
├── release.md
├── frontend/
│   ├── readme.md      # Frontend context
│   ├── roadmap.md
│   └── release.md
└── backend/
    ├── readme.md      # Backend context
    ├── roadmap.md
    └── release.md
```

Create this structure:

``` sh
cd my-company
reerelease context add my-company --inplace
reerelease context add frontend
reerelease context add backend
```

### Single Project Example

``` sh
my-app/
├── readme.md
├── roadmap.md
└── release.md
```

Create this structure:

``` sh
mkdir my-app
cd my-app
reerelease context add my-app --inplace
```

---

## Command Reference

For complete command documentation including all options, arguments, and exit codes, see the [Commands Reference](/docs/commands.md).

**Quick command overview:**

- `context list` / `add` / `remove` / `check` — Manage project contexts
- `milestone list` / `add` / `update` / `remove` / `check` — Manage milestones
- `task` / `problem` — Planned for future releases (see [roadmap](/roadmap.md))

**Global options:** `--quiet`, `--verbosity`, `--version`, `--help`

---

## Best Practices

### Naming Conventions

**Contexts:**

- Use lowercase with hyphens: `my-project`, `api-gateway`
- Avoid spaces and special characters
- Be descriptive but concise

**Milestones:**

- For versions: Use semantic versioning (`0.1.0`, `1.2.3`)
- For phases: Use clear identifiers (`Phase1`, `Q4-2025`, `Beta`)
- Stay consistent within a project

### Workflow Tips

1. **Start with contexts** — Set up your project structure first
2. **Plan milestones early** — Define releases before detailed tasks
3. **Keep tasks actionable** — Each task should be a single, completable unit
4. **Use the Backlog** — Capture ideas without committing to a milestone
5. **Update regularly** — Mark tasks complete as you finish them
6. **Review before release** — Ensure all milestone tasks are complete

### File Management

**Do:**

- Edit roadmap.md directly to add/modify tasks
- Use version control (git) for all markdown files
- Keep descriptions concise and clear

**Don't:**

- Expect this tool to be perfect, it is a work-in-progress

---

## Troubleshooting

### Context Not Found

``` sh
Error: No context found at path
```

**Solution:** Verify the path and ensure readme.md, roadmap.md, and release.md exist.

### Cannot Create Context

``` sh
Error: Context already exists
```

**Solution:** Use `--force` to overwrite, or choose a different name/location.

### Invalid Milestone Name

``` sh
Error: Invalid milestone name format
```

**Solution:** Use alphanumeric characters, dots, hyphens, or underscores only.

### Permission Denied

``` sh
Error: Permission denied writing to file
```

**Solution:** Check file permissions and ensure you have write access to the directory.

---

## Advanced Usage

### Context Discovery Depth

Control how deep REErelease searches for contexts:

``` sh
# Search only current directory
reerelease context list --depth 1

# Deep search (default: 10 levels)
reerelease context list --depth 20
```

### Batch Operations

Use shell scripting for batch operations:

``` sh
# Create multiple contexts
for ctx in frontend backend api; do
  reerelease context add $ctx
done

# List all milestones across contexts
find . -name roadmap.md -exec reerelease milestone list --path {} \;
```

### Integration with Git

Track changes and releases:

``` sh
# After adding milestone
git add roadmap.md
git commit -m "Add milestone 0.1.0"

# When completing a release
git tag -a v0.1.0 -m "Release version 0.1.0"
git push --tags
```

> NOTE: a `release` command is coming in version [0.5.0](/roadmap.md#050) which will help trigger scripts and automate the release of a project

---

## Getting Help

### Command Help

```sh
# General help
reerelease --help

# Command-specific help
reerelease context --help
reerelease milestone add --help
```

### Resources

- **Commands Reference**: See `docs/commands.md` for detailed API documentation
- **DSL Reference**: See `docs/dsl.md` for template system details
- **Repository**: [GitLab - REErelease](https://gitlab.com/real-ee/tool/reerelease)
- **Issues**: Report bugs via GitLab issue tracker

---

## Quick Command Cheatsheet

```sh
# Context management
reerelease context list                   # List contexts
reerelease context add my-project         # Create context
reerelease context remove my-project      # Delete context

# Milestone management
reerelease milestone list                 # List milestones
reerelease milestone add 0.1.0            # Create milestone
reerelease milestone update 0.1.0         # Update milestone
reerelease milestone remove 0.1.0         # Delete milestone

# With options
reerelease context add project --inplace  # Create in current dir
reerelease milestone add 0.1.0 \
  --desc "First release" \
  --date 2025-12-31 \
  --status planned                        # Create with all details

# Common patterns
reerelease context list --path ./src --depth 5
reerelease milestone list --context my-project
reerelease context remove old-project --force
```
