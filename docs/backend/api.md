# Backend API

Cette page illustre les principaux flux REST exposes par le backend FastAPI.

## Base
- URL racine: `http://localhost:8000/api/v1`
- Format: JSON UTF-8
- Authentification: aucune (developpement)

## Gestion des artistes

### Creation d'un artiste
```http
POST /api/v1/artists
Content-Type: application/json

{
  "name": "Alice",
  "availabilities": [
    {"start": "2024-05-10T09:00:00", "end": "2024-05-10T10:00:00"},
    {"start": "2024-05-11T14:00:00", "end": "2024-05-11T15:00:00"}
  ]
}
```

Reponse (201 Created):
```json
{
  "id": "1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62",
  "name": "Alice",
  "availabilities": [
    {"start": "2024-05-10T09:00:00", "end": "2024-05-10T10:00:00"},
    {"start": "2024-05-11T14:00:00", "end": "2024-05-11T15:00:00"}
  ]
}
```

### Mise a jour d'un artiste
```http
PUT /api/v1/artists/1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62
Content-Type: application/json

{
  "name": "Alice Cooper",
  "availabilities": [
    {"start": "2024-05-12T10:00:00", "end": "2024-05-12T12:00:00"}
  ]
}
```

Reponse (200 OK):
```json
{
  "id": "1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62",
  "name": "Alice Cooper",
  "availabilities": [
    {"start": "2024-05-12T10:00:00", "end": "2024-05-12T12:00:00"}
  ]
}
```

### Liste des artistes
```http
GET /api/v1/artists
```

Extrait de reponse (200 OK):
```json
[
  {
    "id": "1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62",
    "name": "Alice Cooper",
    "availabilities": [
      {"start": "2024-05-12T10:00:00", "end": "2024-05-12T12:00:00"}
    ]
  },
  {
    "id": "9fd9d689-53f6-4a61-9c51-09536bbf1509",
    "name": "Bob",
    "availabilities": [
      {"start": "2024-05-10T11:00:00", "end": "2024-05-10T12:00:00"}
    ]
  }
]
```

### Suppression d'un artiste
```http
DELETE /api/v1/artists/9fd9d689-53f6-4a61-9c51-09536bbf1509
```

Reponse: 204 No Content

## Generation de planning

Les plannings reutilisent les artistes persistes. Exemple:

```http
POST /api/v1/plannings
Content-Type: application/json

{
  "event_date": "2024-05-12",
  "artists": [
    {
      "id": "1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62",
      "name": "Alice Cooper",
      "availabilities": [
        {"start": "2024-05-12T10:00:00", "end": "2024-05-12T12:00:00"}
      ]
    }
  ]
}
```

Reponse (201 Created):
```json
{
  "planning_id": "4c3a6d60-9a52-4c47-8961-cf944aacd187",
  "event_date": "2024-05-12",
  "assignments": [
    {
      "artist_id": "1b6f0f32-6ba2-4f83-9c58-3f748d6a3e62",
      "slot": {"start": "2024-05-12T10:00:00", "end": "2024-05-12T12:00:00"}
    }
  ]
}
```

  Ces exemples servent de base pour constituer des jeux de donnees de demonstration et pour alimenter les tests d'integration sur SQLite en memoire.

#### Entetes de synchronisation

Chaque creation de planning declenche la synchronisation externe et ajoute des entetes HTTP:

- `X-Notification-Channels`: canaux de notification utilises (email, telegram, ...).
- `X-Calendar-Targets`: connecteurs calendrier ayant recu le flux ICS (ex: `google,outlook`).
- `X-Storage-Targets`: connecteurs de stockage ayant archive le document (ex: `memory`).
- `X-Calendar-Error` / `X-Storage-Error`: liste des connecteurs en erreur lorsque present.

## Notifications

### Test de configuration
```http
POST /api/v1/notifications/test
```

Reponse (200 OK):
```json
{
  "event": "notifications.test",
  "subject": "Notification de test",
  "channels": ["email", "telegram"],
  "metadata": {
    "purpose": "connectivity-check"
  }
}
```

### Evenement planning
```http
POST /api/v1/notifications/plannings/{planning_id}/events
Content-Type: application/json

{
  "event": "planning.reminder"
}
```

Reponse (200 OK):
```json
{
  "event": "planning.reminder",
  "subject": "Rappel planning J-1 - 2024-05-12",
  "body": "Rappel planning J-1 - 2024-05-12\n\nPlanning: 4c3a6d60-9a52-4c47-8961-cf944aacd187\nDate: 2024-05-12\nAffectations:\n- Alice Cooper: 2024-05-12 10:00 -> 11:00",
  "channels": ["email", "telegram"],
  "metadata": {
    "planning_id": "4c3a6d60-9a52-4c47-8961-cf944aacd187",
    "event_type": "planning.reminder",
    "event_date": "2024-05-12",
    "assignment_count": 1
  }
}
```

## Integrations externes

### Calendriers (Google / Outlook)

- Flux ICS publie automatiquement via `CalendarSyncService` pour chaque planning.
- Journalisation des payloads exportes et des webhooks entrants (`CalendarWebhookReport`).
- Detection des conflits de creneaux lors de l'import ICS (chevauchements d'evenements).
- Variables d'environnement clefs:
  - `BACKEND_CALENDAR_CONNECTORS`: liste des connecteurs actifs (`google,outlook` par defaut).
  - `BACKEND_CALENDAR_NAME`: libelle du calendrier genere.
  - `BACKEND_CALENDAR_WEBHOOK_SECRET`, `BACKEND_CALENDAR_GOOGLE_WEBHOOK_TOKEN`, `BACKEND_CALENDAR_OUTLOOK_WEBHOOK_TOKEN`.

### Stockage documentaire (Google Drive, SharePoint, S3)

- Generation d'un resume texte du planning (nommage `planning-YYYY-MM-DD-<uuid>.txt`).
- Publication multi-connecteurs via `StorageGateway` (memoire par defaut, extensible).
- Metadata exposees: `planning_id`, `event_date`, `assignment_count`.
- Variables d'environnement clefs:
  - `BACKEND_STORAGE_CONNECTORS`: liste des connecteurs actifs (`memory` par defaut).
  - `BACKEND_STORAGE_BUCKET`, `BACKEND_STORAGE_GOOGLE_DRIVE_FOLDER`, `BACKEND_STORAGE_SHAREPOINT_SITE`, `BACKEND_STORAGE_SHAREPOINT_LIBRARY`, `BACKEND_STORAGE_S3_BUCKET`, `BACKEND_STORAGE_S3_REGION`.

### Fournisseur email

Les envois sont centralises via un fournisseur declare dans `BACKEND_NOTIFICATION_EMAIL_PROVIDER` (SMTP par defaut).
Les parametres `BACKEND_NOTIFICATION_EMAIL_SMTP_HOST`, `BACKEND_NOTIFICATION_EMAIL_SMTP_PORT` et `BACKEND_NOTIFICATION_EMAIL_API_KEY`
permettent d'aligner la configuration avec l'infrastructure d'envoi (SendGrid/Postmark).
