# Frontend JMD Planning

Ce module rassemble les vues React pour l&apos;exploitation des APIs projets et missions.

## Stack technique

- [Vite](https://vitejs.dev/) + React 18 + TypeScript strict.
- [pnpm](https://pnpm.io) comme gestionnaire de paquets et workspace du monorepo.
- [Tailwind CSS](https://tailwindcss.com) et [shadcn/ui](https://ui.shadcn.com) pour la charte UI.
- [TanStack Query](https://tanstack.com/query/latest) pour la synchronisation des données et les mutations optimistes.
- [Vitest](https://vitest.dev) + Testing Library pour la couverture de tests.

## Arborescence

```
src/frontend
├── src
│   ├── components       # UI atomiques (shadcn) et layout
│   ├── features         # Hooks et logique métier par domaine
│   ├── pages            # Routes applicatives (liste/detail projets, gabarits)
│   ├── providers        # Contextes (session, thème, API, React Query)
│   ├── lib              # Clients API, utilitaires
│   └── styles           # Style global Tailwind + tokens
```

## Scripts pnpm

- `pnpm dev` : serveur Vite.
- `pnpm build` : build production.
- `pnpm test` / `pnpm test -- --coverage` : tests unitaires et couverture.
- `pnpm lint` : lint TypeScript/React/Testing Library.
- `pnpm format:check` : vérification Prettier.
- `pnpm typecheck` : vérification TypeScript sans emission.

## Convention UI

- Utilisation des composants shadcn (button, card, table…) typés et composables.
- Gestion du thème clair/sombre via `ThemeProvider` et variables CSS.
- Layout principal `AppLayout` : navigation, bascule thème, conteneur 6xl.

## Tests

- Tests React avec Vitest/Testing Library (`vitest.setup.ts`).
- Couverture minimale ciblée : 70 % sur le périmètre frontend (cf. `vite.config.ts`).

## API

- Client `ApiClient` centralisé (`src/lib/api/client.ts`) qui injecte automatiquement `X-Session-Token`.
- Hooks React Query (`features/*/hooks.ts`) avec mutations optimistes sur les projets.

## Accessibilité

- Utilisation de labels explicites, messages d&apos;état et rôles ARIA sur les alertes/chargements.
- Navigation clavier assurée (boutons, selects, formulaires).
