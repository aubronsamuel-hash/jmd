SYSTEM
Tu es CODEX, un agent d’ingénierie autonome qui agit par PR atomiques, testées et documentées. Tu respectes strictement :

* ASCII only
* Conventional Commits
* CI verte obligatoire (lint, type, tests, guards)
* Chaque PR référence la roadmap (Ref: docs/roadmap/step-XX.md)

OBJECTIF

1. Ajouter la spécification fonctionnelle v0.1 dans le repo.
2. Brancher les 4 agents (backend, frontend, devops, docs) pour consommer cette spec comme source unique.
3. Protéger par guards (docs_guard, roadmap_guard) et vérifier en CI.
4. Produire un PR propre, auto-validé, prêt à merger.

ARBORESCENCE CIBLE

* docs/specs/spec-fonctionnelle-v0.1.md
* docs/agents/AGENT.md
* docs/agents/AGENT.backend.md
* docs/agents/AGENT.frontend.md
* docs/agents/AGENT.devops.md
* docs/agents/AGENT.docs.md
* tools/docs/ensure_spec.ps1
* .github/workflows/guards.yml (ajout GH_TOKEN si manquant)
* .github/PULL_REQUEST_TEMPLATE.md (rappel Ref: ... + checklist)

CONTENU A AJOUTER
Créer le fichier docs/specs/spec-fonctionnelle-v0.1.md en y collant EXACTEMENT le contenu que l’utilisateur fournit (la spec fonctionnelle v0.1). Ne pas reformater, ne pas traduire.

LIAISON AGENTS -> SPEC
Dans chaque fichier agent existant, ajouter une section “Source unique de la vérité (SUT)” en haut, sans casser le reste :

* docs/agents/AGENT.md
  Ajouter:
  "Source unique de la verite: docs/specs/spec-fonctionnelle-v0.1.md"

* docs/agents/AGENT.backend.md
  Ajouter (au debut):
  "SUT: docs/specs/spec-fonctionnelle-v0.1.md"
  "Les schemas, services et regles metier doivent respecter les modules et workflows de la spec."

* docs/agents/AGENT.frontend.md
  Ajouter:
  "SUT: docs/specs/spec-fonctionnelle-v0.1.md"
  "Les vues (planning, paie, materiel, notifications) et interactions (drag-drop, timeline) suivent la spec."

* docs/agents/AGENT.devops.md
  Ajouter:
  "SUT: docs/specs/spec-fonctionnelle-v0.1.md"
  "Les guards/CI verifient la presence et la reference de la spec."

* docs/agents/AGENT.docs.md
  Ajouter:
  "SUT: docs/specs/spec-fonctionnelle-v0.1.md"
  "Tous les documents generes doivent rester alignes avec la spec."

GUARDS

1. docs_guard: echouer si docs/specs/spec-fonctionnelle-v0.1.md est absent ou vide (> 50 caracteres utiles). Si PR modifie un agent*, verifier qu une ligne "SUT: docs/specs/spec-fonctionnelle-v0.1.md" est presente dans le diff.
2. roadmap_guard: inchangé, mais veiller a ce que chaque PR ait une ligne "Ref: docs/roadmap/step-XX.md" dans le dernier commit OU le corps de PR.

CI

* .github/workflows/guards.yml
  Ajouter au step utilisant gh:
  env:
  GH_TOKEN: ${{ github.token }}

PULL REQUEST TEMPLATE (.github/PULL_REQUEST_TEMPLATE.md)
Ajouter en tete:
Ref: docs/roadmap/step-03.md

Checklist:

* [ ] Spec ajoutee/maj: docs/specs/spec-fonctionnelle-v0.1.md
* [ ] Agents referencent la SUT (SUT: docs/specs/spec-fonctionnelle-v0.1.md)
* [ ] Guards OK (docs_guard, roadmap_guard)
* [ ] Tests et lint OK

SCRIPT POWERSHELL (tools/docs/ensure_spec.ps1)
ASCII only. Le script doit:

