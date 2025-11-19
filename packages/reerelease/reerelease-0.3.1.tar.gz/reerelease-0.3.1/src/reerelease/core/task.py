from dataclasses import dataclass, field


# ---- Main dataclass ---- #
@dataclass
class Task:
    name: str
    description: str = ""
    completed: bool = False
    assigned_to: str = ""
    labels: list[str] = field(default_factory=list)
