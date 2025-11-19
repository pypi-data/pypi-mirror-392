"""CLI commands for milestone management."""

import datetime
import logging
import pathlib
import sys

import questionary
import typer
from rich.table import Table

from reerelease.config import DEFAULTS, GlobalConfig, get_config
from reerelease.core.context import Context
from reerelease.validators.validate_milestone import validate_milestone_status

from ...errors import (
    AppError,
    NoContextFound,
    NoMilestoneFound,
)
from ...service.context_manager import ContextManager
from ...service.milestone_manager import MilestoneManager
from ...validators.validate_milestone import validate_milestone
from ..console import exit_with, print_exception, quiet_print
from ..error_codes import OK, USAGE_ERROR

milestone_app = typer.Typer()


def _is_interactive_terminal() -> bool:
    """Check if running in an interactive terminal.

    Returns:
        True if both stdin and stdout are TTYs (interactive), False otherwise.
    """
    return sys.stdin.isatty() and sys.stdout.isatty()


def _get_target_context(
    cm: ContextManager,
    path_obj: pathlib.Path,
    context_name: str | None,
) -> Context:
    """Get the target context for milestone operations.

    This helper function discovers contexts and optionally filters by name.

    Args:
        cm: ContextManager instance
        path_obj: Path to search for contexts
        context_name: Optional context name to filter by

    Returns:
        The target Context object to use for milestone operations

    Raises:
        typer.Exit: If context_name is specified but not found
    """
    # Discover contexts - use default search depth to find nested contexts
    rootctx = cm.discover(search_path=path_obj, max_depth=DEFAULTS.search_depth)

    # If no specific context requested, use root
    if not context_name:
        return rootctx

    # Find the specific context by name
    found = cm.find(search_path=path_obj, name=context_name, nb=1)
    if not found:
        quiet_print(f"❌ Context '{context_name}' not found in {path_obj}")
        exit_with(USAGE_ERROR)

    return found[0]  # Return only the first found context


def _add_milestone_interactive(
    context: Context,
    name: str,
    description: str | None = None,
    target_date: str | None = None,
    status: str | None = None,
) -> None:
    """
    Add a milestone with interactive prompts for missing values.

    Core logic extracted from the add command to be reusable.
    Does NOT call exit_with() - raises exceptions instead.

    Args:
        cfg: Global configuration
        context: Target context to add milestone to
        name: Milestone name
        description: Optional description (will prompt if None)
        target_date: Optional target date string (will prompt if None)
        status: Optional status (will prompt if None)

    Raises:
        AppError: If milestone creation fails
        ValueError: If date format is invalid
    """
    cfg: GlobalConfig = get_config()

    mm = MilestoneManager()

    # Check if we're in an interactive terminal
    is_interactive = _is_interactive_terminal()

    # 1. Description: prompt if not provided (defaults to empty string)
    if description is None:
        if is_interactive:
            description = questionary.text("Description (optional):", default="").ask() or ""
        else:
            description = ""

    # 2. Target date: prompt if not provided (defaults to today + offset)
    default_date = datetime.date.today() + datetime.timedelta(
        days=DEFAULTS.milestone_target_date_offset_days
    )
    if target_date is None:
        if is_interactive:
            target_date = questionary.text(
                f"Target date (YYYY-MM-DD) [today + {DEFAULTS.milestone_target_date_offset_days} days]:",
                default=default_date.strftime("%Y-%m-%d"),
            ).ask()
        else:
            # Use default date directly in non-interactive mode
            target_date = default_date.strftime("%Y-%m-%d")

    # Parse the target date (whether from CLI arg, prompt, or default)
    parsed_date = None
    if target_date:
        try:
            parsed_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError as e:
            raise ValueError(f"Invalid date format: {target_date}. Expected YYYY-MM-DD") from e
    else:
        # Fallback if somehow still None
        parsed_date = default_date

    # 3. Status: prompt if not provided (defaults to configured default)
    if status is None:
        if is_interactive:
            valid_choices = [s.desc for s in cfg.milestone_statuses]
            status_value = questionary.select(
                "Status:",
                choices=valid_choices,
                default=cfg.default_milestone_status.desc,
            ).ask()
            # Convert string back to Enum
            status = status_value
        else:
            status = cfg.default_milestone_status.desc

    # Validate status
    valid_statuses = [s.desc for s in cfg.milestone_statuses]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}. Must be one of {[s for s in valid_statuses]}")

    # 4. Create milestone
    milestone = mm.create(
        context=context,
        name=name,
        description=str(description),
        target_date=parsed_date,
        status=status,
    )

    # 5. Print detailed success message
    quiet_print(f"✅ Milestone '{milestone.name}' created successfully!\n")
    quiet_print("📋 Details:")
    quiet_print(f"   Context: {context.name}")
    quiet_print(f"   Status: {milestone.status}")
    quiet_print(f"   Target Date: {milestone.target_date.strftime('%Y-%m-%d')}")
    if milestone.description:
        quiet_print(f"   Description: {milestone.description}")
    quiet_print(f"   Tasks: {len(milestone.tasks)}")
    quiet_print(f"   Problems: {len(milestone.problems)}")


