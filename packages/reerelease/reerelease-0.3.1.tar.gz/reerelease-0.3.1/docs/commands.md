# REErelease Commands Reference

This document provides comprehensive reference for all REErelease CLI commands built with [Typer]. Commands follow [semantic versioning] principles and support standard Unix exit codes.

## Global Options

These options are available for all commands and follow standard CLI conventions:

| Option        | Short | Type   | Values                                | Default   | Description                            |
| ------------- | ----- | ------ | ------------------------------------- | --------- | -------------------------------------- |
| `--quiet`     | `-q`  | flag   | -                                     | `False`   | Disable all logging and console output |
| `--verbosity` | `-v`  | string | DEBUG, INFO, WARNING, ERROR, CRITICAL | `WARNING` | Set logging level                      |
| `--version`   | -     | flag   | -                                     | -         | Show version information and exit      |
| `--help`      | `-h`  | flag   | -                                     | -         | Show help message and exit             |

## Available Commands

Commands are organized by availability and planned implementation. See [roadmap] for detailed development timeline.

| Command                                | Subcommand                                            | Description                               | Since   | Status                  | Migration          |
| -------------------------------------- | ----------------------------------------------------- | ----------------------------------------- | ------- | ----------------------- | ------------------ |
| [`new`](#new-command-legacy)           | -                                                     | Create new project context with templates | [0.1.0] | ⚠️ Deprecated (0.2.0) | Use `add context`  |
| [`contexts`](#contexts-command-legacy) | -                                                     | Discover and display existing contexts    | [0.1.0] | ⚠️ Deprecated (0.2.0) | Use `list context` |
| [`context`](#context-command)          | `list`, `add`, `update`, `remove`, `check`            |                                           | [0.2.0] | 🛠️ Work in progress  |                    |
| [`task`](#task-command)                | `list`, `add`, `remove`                               |                                           | [0.4.0] | 🚧 Planned             |                    |
| [`problem`](#problem-command)          | `list`, `add`, `remove`, `resolve`                    |                                           | [0.4.0] | 🚧 Planned             |                    |
| [`milestone`](#milestone-command)      | `list`, `add`, `update`, `remove`, `release`, `check` |                                           | [0.3.0] | 🛠️ Work in progress  |                    |

---

## Command Reference

### `context` command

Usage:

```sh
reerelease context
reerelease context list [--path] [--depth]
reerelease context add CONTEXT_NAME [--path PATH] [--force] [--inplace]
reerelease context remove CONTEXT_NAME [--path PATH] [--force]
reerelease context check [CONTEXT_NAME] [--path PATH]
```

> NOTE: `reerelease context` default to `reerelease context list .`

#### `context` arguments

| Subcommand | Argument        | Type   | Required | Default | Description                                                                      | Since   | Status      |
| ---------- | --------------- | ------ | -------: | ------- | -------------------------------------------------------------------------------- | ------- | ----------- |
| `list`     | `--path`        | path   |       no | `.`     | Directory path to search for contexts                                            | [0.2.0] | ✅ Tested   |
|            | `--depth`       | int    |       no | 10      | Limit the discovery to a specific amount of depth                                | [0.2.0] | ✅ Tested   |
| `add`      | `CONTEXT_NAME`  | string |      yes |         | Name for the new context                                                         | [0.2.0] | ✅ Tested   |
|            | `--path`        | path   |       no | `.`     | Target path where context will be created                                        | [0.2.0] | ✅ Tested   |
|            | `--inplace`     | bool   |       no | false   | Create the new context directly in `PATH` without subfolder named `CONTEXT_NAME` | [0.2.0] | ✅ Tested   |
|            | `--force`       | bool   |       no | false   | Disable checks to not overwrite an existing context                              | [0.3.0] | ✅ Tested   |
|            | `--domain`      | csv    |       no |         | Domains this context includes                                                    | [0.7.0] | 🚧 Planned |
| `update`   | `CONTEXT_NAME`  | string |      yes |         | Context name to update                                                           | [0.3.0] | 🚧 Planned |
|            | `--path`        | path   |       no | `.`     | Target path where to find the context to update                                  | [0.3.0] | 🚧 Planned |
|            | `--name`        | string |       no |         | New name to give to the context (also rename the context folder)                 | [0.3.0] | 🚧 Planned |
| `remove`   | `CONTEXT_NAME`  | string |      yes |         | Context name to remove                                                           | [0.3.0] | ✅ Tested   |
|            | `--path`        | path   |       no | `.`     | Path from where to search for `CONTEXT_NAME`                                     | [0.3.0] | ✅ Tested   |
|            | `--force`       | bool   |       no | false   | Skip manual confirmation and warnings                                            | [0.3.0] | ✅ Tested   |
|            | `--removechild` | bool   |       no | false   | Remove any child context that is inside the targeted context                     | [0.6.0] | 🚧 Planned |
| `check`    | `CONTEXT_NAME`  | string |       no | `*`     | Context name to validate                                                         | [0.3.0] | ✅ Tested   |
|            | `--path`        | path   |       no | `.`     | Path from where to search for `CONTEXT_NAME`                                     | [0.3.0] | ✅ Tested   |

#### `context` exit codes

| Subcommand | Code | Meaning                                             |
| ---------- | ---: | --------------------------------------------------- |
| `list`     |  `0` | Success - contexts listed                           |
|            |  `1` | Path doesn't exist or permission denied             |
| `add`      |  `0` | Success - context created                           |
|            |  `1` | Error - element already exists or permission denied |
|            |  `2` | Error - invalid arguments                           |
| `update`   |  `0` | Success - context updated successfully              |
|            |  `1` | Error - updating failed, specifics printed          |
| `remove`   |  `0` | Success - context removed                           |
|            |  `1` | Error - element not found or permission denied      |
|            |  `2` | Error - invalid arguments                           |
| `check`    |  `0` | Success - context valid                             |
|            |  `1` | Error - couldn't verify contexts                    |

See also: legacy [`new`](#new-command-legacy)/[`contexts`](#contexts-command-legacy)

### `task` command

This command is mostly intended to be used interactively, but arguments are still available for scripting or testing  
Also typically task are defined manually in the roadmap files without command, this command exist mostly for automation

Usage:

```sh
reerelease task list [--context CONTEXT] [--path PATH]
reerelease task add TASK_TEXT [--context CONTEXT] [--path PATH] [--milestone MILESTONE] [--label LABELS] [--assign USER]
reerelease task remove TASKID [--context CONTEXT] [--path PATH] [--force]
```

#### `task` arguments

| Subcommand | Argument      | Type   | Required | Default      | Description                                              | Since    | Status      |
| ---------- | ------------- | ------ | -------: | ------------ | -------------------------------------------------------- | -------- | ----------- |
| `list`     | `--context`   | string |       no | `*`          | Context name to list tasks from                          | [0.4.0] | 🚧 Planned |
|            | `--path`      | path   |       no | `.`          | Path to search the context to list the task              | [0.4.0] | 🚧 Planned |
| `add`      | `TASK_TEXT`   | string |      yes |              | Short text describing the task                           | [0.4.0] | 🚧 Planned |
|            | `--context`   | string |       no | first found  | Context to which to add the task                         | [0.4.0] | 🚧 Planned |
|            | `--path`      | path   |       no | `.`          | Path to search the context to add the task to            | [0.4.0] | 🚧 Planned |
|            | `--milestone` | string |       no | `Unassigned` | Milestone to assign the task to                          | [0.4.0] | 🚧 Planned |
|            | `--label`     | csv    |       no |              | Labels for categorization                                | [0.6.0] | 🚧 Planned |
|            | `--assign`    | string |       no | `nobody`     | User assigned to the task                                | [0.6.0] | 🚧 Planned |
| `remove`   | `TASKID`      | string |      yes |              | Identifier of the task to remove                         | [0.4.0] | 🚧 Planned |
|            | `--context`   | string |       no | first found  | Context from which to remove the task                    | [0.4.0] | 🚧 Planned |
|            | `--path`      | path   |       no | `.`          | Path to search the context from which to remove the task | [0.4.0] | 🚧 Planned |
|            | `--force`     | bool   |       no | false        | Remove task without manual confirmation                  | [0.4.0] | 🚧 Planned |

#### `task` exit codes

| Subcommand | Code | Meaning                                   |
| ---------- | ---: | ----------------------------------------- |
| `list`     |  `0` | Success - tasks listed                    |
|            |  `1` | Context not found or permission denied    |
| `add`      |  `0` | Success - task created                    |
|            |  `1` | Error - invalid args or permission denied |
|            |  `2` | Error - task already exists               |
| `remove`   |  `0` | Success - task removed                    |
|            |  `1` | Error - task not found                    |

### `problem` command

Usage:

```sh
reerelease problem list [--context CONTEXT] [--path PATH]
reerelease problem add PROBLEM_TEXT [--context CONTEXT] [--path PATH] [--milestone MILESTONE] [--notask] [--solve_milestone SOLVE_MILESTONE] [--assign USER] [--severity SEVERITY]
reerelease problem resolve PROBLEM_ID [--context CONTEXT] [--path PATH] [--comment "..."]
reerelease problem remove PROBLEM_ID [--context CONTEXT] [--path PATH] [--force]
```

#### `problem` arguments

| Subcommand | Argument            | Type   | Required | Default      | Description                                            | Since    | Status      |
| ---------- | ------------------- | ------ | -------: | ------------ | ------------------------------------------------------ | -------- | ----------- |
| `list`     | `--context`         | string |       no | `*`          | Context to list problems from                          | [0.4.0] | 🚧 Planned |
|            | `--path`            | path   |       no | `.`          | Path to search the context to list the problems        | [0.4.0] | 🚧 Planned |
| `add`      | `PROBLEM_TEXT`      | string |      yes |              | Short description of the problem                       | [0.4.0] | 🚧 Planned |
|            | `--context`         | string |       no | first found  | Context to attach the problem to                       | [0.4.0] | 🚧 Planned |
|            | `--path`            | path   |       no | `.`          | Path to search the context to add the problem to       | [0.4.0] | 🚧 Planned |
|            | `--milestone`       | string |       no | `Unassigned` | Milestone to assign the problem to                     | [0.4.0] | 🚧 Planned |
|            | `--notask`          | bool   |       no | false        | Do not automatically create a resolution task          | [0.6.0] | 🚧 Planned |
|            | `--solve_milestone` | string |       no | `Unassigned` | Milestone assigned to the resolution of the problem    | [0.6.0] | 🚧 Planned |
|            | `--assign`          | string |       no | `nobody`     | User assigned                                          | [0.6.0] | 🚧 Planned |
|            | `--severity`        | string |       no | medium       | Severity level                                         | [0.6.0] | 🚧 Planned |
| `resolve`  | `PROBLEM_ID`        | string |      yes |              | Identifier of the problem to resolve                   | [0.4.0] | 🚧 Planned |
|            | `--context`         | string |       no | first found  | Context to resolve the problem from                    | [0.4.0] | 🚧 Planned |
|            | `--path`            | path   |       no | `.`          | Path to search the context to resolve the problem from | [0.4.0] | 🚧 Planned |
|            | `--comment`         | string |       no |              | Add a message about the solution applied               | [0.4.0] | 🚧 Planned |
| `remove`   | `PROBLEM_ID`        | string |      yes |              | Identifier of the problem to remove                    | [0.4.0] | 🚧 Planned |
|            | `--context`         | string |       no | first found  | Context to remove the problem from                     | [0.4.0] | 🚧 Planned |
|            | `--path`            | path   |       no | `.`          | Path to search the context to remove the problem from  | [0.4.0] | 🚧 Planned |
|            | `--force`           | bool   |       no | false        | Remove problem without manual confirmation             | [0.4.0] | 🚧 Planned |

#### `problem` exit codes

| Subcommand | Code | Meaning                                   |
| ---------- | ---: | ----------------------------------------- |
| `list`     |  `0` | Success - problems listed                 |
| `add`      |  `0` | Success - problem created                 |
|            |  `1` | Error - invalid args or permission denied |
| `resolve`  |  `0` | Success - problem resolved                |
|            |  `1` | Error - problem not found                 |
| `remove`   |  `0` | Success - problem removed                 |

### `milestone` command

Usage:

```sh
reerelease milestone list [--context CONTEXT] [--path PATH]
reerelease milestone add MILESTONE [--context CONTEXT] [--path PATH] [--title TITLE] [--date DATE] [--domain LIST_OF_DOMAIN]
reerelease milestone remove MILESTONE [--context CONTEXT] [--path PATH] [--force]
reerelease milestone release MILESTONE [--context CONTEXT] [--path PATH] [--dry-run] [--message MESSAGE]
```

#### `milestone` arguments

| Subcommand | Argument    | Type   | Required | Default              | Description                                                           | Since    | Status      |
| ---------- | ----------- | ------ | -------: | -------------------- | --------------------------------------------------------------------- | -------- | ----------- |
| `list`     | `--context` | string |       no | `*`                  | Context to list milestones from                                       | [0.3.0] | ✅ Tested   |
|            | `--path`    | path   |       no | `.`                  | Path to search the context to list the milestone from                 | [0.3.0] | ✅ Tested   |
| `add`      | `MILESTONE` | string |      yes |                      | Name of the milestone (ie: 0.1.0, A0, etc)                            | [0.3.0] | ✅ Tested   |
|            | `--context` | string |       no | first found          | Context to attach the milestone to                                    | [0.3.0] | ✅ Tested   |
|            | `--path`    | path   |       no | `.`                  | Path to search the context to add the milestone to                    | [0.3.0] | ✅ Tested   |
|            | `--desc`    | string |       no | ``                   | Description of the milestone                                          | [0.3.0] | ✅ Tested   |
|            | `--date`    | string |       no |                      | Target date for the milestone (ISO8601 format)                        | [0.3.0] | ✅ Tested   |
|            | `--status`  | string |       no |                      | Status for the milestone (see [supported status][sup_milestone_stat]) | [0.3.0] | ✅ Tested   |
|            | `--domain`  | csv    |       no |                      | Specific domain covered for this milestone                            | [0.7.0] | 🚧 Planned |
| `update`   | `MILESTONE` | string |      yes |                      | Name of the milestone to update                                       | [0.3.0] | ✅ Tested   |
|            | `--context` | string |       no | first found          | Context in which the milestone is                                     | [0.3.0] | ✅ Tested   |
|            | `--path`    | path   |       no | `.`                  | Path to search the context to update the milestone                    | [0.3.0] | ✅ Tested   |
|            | `--name`    | string |       no |                      | New name to give to the milestone                                     | [0.3.0] | ✅ Tested   |
|            | `--desc`    | string |       no | ``                   | New description of the milestone                                      | [0.3.0] | ✅ Tested   |
|            | `--date`    | string |       no |                      | New target date for the milestone (ISO8601 format)                    | [0.3.0] | ✅ Tested   |
|            | `--status`  | string |       no |                      | New status for the milestone                                          | [0.3.0] | ✅ Tested   |
|            | `--domain`  | csv    |       no |                      | New specific domain covered for this milestone                        | [0.7.0] | 🚧 Planned |
| `remove`   | `MILESTONE` | string |      yes |                      | Milestone name to remove                                              | [0.3.0] | ✅ Tested   |
|            | `--context` | string |       no | first found          | Context to remove the milestone from                                  | [0.3.0] | ✅ Tested   |
|            | `--path`    | path   |       no | `.`                  | Path to search the context to remove the milestone from               | [0.3.0] | ✅ Tested   |
|            | `--force`   | bool   |       no | false                | Remove milestone without manual confirmation                          | [0.3.0] | ✅ Tested   |
| `check`    | `MILESTONE` | string |      yes |                      | Name of the milestone to check                                        | [0.3.0] | ✅ Tested   |
|            | `--context` | string |       no | first found          | Context holding the milestone to check                                | [0.3.0] | ✅ Tested   |
|            | `--path`    | path   |       no | `.`                  | Path to search the context of the milestone                           | [0.3.0] | ✅ Tested   |
| `release`  | `VERSION`   | string |       no | next ready milestone | Milestone to release                                                  | [0.5.0] | 🚧 Planned |
|            | `--context` | string |       no | first found          | Context to release from                                               | [0.5.0] | 🚧 Planned |
|            | `--path`    | path   |       no | `.`                  | Path to search the context of the milestone                           | [0.5.0] | 🚧 Planned |
|            | `--dry-run` | bool   |       no | false                | Do not actually publish things, call dry-run hooks for custom steps   | [0.5.0] | 🚧 Planned |
|            | `--message` | string |       no |                      | Release message to publish                                            | [0.5.0] | 🚧 Planned |

#### `milestone` exit codes

| Subcommand | Code | Meaning                                    |
| ---------- | ---: | ------------------------------------------ |
| `list`     |  `0` | Success - milestone(s) listed              |
|            |  `1` | Error - listing failed, specifics printed  |
| `add`      |  `0` | Success - milestone created                |
|            |  `1` | Error - creation failed, specifics printed |
|            |  `2` | Error - invalid arguments                  |
| `update`   |  `0` | Success - milestone updated                |
|            |  `1` | Error - update failed, specifics printed   |
|            |  `2` | Error - invalid arguments                  |
| `remove`   |  `0` | Success - milestone removed                |
|            |  `1` | Error - removal failed, specifis printed   |
| `release`  |  `0` | Release completed successfully             |
|            |  `1` | Release validation failed                  |
|            |  `2` | Error - invalid arguments                  |

---

## Legacy Commands (Deprecated)

### `new` Command (Legacy)

⚠️ **Deprecated in [0.2.0]** - Use `context add` instead.

#### New Usage (Legacy)

```sh
reerelease new CONTEXT_NAME [PATH]
```

#### New Migration (Legacy)

```sh
# Old command
reerelease new my-project /projects

# New command  
reerelease add context my-project /projects
```

### `contexts` Command (Legacy)

⚠️ **Deprecated in [0.2.0]** - Use `context list` instead.

#### Contexts Usage (Legacy)

```sh
reerelease contexts [PATH]
```

#### Contexts Detection Criteria (Legacy)

A directory is considered a context if it contains ***all three*** required [Markdown] files:

- `release.md` file
- `roadmap.md` file
- `readme.md` file

#### Contexts Migration (Legacy)

```sh
# Old command
reerelease contexts /projects

# New command
reerelease list context /projects
```

<!-- links -->
[sup_milestone_stat]: /docs/metadata.md#milestone---status
[roadmap]: /roadmap.md
[0.1.0]: /roadmap.md#010
[0.2.0]: /roadmap.md#020
[0.3.0]: /roadmap.md#030
[0.4.0]: /roadmap.md#040
[0.5.0]: /roadmap.md#050
[0.6.0]: /roadmap.md#060
[0.7.0]: /roadmap.md#070
[typer]: https://typer.tiangolo.com/
[markdown]: https://www.markdownguide.org/
