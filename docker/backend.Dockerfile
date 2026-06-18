FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY pyproject.toml ./
COPY backend ./backend

RUN python -m pip install --upgrade pip \
  && python -m pip install -e ".[dev]"

EXPOSE 8000

CMD ["python", "-m", "backend.app"]
