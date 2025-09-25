# Step-05.01 Frontend CI hardening

## Summary
- Stabiliser la pipeline frontend avec Node.js 20 et pnpm caches sur GitHub Actions.
- Garantir l'execution headless de Vitest avec rapport de couverture publie en artefact.
- Etendre les guards Codex pour surveiller `.codex/latest/last_output.json` et renforcer le controle roadmap.

## Changes
- Refonte de `.github/workflows/frontend-tests.yml` en deux jobs (`setup`, `lint_build_test`) avec pnpm/action-setup@v4 et cache pnpm dans actions/setup-node@v4.
- Simplification de `.github/workflows/guards.yml` pour reutiliser pnpm et Node 20 puis lancer les guards PowerShell avec `GH_TOKEN` explicite.
- Ajout de `test:ci` et harmonisation des scripts lint/build dans `package.json` racine et `src/frontend/package.json`.
- Inclusion de `tsconfig.node.json` dans ESLint et ajout de `vitest.setup.ts` au `tsconfig.test.json` pour eviter les erreurs de lint typed.
- Verification stricte de `.codex/latest/last_output.json` dans `tools/guards/archive_guard.ps1` et rapport `docs/codex/CI_FRONTEND_STATUS.md` documentant la sante CI.

## Tests
- `pnpm run lint`
- `pnpm run build`
- `pnpm run test:ci`
- (Tentative) `pwsh -File tools/guards/run_all_guards.ps1` (echoue localement faute de PowerShell 7, pris en charge par la CI GitHub).

## VALIDATE?
- yes/no (reserve a Sam)
