### Iteration 1 (v1.0): Minimum Playable Product — Checklist

- [ ] Project scaffolding
  - [x] Confirm Python >=3.11 and `uv` workflow (install, run, export)
  - [x] Create app structure: `app/`, `app/templates/`, `static/css/`, `static/js/`
  - [x] Add FastAPI entrypoint `app/main.py` with Jinja templates setup and health route
  - [x] Add base Pico CSS and custom overrides scaffold in `static/css/`
  - [x] Add `.env.example` with required variables
  - [x] Add `Dockerfile` (multi-stage) and `docker-compose.yml` (app + Postgres); prefer Docker for dev & prod

- [x] Configuration and settings
  - [x] Add `pydantic-settings` to dependencies and use it for env loading (DATABASE_URL, SECRET_KEY, DEBUG)
  - [x] Add admin bootstrap envs for first run (ADMIN_BOOTSTRAP_EMAIL, ADMIN_BOOTSTRAP_PASSWORD or PASSWORD_HASH)
  - [x] Wire uvicorn run config and debug flag

- [x] Database and migrations
  - [x] Initialize Alembic with async SQLAlchemy config
  - [x] Prefer SQLAlchemy Core for schema and queries; provide minimal ORM models only where required by SQLAdmin
- [x] Define Core tables:
        `songs`: id (UUID, pk), original_title, translated_title (required), artist,
        chordpro_content (required), default_key, youtube_url, songlink_url,
        is_draft (boolean, default false), search_vector (tsvector), created_at, updated_at
        `admin_users`: id (UUID, pk), email (unique), password_hash, created_at, updated_at
  - [x] Configure Alembic `env.py` with app metadata for autogenerate
  - [x] Autogenerate initial migration, then edit to add indexes and triggers
  - [x] Add indexes: pk(id), translated_title, artist, created_at DESC
  - [x] Add GIN on `search_vector` and trigger/function to maintain it

- [x] Data access layer
  - [x] Configure async engine and connection management
  - [x] Implement Core-based query helpers for songs (create, get by id, search, list recent) that exclude drafts from public listings
  - [x] Implement Core-based query helpers for admin_users (create, get by email)

- [x] ChordPro parser
  - [x] Implement tokenizer for `[Chord]` and `{start_of_section: Name}` / `{end_of_section}`
  - [x] Build AST with sections and line-level chord/lyric alignment metadata
  - [x] Validate structure: unclosed sections → error; extremely long sections → warning
  - [x] Expose parse function returning structured song data + warnings/errors

- [x] Transposition
  - [x] Add `python-chord` (or equivalent) as dependency
  - [x] Implement transpose function handling semitone intervals and slash chords
  - [x] Preserve chord qualities (maj7, sus4, etc.)

- [x] Rendering engine
  - [x] Implement monospace chord positioning preserving original indices
  - [x] Render two-line blocks (chords above, lyrics below) into HTML
  - [x] Create templates: `base.html`, `song.html` with mobile-first layout
  - [x] Add dark mode via CSS custom properties
  - [x] Add print styles to remove UI chrome

- [x] URL structure and routing
  - [x] Implement single/multi-song parsing from `/?s=<uuid>:<key>,...`
  - [x] Support `&dark=1`, `&chords=0`, `&font=large`
  - [x] Validate parameters; reject unrenderable input
  - [x] Route that renders one or many songs in setlist order
  - [x] Public routes must not include draft songs; admin can preview drafts explicitly

- [x] Search (v1.0 basic)
  - [x] Create search page with input and result list
  - [x] Implement ILIKE-based search on title, artist, chordpro_content
  - [x] Order results per priority rules (title prefix, contains, artist)
  - [x] Exclude drafts from public search results

- [x] Admin interface (SQLAdmin)
  - [x] Configure SQLAdmin and register ModelViews using minimal ORM models
  - [x] Songs: textarea editor for ChordPro content; draft toggle field; block save on parse errors
  - [x] Draft affects visibility only; required fields and validation are enforced regardless of draft state
  - [x] Admin users: create/list admins; hashed passwords; no role distinctions
  - [x] On blur, run backend validation and show status (✅/⚠️/🔴); block save on parse errors
  - [x] Add preset templates for common song structures
- [ ] Optional: auto-save draft toggle if time permits

- [x] Deployment and local dev
  - [x] Docker-first: build and run app via Docker/Compose in dev and prod
  - [x] `docker-compose.yml` includes Postgres, app, volumes, healthchecks
  - [x] Document env setup and run commands in `README.md` (docker-focused)
- [ ] Prepare Dokku deployment steps and env configuration

- [x] Testing and QA
  - [x] Unit tests for tokenizer, AST builder, and transposition (incl. slash chords)
  - [x] Rendering test: positions preserved across transposition
  - [x] Admin validation tests: error and warning cases
  - [x] Draft behavior tests: drafts not in public listings/search; admin preview works
  - [x] Admin user tests: password hashing, login, create another admin
  - [x] API/UI smoke tests: health, search, single-song, multi-song render

- [x] Seed data
  - [x] Add 2–3 sample songs (with varied chords and sections)
  - [x] Provide minimal seeding script or admin import flow
  - [x] Seed an initial admin from env or one-time CLI

- [x] Exit criteria
  - [x] From a clean database, an admin can add a valid ChordPro song and save it
  - [x] A user can open `/?s=<uuid>:<key>` and see correctly rendered chords/lyrics
  - [x] Multi-song setlist renders in order with separators
  - [x] Transposition works for basic and slash chords
  - [x] Search finds songs and orders them reasonably
  - [x] Dark mode and font size parameter work
  - [x] Drafts are hidden from public search/list; admin can toggle draft state
  - [x] Admin can create another admin account
  - [x] App is dockerized, deployable, and runs against Postgres