@milestone_app.callback(invoke_without_command=True)
def _milestone_default(ctx: typer.Context) -> None:
    """Default behavior when `milestone` is called without a subcommand: show the list."""
    # If a subcommand was invoked, do nothing here
    if ctx.invoked_subcommand is not None:
        return

    # Otherwise call the list command
    list(ctx)


@milestone_app.command(help="List all milestones in a context")
def list(
    ctx: typer.Context,
    path: str = typer.Option(".", "--path", "-p", help="Path to the context", show_default=True),
    context_name: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context name (if multiple contexts exist)",
    ),
) -> None:
    """List all milestones in a context."""
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: milestone.list : path:{path}, context:{context_name}")

    path_obj = pathlib.Path(path).resolve()

    cm = ContextManager()
    mm = MilestoneManager()

    try:
        # Get the target context (root or specific named context)
        target_ctx = _get_target_context(cm, path_obj, context_name)

        # Discover milestones
        milestones = mm.read(target_ctx)

        if not milestones:
            quiet_print(f"📋 No milestones found in context '{target_ctx.name}'")
            exit_with(OK)

        # Display milestones in a table
        table = Table(title=f"Milestones in {target_ctx.name}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Target Date", style="yellow")
        table.add_column("Tasks", justify="right", style="green")
        table.add_column("Problems", justify="right")
        table.add_column("Description", max_width=80)

        for milestone in milestones:
            status_emoji = milestone.status.emoji
            status_color = milestone.status.color

            # Calculate task completion stats
            completed_tasks = sum(1 for t in milestone.tasks if t.completed)
            total_tasks = len(milestone.tasks)
            completion_pct = milestone.completion_percentage()

            # Format tasks column with count and percentage
            tasks_display = f"{completed_tasks}/{total_tasks} ({completion_pct:.0f}%)"

            table.add_row(
                milestone.name,
                f"[{status_color}]{status_emoji} {milestone.status.desc}[/{status_color}]",
                milestone.target_date.strftime("%Y-%m-%d"),
                tasks_display,
                str(len(milestone.problems)),
                milestone.description,
            )

        quiet_print(table)

    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@milestone_app.command(help="Add a new milestone to a context")
