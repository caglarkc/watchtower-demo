FROM python:3.12-slim
WORKDIR /app
COPY server.py healthcheck.py ./
ENV LOG_ROOT=/var/log/corp/dhcp
EXPOSE 8080
CMD ["python", "/app/server.py"]
