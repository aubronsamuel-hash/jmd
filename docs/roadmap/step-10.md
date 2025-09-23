# STEP 10 - Integrations externes calendrier et stockage

## CONTEXTE
Les modules planning, disponibilites et notifications sont prets. Il faut maintenant relier la plateforme aux services externes references dans la spec fonctionnelle (calendriers, stockage et email) pour fluidifier les workflows des equipes et garantir la synchronisation documentaire.

## OBJECTIF
Aligner les connecteurs externes avec la spec fonctionnelle afin que les evenements et documents circulent entre le SaaS et les outils clients.

## OBJECTIFS
- Synchroniser les calendriers Google et Outlook via ICS et webhooks de mise a jour.
- Rendre disponible une passerelle de stockage (Google Drive, SharePoint, S3) pour les feuilles de route et documents projet.
- Normaliser l'envoi email via un fournisseur dedie (SMTP ou SendGrid/Postmark) partage avec le module notifications.
- Documenter la configuration et les limites (quotas, reauthentification, gestion des erreurs) pour chaque integration.

## ACTIONS
- Implementer des services d'integration `calendar` et `storage` relies aux modules planning et documents.
- Ajouter des jobs/asynctasks pour importer et diffuser les evenements ICS, avec detection des conflits et journalisation.
- Configurer les connecteurs de stockage pour publier les feuilles de route PDF et assets lies aux missions.
- Exposer les parametres d'environnement requis (secrets OAuth, buckets, endpoints SMTP) et les inclure dans la documentation technique.
- Etendre les tests d'integration pour couvrir les flux ICS et le depot de documents.

## RESULTATS
- Les evenements planifies se synchronisent vers Google/Outlook et peuvent etre mis a jour depuis les retours ICS.
- Les documents generes sont deposees sur l'espace de stockage choisi avec suivi des versions.
- Les emails emis via le module notifications utilisent le fournisseur commun et remontent les statuts d'envoi.
- La documentation detaille les procedures de configuration et de monitoring des connecteurs.

## PROCHAINES ETAPES
- Ouvrir les integrations SMS/Telegram restantes si necessaire.
- Poursuivre avec les analytics et tableaux de bord (module suivant de la spec) une fois les connecteurs stabilises.

## ACCEPTATION
- Import/export ICS operationnel pour Google et Outlook, avec synchronisation bi-directionnelle documentee.
- Depot automatique des feuilles de route et documents projets sur le stockage selectionne, avec verification et journal.
- Emails routes via le fournisseur configure et suivis dans les logs existants.
- Secrets et parametres de chaque integration centralises et proteges (env, vault) avec instructions de rotation.
- Tests d'integration couvrant les flux ICS et stockage executes en CI sans regression de couverture.

VALIDATE? no