def add(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the milestone to add"),
    path: str = typer.Option(".", "--path", "-p", help="Path to the context", show_default=True),
    context_name: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context name (if multiple contexts exist)",
    ),
    description: str | None = typer.Option(
        None, "--description", "--desc", "-d", help="Milestone description"
    ),
    target_date: str | None = typer.Option(
        None,
        "--date",
        "-t",
        help="Target date (YYYY-MM-DD format)",
    ),
    status: str | None = typer.Option(
        None,
        "--status",
        "-s",
        help="Initial status (defaults to configured default)",
    ),
) -> None:
    """Add a new milestone to a context."""
    logger = logging.getLogger("reerelease")
    logger.debug(
        f"CMD: milestone.add : name:{name}, path:{path}, date:{target_date}, status:{status}"
    )

    path_obj = pathlib.Path(path).resolve()

    cm = ContextManager()

    try:
        # Get the target context (root or specific named context)
        target_ctx = _get_target_context(cm, path_obj, context_name)

        # Use the extracted helper function
        _add_milestone_interactive(
            context=target_ctx,
            name=name,
            description=description,
            target_date=target_date,
            status=status,
        )

    except ValueError as e:
        quiet_print(f"❌ {e}")
        exit_with(USAGE_ERROR)
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@milestone_app.command(help="Remove a milestone from a context")
def remove(
    ctx: typer.Context,
    context_name: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context name (if multiple contexts exist)",
    ),
    name: str = typer.Argument(..., help="Name of the milestone to remove"),
    path: str = typer.Option(".", "--path", "-p", help="Path to the context", show_default=True),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
) -> None:
    """Remove a milestone from a context."""
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: milestone.remove : name:{name}, path:{path}, force:{force}")

    path_obj = pathlib.Path(path).resolve()

    cm = ContextManager()
    mm = MilestoneManager()

    try:
        # Get the target context (root or specific named context)
        target_ctx = _get_target_context(cm, path_obj, context_name)

        # Check if milestone exists
        milestone = mm.find(target_ctx, name)

        # Confirmation prompt
        if not force:
            if not _is_interactive_terminal():
                # In non-interactive mode, require explicit --force flag
                logger.info("Cannot confirm removal in non-interactive mode without --force.")
                quiet_print("❌ Deletion cancelled")
                exit_with(OK)
            else:
                confirm = questionary.confirm(
                    f"Delete milestone '{milestone.name}' from '{target_ctx.name}'?",
                    default=False,
                ).ask()

                if not confirm:
                    quiet_print("❌ Deletion cancelled")
                    exit_with(OK)

        # Delete milestone
        mm.delete(target_ctx, name, force=True)

        quiet_print(f"🗑️  Milestone '{milestone.name}' removed successfully!\n")
        quiet_print("📋 Removed milestone details:")
        quiet_print(f"   Context: {target_ctx.name}")
        quiet_print(f"   Status: {milestone.status}")
        quiet_print(f"   Target Date: {milestone.target_date.strftime('%Y-%m-%d')}")
        quiet_print(f"   Tasks: {len(milestone.tasks)}")
        quiet_print(f"   Problems: {len(milestone.problems)}")

    except NoMilestoneFound as e:
        quiet_print(f"❌ Milestone '{name}' not found in context")
        logger.info(str(e))
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@milestone_app.command(help="Update an existing milestone")
def update(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the milestone to update"),
    path: str = typer.Option(".", "--path", "-p", help="Path to the context", show_default=True),
    context_name: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context name (if multiple contexts exist)",
    ),
    new_name: str | None = typer.Option(None, "--name", "-n", help="New milestone name"),
    description: str | None = typer.Option(
        None, "--description", "--desc", "-d", help="New description"
    ),
    target_date: str | None = typer.Option(
        None, "--date", "-t", help="New target date (YYYY-MM-DD)"
    ),
    status: str | None = typer.Option(None, "--status", "-s", help="New status"),
) -> None:
    """Update an existing milestone."""
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: milestone.update : name:{name}, path:{path}")

    path_obj = pathlib.Path(path).resolve()

    cfg = get_config()

    cm = ContextManager()
    mm = MilestoneManager()

    try:
        # == 0. Gather informations ==
        # Get the target context (root or specific named context)
        target_ctx = _get_target_context(cm, path_obj, context_name)

        # Get current milestone state before update
        old_milestone = mm.find(target_ctx, name)

        # Check if we're in interactive mode
        is_interactive = _is_interactive_terminal()

        # Interactive mode: prompt for each missing field individually
        if is_interactive:
            # 1. Name - prompt if not provided
            if new_name is None:
                new_name_input = questionary.text(
                    f"New name (leave empty to keep '{old_milestone.name}'):", default=""
                ).ask()
                new_name = new_name_input if new_name_input else None

            # 2. Description - prompt if not provided
            if description is None:
                current_desc = old_milestone.description or "(empty)"
                description_input = questionary.text(
                    f"New description (leave empty to keep '{current_desc}'):", default=""
                ).ask()
                description = description_input if description_input else None

            # 3. Target date - prompt if not provided
            if target_date is None:
                current_date_str = old_milestone.target_date.strftime("%Y-%m-%d")
                target_date_input = questionary.text(
                    f"New target date [YYYY-MM-DD] (leave empty to keep '{current_date_str}'):",
                    default="",
                ).ask()
                target_date = target_date_input if target_date_input else None

            # 4. Status - prompt if not provided
            if status is None:
                valid_choices = [s.desc for s in cfg.milestone_statuses]
                status_choices = ["(keep current)"] + valid_choices
                status_input = questionary.select(
                    f"New status (current: '{old_milestone.status.desc}'):",
                    choices=status_choices,
                    default="(keep current)",
                ).ask()
                if status_input and status_input != "(keep current)":
                    status = status_input
                else:
                    status = None

        # == 1. Validate ==
        # Parse target date if provided
        parsed_date = None
        if target_date:
            try:
                parsed_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                quiet_print(f"❌ Invalid date format: {target_date}. Expected YYYY-MM-DD")
                exit_with(USAGE_ERROR)

        # Validate status if provided
        # TODO: use validate_milestone_status from validators with new enum validation
        if status:
            issues = validate_milestone_status(status)
            if issues:
                quiet_print(f"❌ Invalid status: {status}. Issues: {', '.join(issues)}")
                exit_with(USAGE_ERROR)

        # == 2. Modify ==
        # Update milestone
        updated = mm.update(
            context=target_ctx,
            name=name,
            new_name=new_name,
            description=description,
            target_date=parsed_date,
            status=status,
        )

        # == 3. Report ==
        quiet_print(f"✅ Milestone '{old_milestone.name}' updated successfully!\n")
        quiet_print("📝 Changes:")

        if new_name and new_name != old_milestone.name:
            quiet_print(f"   Name: {old_milestone.name} → {updated.name}")

        if description is not None and description != old_milestone.description:
            old_desc_preview = (
                old_milestone.description[:40] if old_milestone.description else "(empty)"
            )
            new_desc_preview = updated.description[:40] if updated.description else "(empty)"
            quiet_print(f"   Description: {old_desc_preview}... → {new_desc_preview}...")

        if parsed_date and parsed_date != old_milestone.target_date:
            quiet_print(
                f"   Target Date: {old_milestone.target_date.strftime('%Y-%m-%d')} → {updated.target_date.strftime('%Y-%m-%d')}"
            )

        if status and (status != old_milestone.status.desc):
            quiet_print(f"   Status: {old_milestone.status} → {updated.status}")

        if not any([new_name, description is not None, parsed_date, status]):
            quiet_print("   (No changes were made)")

    except NoMilestoneFound as e:
        quiet_print(f"❌ Milestone '{name}' not found in context")
        logger.info(str(e))
        exit_with(USAGE_ERROR)
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