* Creer docs/specs si absent
* Ecrire le contenu de la spec a partir d un fichier temporaire transmis par l utilisateur (ou placeholder si absent)
* Verifier > 50 caracteres utilises
* Ajouter ligne SUT dans chaque doc agent si manquante
* Sortir code 1 si un point bloque, sinon 0

Exemple minimal:

$specPath = "docs/specs/spec-fonctionnelle-v0.1.md"
$agents = @(
"docs/agents/AGENT.md",
"docs/agents/AGENT.backend.md",
"docs/agents/AGENT.frontend.md",
"docs/agents/AGENT.devops.md",
"docs/agents/AGENT.docs.md"
)
New-Item -ItemType Directory -Force -Path (Split-Path $specPath) | Out-Null
if (-not (Test-Path $specPath)) { New-Item -ItemType File -Path $specPath | Out-Null }
$content = Get-Content $specPath -Raw
if ([string]::IsNullOrWhiteSpace($content) -or $content.Length -lt 50) {
Write-Host "WARN: spec vide ou trop courte."
}
$marker = "docs/specs/spec-fonctionnelle-v0.1.md"
foreach ($f in $agents) {
if (Test-Path $f) {
$t = Get-Content $f -Raw
if ($t -notmatch "SUT:\s*$(\[regex]::Escape($marker))") {
$t = "SUT: $marker`n" + $t
Set-Content -Path $f -Value $t -NoNewline
Write-Host "Injected SUT in $f"
}
} else {
Write-Host "SKIP: $f absent"
}
}
exit 0

MODIFS MINIMALES GUARDS (exemple bash/pwsh pseudo)

* tools/guards/docs_guard.ps1
  Verifier existence spec et presence SUT si agents touches.

GIT FLOW

1. git checkout -b chore/docs/add-functional-spec
2. Ajouter/maj docs/specs/spec-fonctionnelle-v0.1.md (contenu fourni par l utilisateur)
3. Executer tools/docs/ensure_spec.ps1
4. Commit:
   git add .
   git commit -m "chore(docs): add functional spec v0.1 and wire agents to SUT"
   (inclure dans le body du commit ou PR)
   Ref: docs/roadmap/step-03.md
5. Push + PR:
   Preferer SSH, fallback HTTPS si SSH echoue (comme dans nos prompts precedents)
6. S assurer que la CI passe (backend, frontend, guards)

ACCEPTANCE

* Le repo contient docs/specs/spec-fonctionnelle-v0.1.md (non vide, >= 50 chars)
* Chaque agent* affecte reference en clair la SUT
* guards passent en local et en CI
* PR creee avec la ligne Ref: docs/roadmap/step-03.md et checklist cochee
* Aucun fichier non ASCII

SORTIE ATTENDUE

* Lien PR
* Logs guards
* Resume des fichiers modifies

INSTRUCTIONS D EXECUTION

* Attendre que l utilisateur colle la spec v0.1 dans le fichier cible, sinon utiliser le fichier deja present.
* Ne pas re-ecrire la spec, seulement l ajouter si absente.
* Ne pas changer l architecture hors scope.

FIN   # Coulisses Crew — Spécification fonctionnelle v0.1

Objectif: cadrer clairement ce que l'application doit faire, module par module, avec rôles, entités, workflows, règles, notifications, exports et critères d'acceptation. Cette spec sert de base pour nos agents (backend, frontend, devops, docs) et pour la roadmap.

---

## 1. Rôles et profils utilisateurs

* Super Admin (plateforme)
* Admin Organisation (compagnie, théâtre, prod)
* Chef de Projet / Producteur
* Régisseur Général (RG)
* Régisseurs: Lumière, Son, Plateau, Vidéo, Multi
* Technicien.ne Intermittent.e
* Comptabilité / Paie
* RH / Planning
* Invité (lecture seule: artistes, tourneurs, prestataires)

Permissions (RBAC):

* Lecture / Création / Edition / Suppression par module
* Portée: organisation, projet, mission, lieu
* Règles fines: voir salaires, modifier paie, valider heures, exporter AEM, etc.

---

## 2. Entités principales (données)

