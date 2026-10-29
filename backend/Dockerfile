# Build from the repository root: docker build -f backend/Dockerfile .
FROM python:3.13-slim-bookworm AS api
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=backend.core.settings
WORKDIR /app
COPY backend/requirements.lock.txt ./requirements.lock.txt
RUN pip install -r requirements.lock.txt
COPY backend ./backend
RUN useradd --system --uid 10001 --home /app medlive \
    && mkdir -p /data/files && chown medlive:medlive /data/files
USER medlive
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:4000/readyz', timeout=4)"
CMD ["python", "-m", "uvicorn", "backend.core.asgi:application", "--host", "0.0.0.0", "--port", "4000", "--no-proxy-headers", "--timeout-graceful-shutdown", "20"]
