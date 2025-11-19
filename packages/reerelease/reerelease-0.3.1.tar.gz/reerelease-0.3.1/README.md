# REErelease

[![PyPI - Version](https://img.shields.io/pypi/v/reerelease?color=bright-green)][pypi_reerelease_link] ![Coverage](docs/coverage.svg)  ![Tests](docs/tests.svg)

Imagine you had only 3 file to manage and plan your projects: ***readme***, ***roadmap*** and ***release***  
Now imagine a **simple cli** interface to `release`, `update`, `document` the lifecycle of those projects  
So you have time and mental space to put on the actual work and architect your project in a simple straigth-forward way  
This is what [REErelease][repo_link] aims to enable, simple markdown project management, automated yet flexible  
It does support *monorepo* environment and other nested *contexts* scenarios  

Based on [typer]/[click], [jinja2] and [questionary]

## Quick Start

### Installation

```sh
pip install reerelease
```

### Basic Usage

```sh
# Create new project context with templates
reerelease context new my-project

# Discover existing contexts in current directory
reerelease context list
```

> 📖 **Complete command reference**: See the [commands](/docs/commands.md) reference for detailed usage and options.

## Development

### Setup

1. Install [hatch]
2. Clone and setup:

   ```sh
   git clone git@gitlab.com:real-ee/tool/reerelease.git
   cd reerelease
   hatch run setup
   ```

### Git Hooks Setup

**Automated quality assurance** is enforced through Git hooks:

```sh
python tools/setup_hooks.py
```

> NOTE: this is automatically run during [setup](#setup)

This configures:

- 🎨 **Code formatting** (ruff format)
- 🔍 **Linting** (ruff check)
- 🏷️ **Type checking** (mypy)
- 🧪 **Testing** (pytest)
- 📊 **Badge generation** (coverage + test badges)
- 🔒 **Push validation** (ensures quality gates passed)

### Development Workflow

#### Normal Development

```sh
git add .
git commit -m "Your changes"  # Runs full validation pipeline
git push                      # Validates commit has passed checks
```

The hooks runs:

1. Formats code with ruff
2. Runs linting checks
3. Validates type annotations
4. Executes test suite
5. Updates coverage/test badges
6. Adds validation marker to commit

> **NOTE:** They are forced on the main/master branch or you can trigger them manually by adding `[force-hooks]` or `[verify-hooks]` to your commit message
> Alternatively than can be triggered by environment variable `FORCE_HOOKS=1 git commit -m 'feature commit'`

#### Emergency Bypass

```sh
git commit --no-verify -m "Emergency fix [skip-hooks]"
git push --no-verify
```

### Testing

```sh
# Run tests
hatch run test

# Run tests with detailed output
hatch run pytest -- --show-fail-details tests

# Generate coverage report
hatch run cov

# Generate all reports
hatch run reports
```

### VS Code Integration

The project includes [VS Code][vscode_install_link] settings for:

- **Ruff** integration with auto-fix on save
- **MyPy** type checking in Problems Panel
- **Pytest** test discovery and execution
- **Task runners** for common operations

> **Setup**: After opening the project, VS Code should automatically detect the hatch environment. If not, use `Ctrl+Shift+P` → "Python: Select Interpreter" and choose the hatch virtual environment (usually shows as `reerelease` with the hatch path).

#### Available Tasks

Open the project in [VS Code][vscode_install_link] and use `Ctrl+Shift+P` → "Tasks: Run Task":

- **pytest** - Run test suite
- **pytest (show CLI output on fail)** - Run tests with detailed failure output
- **pytest (debug logs)** - Run tests with verbosity set to DEBUG
- **pytest run test under cursor** - Run the test at cursor using helper script
- **pytest generate reports** - Generate coverage and test reports in [docs](/docs/) folder
- **Fix All Ruff Issues** - Auto-fix linting issues
- **Format Code** - Format code with ruff
- **Quality Check (All)** - Run complete quality pipeline
- **MyPy Type Check** - Run MyPy type checking

#### Debug/Launch Configurations

Use `F5` or "Run and Debug" panel:

- **Show Help** - Display reerelease CLI help
- **Quality Check** - Run full quality pipeline
- **Setup: Demo Monorepo** - Create demo monorepo
- **Test: List Demo Monorepo** - List demo monorepo contexts
- **Add Context (demo)** - Create demo context in /tmp
- **List Contexts (demo)** - List contexts in demo directory
- **Emit Test Logs** - Generate test log output

#### Quick Commands

- `Ctrl+Shift+P` → "Python: Configure Tests" (pytest)
- `Ctrl+Shift+P` → "Python: Run All Tests"
- `Ctrl+Shift+P` → "Tasks: Run Task" → Choose from available tasks

### Publishing workflow

1. Bump version in `src/reerelease/__about__.py`
2. Update release notes in release.md
3. Test release (optional but recommended)

   ```sh
   hatch run release-dry-run    
   ```

4. Production release

   ```sh
   hatch run release    
   ```

**Automated release process**:

- Version validation (checks git tags + PyPI)
- Quality checks (format, lint, typecheck, tests)
- Build package and validate distribution
- Create git tag and push to origin
- Publish to PyPI

**Manual alternative**: `python3 tools/release.py [--test-pypi]`

## Project Structure

<details>
<summary>📁 View complete project structure</summary>

``` bash
reerelease/
├── src/
│   └──reerelease/                     # Main package
│      ├── __about__.py                # Package version and metadata
│      ├── __init__.py                 # Package initialization
│      ├── reerelease.py               # Main logic and CLI entry
│      ├── errors.py                   # Custom Exceptions and error types
│      ├── config.py                   # App global configuration and defaults value
│      ├── cli
│      │   ├── commands/               # CLI command modules
│      │   │   ├── context.py
│      │   │   ├── milestone.py
│      │   │   ├── problem.py
│      │   │   └── task.py
│      │   ├── console.py              # Console specific methods
│      │   └── error_codes.py          # CLI exit codes
│      ├── core/                       # Core dataclasses and functions
│      │   ├── context.py              # Memory representation of contextes
│      │   ├── logging.py              # Logging configuration
│      │   ├── milestone.py            # Memory representation of milestones
│      │   └── task.py                 # Memory represnetation of tasks
│      ├── service                     # Middle layer services, contain file io and other complex shared algo
│      │   ├── dsl                     # Custom DSL 
│      │   │   ├── inplace_edit.py     # Inplace edition (minimal-churn) functions
│      │   │   ├── memory_manager.py   # Parsed memory management
│      │   │   ├── phase1_specs.py     # Template annotation parsing phase
│      │   │   ├── phase2_parser.py    # Content input phase
│      │   │   ├── phase3_renderer.py  # Content output phase
│      │   │   ├── phase4_validator.py # Validation phase
│      │   │   └── pipeline.py         # Wrapping oject and simple-to-use API
│      │   ├── context_manager.py      # Context management service
│      │   ├── milestone_manager.py    # Milestone management service
│      │   └── template_manager.py     # Template management and rendering service
│      ├── validators                  # Static validators
│      │   ├── validate_context.py     # Context specific validation
│      │   ├── validate_dsl.py         # Validator for the DSL pipeline
│      │   └── validate_milestone.py   # Milestone specific validation
│      └── templates/                  # Jinja2 templates
│          ├── common/                 # Shared template fragments
│          ├── context/                # Context templates
│          ├── domain/                 # Domain templates
│          ├── milestone/              # Milestone templates
│          └── task/                   # Task templates
├── tests/                             # Test suite
│   └── ...
├── tools/                             # Development tools
│   ├── release.py                     # Automated release script
│   ├── run_pytest_node.py             # Helper to run pytest for editor integrations
│   ├── setup_demo_monorepo.sh         # Demo monorepo setup script
│   ├── setup_hooks.py                 # Git hooks installer
│   └── update_badge.py                # Badge generation script
├── .vscode/                           # VS Code configuration
│   ├── settings.json                  # Editor settings
│   ├── tasks.json                     # Task definitions
│   └── launch.json                    # Debug configurations
├── docs/                              # Documentation and badges
│   ├── architecture.md                # Software architecture description
│   ├── commands.md                    # Command reference
│   ├── coverage.svg                   # Tests coverage badge
│   ├── dsl.md                         # Custom DSL specification and guideline
│   ├── metadata.md                    # Supported metadata specifications
│   ├── tests.svg                      # Tests number and success badge
│   └── user_guide.md                  # Top-level user guide for quick start and understanding
├── pyproject.toml                     # Python project & tooling configuration
├── README.md                          # This file
├── release.md                         # Release log
├── roadmap.md                         # Planned future version and functionnality
└── license.txt                        # License
```

</details>

## Quality Assurance

This project aims to maintains **100% test coverage** and strict code quality through:

- **Modern Python tooling**: Ruff (linting/formatting), MyPy (type checking)
- **Comprehensive testing**: pytest with full coverage reporting
- **Automated validation**: Git hooks ensure all changes pass quality gates
- **Badge tracking**: Visual indicators of test and coverage status

## License

Released under [MIT](/license.txt) open-source license

<!-- links -->

[vscode_install_link]: https://code.visualstudio.com/download
[repo_link]: https://gitlab.com/real-ee/tool/reerelease
[hatch]: https://hatch.pypa.io/1.12/install/
[pypi_reerelease_link]: https://pypi.org/project/reerelease/
[typer]: https://typer.tiangolo.com/
[click]: https://click.palletsprojects.com/en/stable/
[jinja2]: https://jinja.palletsprojects.com/en/stable/
[questionary]: https://github.com/tmbo/questionary
