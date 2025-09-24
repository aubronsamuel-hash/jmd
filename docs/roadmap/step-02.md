# STEP 02 - Projects and missions foundations

## CONTEXT

* Roadmap step aligned with spec modules 3.2 (Projects) and 3.3 (Missions reutilisables) to enable WF-01 end-to-end planning.
* Auth and RBAC baseline from step 01 is available, enabling scoped project ownership and role-based permissions.
* Early delivery unlocks shared entities for planning, availability, and future payroll workflows defined in sections 3.4, 3.6, and 3.7.

## OBJECTIVES

* Implement backend domain for projects and reusable missions with persistence, validation, and RBAC-ready APIs.
* Provide frontend management screens to create and maintain projects, associate venues, and catalogue mission templates.
* Ensure workflows and data models satisfy WF-01 acceptance criteria on project setup and mission reuse.

## CHANGES

* Backend: SQLAlchemy models, Pydantic schemas, CRUD services, and FastAPI routers for Project, Venue linkage, Mission templates, and tags; Alembic migrations with constraints matching spec section 2.
* Backend: RBAC policies covering project/mission scopes, unit and integration tests targeting >=70% coverage for the new domain, seed fixtures for WF-01 scenarios.
* Frontend: React views for project list/detail and mission catalogue with forms, validation, and optimistic updates; shared components for venue selection and tag filters.
* Frontend: State management (query/mutations) for project/mission APIs, Vitest suites covering form logic and mission tagging.
* Docs & tooling: Update architecture diagrams, entity relationships, and usage guides; extend guards or scripts if needed to enforce schema/spec alignment.

## TESTS

* Local: `pytest` (backend domain tests), `pnpm test --filter frontend` (mission/project UI), `tools/guards/run_all_guards.ps1`.
* CI: Ensure `backend-tests.yml`, `frontend-tests.yml`, and `guards.yml` run successfully with coverage >=70% on backend domain modules touched.

## CI

* Reuse existing workflows; verify Alembic migrations execute in CI and seed data available for integration suites.
* Monitor caches for pnpm and pip; no new secrets expected beyond existing database/SMTP placeholders.

## ARCHIVE

* After validation: update `docs/CHANGELOG.md`, `docs/codex/last_output.json`, and `docs/roadmap/ROADMAP.readme.md` history section.

VALIDATE? no
