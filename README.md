# Django Auth Template

Minimal, production-ready Django authentication template using JWT (DRF + SimpleJWT).

## Features
- Custom `User` model with `UserProfile` extension
- JWT auth with refresh + blacklist (logout)
- Registration, login, refresh, logout, forgot/reset password endpoints
- Env-driven configuration via `.env`
- Simple install script and example `.env.example`

## Quick start

A. Run the setup fileby following:
```bash
chmod +x ./install.sh
./install.sh
```

B. step by step process
1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and adjust values

```bash
cp .env.example .env
# edit .env as needed
```

3. Run installation helper (creates DB, runs migrations, collectstatic)

```bash
./install.sh
```

4. Run development server

```bash
cd Django_Auth_Template
python manage.py runserver
```

## Important commands

- Run tests:

```bash
python manage.py test
```

- Collect static (already handled by `install.sh`):

```bash
python manage.py collectstatic --noinput
```

## API endpoints

- `POST /auth/register/` — register
- `POST /auth/login/` — obtain tokens
- `POST /auth/token/refresh/` — refresh access token
- `POST /auth/logout/` — logout (blacklist refresh token)
- `POST /auth/password/forgot/` — request password reset
- `POST /auth/password/reset/` — perform password reset
- `GET /auth/me/` — get current user (auth required)

## Environment

Configure behaviour via `.env` (see `.env.example`). Notable settings:
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`
- `STATIC_ROOT` — where `collectstatic` copies files (added for production)

## Contributing
Open issues or PRs; keep changes small and test new behavior.

## License
MIT
# Django Auth Template

Template Django REST pour une base d'authentification JWT avec utilisateur personnalisé.

## Configuration

Copie `.env.example` vers `.env` et ajuste les valeurs selon ton environnement.

## Fonctions

- utilisateur custom avec email unique
- inscription et connexion par email
- endpoint `me` protégé par JWT
- logout avec blacklist du refresh token
- mot de passe oublié et reset via token sécurisé
- profil utilisateur séparé
- endpoint de healthcheck pour valider le déploiement

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `GET /api/auth/me/`
- `POST /api/auth/logout/`
- `POST /api/auth/password/forgot/`
- `POST /api/auth/password/reset/`
- `POST /api/auth/refresh/`
- `POST /api/auth/token/refresh/`
- `GET /api/health/`
