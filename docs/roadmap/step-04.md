# STEP 04 - Harmoniser les fichiers agents et roadmap

## SUMMARY
- Renommage des fichiers agents et roadmap pour eliminer les doublons et clarifier les roles.
- Ajout d'un script PowerShell pour automatiser les renommages et la mise a jour des liens.

## GOALS
- Standardiser les noms de fichiers agents et roadmap.
- Assurer la presence des en-tetes SUT dans chaque agent specialise.
- Garantir que les guards restent fonctionnels apres renommage.

## CHANGES
- Script `tools/rename_repo.ps1` pour git mv, mise a jour des liens Markdown et verification des SUT.
- Renommage des fichiers AGENT et README selon le mapping fourni.
- Ajustements des scripts de guard et de la spec fonctionnelle pour utiliser les nouveaux chemins.

## TESTS
- `pwsh ./tools/guards/run_all_guards.ps1`

## CI
- Workflow `guards.yml` doit rester vert (execution des guards PowerShell).

## ARCHIVE
- Aucun artefact a archiver pour cette etape.

VALIDATE? yes/no
