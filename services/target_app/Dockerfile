FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY services/target_app ./services/target_app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

ENV PYTHONPATH=/app/packages:/app
EXPOSE 8001

CMD ["uvicorn", "services.target_app.app:app", "--host", "0.0.0.0", "--port", "8001"]
