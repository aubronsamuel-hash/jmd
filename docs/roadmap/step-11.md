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

## ACCEPTATION
- Jeux de donnees analytics mis a jour automatiquement (delta < 15 min) avec pistes de controle pour heures, missions, paie et materiel.
- Tableaux de bord backend/frontend exposes avec filtres multi-dimension et KPIs conformes (taux couverture, heures prevues vs realisees,
  masse salariale, cout horaire moyen, incidents materiel, heatmaps charge).
- Export PNG/PDF/CSV disponible pour chaque vue avec horodatage, metadonnees projet et signature utilisateur.
- Documentation technique precisant architecture, jobs, retention et gouvernance des donnees sensibles.

VALIDATE? no
