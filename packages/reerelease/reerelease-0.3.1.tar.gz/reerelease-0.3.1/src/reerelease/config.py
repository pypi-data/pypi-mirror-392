import logging
import pathlib
from contextvars import ContextVar
from dataclasses import dataclass, field

from .core.milestone import (
    DEFAULT_MILESTONE_ORDER,
    DEFAULT_MILESTONE_STATUS,
    MILESTONE_STATUS,
    MilestoneOrder,
    MilestoneStatus,
)


# ========================= #
# ==== GLOBAL DEFAULTS ==== #
# ========================= #
@dataclass(frozen=True)
class Defaults:
    """Configuration defaults for reerelease."""

    verbosity: int = logging.WARNING
    quiet: bool = False
    search_depth: int = 10
    search_path: pathlib.Path = pathlib.Path(".")
    max_name_length: int = 128
    invalid_path_chars: str = '<>:"|?*\0'
    # milestone stuff
    milestone: str = "backlog"
    milestone_status: MilestoneStatus = field(default_factory=lambda: DEFAULT_MILESTONE_STATUS)
    milestone_order: MilestoneOrder = field(default_factory=lambda: DEFAULT_MILESTONE_ORDER)
    milestone_target_date_offset_days: int = 30
    max_description_length: int = 420
    # tasks stuff
    task_priority: str = "medium"
    # problem stuff
    problem_severity: str = "major"


DEFAULTS = Defaults()


# ======================= #
# ==== GLOBAL CONFIG ==== #
# ======================= #
@dataclass
class GlobalConfig:
    """Global configuration for reerelease commands.

    This is a mutable dataclass accessed via ContextVar (set_config/get_config).
    ContextVar provides thread-safety and context isolation automatically.

    Access config values directly:
        cfg = get_config()
        cfg.verbosity = logging.DEBUG  # direct assignment
        level = cfg.verbosity           # direct access
    """

    verbosity: int = DEFAULTS.verbosity
    quiet: bool = DEFAULTS.quiet
    # -- roadmap stuff -- #
    roadmap_excluded_sections: tuple[str, ...] = (
        "Backlog",
        "Note",
        "Unassigned",
    )  # section not considered a milestone in roadmap
    milestone_statuses: list[MilestoneStatus] = field(
        default_factory=lambda: list(MILESTONE_STATUS.ALL)
    )  # milestone statuses, configurable during run-time for future
    default_milestone_status: MilestoneStatus = field(
        default_factory=lambda: DEFAULTS.milestone_status
    )
    milestone_order: MilestoneOrder = field(default_factory=lambda: DEFAULTS.milestone_order)

    def get_status_by_name(self, name: str) -> MilestoneStatus:
        """Get MilestoneStatus by its name (desc).

        Returns DEFAULT_MILESTONE_STATUS if not found.

        Args:
            name: Name/description of the milestone status"""
        statuses: dict[str, MilestoneStatus] = {s.desc: s for s in self.milestone_statuses}
        return statuses.get(name, self.default_milestone_status)


# ============================= #
# ==== CONFIG CONTEXT VAR  ==== #
# ============================= #
# Thread-safe, async-safe context variable for accessing config
# This allows validators and utility functions to access config
# without explicit parameter passing
_config_context: ContextVar[GlobalConfig | None] = ContextVar("config", default=None)


def set_config(cfg: GlobalConfig) -> None:
    """Set the current config for this execution context.

    This should be called once at the start of CLI execution.

    Args:
        cfg: GlobalConfig instance to set as current

    Example:
        >>> cfg = GlobalConfig(verbosity=logging.DEBUG)
        >>> set_config(cfg)
    """
    _config_context.set(cfg)


def get_config() -> GlobalConfig:
    """Get the current config from execution context.

    Returns a default GlobalConfig if no config was set via set_config().
    This makes validators work gracefully even in simple test scenarios.

    Returns:
        Current GlobalConfig instance

    Example:
        >>> cfg = get_config()
        >>> if cfg.quiet:
        ...     print("Quiet mode enabled")
    """
    cfg = _config_context.get()
    if cfg is None:
        # Return default instance if no config was explicitly set
        # This allows validators to work without requiring config setup
        return GlobalConfig()
    return cfg
