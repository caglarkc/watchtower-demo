FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py healthcheck.py ./
ENV GITEA_URL=http://corp-gitea:3000
ENV LOG_ROOT=/var/log/corp/gitea
EXPOSE 8080
CMD ["python", "/app/server.py"]
