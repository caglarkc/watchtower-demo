FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl libpq-dev gcc \
    && pip install --no-cache-dir psycopg2-binary \
    && apt-get purge -y gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py healthcheck.py ./
ENV PGHOST=corp-postgres
ENV PGUSER=corp
ENV PGPASSWORD=Watchtower1!
ENV PGDATABASE=corpdb
ENV LOG_ROOT=/var/log/corp/postgres
EXPOSE 8080
CMD ["python", "/app/server.py"]
