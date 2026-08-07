from dataclasses import dataclass, field
from typing import List


@dataclass
class ExecutionStep:
    """
    A single synchronization step.
    """

    entity: str
    identifier: str
    action: str = "sync"
    depends_on: List[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """
    Ordered execution plan produced by the planner.
    """

    root_entity: str
    root_identifier: str

    steps: List[ExecutionStep] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    errors: List[str] = field(default_factory=list)

    def add_step(self, step: ExecutionStep):
        self.steps.append(step)

    @property
    def total_steps(self):
        return len(self.steps)

    @property
    def valid(self):
        return len(self.errors) == 0
