FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-dev

COPY . .

ENV PYTHONPATH=/app

CMD ["poetry", "run", "python", "src/main.py"]