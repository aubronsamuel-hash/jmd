# jmd

## Documentation agents
- [AGENT hub](AGENT.md)
- [Sous-agents](docs/agents/README.md)

## Scripts guards
- `tools/guards/run_all_guards.ps1`
- `tools/guards/roadmap_guard.ps1`
- `tools/guards/docs_guard.ps1`

## Roadmap
- Etape courante: [docs/roadmap/step-09.md](docs/roadmap/step-09.md)
- Sommaire: [docs/roadmap/README.md](docs/roadmap/README.md)

## Backend FastAPI
Le backend est un service FastAPI expose sous `backend.main:app` avec un point d'entree `/api/v1`.

### Installation des dependances
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install .[dev]
```

### Lancement de l'API en developpement
```bash
uvicorn backend.main:app --reload
```

### Base de donnees et migrations
- Configuration par defaut: SQLite fichier `planning.db` (modifiable via `BACKEND_DATABASE_URL`).
- Creation automatique du schema au demarrage de l'application.
- Pour orchestrer les migrations Alembic manuellement:
  ```bash
  PYTHONPATH=src alembic -c src/backend/db/alembic.ini upgrade head
  ```
- Variable `BACKEND_SQLALCHEMY_ECHO=true` pour activer les logs SQL durant le debug.

### Endpoints REST
- `GET /api/v1/health` expose l'etat du service.
- `POST /api/v1/artists` cree un artiste et synchronise ses disponibilites.
- `GET /api/v1/artists` liste les artistes persistes tries par nom.
- `GET /api/v1/artists/{artist_id}` retourne un artiste par identifiant.
- `PUT /api/v1/artists/{artist_id}` remplace les informations et disponibilites de l'artiste.
- `DELETE /api/v1/artists/{artist_id}` supprime un artiste et ses disponibilites.
- `POST /api/v1/plannings` genere un planning a partir des artistes fournis.
- `GET /api/v1/plannings` liste les plannings persistes.
- `GET /api/v1/plannings/{planning_id}` retourne un planning par identifiant.
- `POST /api/v1/notifications/test` verifie la configuration des canaux (email, Telegram).
- `POST /api/v1/notifications/plannings/{planning_id}/events` declenche un envoi sur un evenement (`planning.assigned`, `planning.updated`, `planning.reminder`).

Des exemples de requetes et reponses JSON sont disponibles dans [docs/backend/api.md](docs/backend/api.md).

### Notifications
- Parametres environnement: `BACKEND_NOTIFICATION_EMAIL_SENDER`, `BACKEND_NOTIFICATION_EMAIL_RECIPIENTS`, `BACKEND_NOTIFICATION_TELEGRAM_BOT_TOKEN`, `BACKEND_NOTIFICATION_TELEGRAM_CHAT_IDS`.
- Les notifications planifient un message unifie formate puis distribue sur chaque canal configure.
- L'envoi est journalise et expose dans les entetes `X-Notification-Channels` ou `X-Notification-Error*` lors de la creation d'un planning.

### Tests et couverture
```bash
pytest
```
Un rapport `coverage.xml` est genere automatiquement et le seuil minimal de couverture est de 70 %.
