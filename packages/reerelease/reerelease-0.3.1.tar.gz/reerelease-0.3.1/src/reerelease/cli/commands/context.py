import logging
import pathlib as pathlib
import sys
from typing import Any, cast

import click
import questionary
import typer
from anytree import RenderTree
from rich.table import Table

from ...config import DEFAULTS
from ...core.context import Context
from ...core.milestone import MILESTONE_STATUS
from ...errors import (
    AppError,
    NoContextFound,
)
from ...service.context_manager import ContextManager
from ..console import exit_with, print_exception, quiet_print
from ..error_codes import OK
from .milestone import _add_milestone_interactive

context_app = typer.Typer()


def _is_interactive_terminal() -> bool:
    """
    Check if we're running in an interactive terminal.
    Extracted as a separate function to make it easily mockable in tests.
    """

    return sys.stdin.isatty() and sys.stdout.isatty()


def _create_optional_milestones(context: Context) -> None:
    """
    Prompt user to create milestones for a newly created context.

    Loops until user declines creating more milestones. Handles cancellation
    gracefully - context is preserved even if user cancels during milestone input.

    This delegates to the milestone._add_milestone_interactive helper to avoid
    code duplication and ensure consistency with the milestone add command.

    Args:
        context: The newly created context to add milestones to
        cfg: Global configuration
    """

    logger = logging.getLogger("reerelease")

    # Initial prompt - default to yes
    create_milestone = questionary.confirm(
        "\n🎯 Create milestone(s) for this context?",
        default=True,
    ).ask()

    if not create_milestone:
        return

    # Loop to create multiple milestones
    while True:
        try:
            # Prompt for milestone name
            milestone_name = questionary.text(
                "Milestone name:",
                validate=lambda text: len(text.strip()) > 0 or "Name cannot be empty",
            ).ask()

            # User cancelled (Ctrl+C or ESC)
            if milestone_name is None:
                quiet_print("⚠️ Milestone creation declined/cancelled - context preserved")
                break

            # Call the extracted milestone creation helper
            # It will handle all the interactive prompts (description, date, status)
            _add_milestone_interactive(
                context=context,
                name=milestone_name,
                description=None,  # Will prompt interactively
                target_date=None,  # Will prompt interactively
                status=None,  # Will prompt interactively
            )

        except ValueError as e:
            # Handle validation errors gracefully
            logger.warning(f"Invalid milestone data: {e}")
            quiet_print(f"❌ {e}")
            # Continue loop - let user try again
        except AppError as e:
            # Handle milestone creation errors gracefully
            logger.warning(f"Failed to create milestone: {e}")
            quiet_print(f"❌ Failed to create milestone: {e}")
            # Continue loop - let user try again

        # Ask if user wants to create another milestone
        create_another = questionary.confirm(
            "\n🎯 Create another milestone?",
            default=False,
        ).ask()

        if not create_another:
            break


@context_app.callback(invoke_without_command=True)
def _context_default(
    ctx: typer.Context, path: str = typer.Option(".", help="Path to search the context")
) -> None:
    """Default behavior when `context` is called without a subcommand: show the list."""
    # If a subcommand was invoked, do nothing here
    if ctx.invoked_subcommand is not None:
        return

    # Otherwise call the list command
    list(ctx, path=path)


