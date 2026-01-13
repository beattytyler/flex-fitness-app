## Flex Fitness App

Fitness coaching web app built with Flask. It supports trainer and member roles, daily nutrition logging, custom foods/meals, workout templates, and in-app messaging.

### Features
- Member dashboard: log foods, track macros/calories, build custom foods/meals, save “My Meals,” and view trainer-shared meals.
- Trainer tools: manage clients, share meal plans, create workout templates/sessions, review client stats.
- Messaging: trainers can send messages; members read them in the Messages page (unread is marked read on open).
- Themes and mobile-friendly layout using Bootstrap; Plotly charts on the My Stats page.

### Project structure
- `run.py` – app entrypoint.
- `config.py` – configuration and environment variables (DB, email, secrets).
- `app/` – Flask app package.
  - `routes/` – blueprints for auth, main site, member, trainer, templates.
  - `models.py` – SQLAlchemy models.
  - `services/` – nutrition utilities and helpers.
  - `static/`, `templates/` – CSS/JS assets and Jinja templates.
- `migrations/` – Flask-Migrate scripts.
- `scripts/` – data utilities (e.g., USDA caching).

### Prerequisites
- Python 3.11+ recommended
- SQLite (default) or another DB via `DATABASE_URL`

### Setup
```bash
python -m venv venv
venv\Scripts\activate  # on Windows; use source venv/bin/activate on macOS/Linux
pip install -r requirements.txt
```

### Environment variables (optional but recommended)
- `SECRET_KEY` – Flask secret.
- `DATABASE_URL` – override SQLite DB path if desired.
- Email/verification: `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_USE_TLS`, `MAIL_USE_SSL`, `MAIL_DEFAULT_SENDER`.
- `APP_BASE_URL` – used for verification links (defaults to `http://127.0.0.1:5000`).

### Database
Apply migrations (creates `db.sqlite3` by default):
```bash
flask --app run.py db upgrade
```

### Run the app
```bash
flask --app run.py run
# or
python run.py
```
Visit http://127.0.0.1:5000.

### Deploy on Railway
1. Create a Railway project from the repo.
2. (Recommended) Add a PostgreSQL plugin; Railway will provide `DATABASE_URL`.
3. Set environment variables: `SECRET_KEY`, `APP_BASE_URL`, and any `MAIL_*` values you need.
4. Run migrations once via Railway shell/CLI:
```bash
python -m flask --app run.py db upgrade
```

### Useful scripts
- `scripts/cache_exercises.py`, `scripts/cache_usda_json.py`, `add_custom_weights.py` – helpers for populating exercise/nutrition data.

### Notes
- Login supports trainer/member roles; registration requires email verification if mail is configured.
- Theme preference is stored per user/session.
