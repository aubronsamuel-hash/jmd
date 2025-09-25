# Coverage Plan >= 80%

## Objectif
Assurer que la base de tests backend et frontend atteint une couverture globale minimale de 80 % avant la mise en production des prochaines etapes roadmap.

## Actions
- [ ] Instrumenter `pytest` avec `coverage.py` et publier le rapport HTML dans `docs/qa/`.
- [ ] Ajouter la commande `pnpm test -- --coverage` cote frontend et stocker les artefacts dans CI.
- [ ] Mettre a jour les guards CI pour echouer si la couverture descend sous 80 %.
- [ ] Documenter les cas critiques a couvrir (paie, planning, archivage) dans `tests/backend/README.md`.

## Suivi
| Sprint | Cible | Responsable | Statut |
|--------|-------|-------------|--------|
| S1     | 60 %  | QA Lead     | en cours |
| S2     | 70 %  | QA Lead     | planifie |
| S3     | 80 %  | QA Lead     | a lancer |

## VALIDATE?
- yes/no (reserve a Sam)
