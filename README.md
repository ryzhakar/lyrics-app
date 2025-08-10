## Dev quickstart

1. Create venv and install deps

```
uv venv
source .venv/bin/activate
uv sync --extra dev --frozen
```

2. Start Postgres and run migrations

```
docker compose up -d db
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lyrics_app
alembic upgrade head
```

3. Seed sample data and bootstrap admin (optional)

```
uv run python -m app.seed
```
This will create `.env` with `SECRET_KEY`, `DATABASE_URL` and admin bootstrap credentials if missing.

4. Run the app

```
uv run uvicorn app.main:app --reload
```

5. Pre-commit hooks

```
uv run pre-commit install
git add -A
pre-commit run --all-files
```

## Env

See `.env.example` for required variables.
