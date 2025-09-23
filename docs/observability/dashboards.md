# Tableaux de bord observabilite

## API Core
- **Latence p50/p95/p99** via `api_request_duration_seconds` par route et methode.
- **Taux erreurs** via `api_request_total` & `api_request_errors_total` (stacked area).
- **Trace recentre**: lien direct Grafana Tempo utilisant `X-Trace-Id`.
- **Heatmap horaires** pour volumes requetes.

## Integrations Calendrier
- **Exports reussis**: `calendar_sync_exports_total` par connecteur (bar).
- **Delai sync**: `calendar_sync_delay_seconds` p95.
- **Backlog/pending**: gauge `calendar_sync_pending_exports` (alerte queue).
- **Logs correlates**: filtre sur span `calendar.connector.publish`.

## Notifications & Jobs
- **Notifications dispatch**: historique `notification_service.history` via log JSON (info seulement).
- **Jobs retention**: `retention_job_duration_seconds` (line), `retention_job_archived_records` & `retention_job_purged_records` (bars).
- **Failures**: `retention_job_failures_total` (counter) avec annotation PagerDuty.

## Conformite & RGPD
- **RGPD SLA**: difference `due_at` vs `completed_at` (Grafana transformation custom).
- **Backlog requetes**: nombre de demandes `RgpdRequestRecord` status `pending` via requete SQL (panel texte).

## Alerting
- Panel synthese listant dernier evenement par `alerting.history` (table PromQL) avec canal (email/slack/pagerduty).
- Lien runbooks: [docs/observability/runbooks.md](./runbooks.md).
