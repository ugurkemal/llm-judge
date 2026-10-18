from __future__ import annotations

import argparse
import json
import sys

from .backends import OllamaBackend
from .judge import Judge
from .models import Dimension, Rubric


def load_rubric(path: str) -> Rubric:
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    dims = [Dimension(**d) for d in raw["dimensions"]]
    return Rubric(dims, raw.get("min_confidence", 0.5))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate AI outputs with a decision model.")
    p.add_argument("dataset", help="JSONL with fields: input, output, [context]")
    p.add_argument("--rubric", default="rubric.example.json")
    p.add_argument("--model", default=None, help="Ollama model (default: $OLLAMA_MODEL or tev1)")
    args = p.parse_args(argv)

    judge = Judge(OllamaBackend(model=args.model), load_rubric(args.rubric))
    counts = {"pass": 0, "fail": 0, "review": 0}
    with open(args.dataset, encoding="utf-8") as f:
        for line in filter(str.strip, f):
            row = json.loads(line)
            verdict = judge.evaluate(input=row["input"], output=row["output"],
                                     context=row.get("context"))
            counts[verdict.decision] += 1
            print(json.dumps({"input": row["input"], **verdict.to_dict()}, ensure_ascii=False))
    print(json.dumps(counts), file=sys.stderr)
    return 1 if counts["fail"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
