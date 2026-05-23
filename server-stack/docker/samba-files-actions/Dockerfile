FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl smbclient cifs-utils \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY server.py healthcheck.py ./
ENV SAMBA_HOST=corp-samba-files
ENV SAMBA_USER=cfo
ENV SAMBA_PASS=Watchtower1!
ENV LOG_ROOT=/var/log/corp/samba
EXPOSE 8080
CMD ["python", "/app/server.py"]
