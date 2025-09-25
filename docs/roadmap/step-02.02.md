# STEP 02.02 - Interfaces frontend projets et missions

## SUMMARY
- Sous-etape ouverte pour couvrir la partie UI/UX de STEP 02 en livrant les ecrans React listes/détails projet et catalogue des gabarits.
- Viser une integration avec les APIs backend existantes (projects, venues, mission-templates, mission-tags) via React Query.
- Mettre en place la charte UI (shadcn/Tailwind) et les tests Vitest correspondant.

## GOALS
- Livrer les pages React Projet (liste + detail) et Mission Templates avec appels API et gestion des etats de chargement/erreurs.
- Ajouter un store ou React Query pour synchroniser les donnees et fournir des mutations optimistes sur create/update/delete.
- Couvrir les composants et hooks critiques par Vitest/Testing Library avec seuil de couverture >=70% sur le scope frontend.

## CHANGES
- Initialiser la base frontend (`src/frontend`) avec Vite + TypeScript + Tailwind/shadcn et configurer pnpm.
- Implementer les hooks/API clients pour projects, venues, mission tags et templates avec gestion d'erreurs centralisee.
- Creer les composants UI (tables, formulaires, modals) et routage correspondant, en assurant l'accessibilite clavier.
- Ajouter suites Vitest et configurations lint/format specifiques au frontend.

## TESTS
- `pnpm install` puis `pnpm test -- --runInBand` pour la couverture frontend.
- `pnpm lint` et `pnpm format:check` pour garantir la qualite de code.
- Conserver `pytest` pour s'assurer que les APIs backend restent stables durant l'integration.

## CI
- Etendre `frontend-tests.yml` pour inclure lint, build et Vitest.
- Ajuster `guards.yml` si de nouvelles regles documentaires/front sont necessaires (captures, storybook, etc.).

## ARCHIVE
- A cloturer: capture(s) UI dans la documentation, mise a jour du changelog et des diagrammes lorsque les vues seront live.
- Synchroniser `docs/codex/last_output.json` et `docs/roadmap/ROADMAP.readme.md` lorsque la sous-etape sera validee.

VALIDATE? no  (SAM ONLY may flip to yes)
