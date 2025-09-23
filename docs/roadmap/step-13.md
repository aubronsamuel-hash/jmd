# STEP 13 - Observabilite et alerting

## CONTEXTE
Les modules audit et conformite sont en production. Pour aligner la plateforme avec les exigences NFR de la spec fonctionnelle v0.1, nous devons maintenant instrumenter l ensemble du SaaS afin de detecter rapidement les erreurs (5xx), surveiller la latence des flux planning/paie/materiel et piloter les jobs recurrents.

## OBJECTIFS
- Instrumenter les services backend, jobs ETL et connecteurs avec des traces correlees (ex. OpenTelemetry) et des logs structures conservant les identifiants RGPD/audit requis.
- Exposer des metriques normalisees (latence API, erreurs 5xx, delai sync ICS, jobs paie/materiel) via un endpoint Prometheus et livrer des tableaux de bord pre-configures.
- Mettre en place des alertes temps reel (PagerDuty/Slack/email) couvrant erreurs 5xx, saturation des files, derives de latence (>200 ms) et echecs de jobs critiques.
- Documenter les runbooks SRE (triage, escalade, mitigation) et les budgets SLO (uptime, RPO 24h, RTO 4h) relies aux alertes et metriques.

## ACTIONS
- Ajout du module `backend.observability` (traces, metrics registry, alerting service, middleware) et exposition `/metrics` (Prometheus) depuis FastAPI.
- Instrumentation des routes HTTP, services planning, connecteurs calendrier et jobs retention audit avec spans correlables, logs structures et metriques (latence, erreurs, delais sync, executions jobs).
- Activation d alertes email/Slack/PagerDuty (`api.5xx`, `api.latency`, `calendar.queue`, `audit.job.failure`) connectees aux metriques.
- Creation de la documentation SRE (`docs/observability/runbooks.md`, `docs/observability/dashboards.md`) et mise a jour du changelog/codex.

## RESULTATS
- Les reponses HTTP embarquent `X-Trace-Id`, les spans `http.request`, `calendar.synchronize`, `audit.retention.job` sont consultables et enrichis des meta RGPD/audit.
- `/metrics` expose les compteurs/summaries (latence API, erreurs 5xx, delai ICS, jobs retention) alimentees en temps reel, valides par tests `tests/backend/test_observability.py`.
- Trois alertes critiques verifient la diffusion multi-canaux (failures 5xx, file calendrier, job retention) et declenchent les canaux definis.
- Runbooks et tableaux de bord observes centralisent triage/escalade/SLO avec liens vers Tempo/Grafana.

## ACCEPTATION
- Chaque requete API et job critique produit une trace correlee (id requete, utilisateur, organisation) consultable depuis le tableau de bord central.
- Les metriques principales (latence p95, taux erreurs, delais sync, backlog jobs) sont exposees, historisees et visualisees dans des dashboards partages.
- Au moins trois regles d alerte (erreurs 5xx, latence planning, job ETL en echec) declenchent une notification verifiable vers les canaux definis.
- Les runbooks et objectifs SLO/RPO/RTO sont documentes dans la base de connaissance et references dans la roadmap/changelog.

VALIDATE? yes
