import logging

import click
import typer

from .__about__ import __version__
from .cli.commands.context import context_app as context
from .cli.commands.milestone import milestone_app as milestone
from .cli.commands.problem import problem_app as problem
from .cli.commands.task import task_app as task
from .config import DEFAULTS, GlobalConfig, set_config
from .core.logging import configure_logging

app = typer.Typer(name="reerelease", help="Markdown project management tool made for humans")

# Add subcommand groups
app.add_typer(context, name="context", help="Manage contexts")
app.add_typer(task, name="task", help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Manage tasks")
app.add_typer(milestone, name="milestone", help="Manage milestones")
app.add_typer(
    problem,
    name="problem",
    help=click.style("[NOT IMPLEMENTED] ", fg="red") + "Manage problems",
)


@app.command(hidden=True)
def emit_test_logs() -> None:
    """(test-only) Emit log messages at all levels for testing verbosity."""
    logger = logging.getLogger("reerelease")
    logger.debug("test-DEBUG: emit-test-logs called")
    logger.info("test-INFO: emit-test-logs called")
    logger.warning("test-WARNING: emit-test-logs called")
    logger.error("test-ERROR: emit-test-logs called")
    logger.critical("test-CRITICAL: emit-test-logs called")


# Typer callback to configure logging before running commands
@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    quiet: bool = typer.Option(
        DEFAULTS.quiet, "--quiet", "-q", help="Disable all logging and console output."
    ),
    verbosity: str = typer.Option(
        logging.getLevelName(DEFAULTS.verbosity),
        "--verbosity",
        "-v",
        help="Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    ),
    version: bool = typer.Option(False, "--version", help="Show version information and exit."),
) -> None:
    """
    Global options for the reerelease tool.
    """
    if version:
        typer.echo(f"reerelease {__version__}")
        raise typer.Exit()

    # Sanitize verbosity input
    level = getattr(logging, verbosity.upper(), logging.WARNING)

    # # Store global config in context for access in commands
    # if ctx.obj is None:
    #     ctx.obj = {}
    cfg = GlobalConfig(verbosity=level, quiet=quiet)
    # ctx.obj["global_config"] = cfg

    # Set config in context variable for easy access by validators and utilities
    set_config(cfg)

    # Configure logging using the values from the GlobalConfig instance
    configure_logging(level=cfg.verbosity, quiet=cfg.quiet)


def cli_hook() -> None:
    app()


if __name__ == "__main__":
    cli_hook()
