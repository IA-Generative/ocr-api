ARG HARBOR_PROXY_URL

FROM ${HARBOR_PROXY_URL:-docker.io}/python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flower redis celery

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home --home-dir /home/appuser --shell /usr/sbin/nologin appuser \
    && mkdir -p /home/appuser \
    && chown -R appuser:appuser /home/appuser
ENV HOME=/home/appuser
ENV PYTHONDONTWRITEBYTECODE=1

USER appuser

EXPOSE 5555
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python3 -c "import urllib.request as u; u.urlopen('http://127.0.0.1:5555/', timeout=2)" || exit 1
