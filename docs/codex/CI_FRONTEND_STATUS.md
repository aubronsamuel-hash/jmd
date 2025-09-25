# CI Frontend Status

## Runtime
- Node.js 20.x configured via `actions/setup-node@v4`.
- pnpm 8.15.0 installed with `pnpm/action-setup@v4`.
- Cache strategy: `actions/setup-node@v4` with `cache: pnpm` and dependency path `pnpm-lock.yaml`.

## Local verification (2025-09-25)
| Check | Command | Result |
| --- | --- | --- |
| Install | `pnpm install --frozen-lockfile` | 2.676s (cache hit, workspace already up to date) |
| Lint | `pnpm run lint` | PASS |
| Build | `pnpm run build` | PASS |
| Tests | `pnpm run test:ci` | PASS - Vitest run with V8 coverage written under `src/frontend/coverage/` |
| Guards | `pwsh -File tools/guards/run_all_guards.ps1` | WARN - PowerShell 7 unavailable locally (installation blocked by missing libicu packages); workflow uses `pwsh` on GitHub-hosted runners |

## Notes
- `docs/roadmap/step-05.01.md` capture la sous-etape de durcissement CI.
- `.github/workflows/frontend-tests.yml` publie `frontend-coverage` si des rapports sont produits.
- `.codex/latest/last_output.json` est maintenant valide JSON et surveille par `archive_guard.ps1`.
