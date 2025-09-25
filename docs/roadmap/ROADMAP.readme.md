# Roadmap

## SUMMARY
- Iteration active : [STEP 02](./step-02.md) livre le domaine backend projets/missions (RBAC, CRUD, tests) et prepare les travaux frontend.
- Sous-etape en cours : [STEP 02.02](./step-02.02.md) organise la livraison des vues React projets/missions et la toolchain frontend.
- Jalons a suivre : completion frontend/UX missions-projets et mise a jour documentaire/guards pour STEP 02.
- Historique : [STEP 02.01](./step-02.01.md) a aligne les guards CI sur le format roadmap; [STEP 01](./step-01.md) a livre le socle auth multi-organisation et le RBAC initial.

## GOALS
- Assurer la synchronisation entre roadmap, specification fonctionnelle et scripts de verification.
- Donner une vue d'ensemble rapide des etapes actives et completes pour coordonner backend, frontend et devops.

## CHANGES
- Utiliser le gabarit commun (SUMMARY, GOALS, CHANGES, TESTS, CI, ARCHIVE) sur chaque fichier de roadmap, y compris `step-02.01.md` et `step-02.md`.
- Maintenir des liens explicites vers `./step-02.01.md`, `./step-02.md` et `./step-01.md` pour suivre l'avancement.

## TESTS
- Executer `pwsh -File tools/guards/run_all_guards.ps1` avant commit pour verifier roadmap et documentation.
- Surveiller `backend-tests.yml` et `frontend-tests.yml` pour valider les impacts techniques de chaque etape.

## CI
- Le workflow `guards.yml` doit rester vert pour chaque mise a jour de roadmap.
- Les workflows `backend-tests.yml` et `frontend-tests.yml` couvrent respectivement les evolutions API et UI liees a STEP 02.

## ARCHIVE
- Deplacer les etapes finalisees dans la section historique tout en conservant leurs liens (`./step-01.md`).
- Documenter la validation de chaque sous-etape directement dans le fichier correspondant (`./step-02.01.md`, `./step-02.md`).
