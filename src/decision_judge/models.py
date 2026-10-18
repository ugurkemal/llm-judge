from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Kind = Literal["score", "noul"]


@dataclass(frozen=True)
class Dimension:
    """One atomic quality check. `score` uses ordered levels (lowest to highest);
    `noul` is a true/false statement that should be true (or false, if good_when=False)."""

    name: str
    instructions: str
    kind: Kind = "score"
    levels: list[str] = field(default_factory=list)
    pass_at: float = 0.0  # score: minimum level index; noul: minimum probability of "good"
    good_when: bool = True  # noul only
    required: bool = True

    def to_question(self) -> dict:
        q: dict = {"type": self.kind, "instructions": self.instructions}
        if self.kind == "score":
            if len(self.levels) < 2:
                raise ValueError(f"{self.name}: score needs at least 2 levels")
            q["criteria"] = list(self.levels)
        return q


@dataclass(frozen=True)
class Rubric:
    dimensions: list[Dimension]
    min_confidence: float = 0.5  # below this on a dimension -> human review


@dataclass(frozen=True)
class Answer:
    value: float
    confidence: float | None = None
    probabilities: dict[str, float] | None = None


@dataclass
class DimensionResult:
    name: str
    value: float
    confidence: float | None
    passed: bool
    low_confidence: bool


@dataclass
class Verdict:
    decision: Literal["pass", "fail", "review"]
    results: list[DimensionResult]

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "dimensions": [r.__dict__ for r in self.results],
        }
