# STEP 02.01 - Harmoniser les guards avec les sous-etapes

## SUMMARY
- La CI `guards` echoue car les scripts actuels ne reconnaissent pas les references `step-XX.YY` imposees par la nouvelle politique roadmap.
- Les tests automatiques rejettent la ligne finale `VALIDATE? no  (SAM ONLY may flip to yes)` et les titres `STEP XX.YY`, bloquant l'avancement de STEP 02.
- Cette sous-etape cible uniquement la mise a jour des guards pour debloquer la suite de STEP 02.

## GOALS
- Supporter les references `docs/roadmap/step-XX.YY.md` dans les scripts `roadmap_guard` et `ensure_roadmap_ref`.
- Accepter les titres et lignes finales conformes aux nouvelles directives dans `docs_guard`.
- Documenter cette sous-etape et pointer la roadmap vers le fichier `step-02.01.md`.

## CHANGES
- Modifier `tools/guards/roadmap_guard.ps1` pour autoriser les sous-etapes et clarifier les messages d'erreur.
- Mettre a jour `tools/guards/ensure_roadmap_ref.ps1` afin de detecter les references `step-XX.YY` dans commits, PR et ROADMAP.
- Adapter `tools/guards/docs_guard.ps1` aux nouveaux formats de titres et de lignes `VALIDATE?`.
- Creer `docs/roadmap/step-02.01.md` et ajuster `docs/roadmap/ROADMAP.readme.md` pour refleter la sous-etape active.

## TESTS
- Execution locale de `pwsh -File tools/guards/run_all_guards.ps1`.
- Verifier que `roadmap_guard.ps1 -StepPath docs/roadmap/step-02.01.md` aboutit sans erreur.

## CI
- Workflow `guards.yml` attendu vert apres mise a jour.
- Aucun nouveau secret requis; reutilisation des environnements existants.

## ARCHIVE
- Aucune mise a jour du `CHANGELOG` ou de `docs/codex/last_output.json` tant que la sous-etape n'est pas validee.

VALIDATE? Sam yes
