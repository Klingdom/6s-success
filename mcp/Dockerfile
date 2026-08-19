# The 6S Success MCP server.
#
# Serves the 114 micro zone corpus as tools to any Claude user who adds this
# connector. Read only, no auth, no state: the content is already public on
# 6s-success.com, so there is nothing to protect and nothing to write.
FROM python:3.12-slim

WORKDIR /app

# Dependencies first, so a change to the server or the corpus does not
# reinstall them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py content.json ./

# Never run as root. This process needs nothing a normal user lacks.
RUN useradd --create-home --uid 10001 mcp && chown -R mcp:mcp /app
USER mcp

ENV PORT=8974
EXPOSE 8974

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8974/mcp', timeout=4).status < 500 else 1)" || exit 1

CMD ["python", "server.py", "--http"]