@context_app.command(help="List all detected contexts")
def list(
    ctx: typer.Context,
    path: str = typer.Option(".", help="Path to search the context", show_default=True),
    depth: int = typer.Option(
        DEFAULTS.search_depth,
        "--depth",
        "-d",
        help="Depth of context searching and listing",
        show_default=True,
    ),
) -> None:
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: context.list : path:{path} depth:{depth}")

    path_obj = pathlib.Path(path)

    cm = ContextManager()

    try:
        rootctx = cm.discover(search_path=path_obj, max_depth=depth)
        logger.info(f"Discovered context tree with {len(rootctx.descendants) + 1} context(s)")

        # Prepare summary header
        # Show the root context name only when present, if not, dim empty string
        root_name = "[dim]_[/dim] " if rootctx.name == "" else f"{rootctx.name}"
        # overall tree health aggregation
        overall_health = (
            False
            if any(not node.healthy for node in rootctx.descendants) or not rootctx.healthy
            else True
        )
        ctx_nb = len(rootctx.descendants) + 1

        # Build summary line
        summary_line = f"🌳 [bold]{root_name}[/bold] {'✔️' if overall_health else '❌'}  with [grey]{ctx_nb}[/grey] context{'s' if ctx_nb > 1 else ''} in [yellow]{rootctx.filepath}[/yellow]"
        quiet_print(summary_line)
        logger.debug(
            f"Root context: {rootctx.name}, healthy: {overall_health}, total contexts: {ctx_nb}"
        )

        # Print each context with its latest milestone info
        for prefix, _, node in RenderTree(rootctx, childiter=cast(Any, Context.iter_sorting)):
            # Get the latest completed/released or in-progress milestone
            milestone_info = ""
            latest_milestone = None

            # First try to find completed or released milestones
            completed_or_released = [
                m
                for m in node.milestones
                if m.status in [MILESTONE_STATUS.COMPLETED, MILESTONE_STATUS.RELEASED]
            ]

            if completed_or_released:
                # Get the most recent one (assuming they're sorted by date or order)
                latest_milestone = completed_or_released[-1]
                color = latest_milestone.status.color
                emoji = latest_milestone.status.emoji
                # Make milestone names consistently bold for better visual consistency
                milestone_info = f" [{color}]{emoji} [bold]{latest_milestone.name}[/bold][/{color}]"
                logger.debug(
                    f"Context '{node.name}': showing {latest_milestone.status.desc} milestone '{latest_milestone.name}'"
                )
            else:
                # No completed/released, look for other than cancelled or invalid
                in_progress = [
                    m
                    for m in node.milestones
                    if m.status not in [MILESTONE_STATUS.CANCELLED, MILESTONE_STATUS.INVALID]
                ]
                if in_progress:
                    latest_milestone = in_progress[-1]
                    completion = latest_milestone.completion_percentage()
                    color = latest_milestone.status.color
                    emoji = latest_milestone.status.emoji
                    # Make milestone names consistently bold for better visual consistency
                    milestone_info = f" [{color}]{emoji} [bold]{latest_milestone.name}[/bold] ({completion:.0f}%)[/{color}]"
                    logger.debug(
                        f"Context '{node.name}': showing in-progress milestone '{latest_milestone.name}' at {completion:.0f}%"
                    )
                else:
                    logger.debug(f"Context '{node.name}': no milestone to display")

            # Build tree line
            tree_part = f"{prefix}{node.name} {'✔️' if node.healthy else '❌'}  [dim]({node.filepath.relative_to(rootctx.filepath)})[/dim]{milestone_info}"
            quiet_print(tree_part)

    except NoContextFound:
        quiet_print(f"🪵 No context found in [yellow]{path_obj}[/yellow]")
        logger.info(f"No context found in {path_obj}")
        exit_with(OK)
    except AppError as e:
        logger.error(f"Error listing contexts: {e}")
        exit_with(print_exception(e))  # handle other AppErrors with detailed printing

    logger.info("Context list command completed successfully")
    exit_with(OK)


@context_app.command(help="Add a new context")
def add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the context to add"),
    path: str = typer.Option(".", help="Path to create the context in", show_default=True),
    inplace: bool = typer.Option(
        False, "--inplace", "-i", help="Create context in the specified path without subfolder"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Disable overwriting checks"),
) -> None:
    """Add a new context"""
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: context.add : {name} at {path}, inplace: {inplace}, force: {force}")

    path_obj = pathlib.Path(path)

    cm = ContextManager()

    try:
        context = cm.create(path=path_obj, name=name, inplace=inplace, force=force)

        quiet_print(f"➕ Context '{context.name}' created successfully at {context.filepath}")

        # Interactive milestone creation loop (only in interactive mode)
        if _is_interactive_terminal():
            _create_optional_milestones(context)

    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@context_app.command(help="Remove an existing context")
