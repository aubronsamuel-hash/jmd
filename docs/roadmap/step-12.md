# STEP 12 - Audit et conformite

## CONTEXTE
Les tableaux de bord analytics sont en place et exposes aux equipes. Nous devons
apporter les garanties de tracabilite et de conformite demandees dans la spec
fonctionnelle afin de securiser l exploitation des donnees sensibles.

## OBJECTIFS
- Mettre en place un journal d audit centralise pour les evenements critiques
  (creation, modification, export, droits) sur l ensemble des modules.
- Encadrer la retention des traces, leur archivage et les politiques de purge en
  accord avec les exigences RGPD.
- Offrir des exports JSON et CSV filtres par periode, utilisateur ou module pour
  soutenir les controles internes et externes.
- Industrialiser les procedures de droit d acces, suppression et anonymisation
  des donnees personnelles.

## ACTIONS
- Ajouter un service `AuditTrailService` cote backend avec stockage immuable,
  versionnage des payloads et signature des evenements.
- Propager des hooks d audit dans les modules planning, paie, materiel,
  notifications et integrations pour journaliser les actions sensibles et les
  reponses externes.
- Mettre en place des jobs de retention configurables par organisation afin de
  purger, archiver et tracer les demandes RGPD (acces, rectification,
  effacement) dans un registre dedie.
- Documenter les exigences de conformite (roles, retention, chiffrement au
  repos, sauvegardes) et mettre a jour les guards pour verifier la presence du
  registre d audit.

## RESULTATS
- Journal des actions accessible via API `/api/v1/audit/logs` avec filtres sur
  la periode, le module et l utilisateur, plus export JSON/CSV horodate.
- Workflow RGPD formalise (demande, traitement, confirmation) avec traces et SLA
  documentes pour chaque type de requete.
- Plans de retention parametres par organisation et executes automatiquement
  avec notifications aux administrateurs.
- Documentation et guards valides prouvant la prise en compte des obligations
  legales et des besoins de tracabilite.

## ACCEPTATION
- Toute action critique (CRUD donnees sensibles, export, configuration) est
  journalisee avec horodatage, auteur, contexte et hash d integrite.
- Les exports JSON/CSV sont accessibles aux roles autorises et filtrables par
  periode, module et utilisateur.
- Les demandes RGPD (acces, rectification, effacement) sont tracees, executees
  et confirmees dans les delais contractuels.
- Les politiques de retention et d archivage sont configurables, documentees et
  testees en CI (jobs de purge, alertes de quotas).

VALIDATE? no