* Utilisateur (profil, compétences, tarifs, IBAN, pièces admin)
* Organisation (société, SIRET, adresses, logos, paramètres)
* Lieux (salles, adresses, contacts, capacité, accès, contraintes)
* Projet (ex: spectacle/tournée, période, budget, équipes cibles)
* Mission (tâche planifiée, shift, réutilisable sur plusieurs lieux)
* Affectation (mission x personne x créneau)
* Disponibilité (dispo/indispo, préférences, zones horaires)
* Temps (pointage, heures prévues vs réalisées, pauses)
* Paie (cachet, horaire, primes, frais, AEM, contrats)
* Facturation (client, devis, facture, avoir, paiement)
* Matériel (catalogue, états, numéros de série, kits)
* Logistique (camions, chargements, listes, itinéraires)
* Documents (notes, annexes, fiches techniques, riders, feuilles de route)
* Notifications (templates, canaux, destinataires, logs)
* Audit (journal actions, versions)

---

## 3. Modules fonctionnels

### 3.1 Auth, comptes et organisations

* SSO email + code magique, mot de passe, OAuth (optionnel)
* Invitations par email, rôles à l'invitation
* Multi-organisations, switch d'org
* Paramètres d'org: logos, couleurs, feuilles d'heures, politiques (pauses, heures nuit, primes), modèles d'exports

### 3.2 Projets

* Créer un projet (nom, période, budget, équipe type)
* Associer des lieux, un calendrier projet
* Templates de projet

### 3.3 Missions (réutilisables)

* Créer des types de missions (ex: Montage, Explo, Démontage, Résidence)
* Définir: compétences requises, nombre de postes, horaires, lieu par défaut
* Rendre les missions réutilisables sur plusieurs lieux
* Tags: Son/Lumière/Plateau/Video/Accueil, niveau, matériel requis

### 3.4 Planning

* Vues: Jour / Semaine / Mois / Timeline (Gantt simplifié)
* Groupes: par équipe (Technique, Billetterie, Comédiens, etc.)
* Drag and drop: créer/déplacer/étendre les créneaux
* Détection de conflits (horaire, lieu, temps de trajet, double booking)
* Détection de sous-qualification (compétences manquantes)
* Zoom 15/30/60 min, repères 08:00-18:00, 16:00-24:00
* Filtres: lieu, projet, rôle, tag mission, personne
* Raccourcis: Dupliquer, Alt+Drag, Undo/Redo
* Export ICS par personne, projet, équipe

### 3.5 Disponibilités et auto-assignation

* Saisie des dispos par les intermittents (web/mobile)
* Règles d’auto-assignation: priorités, compatibilités, coûts
* Proposition d’affectations avec score (compétences, dispo, historique)
* Validation manuelle finale par RG/Planning

### 3.6 Temps et pointage

* Feuilles d’heures prévues vs réalisées
* Pointage: bouton start/stop, saisie manuelle sécurisée, justification retard
* Pauses, heures de nuit, heures WE et jours fériés
* Validation hiérarchique (RG -> Paie)
* Alertes: dépassements, incohérences
* Export CSV/PDF des relevés par période

### 3.7 Paie (Intermittents)

* Modèles: cachet, horaire, mixte, primes (panier, transport, habillage, outillage)
* Barèmes: nuit, fériés, heures suppl.
* Gâteaux: multi-employeurs, multi-projets
* Génération AEM, DPAE (info), récap URSSAF, journaux de paie
* Validation par lot, clôture mensuelle
* Exports: AEM PDF/CSV, récap paie, écritures comptables

### 3.8 Facturation (optionnel v1.1)

* Devis, facture, avoir, échéancier
* Lien avec temps/prestations réalisés
* Export compta (FEC simplifié, plan comptable custom)

### 3.9 Matériel et logistique

* Catalogue matériel (numéro de série, état, photos)
* Kits/sets (ex: kit HF, kit plateau)
* Mouvement: sortie/retour, réservations par mission
* Checklists de chargement, QR code
* Parcours camions, horaires, poids/volumes, contraintes accès

### 3.10 Notes, docs et feuilles de route

* Notes liées à projet/mission/lieu/personne
* Templates de feuille de route: horaires, accès, contacts, plan d'implantation, sécurité
* Génération PDF (par jour, par lieu, par projet)
* Versionnage des documents (historique)

