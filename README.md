## Dev quickstart

1. Create venv and install deps

```
uv venv
uv pip install -r requirements.txt
uv pip install '.[dev]'
```

2. Start Postgres and run migrations

```
docker compose up -d db
alembic upgrade head
```

3. Seed sample data and bootstrap admin (optional)

```
uv run python -m app.seed
```
This will create `.env` with `SECRET_KEY`, `DATABASE_URL` and admin bootstrap credentials if missing.

4. Run the app

```
uvicorn app.main:app --reload
```

## Env

See `.env.example` for required variables.
