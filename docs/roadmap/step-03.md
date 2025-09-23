# STEP 03 - Functional spec baseline

## SUMMARY
Ajout de la specification fonctionnelle v0.1 et branchement des agents sur cette source unique.

## GOALS
- Publier `docs/specs/spec-fonctionnelle-v0.1.md` comme reference produit.
- Relier les documents agents a la SUT definie dans la spec.
- Etendre les guards pour verifier la presence et la qualite de la spec.

## CHANGES
- Creation de la spec fonctionnelle detaillee (roles, modules, workflows, criteres, roadmap).
- Ajout des en-tetes SUT/Source unique dans les fichiers AGENTs.
- Ajout du script `tools/docs/ensure_spec.ps1` et evolution du guard documentaire.

## TESTS
- Execution de `tools/docs/ensure_spec.ps1` via PowerShell 7 pour valider les injections.
- Lancement de `tools/guards/run_all_guards.ps1` pour controler docs et roadmap.

## CI
- Workflow `guards.yml` consommera la spec et les guards mis a jour.

## ARCHIVE
- Archiver les versions precedentes des AGENTs avant SUT si necessaire.

VALIDATE? yes/no