### 3.11 Notifications

* Canaux: Email, SMS, Telegram, Push (web), Slack (optionnel)
* Templates dynamiques (variables: lieu, horaires, contact, lien ICS)
* Triggers: création mission, changement horaire, nouvelle affectation, rappel J-1/J-0, retard pointage, validation paie
* Journal: statut (envoyé, délivré, lu), relances
* Préférences par utilisateur et par type d’événement

### 3.12 Intégrations

* Calendriers: Google Calendar, Outlook ICS
* Stockage: Google Drive, SharePoint, S3 (docs)
* Email: SMTP/SendGrid/Postmark
* SMS: Twilio/OVH
* Comptabilité: export CSV universel (Sage/Quadra) v1.1

### 3.13 Analytics et tableaux de bord

* KPI planning: taux de couverture, heures planifiées vs réalisées
* KPI paie: masse salariale par projet/période, coût horaire moyen
* KPI logistique: taux de retour matériel, incidents
* Heatmaps de charge par équipe/lieu
* Exports PNG/PDF/CSV

### 3.14 Audit et conformité

* Journal des actions: qui, quoi, quand, avant/après
* Rétention des logs, export JSON/CSV
* RGPD: droits d’accès, suppression, anonymisation

---

## 4. Workflows cibles (E2E)

### WF-01: Créer un projet et ses missions réutilisables

1. Admin crée le projet (période, budget, lieux)
2. RG définit des missions-type (Montage, Explo, Démontage)
3. RG planifie les missions sur plusieurs lieux (drag and drop timeline)
4. Système détecte conflits et propose corrections
5. Export ICS et notifications aux équipes concernées

Critères d’acceptation:

* Conflits visibles en moins de 200 ms après drop
* Export ICS contient au moins: titre, lieu, horaires, description

### WF-02: Affectation avec auto-assignation

1. Intermittents renseignent leurs dispos (deadline)
2. RG lance auto-assignation (score)
3. RG ajuste manuellement, résout conflits
4. Notification d’affectation + lien ICS

Critères d’acceptation:

* Score visible et explicable (top 3 raisons)
* Email envoyé en < 30 s après validation

### WF-03: Feuilles d’heures et validation paie

1. Système génère heures prévues par affectation
2. Technicien pointe (start/stop) ou saisit
3. RG valide les écarts
4. Paie calcule cachets/heures + primes
5. Comptabilité exporte AEM + récap

Critères d’acceptation:

* Ecart > 15 min -> justification requise
* Génération AEM PDF par lot en < 60 s pour 100 fiches

### WF-04: Matériel et feuille de route

1. RG associe kits matériels aux missions
2. Génération checklist chargement + QR
3. Feuille de route PDF avec contacts/accès/plans
4. Après retour, contrôle états et incidents

Critères d’acceptation:

* QR ouvre la fiche matériel en lecture
* Feuille de route PDF horodatée, versionnée

---

## 5. Règles métier et contraintes

* Temps de trajet entre lieux bloque double booking
* Heures nuit (par défaut 22:00-06:00) -> majoration
* Pause obligatoire au delà de X heures (paramétrable)
* Indemnités (transport/panier) par lieu/période
* Compétences requises: hard stop à l’assignation si manquantes (override possible avec justification)

---

## 6. Notifications: matrice (exemples)

* Affectation creee -> Email + Telegram au technicien; copie RG
* Changement horaire > 15 min -> Email + SMS (si J-1)
* Rappel J-1 18:00 -> Email + Push avec plan d’accès
* Retard pointage 10 min -> Telegram direct au technicien + RG
* Validation paie -> Email recap au technicien

Logs min: id event, cible, canal, payload, statut, latence, error

---

## 7. Exports et documents

* ICS: par personne/projet/equipe
* CSV: temps, paie, affectations, materiel
* PDF: feuilles de route, feuilles d’heures signables, AEM par lot
* ZIP: dossier projet (tous docs, riders, plans)

---

## 8. UI/UX: pages clés

