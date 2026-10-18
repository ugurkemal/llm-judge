# decision-judge

Valideert de output van een AI-applicatie met een *decision model* (geen vrije tekst, maar getypeerde antwoorden + kansen).
Draait lokaal met het decision model `tev1` via Ollama (`/v1/systemone`, Ollama 0.35+; `ollama pull tev1`).
Optionele env: `OLLAMA_HOST` (standaard `http://localhost:11434`), `OLLAMA_MODEL` (standaard `tev1`).

Een rubric bestaat uit atomaire dimensies (`score` of `noul`). Resultaat per item: `pass`, `fail` of `review` (lage zekerheid, naar een mens).

```bash
pip install -e .[dev]
pytest
decision-judge samples.jsonl --rubric rubric.example.json
```

Exitcode is 1 als er minstens één `fail` is (bruikbaar in CI).

## Docker

```bash
docker build -t decision-judge .
docker run --rm decision-judge
docker run --rm -v "${PWD}:/data" decision-judge /data/mijn.jsonl --rubric /data/rubric.example.json
```

De container bereikt Ollama op de host via `OLLAMA_HOST=http://host.docker.internal:11434`. Overschrijf dit met `-e OLLAMA_HOST=...` als Ollama elders draait.
Bestanden in UTF-8 zonder BOM opslaan (Windows PowerShell 5: `Set-Content -Encoding utf8` voegt een BOM toe).
Valideer drempels (`pass_at`, `min_confidence`) altijd op eigen gelabelde voorbeelden.
