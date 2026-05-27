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
