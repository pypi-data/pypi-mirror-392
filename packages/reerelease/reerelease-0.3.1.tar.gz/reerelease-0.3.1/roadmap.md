# REErelease roadmap

---

## Unassigned

Unschedule but planned development

- [ ] advanced template composition with dependency resolution between sections
- [ ] (MAYBE) bulk section operations (add multiple related sections in single command)
- [ ] capability to release multiple ready *milestone* at the same-time (will still be different commit)
- [ ] (MAYBE) template inheritance chains (base → domain → project-specific customizations)
- [ ] (MAYBE) template variable inheritance system from context to sections to domains
- [ ] frontmatter support for extra custom metadata and logic
- [ ] manage estimated duration for milestone instead of fixed target date
- [ ] encode context configuration in themself in a standard way, readable by DSL
  - [ ] *milestone* statuses in a legend in roadmap
  - [ ] *milestone* ordering for roadmap in roadmap
  - [ ] *developper* list in readme for assigning tasks
  - [ ] *domains* included in the *context* in readme so we have visibility

---

## 0.7.0

Advanced modular template system  
**Target release date:** 2025-11-28

- [ ] domain-specific template library expansion (embedded systems, web development, data science, etc)
- [ ] template marketplace/registry concept for community-contributed sections
- [ ] intelligent template suggestion based on context analysis and file patterns
- [ ] template validation system to ensure section compatibility and variable consistency
- [ ] automated cross-linking maintenance when sections are added/removed/modified
- [ ] mixed domain support within single context for mono-repo patterns
- [ ] section template composition system for combining multiple sections
- [ ] `milestone` command
  - [ ] `add` `--domain` specify a specific *domain* covered by this *milestone*
- [ ] modular template functionality, `context add CONTEXT --domain DOMAIN1,DOMAIN2,etc`
  - [ ] modular template architecture with base/sections/domains structure
  - [ ] domain-specific template sections (python/pcb/rust/firmware/etc) with explicit selection
  - [ ] smart parsing to detect existing structure and insert sections appropriately
  - [ ] template section insertion mechanism with marker-based parsing (`<!-- reerelease:section_name -->`)
  - [ ] complete release *template*
  - [ ] complete roadmap *template*
  - [ ] complete readme *template*

---

## 0.6.0

Tasks management improvement  
**Target release date:** 2025-11-14

- [ ] *subtask* capabilities (parsing, mapping, auto-parent-completion, etc)
- [ ] *problem* to *task* resolution linking
- [ ] *Developper* listing and linking in readme
- [ ] *Tasks* *labels* definition in readme
- [ ] section template versioning and update mechanism

### 0.6.0 API addition

- [ ] `task` command
  - [ ] `add` `--label` adding a tasks with specified labels from a list (from context)
  - [ ] `add` `--assign` assigning the new task to one of the developper listed (from context)
- [ ] `problem` command
  - [ ] `add` `--notask` disabling the auto-creation of a resolving *tasks* for *problems*
  - [ ] `add` `--solve_milestone` determining which milestone the resolving *task* is attached to
  - [ ] `add` `--assign` assigning the resolving task to one of the developper listed (from context)
  - [ ] `add` `--severity` designating a severity to the *problem* and the resolving *task*
- [ ] `context` command
  - [ ] `remove` `--removechild` also remove child context of the targeted context

---

## 0.5.0

Release functionnality  
**Target release date:** 2025-10-31

- [ ] documented guideline on the release process
- [ ] file logging capabilities
- [ ] additional execution hook at pre/post `release` command
- [ ] additional execution hook for documentation at post `update` command
- [ ] cross-reference generation between roadmap and release sections automatically
- [ ] `milestone` `release` command
  - [ ] `--context` and `--path` arguments
  - [ ] `--dry-run` to try the release without doing it
  - [ ] `--message` giving the actual message for the release
  - [ ] release title and message (saved to both release.md and git history)
  - [ ] automatic date tagging
  - [ ] automatic git tagging
  - [ ] automatic update of release file and completed defined *task* for a *milestone*
  - [ ] automatic linking between release and roadmap files

---

## 0.4.0

Task and problem functionnality  
**Target release date:** 2025-10-21
**Status:** planned

### 0.4.0 Functionality change

- [ ] ignoring mecanism to skip folder under the root context (useful for external lib that would use reerelease)
- [ ] *task* functionality
  - [ ] automatic unique id assigned to each *tasks* (within a context)
- [ ] *problem* functionality
  - [ ] automatic unique id assigned to each *problem* (based on root context)
- [ ] Progress bar/display during file searching/parsing
- [ ] Add a ParsedMemory visualization user debugging function (printing in a clear way, what is understood by the app to the user)
- [ ] Architecture proper documentation
  - [ ] Layer interaction diagram
  - [ ] Dependency graph
- [ ] Refactoring of services for clearer processes
  - [ ] Single file manipulator service
  - [ ] Streamline the DSL pipeline to take a path and extract all information discovered and available into usable Context tree object
- [ ] Roadmap's *milestone* ordering control via config (name decreasing (DEF), name increasing, date dec/inc, arbitrary)

### 0.4.0 API addition

