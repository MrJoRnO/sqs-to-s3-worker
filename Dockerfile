FROM python:3.12-slim

ARG BUILD_DATE
ARG GIT_SHA
LABEL org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.source="github.com/platform/sqs-to-s3-app"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

RUN groupadd -r -g 1000 appuser && \
    useradd  -r -u 1000 -g appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

CMD ["python", "-m", "src.main"]
