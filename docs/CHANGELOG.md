# Changelog

## 2025-09-24
- Initialisation du plan STEP 01 (auth foundations) et synchronisation roadmap/codex. Ref: docs/roadmap/step-01.md

## 2025-09-25
- Livraison du socle auth backend (FastAPI, RBAC, sessions, liens magiques) avec tests Pytest a 86 % et documentation de la resolution des erreurs de persistance/UTC. Ref: docs/roadmap/step-01.md

## 2025-09-26
- Livraison du domaine backend projets/missions (models SQLAlchemy, APIs FastAPI, RBAC et tests Pytest 79.74 %) couvrant venues, tags et gabarits reutilisables. Ref: docs/roadmap/step-02.md

## 2025-09-28
- Livraison du socle frontend React (pnpm workspace, Vite, Tailwind/shadcn, TanStack Query) avec pages projets et gabarits missions testees (Vitest 76 %) et documentation outillage. Ref: docs/roadmap/step-02.02.md

## 2025-09-27
- Renforcement des tests Pytest sur les lieux (CRUD, conflits, permissions) via `tests/backend/test_venues.py` pour consolider STEP 02. Ref: docs/roadmap/step-02.md
- Ouverture de la sous-etape frontend projets/missions [STEP 02.02](./roadmap/step-02.02.md) afin de planifier la livraison UI et la toolchain React. Ref: docs/roadmap/step-02.02.md
