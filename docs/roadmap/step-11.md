# STEP 11 - Analytics et tableaux de bord

## CONTEXTE
Les connecteurs externes sont operationnels et synchronisent les plannings, documents et notifications. Il faut maintenant exploiter
ces flux de donnees pour fournir la visibilite attendue dans la spec fonctionnelle sur les KPI planning, paie et logistique, tout
en preparant les exports et visualisations prevus.

## OBJECTIFS
- Structurer un entrepot analytique (modeles heures, missions, paie, materiel) alimente par les evenements et validations existants.
- Produire des tableaux de bord pour les KPIs planning, paie et logistique avec filtres par projet, lieu, periode et equipe.
- Generer des visualisations avancees (heatmaps de charge, courbes comparatives) et permettre exports PNG/PDF/CSV conformes a la spec.
- Documenter les besoins d'infrastructure (scheduler ETL, stockage metriques, quotas) et lister les donnees sensibles a proteger.

## ACTIONS
- Ajout de l'entrepot analytics `analytics_mission_events`, `analytics_payroll_records` et `analytics_equipment_incidents` (SQLAlchemy + migrations metadata).
- Creation du service domaine `backend.domain.analytics` (agrégation KPIs, heatmap, comparaisons, controles de latence) et exposition FastAPI `/api/v1/analytics/dashboard` & `/api/v1/analytics/exports`.
- Generation d'exports CSV/PDF/PNG horodatés et signes (base64 + SHA-256) avec metadonnees projet/filtre, heatmap et courbes.
- Extension des tests backend (pytest) pour couvrir agrégation des donnees, filtres multi-dimension, controles de latence (< 15 min) et exports multi-formats.
- Documentation roadmap/changelog/codex mise a jour (architecture ETL, besoins scheduler + retention, donnees sensibles).

## RESULTATS
- KPIs planning/paie/logistique exposes via `/api/v1/analytics/dashboard` (coverage rate, heures planifiees/reelles, masse salariale, incidents materiel, heatmap horaire, comparatifs journaliers).
- Export `/api/v1/analytics/exports` disponible en CSV/PDF/PNG avec metadonnees horodatage, signature et compatibilite connectors (stockage documentaire existant).
- Entrepot analytics alimente par les evenements mission/paie/materiel avec latence controlee (< 10 min sur le scope de tests) et consolidation par projet/lieu/equipe.
- Notes d'infrastructure precisees (scheduler ETL 15 min, stockage metriques dedie, classification donnees sensibles RH/logistique).

## PROCHAINES ETAPES
- Brancher les connecteurs temps reel (webhooks planning/paye/logistique) sur l'entrepot et historiser les deltas.
- Outiller la generation automatique de rapports (planification exports, diffusion storage gateway) et le suivi quotas/archivage.
- Etendre la couverture frontend (tableaux, filtres, heatmap interactive) en coordination avec le module React/Vite.

## ACCEPTATION
- Jeux de donnees analytics mis a jour automatiquement (delta < 15 min) avec pistes de controle pour heures, missions, paie et materiel.
- Tableaux de bord backend/frontend exposes avec filtres multi-dimension et KPIs conformes (taux couverture, heures prevues vs realisees, masse salariale, cout horaire moyen, incidents materiel, heatmaps charge).
- Export PNG/PDF/CSV disponible pour chaque vue avec horodatage, metadonnees projet et signature utilisateur.
- Documentation technique precisant architecture, jobs, retention et gouvernance des donnees sensibles.

VALIDATE? yes
