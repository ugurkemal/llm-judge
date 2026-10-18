from __future__ import annotations

from typing import Any, Protocol

from .models import Answer, DimensionResult, Rubric, Verdict


class Backend(Protocol):
    def ask(self, state: Any, questions: dict[str, dict]) -> dict[str, Answer]: ...


class Judge:
    """Validates an AI application's output against a rubric using a decision model."""

    def __init__(self, backend: Backend, rubric: Rubric):
        self.backend = backend
        self.rubric = rubric

    def evaluate(self, *, input: str, output: str, context: str | None = None) -> Verdict:
        state: dict[str, str] = {"user_input": input, "ai_output": output}
        if context:
            state["reference_context"] = context
        questions = {d.name: d.to_question() for d in self.rubric.dimensions}
        answers = self.backend.ask(state, questions)

        results: list[DimensionResult] = []
        for d in self.rubric.dimensions:
            a = answers[d.name]
            if d.kind == "noul":
                p_good = a.value if d.good_when else 1 - a.value
                passed = p_good >= d.pass_at
                # a noul probability near 0.5 is the uncertainty signal
                conf = a.confidence if a.confidence is not None else abs(a.value - 0.5) * 2
            else:
                passed = a.value >= d.pass_at
                conf = a.confidence
            low = conf is not None and conf < self.rubric.min_confidence
            results.append(DimensionResult(d.name, a.value, conf, passed, low))

        required = [(r, d.required) for r, d in zip(results, self.rubric.dimensions)]
        confident_fail = any(not r.passed and not r.low_confidence for r, req in required if req)
        unsure = any(r.low_confidence for r in results)
        if confident_fail:
            decision = "fail"
        elif unsure:
            decision = "review"
        else:
            decision = "pass"
        return Verdict(decision, results)