@milestone_app.command(help="Check milestone validation status")
def check(
    ctx: typer.Context,
    name: str | None = typer.Argument(None, help="Name of the milestone to check"),
    path: str = typer.Option(".", "--path", "-p", help="Path to the context", show_default=True),
    context_name: str | None = typer.Option(
        None,
        "--context",
        "-c",
        help="Context name (if multiple contexts exist)",
    ),
) -> None:
    """Check validation status of milestones."""
    logger = logging.getLogger("reerelease")
    logger.debug(f"CMD: milestone.check : name:{name}, path:{path}")

    path_obj = pathlib.Path(path).resolve()

    cm = ContextManager()
    mm = MilestoneManager()

    try:
        # Get the target context (root or specific named context)
        target_ctx = _get_target_context(cm, path_obj, context_name)

        # Get milestones
        milestones = mm.read(target_ctx)

        # Filter by name if provided
        if name:
            milestones = [m for m in milestones if m.name == name]
            if not milestones:
                quiet_print(f"❌ Milestone '{name}' not found")
                exit_with(USAGE_ERROR)

        # Validate each milestone
        has_issues = False
        for milestone in milestones:
            issues = validate_milestone(milestone)

            if issues:
                has_issues = True
                quiet_print(f"\n❌ Milestone '{milestone.name}' has issues:")
                for issue in issues:
                    quiet_print(f"  • {issue}")
            else:
                quiet_print(f"✅ Milestone '{milestone.name}' is healthy")

        if has_issues:
            exit_with(USAGE_ERROR)

    except NoContextFound:
        quiet_print(f"❌ No context found in {path_obj}")
        exit_with(USAGE_ERROR)
    except AppError as e:
        exit_with(print_exception(e))

    exit_with(OK)


if __name__ == "__main__":
    print("This module is intended to be used as a subcommand group and not run directly")
