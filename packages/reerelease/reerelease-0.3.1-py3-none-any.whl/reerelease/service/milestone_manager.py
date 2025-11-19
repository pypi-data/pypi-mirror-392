"""Management of Milestone objects: creation, discovery, updating, deletion.

This service handles milestones within Context roadmap.md files.
Milestones are stored as markdown sections in the roadmap.md file.
"""

from __future__ import annotations

import datetime
import logging
from typing import TYPE_CHECKING

from reerelease.config import DEFAULTS, get_config

if TYPE_CHECKING:
    from ..service.dsl.phase2_parser import ParsedMemory

from ..core.context import Context
from ..core.milestone import MILESTONE_STATUS, Milestone
from ..core.task import Task
from ..errors import (
    DuplicateMilestone,
    InvalidMilestoneDate,
    InvalidMilestoneName,
    InvalidMilestoneStatus,
    MilestoneCreationError,
    MilestoneDeletionError,
    MilestoneDiscoveryError,
    MilestoneUpdateError,
    NoMilestoneFound,
)
from ..service.dsl import DSLPipeline
from ..service.template_manager import TemplateManager
from ..validators.validate_milestone import (
    validate_milestone,
    validate_milestone_date,
    validate_milestone_description,
    validate_milestone_name,
    validate_milestone_status,
)