def remove(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the context to remove"),
    path: str = typer.Option(".", help="Path to search the context", show_default=True),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Disable checks and confirmations",
    ),
    removechild: bool = typer.Option(
        False,
        "--removechild",
        help=click.style("[NOT IMPLEMENTED] ", fg="red")
        + "Remove child (if present) contexts as well",
    ),
) -> None:
    """Remove an existing context"""
    logger = logging.getLogger("reerelease")
    logger.debug(
        f"CMD: context.remove : {name} at {path}, force: {force}, removechild: {removechild}"
    )

    path_obj = pathlib.Path(path).resolve()
    cm = ContextManager()
    target_ctx = None

    try:
        # 1. Find the context to remove
        found = cm.find(search_path=path_obj, name=name, nb=1)

        # 2. Discover the attached tree (if any)
        if found:
            target_ctx = cm.discover(
                search_path=found[0].filepath, max_depth=1
            )  # We only need to validate this context and its immediate children

        if not target_ctx:
            raise NoContextFound(f"No matching context found to remove: {name} in {path_obj}")

        # 3. Confirm removal (unless forced)
        if not force:
            if not _is_interactive_terminal():
                # In non-interactive mode, require explicit --force flag
                logger.info("Cannot confirm removal in non-interactive mode without --force.")
                exit_with(OK)
            else:
                confirm = questionary.confirm(
                    message=f"Removing the context '{target_ctx.name}' at '{target_ctx.filepath}'?",
                    default=False,
                ).ask()
                if not confirm:
                    quiet_print(
                        f"↩️ Aborted removal of context: {target_ctx.name} at {target_ctx.filepath}"
                    )
                    logger.debug(f"User skipped removal for {target_ctx.filepath}")
                    exit_with(OK)

        # 4. Remove the context
        cm.delete(target_ctx, delete_dir=force, force=force)

        logger.info(f"Removed context {target_ctx.name} at {target_ctx.filepath}")
        quiet_print(f"➖ Removed context: {target_ctx.name} at {target_ctx.filepath}")

    except NoContextFound:
        quiet_print(f"❔ No matching context found to remove: {name} in {path_obj}")
        logger.info(f"No matching context found to remove: {name} in {path_obj}")
        exit_with(OK)
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@context_app.command(help="Update an existing context (rename)")
def update(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the context to update"),
    new_name: str = typer.Argument(..., help="New name for the context"),
    path: str = typer.Option(
        ".",
        help="Path to search the context",
        show_default=True,
    ),
    rename_folder: bool = typer.Option(
        True,
        "--rename-folder/--no-rename-folder",
        help="Rename the folder if it matches/contains the old name",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Disable checks and confirmations",
    ),
) -> None:
    """Update (rename) an existing context."""
    logger = logging.getLogger("reerelease")
    logger.debug(
        f"CMD: context.update : {name} -> {new_name} at {path}, "
        f"rename_folder: {rename_folder}, force: {force}"
    )

    path_obj = pathlib.Path(path).resolve()
    cm = ContextManager()
    target_ctx = None

    try:
        # 1. Find the context to update
        found = cm.find(search_path=path_obj, name=name, nb=1)

        if found:
            # Discover and get only the top node to get full context tree (for validation)
            target_ctx = cm.discover(search_path=found[0].filepath, max_depth=1)

        if not target_ctx:
            raise NoContextFound(f"No matching context found to update: {name} in {path_obj}")

        # 2. Confirm update (unless forced)
        if not force:
            if not _is_interactive_terminal():
                # In non-interactive mode, require explicit --force flag
                logger.info("Cannot confirm update in non-interactive mode without --force.")
                quiet_print(f"↩️ Aborted update of context: {name} at {target_ctx.filepath}")
                exit_with(OK)
            else:
                folder_msg = ""
                if rename_folder:
                    if target_ctx.filepath.name == name:
                        folder_msg = f" and folder '{target_ctx.filepath.name}'"
                    elif name in target_ctx.filepath.name:
                        new_folder_name = target_ctx.filepath.name.replace(name, new_name)
                        folder_msg = (
                            f" and folder '{target_ctx.filepath.name}' -> '{new_folder_name}'"
                        )

                confirm = questionary.confirm(
                    message=f"Rename context '{target_ctx.name}' to '{new_name}'{folder_msg}?",
                    default=False,
                ).ask()

                if not confirm:
                    quiet_print(
                        f"↩️ Aborted update of context: {target_ctx.name} at {target_ctx.filepath}"
                    )
                    logger.debug(f"User skipped update for {target_ctx.filepath}")
                    exit_with(OK)

        # 3. Update the context
        updated_ctx = cm.update(target_ctx, new_name, rename_folder=rename_folder, force=force)

        logger.info(
            f"Updated context from '{name}' to '{updated_ctx.name}' at {updated_ctx.filepath}"
        )
        quiet_print(
            f"✏️ Renamed context: '{name}' -> '{updated_ctx.name}' at {updated_ctx.filepath}"
        )

    except NoContextFound:
        quiet_print(f"❔ No matching context found to update: {name} in {path_obj}")
        logger.info(f"No matching context found to update: {name} in {path_obj}")
        exit_with(OK)
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@context_app.command(help="Check the status of a context")
def check(
    ctx: typer.Context,
    name: str = typer.Argument("*", help="Name of the context to check"),
    path: str = typer.Option(
        ".",
        help="Path to search the context",
        show_default=True,
    ),
) -> None:
    """Check the status of a context."""

    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: context.check : {name} at {path}")

    path_obj = pathlib.Path(path).resolve()
    cm = ContextManager()

    try:
        # Step 1: Find the context(s) to check
        # Step 2: Validate each context (already done by discover/find via validate_tree)
        # The healthy property is set during discovery/validation
        if name == "*":
            # Check all contexts in the given path
            logger.debug(f"Discovering all contexts in {path_obj}")
            rootctx = cm.discover(search_path=path_obj, max_depth=DEFAULTS.search_depth)
            all_contexts = [rootctx, *rootctx.descendants]
            logger.info(f"Found {len(all_contexts)} context(s) to check")
        else:
            # Find specific context by name
            logger.debug(f"Finding context by name: {name}")
            found = cm.find(search_path=path_obj, name=name, nb=0)
            if not found:
                logger.warning(f"No context found with name '{name}' in {path_obj}")
                raise NoContextFound(f"No matching context found: {name} in {path_obj}")

            logger.info(f"Found {len(found)} matching context(s)")
            # For each found context, discover its tree to validate children
            all_contexts = []
            for ctx_item in found:
                logger.debug(
                    f"Discovering tree for context: {ctx_item.name} at {ctx_item.filepath}"
                )
                discovered = cm.discover(search_path=ctx_item.filepath, max_depth=1)
                all_contexts.append(discovered)

        # Step 3: Explore context details and gather statistics
        logger.debug("Gathering statistics from contexts")
        table_data = []
        for context in all_contexts:
            # Get parent context name (immediate parent) - show '.' when none
            parent_name = context.parent.name if context.parent else "."

            # Calculate statistics for this context
            milestone_count = len(context.milestones)
            task_count = sum(len(m.tasks) for m in context.milestones)
            problem_count = sum(len(m.problems) for m in context.milestones)

            logger.debug(
                f"Context '{context.name}': {milestone_count} milestones, "
                f"{task_count} tasks, {problem_count} problems, healthy={context.healthy}"
            )

            table_data.append(
                {
                    "parent": parent_name,
                    "name": context.name,
                    "healthy": context.healthy,
                    "milestones": milestone_count,
                    "tasks": task_count,
                    "problems": problem_count,
                }
            )

        # Step 4: Report summary and stats in a table
        logger.debug(f"Displaying check results for {len(table_data)} context(s)")
        table = Table(title="Context Status Report")
        table.add_column("Parent", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Health", justify="center")
        table.add_column("Milestones", justify="right", style="yellow")
        table.add_column("Tasks", justify="right", style="green")
        table.add_column("Problems", justify="right", style="red")

        for row in table_data:
            health_symbol = "✔️" if row["healthy"] else "❌"
            table.add_row(
                row["parent"],
                row["name"],
                health_symbol,
                str(row["milestones"]),
                str(row["tasks"]),
                str(row["problems"]),
            )

        quiet_print(table)
        logger.info(f"Check completed successfully for {len(table_data)} context(s)")

    except NoContextFound as e:
        quiet_print(f"❔ {e}")
        logger.info(f"No context found: {e}")
        exit_with(OK)
    except AppError as e:
        logger.error(f"Error checking context: {e}")
        exit_with(print_exception(e))

    exit_with(OK)


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
