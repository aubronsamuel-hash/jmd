# STEP 02.02 - Interfaces frontend projets et missions

## SUMMARY
- Sous-etape consacree a la creation du socle frontend React pour exploiter les APIs projets/missions livrées en STEP 02.
- Livraison ciblee des vues liste/detail projet et du catalogue de gabarits de mission avec React Query et mutations optimistes.
- Mise en place de la charte UI (Tailwind + shadcn/ui) et de la chaine de qualite (Vitest, lint, format) partagee.

## GOALS
- Livrer les pages React Projet (liste + détail) et Mission Templates avec appels API robustes et gestion des états de chargement/erreur.
- Installer React Query (ou équivalent store) pour synchroniser les données projets, lieux, tags et gabarits avec support des mutations CRUD.
- Couvrir les composants, hooks et utilitaires critiques par Vitest/Testing Library et atteindre >=70 % de couverture sur le scope frontend.

## ACTIONS
- Initialiser la base frontend (`src/frontend`) avec Vite + TypeScript + Tailwind/shadcn, configurer pnpm et partager les scripts dans le monorepo.
- Définir les clients d'API et hooks React Query pour projects, venues, mission-tags et mission-templates, incluant la gestion centralisée des erreurs et des loaders.
- Construire les routes React (liste/detail projet, catalogue gabarits) avec composants accessibles (tables, formulaires, modals) et navigation coherent avec la spec.
- Ajouter la configuration eslint/prettier front, les commandes `pnpm lint`, `pnpm format:check`, `pnpm test`, et mettre en place la collecte de couverture Vitest.
- Documenter les conventions UI (arborescence, composants partages, schema de theming) dans `docs/specs` ou un README frontend dédié.

## RESULTATS
- Workspace pnpm initialise avec package frontend `@jmd/frontend`, tooling Vite + Tailwind/shadcn et scripts lint/format/test disponibles au monorepo.
- Pages React projets (liste + détail) et mission templates livrées avec hooks TanStack Query pour projects, venues, mission-tags et mission-templates.
- Couverture Vitest 76.45 % (`pnpm --filter @jmd/frontend test:coverage`) et documentation du socle (`src/frontend/README.md`).

## PROCHAINES ETAPES
- Consolider les captures UI et peaufiner les tests d'accessibilité avant les prochaines evolutions (drag & drop planning, etc.).
- Evaluer l'opportunité d'un Storybook ou d'une librairie de composants partagés pour les évolutions des steps 03+.

## TESTS
- `pnpm --filter @jmd/frontend lint`
- `pnpm --filter @jmd/frontend format:check`
- `pnpm --filter @jmd/frontend test:coverage`

## CI
- Etendre `frontend-tests.yml` pour inclure lint, build et Vitest.
- Ajuster `guards.yml` si de nouvelles règles documentaires/front sont nécessaires (captures, storybook, etc.).

## ARCHIVE
- A clore : capture(s) UI dans la documentation, mise à jour du changelog et des diagrammes lorsque les vues seront live.
- Synchroniser `docs/codex/last_output.json` et `docs/roadmap/ROADMAP.readme.md` lorsque la sous-etape sera validée.

VALIDATE? yes
