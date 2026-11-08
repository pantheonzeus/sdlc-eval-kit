# Sandbox for agent trials and scoring. Agent and scorer each get a fresh container from
# this image with no network; the seed repos need nothing beyond pytest.
FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir pytest==9.2.0 pyyaml==6.0.3 \
    && git config --global user.email agent@sdlc-eval-kit.invalid \
    && git config --global user.name agent \
    && git config --global init.defaultBranch main

ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /work
