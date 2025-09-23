SUT: docs/specs/spec-fonctionnelle-v0.1.md
Tous les documents generes doivent rester alignes avec la spec.

# AGENT docs

## Objectifs
- Maintenir une documentation a jour, coherente et navigable.
- Synchroniser les mises a jour des READMEs, AGENTs et roadmap.
- Assurer la presence d'un changelog et d'un journal d'execution minimal.

## Architecture documentaire
- `AGENT.md` hub principal, relie l'ensemble des sous-agents.
- `docs/agents/` detaille les roles specifiques (backend, frontend, devops, docs).
- `docs/roadmap/` trace les iterations numerotees (`step-XX.md`).
- `docs/CHANGELOG.md` consigne les livraisons.
- `docs/codex/last_output.json` conserve le plan et l'etat d'execution.

## Regles de liens et sommaires
- Utiliser des liens relatifs exclusivement.
- Fournir un sommaire minimal dans chaque dossier de documentation.
- Mettre a jour `docs/agents/README.md` a chaque ajout de sous-agent.
- Verifier que la roadmap reference les livraisons et contient `VALIDATE?`.

## Docs guard
- `tools/guards/docs_guard.ps1` verifie la presence de sommaires et de liens valides.
- Tout echec doit etre corrige avant merge et documente dans la roadmap.

## Mise a jour roadmap
- Chaque iteration doit completer `docs/roadmap/step-XX.md` avec sections Objectif, Actions, Resultats, Prochaines etapes.
- Ajouter ou mettre a jour le bloc final `VALIDATE? yes/no`.

## Changelog et journal
- Append-only sur `docs/CHANGELOG.md` avec date ISO, resume, reference roadmap.
- `docs/codex/last_output.json` doit etre actualise a chaque execution.

## Checklist revue docs
- [ ] AGENT.md et sous-agents synchronises et lies.
- [ ] Roadmap et changelog mis a jour.
- [ ] Sommaires `docs/*` a jour.
- [ ] Guards documentaires passent.
- [ ] Reference roadmap presente dans commits/PR.

