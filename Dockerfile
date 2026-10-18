FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY rubric.example.json samples.jsonl ./

# Reach Ollama on the Docker host by default
ENV OLLAMA_HOST=http://host.docker.internal:11434

ENTRYPOINT ["decision-judge"]
CMD ["samples.jsonl", "--rubric", "rubric.example.json"]
