# STEP 07 - Persistence SQLAlchemy du planning

## SUMMARY
Introduire une couche de persistence relationnelle pour les artistes et plannings afin de conserver les donnees au-dela de la requete FastAPI.

## GOALS
- Ajouter SQLAlchemy 2.x et Alembic au projet backend pour gerer les schemas et migrations.
- Definir des models persistants (artistes, disponibilites, plannings, affectations) alignes avec les schemas Pydantic existants.
- Mettre en place un module `backend.db` pour l'initialisation de l'engine, la gestion de session et la configuration via variables d'environnement.
- Adapter le service de domaine `create_planning` pour enregistrer le planning genere et permettre sa consultation ulterieure.
- Exposer de nouveaux endpoints REST pour lister les plannings enregistres et consulter un planning par identifiant.

## CHANGES
- Mise a jour de `pyproject.toml` pour inclure SQLAlchemy, Alembic et les dependances utilitaires (typing-extensions, sqlalchemy-utils si necessaire).
- Creation d'un repertoire `src/backend/db/` contenant l'engine, la session et les utilitaires de migrations.
- Ajout d'un module `src/backend/models/` avec les entites persistantes et leurs relations.
- Evolution de `src/backend/main.py` et des routes pour orchestrer la persistence et exposer les nouveaux endpoints.
- Extension de la batterie de tests avec une base SQLite en memoire, y compris des tests d'integration pour les nouveaux endpoints.
- Mise a jour de la documentation (README, AGENT backend) et du changelog lors de la validation.

## TESTS
- Execution de `pytest` sur une base SQLite en memoire couvrant les operations de creation et de lecture des plannings.
- Verification de la generation d'un rapport de couverture et du respect du seuil de 70 %.

## CI
- Adapter le workflow `backend-tests` pour initialiser la base SQLite, executer les migrations Alembic et lancer les tests.
- Publier le rapport de couverture et s'assurer que les artefacts sont archives.

## ARCHIVE
- Mettre a jour `docs/CHANGELOG.md`, `docs/codex/last_output.json` et la roadmap une fois l'etape livree.
- Documenter les commandes d'initialisation de la base et des migrations dans le README backend.

## RESULTS
- A remplir apres livraison de l'etape.

VALIDATE? no
