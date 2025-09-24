# STEP 02 - Projects and missions foundations

## SUMMARY
- Roadmap step alignee avec les modules 3.2 (Projects) et 3.3 (Missions reutilisables) de la spec pour couvrir WF-01 bout-en-bout.
- Le socle Auth et RBAC de STEP 01 est disponible et permet de borner la propriete des projets et les permissions basees sur les roles.
- La livraison anticipee debloque les entites partagees des sections 3.4, 3.6 et 3.7 (planning, disponibilites, paie) pour les iterations suivantes.

## GOALS
- Implementer le domaine backend pour projets et missions reutilisables avec persistence, validation et APIs compatibles RBAC.
- Fournir des interfaces frontend pour creer et maintenir les projets, associer les lieux et cataloguer les gabarits de mission.
- Garantir que workflows et modeles de donnees satisfont les criteres d'acceptation WF-01 sur la mise en place des projets et missions reutilisables.

## CHANGES
- Backend : SQLAlchemy models, schemas Pydantic, services CRUD et routes FastAPI pour Project, lien Venue, templates de mission et tags; migrations Alembic et contraintes spec section 2.
- Backend : politiques RBAC couvrant les scopes projet/mission, tests unitaires et d'integration avec >=70 % de couverture pour le nouveau domaine, jeux de donnees WF-01.
- Frontend : vues React pour la liste/detail projet et le catalogue de missions avec formulaires, validations et mises a jour optimistes; composants partages pour selection de lieu et filtres de tags.
- Frontend : gestion d'etat (requete/mutations) pour les APIs projet/mission, suites Vitest couvrant la logique des formulaires et du tagging de mission.
- Docs & tooling : mettre a jour les diagrammes d'architecture, relations d'entites et guides d'usage; etendre guards/scripts si necessaire pour imposer l'alignement schema/spec.

## TESTS
- Local : `pytest` (domaines backend), `pnpm test --filter frontend` (UI missions/projets), `tools/guards/run_all_guards.ps1`.
- CI : assurer l'execution reussie de `backend-tests.yml`, `frontend-tests.yml` et `guards.yml` avec couverture >=70 % sur le domaine backend touche.

## CI
- Reutiliser les workflows existants; verifier qu'Alembic s'execute en CI et que les donnees seeds sont disponibles pour les suites d'integration.
- Surveiller les caches pnpm/pip; aucun nouveau secret attendu au-dela des placeholders base de donnees/SMTP.

## ARCHIVE
- Apres validation : mettre a jour `docs/CHANGELOG.md`, `docs/codex/last_output.json` et la section historique de `docs/roadmap/ROADMAP.readme.md`.

VALIDATE? no  (SAM ONLY may flip to yes)
