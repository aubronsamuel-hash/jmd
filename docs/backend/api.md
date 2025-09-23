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
