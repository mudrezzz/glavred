FROM node:20-bookworm-slim AS node20

FROM python:3.12-slim AS python-deps
WORKDIR /build
COPY pyproject.toml ./
COPY backend ./backend
RUN python -m pip install --target /opt/glavred-python-deps ".[dev]"

FROM mcr.microsoft.com/playwright:v1.60.0-noble

COPY --from=node20 /usr/local/bin/node /usr/local/bin/node
COPY --from=node20 /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=python-deps /opt/glavred-python-deps /opt/glavred-python-deps
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
  && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
  && ln -sf /usr/bin/python3 /usr/local/bin/python \
  && node --version | grep '^v20\.' \
  && python --version | grep '^Python 3\.12\.' \
  && python -c 'import ssl; print(ssl.OPENSSL_VERSION)'

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/glavred-python-deps

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

CMD ["sleep", "infinity"]
