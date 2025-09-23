# Runbooks SRE - Observabilite JMD

## Objectifs SLO
- **Disponibilite API (uptime)**: 99.5 % mensuel. Breche si > 3,6 h d'indisponibilite cumul.
- **RPO**: 24 h sur les journaux audit/analytics. Toute perte >24 h declenche incident majeur.
- **RTO**: 4 h pour restaurer les API critiques planning/notifications/audit apres incident.

## Alerte "api.5xx"
- **Declencheur**: augmentation de `api_request_errors_total` (HTTP 5xx) sur une route.
- **Canaux**: email NOC, Slack `#sre-alerts`, PagerDuty niveau SEV2.
- **Triage**:
  1. Ouvrir Grafana tableau "API Core" (latence & erreurs).
  2. Filtrer par `path` et consulter traces correlees via ID `X-Trace-Id`.
  3. Inspecter derniers deploys/feature flags.
- **Mitigation**:
  - Rollback dernier deploiement si regression applicative (<15 min).
  - Activer circuit breaker connecteurs externes si saturation (via console ops).
  - Purger jobs en erreur et relancer file si queue saturee.
- **Escalade**: si >15 min sans resolution, contacter Tech Lead + On-call Backend. Monter SEV1 si SLA menace.
- **Validation RTO**: plan de reprise doit remettre API en service <4 h.

## Alerte "api.latency"
- **Declencheur**: `api_request_duration_seconds` p95 > 200 ms.
- **Canaux**: Slack `#sre-alerts` (warning), email equipe backend.
- **Triage**:
  1. Verifier dashboards latence par route / dependance.
  2. Consulter traces OTel pour identifier segments lents (requetes SQL, connecteurs).
  3. Verifier file d'attente notifications/calendrier.
- **Mitigation**:
  - Activer mode degrade (desactivation exports lourds) via feature flag.
  - Purger caches applicatifs si suspicion derive (commandes `flush-cache`).
  - Ajuster pool SQLAlchemy (`BACKEND_SQLALCHEMY_ECHO` off, pool_size+5) temporairement.
- **Escalade**: prevenir DevOps si cause infra (CPU >80 %, DB saturee). Post-mortem si depassement SLA >1 h.

## Alerte "calendar.queue"
- **Declencheur**: `calendar_sync_pending_exports` >= 1 (echecs publication ICS).
- **Canaux**: Slack `#integrations`, email support ops.
- **Triage**:
  1. Consulter `X-Calendar-Error` sur dernieres requetes.
  2. Verifier connecteurs (Google, Outlook) via observability -> connecteur failing.
  3. Controler files ICS dans storage (dossier retry).
- **Mitigation**:
  - Relancer connecteur fautif (`tools/retry_calendar_export.py`).
  - Bascule vers connecteur secondaire (configuration `BACKEND_CALENDAR_CONNECTORS`).
  - Informer clients impactes si RTO estime >1 h.
- **Escalade**: si >30 min d'echec continu, solliciter equipe Integrations + support client.

## Alerte "audit.job.failure"
- **Declencheur**: `retention_job_failures_total` incremente (job purge/archivage en erreur).
- **Canaux**: PagerDuty SEV2, email data compliance.
- **Triage**:
  1. Verifier journaux job (`audit_retention_events`, span `audit.retention.job`).
  2. Controler acces stockage archive (S3/SharePoint).
  3. Inspecter signature HMAC (cles expirees ?).
- **Mitigation**:
  - Relancer job manuellement (`POST /api/v1/audit/organizations/{org}/retention/run`).
  - Forcer archivage vers bucket fallback si stockage principal HS.
  - Mettre en pause purge automatique si integrity check echoue.
- **Escalade**: notifier DPO si retard >24 h (RPO). Rediger rapport incident.

## Post-Incident
- Mettre a jour roadmap `docs/roadmap/step-13.md` section RESULTATS.
- Completer post-mortem (template `docs/compliance/postmortem.md`).
- Mettre a jour budgets SLO/SLA si evolution scope.