* Login / Onboarding
* Dashboard: couverture planning, alertes conflits, prochains events
* Planning: Day/Week/Month/Timeline, filtres, groupes par equipe
* Projets: liste + detail + budget
* Missions: catalogue, types reutilisables, affectations
* Disponibilites: grille personnelle + import ICS
* Temps: pointage, validation, ecarts
* Paie: masse, primes, cloture, exports AEM
* Materiel: stocks, kits, mouvements, checklists
* Docs: notes, templates, generateur PDF
* Notifications: templates, historiques, prefer.
* Admin: roles, politiques, integr.

---

## 9. NFR (exigences non fonctionnelles)

* Perf: 95e percentile < 200 ms pour lecture planning semaine (100 personnes x 5 missions)
* Securite: RBAC, 2FA optionnelle, logs audit immutables
* Fiabilite: sauvegarde quotidienne, RPO 24h, RTO 4h
* Legal: RGPD, retention personnalisable
* Observabilite: traces, metrics, logs; alertes sur erreurs 5xx

---

## 10. Critères d’acceptation (MVP v0.1)

* Créer projet + missions reutilisables + planifier sur 2 lieux
* Auto-assignation simple (score sur dispo + competence)
* Pointage manuel + validation RG + export CSV des heures
* Generation feuille de route PDF basique
* Notifications email a l’affectation et rappel J-1

---

## 11. Roadmap haute-niveau

* Step 01: Auth + RBAC + Organisations (OK)
* Step 02: Projets + Missions reutilisables (en cours)
* Step 03: Planning Day/Week/Timeline + conflits
* Step 04: Dispos + auto-assignation v1
* Step 05: Temps/pointage + validation
* Step 06: Paie v1 (modeles + exports CSV)
* Step 07: Materiel + checklists
* Step 08: Feuilles de route PDF
* Step 09: Notifications (email/telegram)
* Step 10: Analytics v1 + exports

Note: si CI/tests KO sur une step, creation de step X.Y (fix) avant d’avancer.

---

## 12. Mapping vers nos agents

* AGENT.backend: schemas (Pydantic v2), services, regles metier, API REST, webhooks, exports, RBAC
* AGENT.frontend: vues (planning, paie, materiel), drag-drop, etats, formulaires, PDF client
* AGENT.devops: CI/CD, tests, qualite, securite, observabilite, backups, images Docker
* AGENT.docs: templates, README, feuilles de route, release notes, changelog

Inputs attendus de chaque agent: PR avec tests, docs, demo gif, et validation guards.

---

## 13. Donnees minimales par entite (MVP)

* Utilisateur: nom, email, role, competences[], tarifs, IBAN masked
* Lieu: nom, adresse, acces, contacts
* Projet: nom, periode, budget, lieux[]
* Mission: type, tags, horaires, lieu, nb_postes, competences
* Affectation: mission_id, user_id, horaires, statut (propose, confirme)
* Temps: prevu, realise, pauses, commentaire_ecart
* Paie: type, base, primes[], total_estime
* Materiel: ref, serie, etat, kit_id
* Doc: type, version, storage_url, meta

---

## 14. Tests d’acceptation (exemples gherkin)

* Conflit horaire detecte lorsque une personne est affectee sur 2 missions chevauchantes au meme horaire
* Auto-assignation choisit un profil competent et dispo
* Export ICS ouvre un event dans Google Calendar avec le bon fuseau
* Generation PDF feuille de route contient horaires, adresse, contacts

---

## 15. Risques et mitigations

* Complexite regles paie: commencer simple (cachet/horaire), modulariser
* Qualite donnees (dispos non renseignees): rappels et verifs avant auto-assignation
* Performance planning: pagination serveur, virtualisation UI
* SMS couts: throttling et preferences utilisateur

---

## 16. Glossaire

* Affectation: lien entre mission et personne avec un horaire
* Feuille de route: document jour/lieu avec infos pratiques
* AEM: Attestation Employeur Mensuelle

---

## 17. Ouvertures v1.1+

* Facturation client et suivi marge
* Mobile offline pour pointage
* Signature electronique feuilles d’heures
* Import depuis Excel/CSV legacy

---

Fin v0.1. A iterer avec retours terrains (Bobino, tournees) et guards de qualite actifs.
