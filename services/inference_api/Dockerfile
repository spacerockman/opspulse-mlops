# TODO(Sprint 2, Member A, Issue #7):
# Convert this PoC Dockerfile into a multi-stage build with a non-root user
# and image size < 300MB, ready for AWS ECR & ECS Fargate deployment.
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services/inference_api ./services/inference_api

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PYTHONPATH=/app/packages:/app
EXPOSE 8002

CMD ["uvicorn", "services.inference_api.app:app", "--host", "0.0.0.0", "--port", "8002"]
