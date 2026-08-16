# 6S Success website — static site served by nginx.
FROM nginx:1.27-alpine

# our server config (gzip, caching, correct MIME for woff2/pdf)
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

# copy the whole site into the web root, then strip the infra files back out
COPY . /usr/share/nginx/html
RUN cd /usr/share/nginx/html && \
    rm -rf nginx Dockerfile docker-compose.yml .dockerignore .gitignore DEPLOY.md .github .git

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1
