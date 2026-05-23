FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl bind9-dnsutils && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py healthcheck.py ./
EXPOSE 389 8080
CMD ["python", "/app/server.py"]
