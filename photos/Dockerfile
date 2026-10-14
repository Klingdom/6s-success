# 6S Success photos API. Built from the REPOSITORY ROOT so the methodology is
# read from the same files the website is built from:
#   docker build -f photos/Dockerfile -t 6s-photos .
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "Pillow==11.3.0"
COPY content/manual/source/content.json content/manual/source/content.json
COPY ops/zone-name-map.json ops/root_causes.py ops/
COPY photos/methodology.py photos/store.py photos/analyze.py photos/server.py photos/
ENV SIXS_ROOT=/app PHOTOS_DATA=/data PHOTOS_HOST=0.0.0.0
RUN useradd --create-home --uid 10002 photos && mkdir -p /data && chown -R photos:photos /data /app
USER photos
EXPOSE 8975
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8975/v1/health', timeout=4).status == 200 else 1)" || exit 1
CMD ["python", "photos/server.py", "--port", "8975"]
