from __future__ import annotations

import datetime
import reprlib
from dataclasses import dataclass, field
from enum import Enum

# from typing import Literal, get_args
# Forward reference to avoid circular import
# MilestoneError will be imported when needed
from .task import Task

# == Milestone status == #
# TODO: refactor to use an Enum instead of Literal
# Type alias for milestone status - SINGLE SOURCE OF TRUTH
# MilestoneStatus = Literal["invalid", "planned", "in-progress", "completed", "cancelled", "released"]

# Runtime access to valid statuses (derived from the Literal type)
# VALID_MILESTONE_STATUSES: tuple[str, ...] = get_args(MilestoneStatus)

# Default milestone status
# DEFAULT_MILESTONE_STATUS: MilestoneStatus = "planned"


@dataclass(frozen=True)
class MilestoneStatus:
    """Milestone status representation"""

    desc: str
    color: str
    emoji: str


class MILESTONE_STATUS:
    """Default milestone statuses to start the accepted statuses list from"""

    INVALID = MilestoneStatus("invalid", "yellow", "⚠️")
    PLANNED = MilestoneStatus("planned", "blue", "📅")
    IN_PROGRESS = MilestoneStatus("in-progress", "cyan", "🚧")
    COMPLETED = MilestoneStatus("completed", "green", "✅")
    CANCELLED = MilestoneStatus("cancelled", "red", "❌")
    RELEASED = MilestoneStatus("released", "magenta", "🚀")

    ALL: tuple[MilestoneStatus, ...] = (
        INVALID,
        PLANNED,
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
        RELEASED,
    )

    BY_NAME: dict[str, MilestoneStatus] = {s.desc: s for s in ALL}

    @classmethod
    def get(cls, name: str) -> MilestoneStatus:
        """Return known status or INVALID as fallback."""
        return cls.BY_NAME.get(name, cls.INVALID)


# Default milestone status to apply to milestone when unknown
DEFAULT_MILESTONE_STATUS: MilestoneStatus = MILESTONE_STATUS.PLANNED


# == Milestone ordering == #
class MilestoneOrder(str, Enum):
    """Milestone ordering options for roadmap display"""

    NAME_INC = "name_increasing"
    NAME_DEC = "name_decreasing"
    DATE_INC = "date_increasing"
    DATE_DEC = "date_decreasing"
    ARBITRARY = "arbitrary"


# Default milestone ordering in roadmap
DEFAULT_MILESTONE_ORDER: MilestoneOrder = MilestoneOrder.NAME_DEC


# ---- Main dataclass ---- #
@dataclass
class Milestone:
    """Represents a project milestone with tasks, problems, and status tracking.

    Attributes:
        name: Unique identifier for the milestone
        description: Detailed description of milestone goals
        target_date: Target completion date
        status: Current milestone status
        tasks: List of associated tasks
        problems: List of known problems/blockers
        domains: List of associated domain tags
        issues: List of validation issues
        healthy: Whether milestone passes all validations
        release_link: Optional link to release notes
    """

    name: str
    description: str = ""
    target_date: datetime.date = field(default_factory=lambda: datetime.date.today())
    status: MilestoneStatus = field(default_factory=lambda: MILESTONE_STATUS.INVALID)
    tasks: list[Task] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)  # change to correct domain type when available
    issues: list[str] = field(default_factory=list)
    release_link: str = ""

    def __str__(self) -> str:
        return (
            f"{self.name} [{self.status.desc}] "
            f"(target: {self.target_date}) "
            f"with {len(self.tasks)} tasks, {len(self.problems)} problems"
        )

    def __repr__(self) -> str:
        r = reprlib.Repr()
        r.maxlist = 8
        r.maxstring = 120
        r.maxother = 120
        return (
            "Milestone("
            f"name={r.repr(self.name)}, "
            f"description={r.repr(self.description)}, "
            f"target_date={r.repr(self.target_date)}, "
            f"status={r.repr(self.status.desc)}, "
            f"tasks={r.repr(self.tasks)}, "
            f"problems={r.repr(self.problems)}, "
            ")"
        )

    def pretty(self, indent: int = 0) -> str:
        """Return a multi-line, indented, readable representation of the Milestone."""
        pad = " " * indent
        inner = " " * (indent + 2)
        lines: list[str] = [f"{pad}Milestone("]
        lines.append(f"{inner}name: {self.name!r},")
        lines.append(f"{inner}description: {self.description!r},")
        lines.append(f"{inner}target_date: {self.target_date!r},")
        lines.append(f"{inner}status: {self.status.desc!r},")
        lines.append(f"{inner}tasks: {self.tasks!r},")
        lines.append(f"{inner}problems: {self.problems!r},")
        lines.append(f"{pad})")
        return "\n".join(lines)

    def add_task(self, task: Task) -> None:
        """Add a task to this milestone."""
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this milestone."""
        if not isinstance(task, Task):
            raise TypeError("task must be an instance of Task")
        try:
            self.tasks.remove(task)
        except ValueError:
            # Import here to avoid circular dependency
            from ..errors import MilestoneError

            raise MilestoneError(f"task not found: {task}") from None

    def set_target_date(self, target_date: datetime.date) -> None:
        """Update the target completion date."""
        if not isinstance(target_date, datetime.date):
            raise TypeError("target_date must be an instance of datetime.date")
        self.target_date = target_date

    def set_status(self, status: MilestoneStatus) -> None:
        """Update the milestone status.

        Args:
            status: A valid MilestoneStatus enum value
        """
        if not isinstance(status, MilestoneStatus):
            raise TypeError("status must be an instance of MilestoneStatus Enum")
        self.status = status

    def is_healthy(self) -> bool:
        """Check if milestone is healthy (no issues)."""
        return len(self.issues) == 0

    def is_done(self) -> bool:
        """Check if milestone is completed."""
        # Return True only if this milestone's status is one of the
        # terminal statuses: completed, cancelled, or released.
        return self.status in (
            MILESTONE_STATUS.COMPLETED,
            MILESTONE_STATUS.CANCELLED,
            MILESTONE_STATUS.RELEASED,
        )

    def is_overdue(self) -> bool:
        """Check if milestone is past its target date and not completed."""
        return not self.is_done() and self.target_date < datetime.date.today()

    def completion_percentage(self) -> float:
        """Calculate task completion percentage."""
        if not self.tasks:
            return 0.0
        completed = sum(1 for task in self.tasks if task.completed)
        return (completed / len(self.tasks)) * 100.0
