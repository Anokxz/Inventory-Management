# Inventory Management — Dockerized

This repository contains a small Flask-based inventory management app.

This README shows how to build and run the app using Docker. The project uses `uv` for package management with a lockfile (`uv.lock`). The Dockerfile installs `uv` and installs the pinned dependencies from the lockfile.

Quick steps (build + run with docker-compose):

1. Build and start the services:

```bash
docker compose up --build
```

2. The app will be available at http://localhost:5000

Notes about dependency installation:

- The Dockerfile installs `uv` (the upstream tool that knows how to read `uv.lock`) and tries `uv install --no-dev` to reproduce the locked environment. If `uv` is not available in your environment or if the install fails, the Dockerfile falls back to `pip install .` so the image still builds.
- During development you can also use `uv` locally:

```bash
# install uv in your venv
python -m pip install uv
# and install locked deps
uv install --no-dev
```

Environment variables used by the app:

- DB_HOST, DB_USER, DB_PASSWD, DB_NAME, DB_PORT — database connection
- SECRET_KEY — Flask secret key
- HOST, PORT, FLASK_DEBUG — app runtime options

Security:

This repo includes a `docker-compose.yml` for local development only. Do not use the example database passwords in production.
