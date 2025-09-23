# AGENT frontend

## Objectifs
- Concevoir une interface React accessible pour la planification des intermittents.
- Harmoniser la charte UI/UX avec Tailwind et composants shadcn.
- Maintenir une base de code TypeScript typée et testable.

## Structure UI et state management
- Architecture proposee: `/src/frontend` avec separation `components`, `features`, `pages`, `lib`.
- Utiliser React Query ou equivalent pour la synchronisation serveur (a confirmer dans roadmap).
- Centraliser les etats globaux sensibles (auth, configuration) dans un store dedie (Zustand ou Redux Toolkit selon choix).

## Conventions TypeScript
- Strict mode active dans `tsconfig.json`.
- Types explicites pour props et hooks personnalisés.
- Respecter la regle d'export par defaut uniquement pour pages, sinon exports nommes.
- Tests unitaires avec Vitest et React Testing Library.

## Accessibilite et UX
- Utiliser les composants shadcn avec attention sur les roles ARIA.
- Garantir navigation clavier et focus management.
- Ajouter tests axe ou verifications manuelles pour les composants critiques.

## Tests frontend
- Commande de reference: `pnpm test -- --runInBand` (adapter selon gestionnaire de paquets).
- Inclure tests snapshot/storybook si outils disponibles.
- Automatiser la verification lint/format (`pnpm lint`, `pnpm format:check`).

## Performance
- Surveiller le bundle via Vite analyse (`pnpm build --mode analyze`).
- Appliquer code splitting par routes/feature lorsque necessaire.

## Checklist revue frontend
- [ ] UI respecte la charte et les guidelines accessibilite.
- [ ] Types et lint passent sans erreur.
- [ ] Tests Vitest passent localement et en CI.
- [ ] Stories/Docs UI mises a jour si applicable.
- [ ] Reference roadmap presente dans commits/PR.

