# 6S Success website - static site served by nginx.
#
# The repository root holds the operating system (CLAUDE.md, control docs,
# agents, super prompts). Only site/ is the published website, so this image
# copies site/ and nothing else. Build context stays the repo root because
# Hostinger's Docker Manager clones the repo and builds from there.
FROM nginx:1.27-alpine

# our server config (gzip, caching, correct MIME for woff2/pdf, /stats proxy)
COPY site/nginx/default.conf /etc/nginx/conf.d/default.conf

# default.conf writes a second, date-named access log here. Created in the
# image so a missing bind mount costs history, not uptime: without this
# directory nginx cannot open the log and refuses to start, which would mean a
# logging change could take the whole site down. The mount is in
# docker-compose.hostinger.yml.
RUN mkdir -p /var/log/nginx/persist

# Fail the build on a bad config rather than the deploy. Without this a syntax
# error ships a green image that crash loops on the host, which is a much worse
# place to find out.
RUN nginx -t

# copy the site into the web root, then strip the infra files back out
COPY site/ /usr/share/nginx/html
RUN cd /usr/share/nginx/html && \
    rm -rf nginx .gitignore

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1
