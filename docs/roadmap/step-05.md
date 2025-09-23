# STEP 05 - Generalisation des guards et de pnpm

## SUMMARY
Rendre la detection de l'etape roadmap generique et assurer la configuration pnpm dans la CI pour tous les workflows Node.

## GOALS
- Detecter dynamiquement `docs/roadmap/step-XX.md` via commit, PR, variable ou entree explicite.
- Ajouter le setup pnpm mutualise a chaque workflow Node.
- Normaliser les sections des fichiers roadmap et publier un template reutilisable.
- Automatiser l'injection de la reference roadmap dans commits ou PR.

## CHANGES
- Creation de `tools/guards/ensure_roadmap_ref.ps1` avec detection multi-sources.
- Evolution des guards `roadmap_guard.ps1` et `docs_guard.ps1` pour supporter toutes les etapes.
- Mise a jour des workflows GitHub Actions (`frontend-tests`, `guards`) avec pnpm/action-setup et corepack.
- Ajout de `docs/roadmap/README.md` et du template `_template_step.md`.

## TESTS
- Execution locale de `./tools/guards/run_all_guards.ps1`.
- Verification des nouveaux scripts PowerShell en environnement local.

## CI
- `frontend-tests.yml` et `guards.yml` disposent de pnpm/action-setup@v4 (version 9) et du cache pnpm.
- Les guards CI declenchent `ensure_roadmap_ref.ps1` avant validation documentaire.

## ARCHIVE
- Template roadmap pret pour les futures etapes.
- Historisation de l'etape 04 dans `docs/roadmap/README.md`.

VALIDATE? yes