- [ ] `task` command
  - [ ] `list` discovers and show all the *task* with `--context` and `--path` arguments
  - [ ] `add` add a *task* to a context with `--context`, `--path` and `--milestone` arguments
  - [ ] `remove` deletes a task with `--context` and `--path` arguments
  - [ ] `remove` `--force` skipping confirmation check
- [ ] `problem` command
  - [ ] `list` discovers and show all the *problems* with `--context` and `--path` arguments
  - [ ] `add` add a *problem* to a context with `--context`, `--path` and `--milestone` arguments
  - [ ] `resolve` completes a problem with `--context`, `--path` and `--comment` arguments
  - [ ] `remove` deletes a problem with `--context` and `--path` arguments
  - [ ] `remove` `--force` skipping confirmation check

---

## 0.3.2

API patch and bug fixes
**Target date:** 2025-11-14
**Status:** planned

### API fix

- [ ] Add `-p` alias to **all** `--path` argument

---

## 0.3.0

Longterm restructure, milestone and interactivity, introducing template DSL  
**Target date:** 2025-10-03
**Status:** [released](/release.md#031)
**Note:** version 0.3.0 became 0.3.1 because of an erroneous upload to pypi.org

### 0.3.0 Functionality change

- [x] documented guideline on the new context creation process
- [x] update command reference guide
- [x] document the interaction of different app parts
- [x] introduce a [DSL](/docs/dsl.md) to define markdown file I/O variables and format
  - [x] refactor contexts templates
  - [x] implement milestone section template
  - [x] implement links section template
  - [x] implement DSL tested pipeline with >90% test coverage and openness to future modification
  - [x] implement minimal churn edits to preserve unmanaged blocks
  - [x] document DSL syntax
- [x] refactor the overall structure in an MVC pattern
  - [x] core holds dataclasses, representation and manipulation
    - [x] *context* dataclass object representing the parsed context
    - [x] *milestone* dataclass object
    - [x] *task* dataclass object
  - [x] service holds the state and flow control stuff
    - [x] move *contexts* manipulation methods instead of adhoc in *commands*
      - [x] refactor *context* discovery
      - [x] refactor *context* creation
      - [x] *context* removal (limited to leaf context for now)
    - [x] move *template* manager to service
    - [x] *milestone* manipulation methods in core
      - [x] *milestone* detection/parsing
      - [x] *milestone* creation
      - [x] *milestone* removal
  - [x] validators added for issues detecting and reporting
    - [x] *context* validation
      - [x] file presences and read/write permissions
      - [x] file content make sense (validated by DSL pipeline phase 4: validation)
    - [x] *milestone* validation
      - [x] content syntax is valid
      - [x] multiple milestone orders in context's roadmap is correct
  - [x] cli wires things together and may call extra ui eventually
    - [x] refactor for thin commands that calls on *services*
    - [x] introduction of [questionary](https://github.com/tmbo/questionary) for interactive menu and selection
      - [x] basic interactive prompt when creating a new context to create optional milestones
      - [x] `context` `remove` confirmation prompt
      - [x] `milestone` `remove` confirmation prompt
      - [x] `milestone` `add` & `update` argument input in interactive mode if not provided
  - [x] refactor tests to follow new structure

### 0.3.0 API addition

- [x] `milestone` command
  - [x] `list` with `--context` and `--path` arguments
  - [x] `add` with *MILESTONE*, `--context`, `--path`, `--title`, `--status` and `--date` arguments
  - [x] `remove` with *MILESTONE*, `--context` and `--path` arguments
  - [x] `remove` `--force` skipping confirmation check
  - [x] `update` with *MILESTONE*, `--context`, `--path`, `--title`, `--status`, `--name` and `--date` arguments
  - [x] `check` with *MILESTONE*, `--context`, `--path`
- [x] `context` command
  - [x] `remove` with *CONTEXT*, `--path` argument
  - [x] `remove` `--force` skipping confirmation check
  - [x] `add` `--force` skipping overwriting check
  - [x] `update` with *CONTEXT_NAME*, *CONTEXT_NEW_NAME*, `--path`, `--force`, `--rename_folder` arguments
  - [x] `check` with `--path` argument

### 0.3.0 API removal

- [x] remove `new` command (replaced by [`context add`](/docs/commands.md#context-command))
- [x] remove `contexts` command (replaced by [`context list`](/docs/commands.md#context-command))

---

## 0.2.0

Command restructuring, modular templating  
**Target date:** 2025-09-19
**Status:** [released](/release.md#020)

### 0.2.0 Tasks

- [x] automatic hook to run linting, formating and typechecking
- [x] *commands* restructuring and improvement
  - [x] `context` command with subcommand: `list`, `add`, `remove`, `check`
  - [x] skeleton commands: `task`, `problem`, `milestone`
  - [x] `contexts` forwarded to `context list`
  - [x] `new` forwarded to `context add`

---

## 0.1.0

Initial cli & template creation  
**Target date:** 2025-09-05
**Status:** [released](/release.md#010)

### 0.1.0 Tasks

- [x] full python tdd setup and workflow
- [x] automatic hook to run tests and coverage
- [x] logging system to stderr
- [x] templating engine creating basic templates at targeted path
- [x] no overwriting of existing *context*
- [x] *context* detection with name and path extraction
- [x] release template
- [x] roadmap template
- [x] readme template
