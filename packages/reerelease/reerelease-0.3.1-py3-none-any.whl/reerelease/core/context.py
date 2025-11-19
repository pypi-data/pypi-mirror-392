"""Context detection and management utilities."""

# Use built-in generics (PEP 585) with `from __future__ import annotations`
from __future__ import annotations

import os
import pathlib
import reprlib
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import cast

from anytree import NodeMixin

from ..errors import ContextError
from .milestone import Milestone


# ---- Main dataclass ---- #
@dataclass
class Context(NodeMixin):  # type: ignore[misc]
    name: str
    filepath: pathlib.Path

    children: list[Context] = field(default_factory=list)

    healthy: bool = False
    issues: list[str] = field(default_factory=list)
    milestones: list[Milestone] = field(default_factory=list)
    developers: list[str] = field(
        default_factory=list
    )  # placeholder until developper function is available
    domains: list[str] = field(default_factory=list)  # change to correct domain type when available

    def __post_init__(self) -> None:
        # Accept pathlib.Path, str, and os.PathLike
        filepath = cast(pathlib.Path | str | os.PathLike[str], self.filepath)
        if isinstance(filepath, pathlib.Path):
            return
        try:
            object.__setattr__(self, "filepath", pathlib.Path(filepath))
        except TypeError:
            raise ContextError(
                "Context.filepath must be a pathlib.Path, str, or os.PathLike"
            ) from None

    def __str__(self) -> str:
        return f"{self.name} @ {self.filepath} ({'healthy' if self.healthy else 'broken'}) with {len(self.milestones)} milestones, {len(self.developers)} developers"

    def __repr__(self) -> str:
        # Use reprlib.Repr to avoid dumping extremely large lists/strings in reprs.
        r = reprlib.Repr()
        # sensible truncation limits; tweak if needed
        r.maxlist = 8
        r.maxstring = 120
        r.maxother = 120
        return (
            "Context("
            f"name={r.repr(self.name)}, "
            f"filepath={r.repr(self.filepath)}, "
            f"healthy={r.repr(self.healthy)}, "
            f"issues={r.repr(self.issues)}, "
            f"milestones={r.repr(self.milestones)}, "
            f"developers={r.repr(self.developers)}, "
            f"domains={r.repr(self.domains)}"
            ")"
        )

    def pretty(self, indent: int = 0) -> str:
        """Return a multi-line, indented, readable representation of the Context.

        Example:
            Context(
              name: 'myctx',
              filepath: '/tmp/dir',
              healthy: True,
              issues: [],
              milestones: [],
            )
        """
        pad = " " * indent
        inner = " " * (indent + 2)
        lines: list[str] = [f"{pad}Context("]
        lines.append(f"{inner}name: {self.name!r},")
        lines.append(f"{inner}filepath: {self.filepath!r},")
        lines.append(f"{inner}healthy: {self.healthy!r},")
        lines.append(f"{inner}issues: {self.issues!r},")
        lines.append(f"{inner}milestones: {self.milestones!r},")
        lines.append(f"{inner}developers: {self.developers!r},")
        lines.append(f"{inner}domains: {self.domains!r},")
        lines.append(f"{pad})")
        return "\n".join(lines)

    def add_child(self, child: Context) -> None:
        if not isinstance(child, Context):
            raise TypeError("child must be an instance of Context")
        child.parent = self  # anytree will handle adding to children list

        self.sort_children()

    def remove_child(self, child: Context) -> None:
        if not isinstance(child, Context):
            raise TypeError("child must be an instance of Context")
        if child not in self.children:
            raise ContextError(f"child not found: {child}")
        child.parent = None  # detach child from parent

    @staticmethod
    def iter_sorting(children: Iterable[Context]) -> list[Context]:
        """Takes and return a list of children sorted by name and filepath (useful for RenderTree)"""
        return sorted(children, key=lambda c: (c.name.lower(), str(c.filepath)))

    def sort_children(self) -> None:
        """Sort this node's children alphabetically by name (case-insensitive),
        and by filepath as a tiebreaker if names are identical.
        """
        if not self.children:
            return

        try:
            # Reassign via property (don't touch internal _children)
            self.children = self.iter_sorting(self.children)
        except AttributeError:
            # The node might not have initialized children or filepath yet
            pass

    def add_milestone(self, milestone: Milestone) -> None:
        if not isinstance(milestone, Milestone):
            raise TypeError("milestone must be an instance of Milestone")
        self.milestones.append(milestone)

    def remove_milestone(self, milestone: Milestone) -> None:
        if not isinstance(milestone, Milestone):
            raise TypeError("milestone must be an instance of Milestone")
        try:
            self.milestones.remove(milestone)
        except ValueError:
            raise ContextError(f"milestone not found: {milestone}") from None
