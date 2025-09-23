# STEP 12 - Audit et conformite

## CONTEXTE
Les tableaux de bord analytics sont en place et exposes aux equipes. Nous devons
apporter les garanties de tracabilite et de conformite demandees dans la spec
fonctionnelle afin de securiser l exploitation des donnees sensibles.

## OBJECTIFS
- Mettre en place un journal d audit centralise pour les evenements critiques
  (creation, modification, export, droits) sur l ensemble des modules.
- Encadrer la retention des traces, leur archivage et les politiques de purge en
  accord avec les exigences RGPD.
- Offrir des exports JSON et CSV filtres par periode, utilisateur ou module pour
  soutenir les controles internes et externes.
- Industrialiser les procedures de droit d acces, suppression et anonymisation
  des donnees personnelles.

## ACTIONS
- Introduit `backend.domain.audit` avec `AuditTrailService`, enums et schemas
  Pydantic (journal immuable signe, exports JSON/CSV, registres RGPD).
- Etendu `backend.main` pour tracer artistes/plannings/notifications, exposer
  les routes `/api/v1/audit/*` et `/api/v1/rgpd/*`, instancier le service avec
  la configuration.
- Ajoute les modeles SQLAlchemy (`audit_logs`, `audit_retention_*`,
  `rgpd_requests`) et migration `20241002_03_audit_trail`.
- Rendu la retention parametrable + jobs de purge/archivage, workflow RGPD avec
  historique et signature HMAC.
- Nouvelle doc `docs/compliance/audit-register.md`, guard mis a jour, roadmap
  et changelog synchronises.

## RESULTATS
- `/api/v1/audit/logs` filtre par organisation/module/utilisateur/date et exporte
  en JSON ou CSV signe (payload Base64 + digest HMAC).
- `AuditTrailService` journalise artistes, plannings, notifications, stockage,
  RGPD; les tests `tests/backend/test_audit.py` couvrent creation, export,
  workflow RGPD et retention.
- `/api/v1/audit/organizations/{org}/retention` configure, journalise et lance
  les jobs de purge/archivage; `audit_retention_events` suit les executions.
- `/api/v1/rgpd/requests` gere creation/completion avec historique dedie et SLA
  automatique, chaque transition alimente le registre.
- `docs/compliance/audit-register.md` centralise les exigences et le guard
  PowerShell verifie sa presence.

## ACCEPTATION
- Toute action critique (CRUD donnees sensibles, export, configuration) est
  journalisee avec horodatage, auteur, contexte et hash d integrite.
- Les exports JSON/CSV sont accessibles aux roles autorises et filtrables par
  periode, module et utilisateur.
- Les demandes RGPD (acces, rectification, effacement) sont tracees, executees
  et confirmees dans les delais contractuels.
- Les politiques de retention et d archivage sont configurables, documentees et
  testees en CI (jobs de purge, alertes de quotas).

VALIDATE? yes
