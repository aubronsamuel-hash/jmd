# STEP 09 - Notifications temps reel

## CONTEXTE
Les fonctionnalites de planning, disponibilites et feuilles de route sont en place. Il faut maintenant prevenir les artistes et coordinateurs lorsqu'un evenement cle survient (affectation, rappel, modification). La spec fonctionnelle v0.1 demande la prise en charge des notifications email et Telegram pour assurer un suivi proactif.

## OBJECTIFS
- Mettre en place un module de notifications unifie permettant d'orchestrer les canaux email et Telegram.
- Exposer des jobs ou webhooks qui reagissent aux evenements de planning (affectation, modification, rappel J-1).
- Fournir les gabarits de messages et les parametres de configuration (expediteur, templates, secrets API) documentes.
- Couvrir l'ensemble par des tests automatises backend validant l'envoi et la personnalisation des messages.
- Mettre a jour la documentation produit et technique (README, agents) pour decrire les flux de notifications.

## ACCEPTATION
- Une commande de service ou un endpoint permet de declencher une notification de test sur chaque canal configure.
- Les evenements cibles declenchent des notifications personnalisees avec les bonnes donnees (lieu, horaires, contact).
- Les erreurs d'envoi sont journalisees et exposees via l'observabilite existante pour faciliter le support.
- La configuration est securisee (variables d'environnement, secrets) et documentee pour les environnements.
- CI/guards executent les tests et verifient la couverture minimale sans regression.

## RESULTS
- Service `backend.notifications` compose les messages unifies et pilote les canaux email/Telegram.
- Creation de planning declenche automatiquement l'envoi et renseigne les entetes de suivi HTTP.
- Endpoints `/api/v1/notifications/test` et `/api/v1/notifications/plannings/{planning_id}/events` exposes pour tests et jobs externes.
- Tests backend (`tests/backend/test_notifications.py`) garantissent la personnalisation des messages et la presence des canaux.
- Documentation mise a jour (README, API backend, agent backend) et roadmap archivee.

VALIDATE? yes
