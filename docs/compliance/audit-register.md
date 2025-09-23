# Registre d'audit et conformite

## Journalisation
- Service `AuditTrailService` instancie dans `backend.main` avec signature HMAC et organisation par defaut.
- Evenements traces pour les modules planning, artistes, notifications, integrations et RGPD.
- Empreinte calculee a partir de l'organisation, du module, du type d'evenement, de la cible et du payload versionne.
- Endpoint `GET /api/v1/audit/logs` expose les filtres `organization_id`, `module`, `actor_id`, `event_type`, `start_at`, `end_at`.

## Exports
- `GET /api/v1/audit/logs/export?format=json|csv` retourne un package `AuditExport` (base64 + signature) avec metadonnees de filtre.
- Exports CSV contiennent les colonnes clefs (`id`, `created_at`, `module`, `event_type`, `action`, `payload`, `signature`).
- Exports JSON serialisent la collection d'evenements via `AuditLogCollection`.

## Retention et archivage
- Politique configuree par organisation via `PUT /api/v1/audit/organizations/{org}/retention`.
- Jobs declenches par `POST /api/v1/audit/organizations/{org}/retention/run` archivent (marquage `archived_at`) puis purgent selon les delais.
- Execution journalisee dans `audit_retention_events` + evenement `audit.retention.executed`.

## RGPD
- Workflow de demandes (`POST /api/v1/rgpd/requests`, `POST /api/v1/rgpd/requests/{id}/complete`) avec calcul SLA automatique.
- Historique `rgpd_request_history` conserve l'ensemble des transitions avec notes.
- Chaque changement genere un evenement `rgpd.request.*` dans le registre d'audit.

## Tables
- `audit_logs`: journal immuable signe (signature SHA-256, archivable).
- `audit_retention_policies`: fenetres de retention/archivage par organisation avec contraintes de coherence.
- `audit_retention_events`: compte-rendus d'executions (purge, archivage, anonymisation).
- `rgpd_requests` et `rgpd_request_history`: registre RGPD avec statut, echeance et notes.

## Tests et gardes
- Tests backend `tests/backend/test_audit.py` couvrent journalisation, exports, workflow RGPD et job de retention.
- Guard documentaire verifie la presence de ce registre.
