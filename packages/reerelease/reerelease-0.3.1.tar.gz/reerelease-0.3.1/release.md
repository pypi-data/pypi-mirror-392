# REErelease releases

## 0.3.1

Restructure, milestone and DSL pipeline
**Release date:** 2025-11-17
**Release artifact:** [pypi 0.3.1](https://pypi.org/project/reerelease/0.3.1/)
**Note:** Should have been 0.3.0 but release scripts failed and pypi.org doesn't allow re-using version

**Improvements:**

- Massive refactoring for long-term scalability (still needs work on the DSL part)
- Added user guide and overall documentation
- Added a DSL system to read annotation in the jinja templates making them bidirectionnal
- Added an inplace edit mecanism to make chirugical modification in files (fallback to full render)
- Extended the service layer (context_manager, milestone_manager, template_manager) to improve separation of concern and re-usability
- Improved validation methods
- Added a global config object giving r/w access to global configuration to almost all code context
- CLI code is now a thin layer calling services and reporting on it, arguably a real MVC now
- API now has `milestone` command operationnal (see [commands.md](/docs/commands.md)) for details
- API now has `context` command refactored and functionnal with more information and overall usefulness

## 0.2.0

Scalable command structure  
**Release date:** 2025-09-16  
**Release artifact:** [pypi 0.2.0](https://pypi.org/project/reerelease/0.2.0/)

**Improvement:**

- Improved command structure: added `context` command with subcommands (`list`, `add`, `remove`, `check`) and forwarded aliases `contexts` → `context list`, `new` → `context add`.
- Added skeleton commands for `task`, `problem`, and `milestone` to prepare for future task/problem management features.
- Integrated automatic hooks for linting, formatting, and type checking to run as part of the development workflow.
- Modular templating groundwork laid for later expansion into domain-specific templates and composition (no breaking changes to existing templates).
- Documentation and roadmap updated to reflect planned features and next milestones.

## 0.1.1

Minor metadata correction  
**Release date:** 2025-09-08  
**Release artifact:** [pypi 0.1.1](https://pypi.org/project/reerelease/0.1.1/)

**Correction:**

- Removed untested python version
- Added classifier for pypi publishing

## 0.1.0

Initial CLI & template creation  
**Release date:** 2025-09-08  
**Release artifact:** [pypi 0.1.0](https://pypi.org/project/reerelease/0.1.0/)

**New Commands:**

- `reerelease new <context-name> [path]` - Create new context with templates
- `reerelease contexts [path]` - Discover and display existing contexts

**Features:**

- Full Python TDD setup with automated testing and coverage
- Logging system with configurable verbosity levels
- Jinja2 templating engine for document generation
- Safe context creation (no overwriting existing contexts)
- Automatic context detection with name and path extraction
- Basic templates: release.md, roadmap.md, readme.md

**Foundation:**

Establishes the core architecture for template-based project documentation management with CLI interface and context discovery system.

**Known problem:**

- Very basic templating system
- Command structure not scalable
