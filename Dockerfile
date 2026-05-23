FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY watchtower ./watchtower

RUN pip install --no-cache-dir .

ENV WATCHTOWER_DATABASE_PATH=/data/watchtower.db \
    WATCHTOWER_BACKUP_DIR=/backups \
    PYTHONUNBUFFERED=1

RUN mkdir -p /data /backups

VOLUME ["/data", "/backups"]

COPY scripts/docker-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD ["wt", "health", "--json"]

ENTRYPOINT ["/entrypoint.sh"]
CMD ["wt", "status"]