class MilestoneManager:
    """Manager for Milestone objects: creation, discovery, updating, deletion.

    Milestones are stored as sections in the roadmap.md file of a context.
    This manager provides CRUD operations for milestones and handles
    the parsing and updating of roadmap.md files.

    The manager uses the DSL pipeline for parsing and rendering individual
    milestone sections with proper validation.
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger("reerelease")
        self.tm = TemplateManager()

        self.cfg = get_config()

        # Initialize DSL pipeline for roadmap (not individual milestone) parsing and rendering
        roadmap_template_path = self.tm.get_template_path("context/roadmap.md.j2")
        templates_dir = self.tm.get_templates_dir()

        # Create DSL pipeline from annotated roadmap template
        self.dsl_pipeline = DSLPipeline.from_template(roadmap_template_path, templates_dir)

    def _get_milestone_pipeline(self) -> DSLPipeline:
        """Get a DSL pipeline for parsing individual milestone sections.

        Returns:
            DSLPipeline configured for milestone template
        """
        milestone_template_path = self.tm.get_template_path("milestone/milestone_section.j2")
        templates_dir = self.tm.get_templates_dir()
        return DSLPipeline.from_template(milestone_template_path, templates_dir)

    def _parsed_memory_to_milestone(self, memory: ParsedMemory) -> Milestone:
        """
        Convert a ParsedMemory object (from milestone DSL template) to a Milestone object.

        Args:
            memory: ParsedMemory from milestone DSL parsing

        Returns:
            Milestone object
        """
        # Extract field values
        name = memory.fields.get("name", None)
        if name:
            name_str = name.value
        else:
            raise ValueError("Milestone name is required")

        description = memory.fields.get("description", None)
        description_str = description.value if description else ""

        target_date_str = memory.fields.get("target_date", None)
        if not target_date_str:
            raise ValueError("Milestone target_date is required")
        target_date = datetime.datetime.strptime(target_date_str.value, "%Y-%m-%d").date()

        status_str = memory.fields.get("status", None)
        if not status_str:
            raise ValueError("Milestone status is required")
        status = self.cfg.get_status_by_name(status_str.value)

        # Extract tasks from section
        tasks: list[Task] = []
        tasks_section = memory.sections.get("tasks", None)
        if tasks_section:
            for item in tasks_section.items:
                task = Task(
                    name=item.text,
                    completed=item.complete if item.complete is not None else False,
                    assigned_to=item.metadata.get("assigned", "") or "",
                )
                tasks.append(task)

        # Extract problems from section
        problems: list[str] = []
        problems_section = memory.sections.get("problems", None)
        if problems_section:
            problems = [item.text for item in problems_section.items]

        return Milestone(
            name=name_str,
            description=description_str,
            target_date=target_date,
            status=status,
            tasks=tasks,
            problems=problems,
        )

    def _milestone_to_parsed_memory(self, milestone: Milestone) -> ParsedMemory:
        """
        Convert a Milestone object to a ParsedMemory object (for milestone DSL template).

        Args:
            milestone: Milestone object

        Returns:
            ParsedMemory for rendering with milestone DSL template
        """
        from ..service.dsl.phase2_parser import ParsedField, ParsedItem, ParsedMemory, ParsedSection

        memory = ParsedMemory()

        # Add fields
        memory.fields["name"] = ParsedField(field_id="name", value=milestone.name)
        memory.fields["description"] = ParsedField(
            field_id="description", value=milestone.description or ""
        )
        memory.fields["target_date"] = ParsedField(
            field_id="target_date", value=milestone.target_date.strftime("%Y-%m-%d")
        )
        memory.fields["status"] = ParsedField(field_id="status", value=str(milestone.status.desc))

        # Add tasks section
        tasks_section = ParsedSection(section_id="tasks")
        for task in milestone.tasks:
            item = ParsedItem(
                text=task.name,
                complete=task.completed,
                metadata={"assigned": task.assigned_to} if task.assigned_to else {},
            )
            tasks_section.items.append(item)
        memory.sections["tasks"] = tasks_section

        # Add problems section
        problems_section = ParsedSection(section_id="problems")
        for problem in milestone.problems:
            item = ParsedItem(text=problem)
            problems_section.items.append(item)
        memory.sections["problems"] = problems_section

        return memory

    def _parse_roadmap_full(self, roadmap_content: str, context: Context) -> list[Milestone]:
        """
        Parse entire roadmap.md file and extract all milestones.

        Uses DSL pipeline to parse the roadmap as one cohesive document,
        extracting all ## level sections that are not in the excluded list
        (Backlog, Note, Unassigned, etc.) as milestones.

        Args:
            roadmap_content: Full roadmap.md markdown content
            context: Context for logging

        Returns:
            List of Milestone objects

        Raises:
            MilestoneDiscoveryError: If parsing fails
        """

        try:
            # Extract all ## sections from the markdown manually
            # since we need to identify which sections are milestones
            # (those NOT in the excluded list)
            milestones: list[Milestone] = []

            # Split by ## headers to extract individual milestone sections
            import re

            section_pattern = r"^## (.+)$"
            lines = roadmap_content.split("\n")

            current_section_name = None
            current_section_lines: list[str] = []

            for line in lines:
                match = re.match(section_pattern, line)
                if match:
                    # Process previous section if it was a milestone
                    if (
                        current_section_name
                        and current_section_name not in self.cfg.roadmap_excluded_sections
                    ):
                        section_content = "\n".join(current_section_lines)
                        try:
                            # Parse this individual milestone section with milestone DSL
                            milestone_pipeline = self._get_milestone_pipeline()

                            milestone_memory = milestone_pipeline.parse(section_content)
                            milestone = self._parsed_memory_to_milestone(milestone_memory)
                            milestones.append(milestone)

                        except Exception as e:
                            self.logger.warning(
                                f"Failed to parse milestone '{current_section_name}' in {context.name}: {e}"
                            )

                    # Start new section
                    current_section_name = match.group(1).strip()
                    current_section_lines = [line]
                else:
                    current_section_lines.append(line)

            # Process last section
            if (
                current_section_name
                and current_section_name not in self.cfg.roadmap_excluded_sections
            ):
                section_content = "\n".join(current_section_lines)
                try:
                    milestone_pipeline = self._get_milestone_pipeline()

                    milestone_memory = milestone_pipeline.parse(section_content)
                    milestone = self._parsed_memory_to_milestone(milestone_memory)
                    milestones.append(milestone)

                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse milestone '{current_section_name}' in {context.name}: {e}"
                    )

            return milestones

        except Exception as e:
            raise MilestoneDiscoveryError(f"Failed to parse roadmap for {context.name}: {e}") from e

    def _render_roadmap_full(self, context: Context, milestones: list[Milestone]) -> str:
        """
        Render entire roadmap.md from list of Milestone objects.

        Uses DSL pipeline to render the complete roadmap as one document,
        with all milestones rendered using the milestone DSL template.

        Args:
            context: Context containing the roadmap
            milestones: List of Milestone objects to render

        Returns:
            Complete roadmap.md markdown content

        Raises:
            MilestoneUpdateError: If rendering fails
        """
        try:
            # Convert each milestone to the context format expected by the template
            # The milestone template expects milestone_* prefixed variables
            milestones_context = []
            for milestone in milestones:
                # Convert to context dict with milestone_ prefix
                milestone_ctx: dict[str, object] = {
                    "milestone_name": milestone.name,
                    "milestone_description": milestone.description or "",
                    "milestone_target_date": milestone.target_date.strftime("%Y-%m-%d"),
                    "milestone_status": str(milestone.status.desc),
                }

                # Convert tasks
                milestone_ctx["milestone_tasks"] = [
                    {
                        "name": task.name,
                        "completed": task.completed,
                        "assigned_to": task.assigned_to,
                    }
                    for task in milestone.tasks
                ]

                # Convert problems
                milestone_ctx["milestone_problems"] = milestone.problems

                milestones_context.append(milestone_ctx)

            # Render roadmap with milestones
            roadmap_context = {
                "context_name": context.name,
                "milestones": milestones_context,
            }

            rendered = self.dsl_pipeline.render("context/roadmap.md.j2", roadmap_context)
            return rendered

        except Exception as e:
            raise MilestoneUpdateError(f"Failed to render roadmap for {context.name}: {e}") from e

    def read(self, context: Context) -> list[Milestone]:
        """Read all milestones in a context by parsing its roadmap.md file.

        Uses the new DSL-based full roadmap parsing approach.

        Args:
            context: The Context object to discover milestones in

        Returns:
            List of discovered Milestone objects

        Raises:
            MilestoneDiscoveryError: If discovery fails
        """
        self.logger.debug(f"mm.read called : context: {context.name}")

        roadmap_path = context.filepath / "roadmap.md"

        if not roadmap_path.exists():
            self.logger.warning(f"No roadmap.md found in {context.filepath}")
            return []

        try:
            content = roadmap_path.read_text(encoding="utf-8")
            milestones = self._parse_roadmap_full(content, context)
            self.logger.info(f"Discovered {len(milestones)} milestones in {context.name}")
            return milestones
        except Exception as e:
            self.logger.error(f"Failed to discover milestones: {e}")
            raise MilestoneDiscoveryError(
                "Failed to parse milestones from roadmap.md", issues=[str(e)]
            ) from e

    def create(
        self,
        context: Context,
        name: str,
        description: str = "",
        target_date: datetime.date | None = None,
        status: str | None = None,
    ) -> Milestone:
        """Create a new milestone in a context's roadmap.

        Uses full roadmap CRUD: parse → modify → render → write.

        Args:
            context: The Context to add the milestone to
            name: Milestone name
            description: Milestone description
            target_date: Target completion date (defaults to today)
            status: Initial status (defaults to configured default)

        Returns:
            The created Milestone object

        Raises:
            InvalidMilestoneName: If the milestone name is invalid
            InvalidMilestoneDate: If the target date is invalid
            InvalidMilestoneStatus: If the status is invalid
            DuplicateMilestone: If a milestone with the same name already exists
            MilestoneCreationError: If creation fails
        """
        self.logger.debug(
            f"mm.create called : name: '{name}', context: '{context.name}', date: {target_date}, status: {status}, description: '{description}'"
        )

        # 1. Validate inputs
        name_issues = validate_milestone_name(name)
        if name_issues:
            self.logger.debug(f"Milestone name validation issues: {name_issues}")
            raise InvalidMilestoneName("Invalid milestone name", name=name, issues=name_issues)

        # 2. Validate status
        if status is None:  # Apply defaults
            status = DEFAULTS.milestone_status.desc
        status_issues = validate_milestone_status(status)
        if status_issues:
            self.logger.debug(f"Milestone status validation issues: {status_issues}")
            raise InvalidMilestoneStatus(
                "Invalid milestone status", status=status, issues=status_issues
            )

        # 3. Validate date
        if target_date is None:
            target_date = datetime.date.today() + datetime.timedelta(
                days=DEFAULTS.milestone_target_date_offset_days
            )

        date_issues = validate_milestone_date(target_date)
        if date_issues:
            self.logger.debug(f"Milestone date validation issues: {date_issues}")
            raise InvalidMilestoneDate(
                "Invalid milestone date", date=str(target_date), issues=date_issues
            )

        # 4. Create milestone object
        milestone = Milestone(
            name=name,
            description=description,
            target_date=target_date,
            status=MILESTONE_STATUS.get(status),
        )

        # 5. Validate the complete milestone
        issues = validate_milestone(milestone)
        if issues:
            self.logger.warning(f"Milestone validation issues: {issues}")

        # Full roadmap CRUD: parse all, add new, render all, write all
        try:
            roadmap_path = context.filepath / "roadmap.md"

            # 1. Parse existing milestones
            existing_milestones: list[Milestone] = []
            if roadmap_path.exists():
                content = roadmap_path.read_text(encoding="utf-8")
                existing_milestones = self._parse_roadmap_full(content, context)

            # 2. Check for duplicate milestone name
            for existing in existing_milestones:
                if existing.name == name:
                    self.logger.debug(f"Duplicate milestone found: {name}")
                    raise DuplicateMilestone(
                        f"Milestone '{name}' already exists in context '{context.name}'",
                        milestone_name=name,
                        context_filepath=str(context.filepath),
                    )

            # 3. Add new milestone
            all_milestones = existing_milestones + [milestone]

            # 4. Render complete roadmap
            rendered = self._render_roadmap_full(context, all_milestones)

            # 5. Write back
            roadmap_path.write_text(rendered, encoding="utf-8")

            self.logger.info(f"Created milestone '{name}' in context '{context.name}'")
            return milestone
        except DuplicateMilestone:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create milestone: {e}")
            raise MilestoneCreationError(
                "Failed to add milestone to roadmap", issues=[str(e)]
            ) from e

    def find(self, context: Context, name: str) -> Milestone:
        """Find a milestone by name in a context.

        Args:
            context: The Context to search in
            name: The milestone name to find

        Returns:
            The found Milestone object

        Raises:
            NoMilestoneFound: If milestone is not found
        """
        self.logger.debug(f"mm.find called: name: '{name}', context: '{context.name}'")

        milestones = self.read(context)

        for milestone in milestones:
            if milestone.name == name:
                return milestone

        raise NoMilestoneFound(
            f"Milestone '{name}' not found",
            milestone_name=name,
            context_filepath=str(context.filepath),
        )

    def delete(self, context: Context, name: str, force: bool = False) -> None:
        """Delete a milestone from a context's roadmap.

        Uses full roadmap CRUD: parse all → remove → render all → write all.

        Args:
            context: The Context to delete from
            name: The milestone name to delete
            force: Skip confirmations

        Raises:
            NoMilestoneFound: If milestone doesn't exist
            MilestoneDeletionError: If deletion fails
        """
        self.logger.debug(
            f"mm.delete called : name: '{name}', context: '{context.name}', force: {force}"
        )

        try:
            roadmap_path = context.filepath / "roadmap.md"
            if not roadmap_path.exists():
                raise NoMilestoneFound(f"No roadmap found in context {context.name}")

            # Parse all milestones
            content = roadmap_path.read_text(encoding="utf-8")
            milestones = self._parse_roadmap_full(content, context)

            # Find and remove the milestone
            milestone_found = False
            filtered_milestones = []
            for m in milestones:
                if m.name == name:
                    milestone_found = True
                else:
                    filtered_milestones.append(m)

            if not milestone_found:
                raise NoMilestoneFound(f"Milestone '{name}' not found in context {context.name}")

            # Render complete roadmap without the deleted milestone
            rendered = self._render_roadmap_full(context, filtered_milestones)

            # Write back
            roadmap_path.write_text(rendered, encoding="utf-8")

            self.logger.info(f"Deleted milestone '{name}' from context '{context.name}'")

        except NoMilestoneFound:
            raise
        except Exception as e:
            self.logger.error(f"Failed to delete milestone: {e}")
            raise MilestoneDeletionError(
                "Failed to remove milestone from roadmap", issues=[str(e)]
            ) from e

    def update(
        self,
        context: Context,
        name: str,
        new_name: str | None = None,
        description: str | None = None,
        target_date: datetime.date | None = None,
        status: str | None = None,
    ) -> Milestone:
        """Update an existing milestone.

        Uses full roadmap CRUD: parse all → find and modify → render all → write all.

        Args:
            context: The Context containing the milestone
            name: Current milestone name
            new_name: New name (if renaming)
            description: New description
            target_date: New target date
            status: New status

        Returns:
            The updated Milestone object

        Raises:
            NoMilestoneFound: If milestone doesn't exist
            MilestoneUpdateError: If update fails
        """
        self.logger.debug(
            f"mm.update called : name: '{name}', context: '{context.name}', new_name: '{new_name}', date: {target_date}, status: {status}, description: '{description}'"
        )

        try:
            roadmap_path = context.filepath / "roadmap.md"
            if not roadmap_path.exists():
                raise NoMilestoneFound(f"No roadmap found in context {context.name}")

            # Parse all milestones
            content = roadmap_path.read_text(encoding="utf-8")
            milestones = self._parse_roadmap_full(content, context)

            # Find the milestone to update
            milestone = None
            for m in milestones:
                if m.name == name:
                    milestone = m
                    break

            if not milestone:
                raise NoMilestoneFound(f"Milestone '{name}' not found in context {context.name}")

            # Update fields
            if new_name is not None:
                name_issues = validate_milestone_name(new_name)
                if name_issues:
                    raise InvalidMilestoneName(
                        "Invalid new milestone name", name=new_name, issues=name_issues
                    )
                milestone.name = new_name

            if description is not None:
                description_issues = validate_milestone_description(description)
                if description_issues:
                    raise MilestoneUpdateError(
                        "Invalid milestone description", issues=description_issues
                    )
                milestone.description = description

            if target_date is not None:
                date_issues = validate_milestone_date(target_date)
                if date_issues:
                    raise InvalidMilestoneDate(
                        "Invalid target date", date=str(target_date), issues=date_issues
                    )
                milestone.target_date = target_date

            if status is not None:
                # Validate status format first
                status_issues = validate_milestone_status(status)
                if status_issues:
                    raise InvalidMilestoneStatus(
                        "Invalid status", status=status, issues=status_issues
                    )

                milestone.status = self.cfg.get_status_by_name(
                    status
                )  # TODO: this list will be context-specific at some point

            # Render complete roadmap with updated milestone
            rendered = self._render_roadmap_full(context, milestones)

            # Write back
            roadmap_path.write_text(rendered, encoding="utf-8")

            self.logger.info(f"Updated milestone '{milestone.name}' in context '{context.name}'")
            return milestone

        except (
            NoMilestoneFound,
            InvalidMilestoneName,
            InvalidMilestoneDate,
            InvalidMilestoneStatus,
        ):
            raise
        except Exception as e:
            self.logger.error(
                f"Failed to update milestone '{name}' in context '{context.name}': {e}"
            )
            raise MilestoneUpdateError("Failed to update milestone", issues=[str(e)]) from e
