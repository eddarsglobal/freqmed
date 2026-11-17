# RoadMap.md — FREQMED | Système de génération physique acoustique et électromagnétique

**Version :** 1.0.0 — refonte radicale de mission demandée par le propriétaire le 12 novembre 2026.
**Projet :** FREQMED — générateurs physiques de fréquences acoustiques et électromagnétiques.
**Dépôt officiel :** `eddarsglobal/freqmed` ; dossier Mac : `~/Documents/App_py/freqmed`.
**Contrainte :** ZERO_COST_FOSS=ENFORCED, NEVER_SIMULATION=ENFORCED, 10 langues, mobile-first, thèmes système/clair/sombre.
**Design approuvé :** mélange Windows 11 Fluent et macOS, conserver la direction UI V5, ne pas relancer de refonte non sollicitée.
**État :** MISSION_REBASE_IN_PROGRESS ; P0.00=CERTIFIED_GOVERNANCE_ONLY_HISTORICAL ; P0.01=IN_PROGRESS_REBASE_REVIEW ; REAL_OUTPUT=NOT_AUTHORIZED ; BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED ; PRODUCTION=NOT_AUTHORIZED.

> **Mission impérative.** FREQMED est d'abord un **système qui commande et génère réellement des fréquences physiques acoustiques et électromagnétiques**, à travers des dispositifs matériels adaptés. Ce n'est ni un lecteur de relevés, ni une plate-forme de recherche documentaire, ni un simulateur. Le Bureau gère la recherche scientifique, la définition des spécifications, les essais, la sûreté, la vérification et les certifications. Le logiciel et ses sorties physiques sont développés par l'équipe d'ingénierie sous contrôle du Bureau.

## A. Constitution et décisions propriétaires

1. **JAMAIS DE SIMULATION.** Aucun champ simulé, jumeau numérique, fausse expérience, faux appareil, fausse mesure, mode simulation ou courbe artificielle. Les **consignes de commande** et la génération de flux de commande numériques nécessaires à une **sortie physique réelle** ne sont pas des observations scientifiques : elles ne deviennent une fréquence *émise* qu'après sortie matérielle vérifiée. Un fichier WAV, une consigne en Hz ou un calcul n'est jamais une preuve d'émission physique.
2. **GÉNÉRATION PHYSIQUE, pas simple analyse.** Deux sous-systèmes produits distincts : (A) sortie acoustique vers transducteur/audio réel ; (B) générateur électromagnétique via équipement physique dédié, autorisé et compatible. Aucun Mac/iPhone, port réseau ou radio intégré n'est présenté comme un émetteur arbitraire d'EM. Aucune association fabricant, licence commerciale ou signature extérieure imposée au développement logiciel.
3. **SÉCURITÉ AVANT ÉMISSION.** Le développement du code hors ligne est autorisé comme candidat ; toute activation de haut-parleur, transducteur, bobine, appareil électrique, antenne ou source RF reste **bloquée** tant que le Bureau n'a pas certifié la configuration d'essai non biologique, les limites, les interverrouillages et le matériel. La consigne propriétaire de développer ne vaut pas autorisation de produire des champs ou d'exposer quelqu'un. Aucune exposition de cellule, animal ou humain ; aucune thérapie, diagnostic, fréquence « qui soigne » ni auto-expérimentation.
4. **FOSS, coût logiciel nul.** Audit des droits directs/transitifs et des outils de compilation. APIs système macOS propriétaires autorisées seulement comme dépendances **de plateforme explicitement signalées** (pas de prétention « pile 100 % FOSS » sur macOS) ; cœur FREQMED diffusé sous licence libre. Aucun SDK payant imposé, aucun SaaS, compte ni pilote propriétaire obligatoire. Pas de simulation.
5. **Bureau souverain pour la science.** Les décisions de recherche, sécurité, métrologie et certification relèvent des fonctions du Bureau, non des autotests de l'assistant. Les dix fonctions historiques B01–B10 sont conservées ; un rôle nommé dans le tableau n'implique pas qu'une personne l'occupe. Nomination effective et approbations doivent être tracées sans être inventées.
6. **RoadMapGuardian séquentiel.** Seul ce `RoadMap.md` fait foi. Statuts : PENDING → IN_PROGRESS → TESTING → CERTIFIED ; REMEDIATE et BLOCK sont possibles. Une preuve informatique PASS ne fait jamais passer un jalon à CERTIFIED. Pas de progression de jalon avant certification explicite du prédécesseur. Un changement de portée ne rétro-certifie pas d'anciens travaux.
7. **Confidentialité, provenance, arrêt.** Sortie OFF au démarrage, aucune émission automatique, sortie interdite en cas d'absence de matériel/profil/autorisation ou d'erreur. Arrêt d'urgence indépendant des réglages graphiques, durées maximales validées, limites non contournables, avertissement d'exposition. Journaliser commandes et arrêts sans stocker secrets ni données personnelles.
8. **Langues et UI.** EN (défaut), FR, DE, AR (RTL), ES, PT, HR, IT, ZH, KO ; unités et états de sécurité invariants ; design Windows 11 × macOS gelé pour la phase en cours, sans faux oscilloscopes ni courbes de mesure.
9. **Distinction centrale.** Le générateur **commande** le matériel. La métrologie **mesure indépendamment** les sorties produites ; une mesure sert à les caractériser, pas à redéfinir FREQMED comme lecteur CSV. Le Bureau **recherche** et certifie ; les développeurs implémentent.

## B. Architecture produit ciblée

### B1. Frequency Command Core (commun)

Moteur de consignes typées (acoustique/EM), unités et profils, état OFF→READY→ARMED→ACTIVE→STOPPING→OFF (états futurs soumis aux gates), limites de fréquence/amplitude/durée déterminées pour **l'équipement choisi**, verrou d'activation, validation du consentement opérateur, arrêt matériel, journal d'événements, protections anti-débordement, timeout watchdog, aucune exécution automatique au chargement. Les commandes numériques sont des **instructions de sortie**, jamais des résultats mesurés.

### B2. Acoustic Physical Generator

Pilote local vers une **sortie audio véritable** (ex. CoreAudio sur Mac Intel) et transducteur approprié ; moteur de génération acoustique continue/limitée, enveloppes de mise en route/arrêt pour éviter les transitoires, limites propres au banc, interrupteur d'arrêt et contrôle séparé de la chaîne acoustique. Aucune équivalence implicite entre amplitude numérique et pression acoustique en Pa ; aucune garantie de sécurité basée sur le seul volume numérique. Source initiale **compilable mais non émettrice sans gate d'essai certifié**.

### B3. Electromagnetic Physical Generator

Contrat matériel **device-specific** pour un générateur de fonctions/équipement EM externe ayant une voie d'émission autorisée, des limites matérielles vérifiées et un arrêt physique. Aucun pilote universel RF, aucune conversion improvisée d'une carte son en émetteur, aucun contrôle direct du Wi-Fi, Bluetooth ou radio de téléphone pour produire une fréquence arbitraire. Tant qu'aucun matériel qualifié, profil de sûreté et banc autorisé ne sont identifiés : `EM_OUTPUT=BLOCKED_NO_QUALIFIED_HARDWARE`. Code de protocoles et intégration ultérieure sans simulation de matériel.

### B4. Bureau & Independent Safety Guardian

Étude des risques par dispositif, limites d'émission, légalité RF/EMC, chaîne d'étalonnage et vérification extérieure indépendante, extinction sécurisée, conformité régionale, avis scientifiques. La sécurité ne repose jamais uniquement sur une case à cocher de l'UI. Le Bureau doit rendre un verdict tracé pour toute autorisation expérimentale.

### B5. Application locale

Une UI conservant la direction visuelle approuvée ; panneau GÉNÉRATION (acoustique, EM), états de sortie physiques, appareils qualifiés, interverrouillages, arrêt, profil et journaux. Les anciens prototypes V4/V5 et R29–R32 peuvent être réutilisés **comme composants secondaires** pour l'historique/traçabilité mais **ne sont pas des jalons de génération validés**.

## C. Bureau : responsabilités (fonctions non présumées pourvues)

| Fonction | Responsabilité dans la nouvelle mission |
|---|---|
| B01 — Oncologie clinique | Séparer recherche autorisée et revendications cliniques, aucune exposition hors processus institutionnel |
| B02 — Biologie/pathologie | Concevoir les hypothèses et contrôles biologiques futurs, aucune étude non autorisée |
| B03 — Biophysique | Revue scientifique des mécanismes physiques et interactions éventuelles |
| B04 — Métrologie acoustique | Spécifier transducteur, pression/niveau mesurable, étalonnage et banc acoustique sûr |
| B05 — Métrologie électrique/EM | Spécifier équipement EM, champs, limites, compatibilité et conformité RF/EMC |
| B06 — Instrumentation/imagerie | Qualification physique des capteurs et instruments de contrôle |
| B07 — Acoustique/DSP | Validation des signaux de commande, stabilité, artéfacts et conformité de sortie |
| B08 — Logiciel scientifique | Vérifier logiciel, unités, délais, répétabilité et calculs à partir de mesures réelles |
| B09 — Architecture/cybersécurité/UX | Construire, auditer et porter le produit 10 langues, assurer le fail-closed |
| B10 — Sécurité/éthique/réglementaire | Gouvernance des autorisations, essais non biologiques, arrêt, risques, cadre légal |

Le Bureau **ne remplace pas l'équipe qui code**. Il définit, vérifie et certifie les exigences scientifiques et de sûreté. Les rôles non pourvus ne peuvent certifier par anticipation.

## D. RoadMap de développement — 28 jalons stables, ordre strict

*La refonte remplace les anciens intitulés P0.01–P8.02 ; leur historique demeure dans Git et les rapports de preuve. Les identifiants sont maintenus pour continuité. Aucune ancienne certification ne s'applique aux nouveaux contenus.*

| ID | Travail prioritaire | Critère de sortie et preuve | Responsable | Statut |
|---|---|---|---|---|
| P0.00 | Constitution scientifique historique | Certification R4 de gouvernance du périmètre initial, sans matériel autorisé | Owner/B09/B10 | **CERTIFIED — HISTORICAL_GOVERNANCE_ONLY** |
| P0.01 | **Refondre la mission et la gouvernance du générateur** | RoadMap v1.0, revue Bureau, séparation émission/recherche/mesure, reconnaissance des anciens candidats | Owner/B09/B10 | **IN_PROGRESS — REBASE_REVIEW** |
| P0.02 | Cadre de sûreté des émissions acoustiques/EM | Analyse risques, types de sorties, interdictions d'exposition, conditions arrêt et conformité | B04/B05/B10 | PENDING |
| P0.03 | Vérification FOSS/zéro coût et architecture des générateurs | Inventaire code/licences, dépendances build et séparation Mac/projet libre | B09/B10 | PENDING |
| P0.04 | Inventaire matériel réel et définition du premier banc non biologique | Capteurs/transducteurs/équipement de sortie existants, critères de compatibilité, aucune obligation de partenaire | B04/B05/B06 | PENDING |
| P1.01 | **Frequency Command Core** | Consignes typées, états fail-closed, watchdog/arrêt, tests sans aucune émission | B07/B09/B10 | PENDING |
| P1.02 | **Acoustic Generator — backend physique Mac** | Code de sortie audio réelle, OFF par défaut ; build audit et autorisation de bench distincte | B04/B07/B09 | PENDING |
| P1.03 | Qualification des sorties acoustiques et limites | Appareil identifié, protection contre surcharge, arrêt indépendant, protocole de banc | B04/B07/B10 | PENDING |
| P2.01 | **EM Generator — contrat matériel strict** | API de contrôle explicite, identité matérielle, limites approuvées ; refus sans appareil | B05/B09/B10 | PENDING |
| P2.02 | EM backend pour matériel qualifié | Adapter une **interface matérielle réellement disponible**, sans commande RF générique | B05/B09 | PENDING |
| P2.03 | Interverrouillages EM indépendants | Arrêt matériel/logiciel, limites mesurées, conformité du banc et journal indépendant | B05/B06/B10 | PENDING |
| P3.01 | Essai acoustique non biologique autorisé | Sortie réellement vérifiée par mesure indépendante, arrêt démontré ; zéro exposition biologique | B04/B06/B07/B10 | PENDING |
| P3.02 | Caractérisation acoustique | Plage, stabilité, niveau, distorsion, incertitudes ; mesures physiques brutes et répétabilité | B04/B07/B08 | PENDING |
| P3.03 | Essai EM non biologique autorisé | Matériel/légalité/sûreté établis avant toute émission, observation indépendante | B05/B06/B10 | PENDING |
| P4.01 | Moteur d'enveloppes, durées, extinction | Pas de démarrage automatique, transitions bornées, watchdog, erreurs OFF | B07/B09/B10 | PENDING |
| P4.02 | Contrôle indépendant des Hz/acoustique/EM | Mesurer la **sortie physique** réellement produite, pas seulement la consigne | B04/B05/B08 | PENDING |
| P4.03 | Répétabilité et traçabilité générateur | Preuves appareil/conditions, logs arrêts, étalonnage lorsqu'une précision est revendiquée | B06/B08/B10 | PENDING |
| P5.01 | UI générateur, identité visuelle approuvée | 10 langues/RTL/mobile, affichage honnête sorties et interverrouillages | B09 | PENDING |
| P5.02 | Distribution multiplateforme graduelle | macOS Intel en premier, autres OS uniquement si API/hardware sûrs et zéro coût | B09 | PENDING |
| P5.03 | Audit cyber et sécurité de la commande | Permissions, refus réseau par défaut, absence de bypass, build reproductible | B09/B10 | PENDING |
| P6.01 | Revue du Bureau des objectifs de recherche | Hypothèses, protocole non biologique/biologique futur, état de preuve sans promesse de soin | B01/B02/B03/B10 | PENDING |
| P6.02 | Dossier d'éligibilité future à une étude biologique | Institution, biosécurité, éthique, connaissances, interdiction d'exposition en absence d'autorisation | B01/B02/B03/B10 | PENDING |
| P6.03 | Gate expérimentation biologique éventuelle | Autorisations écrites institutionnelles distinctes, hors périmètre du développement actuel | B01/B02/B10 | LOCKED |
| P7.01 | Qualification de conformité par destination | Acoustique/EM : règles de sécurité, CEM/émissions, logiciel et éventuellement médical | B05/B09/B10 | LOCKED |
| P7.02 | Dossier de sécurité du produit | Preuves complètes de protection matérielle/logicielle et suivi des défauts | B09/B10 | LOCKED |
| P7.03 | Décision distincte sur étude clinique éventuelle | Aucun acte ni revendication clinique sans autorisations compétentes | B01/B10 | LOCKED |
| P8.01 | Publication générateur non médical si autorisée | Sortie réelle certifiée, documentation, conformité locale, FOSS/zéro coût, 10 langues | B09/B10 | LOCKED |
| P8.02 | Produit médical éventuel, dossier séparé | Requiert preuves cliniques et voie réglementaire distincte | B01/B10 | LOCKED / HORS_PÉRIMÈTRE |

## E. Séquence d'ingénierie permise AVANT les certifications

La **construction de candidats sources isolés et sans émission** peut préparer P1.01/P1.02/P2.01 sans les déclarer IN_PROGRESS/CERTIFIED. Cette exception de préparation **ne déroge pas au séquencement des certifications** et n'autorise aucun essai physique.

- Candidat **GEN-CORE-01** : garde logiciel, consignes typées, machine à états OFF et arrêt, tests informatiques uniquement ; aucune donnée physique synthétique.
- Candidat **GEN-ACOUSTIC-01** : implémentation de sortie audio réelle vers CoreAudio, **compilation excluant explicitement l'émission jusqu'à gate** ; pas de sons de démonstration.
- Candidat **GEN-EM-01** : frontière matérielle définie et réponse `BLOCKED_NO_QUALIFIED_DEVICE` tant qu'aucun instrument réel n'est qualifié ; aucun pilote RF universel.
- Les moteurs de lecture CSV R29, de registre R30, d'analyse R31, de pont UI R32 restent des **outils secondaires documentaires** hors jalon, sans preuve d'acquisition physique. Aucune refonte du design.
- Aucun logiciel ne peut déclarer « sortie physique effectuée » sans témoin matériel et contrôle indépendant.

## F. Gates non négociables

**G0** Mission v1 revue et approuvée explicitement ; Bureau consulté ; droits vérifiés.
**G1** Tests moteurs OFF et fail-closed, absence d'émission.
**G2** Profil matériel réel/limites et interverrouillage qualifiés.
**G3** Autorisation spécifique du premier banc acoustique non biologique ; aucune auto-activation.
**G4** Autorisation spécifique matériel EM, respect de l'environnement réglementaire ; aucune émission sans revue.
**G5** Mesure indépendante des champs/pressions produits et incertitudes ; pas de courbe fictive.
**G6** Validation produit multi-plateforme, libre/zéro coût, 10 langues.
**G7** Expériences biologiques et usages médicaux restent BLOCK hors autorisations distinctes.

## G. Historique et non-régression

- 2026-11-13 : preuve propriétaire GEN-R10 Mac Intel 195/195 tests Python + 33/33 assertions natives C PASS, backend source non lié et sortie bloquée ; **ne vaut pas certification du Bureau**.
- 2026-11-13 : GEN-R11 FIX1 Mac Intel validé logiciellement : **215/215 tests Python + 33/33 assertions C PASS**, cinq objets natifs non liés, aucune émission. Certification du Bureau toujours PENDING.
- 2026-11-13 : GEN-R12 Mac Intel première exécution : 70/70 fichiers intègres, 5 objets isolés compilés, 33/33 assertions C, contrôle de symboles PASS; 235 tests Python exécutés, **3 FAIL** hérités R9/R10/R11, donc R12 non validé.
- 2026-11-13 : GEN-R12 FIX1 validé logiciellement sur Mac Intel : **235/235 tests Python + 33/33 assertions natives C PASS**, cinq objets isolés, aucune émission, Bureau PENDING.
- 2026-11-13 : GEN-R13 validé logiciellement sur Mac Intel : **255/255 Python PASS + 33/33 assertions C PASS**, 74 fichiers intègres, 5 objets compilés non liés et aucune émission ; certification Bureau PENDING.
- 2026-11-13 : GEN-R14 validé logiciellement sur Mac Intel : **275/275 tests Python + 33/33 assertions natives C PASS**, 78 fichiers intègres, cinq objets compilés non liés, aucun son ou champ émis, Bureau PENDING.
- 2026-11-13 : GEN-R15 témoin Mac Intel initial : 82/82 sources intègres, 5 objets compilés **non liés**, 33/33 assertions C et audit de symboles PASS ; **295 tests Python exécutés, 3 FAIL** hérités R9/R10/R11, donc GEN-R15 non validé.
- 2026-11-13 : GEN-R15 FIX1 **validé logiciellement sur Mac Intel** : **295/295 Python PASS, 33/33 assertions C PASS**, 82/82 sources intègres, cinq objets natifs non liés, aucune émission ; Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-13 : GEN-R16 validé logiciellement sur Mac Intel : **315/315 tests Python PASS, 33/33 assertions C PASS, 25/25 contrôles statiques PASS**, 87 fichiers intègres, cinq objets natifs compilés non liés, aucune émission ; certif. Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-14 : GEN-R17 validé logiciellement sur Mac Intel : **335/335 tests Python PASS, 33/33 assertions C PASS, 25/25 contrôles R16 PASS**, vérificateur indépendant R17 PASS, 92/92 fichiers intègres, cinq objets natifs non liés, aucune émission ; Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-14 : GEN-R18 validé logiciellement sur Mac Intel : **355/355 Python PASS, 33/33 C PASS**, R16/R17/R18 preuves PASS, 13 retours / 4 libérations / 6 relâchements contrôlés, 97/97 sources intègres, cinq objets natifs isolés/non liés, aucune émission. Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-14 : GEN-R19 validé logiciellement sur Mac Intel : **375/375 Python PASS, 33/33 C PASS, 13/13 contrôles adversariaux PASS**, R16/R17/R18 PASS, 103/103 sources intègres, archive privée des quatre JSON créée et vérifiée, backend natif non lié et aucune émission. Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-14 : GEN-R20 validé logiciellement sur Mac Intel : **395/395 Python PASS, 33/33 C PASS**, 108/108 sources intègres ; archive R19 historique de 103 fichiers et quatre JSON revérifiée en lecture seule ; dossier du Bureau créé, **11 portes PENDING**, `REVIEWABLE_NOT_CERTIFIED`, aucun backend de sortie lié ni émission.
- 2026-11-14 : GEN-R20 FIX1 validé logiciellement sur Mac Intel : **397/397 Python PASS, 33/33 C PASS**, 108/108 fichiers intègres, avertissements invalides de chaînes Python éliminés, archive originale R19 requalifiée documentaire (103 fichiers, quatre JSON), aucune émission ; Bureau PENDING, P0.01 IN_PROGRESS.
- 2026-11-14 : GEN-R21 validé logiciellement sur Mac Intel : **417/417 Python PASS, 33/33 C PASS**, 113/113 sources intègres, archive historique R19 103 fichiers/4 JSON revérifiée, audit des onze portes `R21_BUREAU_GAP_REVIEW=PASS`, **11 OPEN, 0 résolue**, quatre fichiers du Bureau R20/R21 SHA-256 vérifiés ; sans émission ni simulation, P0.01 IN_PROGRESS et Bureau PENDING.
- 2026-11-15 : GEN-R22 validé logiciellement sur Mac Intel : **437/437 Python PASS, 33/33 C PASS, 118/118 fichiers sources intègres**, 17 observations statiques, trois risques non prouvés ; dossier privé R20–R22 de six fichiers JSON/Markdown vérifiés SHA-256, archive R19 en lecture seule, 11 portes du Bureau OPEN, 0 résolue, aucune émission.
- 2026-11-15 : GEN-R23 validé logiciellement sur Mac Intel au commit `e52a18b39c4e29203fef23c3a63c4537317794a5` : **457/457 Python PASS, 33/33 C PASS, 123/123 sources intègres**, 15 obligations de preuve OPEN, 0 acquittée, dossier privé de huit rapports R20–R23 vérifié SHA-256, archive R19 en lecture seule, onze portes du Bureau OPEN, aucune émission ni simulation.
- 2026-11-15 : GEN-R24 validé logiciellement sur Mac Intel au commit `78d6f8667de4c9834b4b89feb0c36ca39a5e3c87` : **477/477 Python PASS, 33/33 assertions C PASS, 128/128 sources intègres**, 19 champs C11, 112 références lexicales, 11 points d'appel AudioQueue, 7 constats R24 ouverts et 15 obligations R23 ouvertes, dossier privé de 10 rapports R20–R24 vérifiés SHA-256 ; aucune simulation ou émission.
- 2026-11-15 : GEN-R25 validé sur Mac Intel au commit `646403a02ac9664b97c3fce954cbcf69415cee8e` : **497/497 Python PASS, 33/33 assertions C PASS, 133/133 sources intègres**, neuf remédiations documentaires, zéro patch C appliqué, douze fichiers R20–R25 vérifiés SHA-256, 15 obligations R23 et 7 constats R24 OPEN, 11 portes Bureau OPEN, aucune émission ni simulation.
- 2026-11-15 : GEN-R26 validé logiciellement sur Mac Intel au commit `55719fbe6f30a96b6142b26c554bbb5656875e7d` : **517/517 Python PASS, 33/33 C PASS, 139/139 sources SHA-256 vérifiées**, trois modifications C dans `generator/candidates/acoustic_macos_r26.c`, zéro changement `generator/src/acoustic_macos.c`, objet natif candidat COMPILED_UNLINKED, quatorze rapports privés R20–R26 vérifiés SHA-256, aucune simulation, callback CoreAudio ni émission.
- 2026-11-15 : GEN-R27 candidat **Independent Native C11 Patch Adversarial & Ownership Review** : neuf constats source-ancrés ouverts (18 lignes C sous SHA-256), notamment accès concurrent potentiel à `ctx->queue` pendant disposal, `AudioQueueEnqueueBuffer` sous verrou PCM, compteurs d'entrée tardifs, propriété des listeners, erreurs OS et mémoire en quarantaine. Vingt nouveaux tests Python de revue et altérations textuelles fail-closed, chaîne R16–R26 requalifiée, aucune modification C natif, 16 rapports R20–R27 après PASS réel. Deux contrôles de cardinalité R26 changés de ==139 à >=139 pour compatibilité. **537 Python + 33 C attendus, 144 fichiers épinglés, GEN-R27 Mac PENDING**. Neuf risques R27 OPEN_NOT_PROVEN, quinze obligations R23 OPEN, sept constats R24 OPEN, onze portes Bureau OPEN ; aucune race reproduite, simulation ou émission.

- 2026-11-09 : P0.00-R4 gouvernance initiale certifiée ; **l'ancien P0.01 est un audit documentaire, pas une certification du nouveau générateur**.
- 2026-11-10/12 : séries documentaires R2–R28 ; UI V4/V5 ; moteurs candidats R29–R32 en dehors de la branche officielle.
- 2026-11-12 : correction impérative de mission par le propriétaire : **FREQMED = générateurs physiques acoustique ET EM**, recherche scientifique sous Bureau. La présente refonte ne crée aucune autorisation d'émission.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R28 — Independent C11 Queue Lifetime & Callback Admission Remediation Design

- **Statut :** CANDIDATE_SOURCE_ONLY, MAC_INTEL_PENDING, BUREAU_CERTIFICATION=PENDING. **P0.01 reste IN_PROGRESS ; aucune promotion ni signature indépendante.**
- Référence témoin **GEN-R27 Mac Intel logiciel PASS** : 537 Python, 33 assertions natives C, 144 sources SHA-256, 16 rapports SHA-256 ; neuf risques adversariaux non démontrés ouverts.
- Contrat C11 isolé `generator/candidates/r28_callback_admission_gate.c` (admission CAS bornée, fermeture atomique irréversible, comptage des leases) : **ne relie pas et n'active pas CoreAudio** ; son état fermé/vide n'établit ni fin des callbacks de l'OS ni validité d'`AudioQueueRef`.
- Nouveau dossier B07/B09/B10 : **5 obligations de conception OPEN_NOT_PROVEN**, outre les **9 constats R27, 15 obligations R23, 7 constats R24 et 11 portes du Bureau OPEN**. C historique et candidat R26 inchangés ; la PR #1 reste DRAFT.
- **Validation attendue, non présumée :** 557 tests Python, 33 assertions C, 150 fichiers SHA-256, 18 rapports vérifiés, cinq objets existants et deux candidats compilés en objets séparés non liés, audit `nm` non émetteur.
- Limites permanentes : `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R29 — Independent C11 Admission Integration & Queue Ownership Proof Review

- **État :** CANDIDATE_SOURCE_ONLY ; MAC_INTEL_PENDING ; BUREAU_CERTIFICATION=PENDING ; RoadMap P0.01 toujours IN_PROGRESS. Pas de progression ni de certification implicite.
- **Référence :** GEN-R28 réellement exécuté sur Mac Intel, 557 Python + 33 C + 150 source SHA-256 + 18 rapports de Bureau PASS, mais tous les risques C11 et CoreAudio encore ouverts.
- **Livrable C :** un nouveau candidat `generator/candidates/acoustic_macos_r29.c` issu du candidat R26, intégrant localement le protocole de bail R28 dans l'admission des callbacks/listeners et la fermeture avant disposition, **uniquement compilé en objet isolé**. Aucun changement au backend original, au C R26 ou au C11 R28. Aucune API d'émission n'est liée au binaire non émetteur.
- **Bureau B07/B09/B10 :** sept nouveaux constats I29 ouverts. La validité de userdata avant l'admission reste une obligation OS; closed-and-empty ne démontre ni qu'aucun callback futur ne se présentera ni la qualification des retours `AudioQueueDispose`. La fermeture avec un bail actif provoque une quarantaine sans disposition et peut conserver des ressources OS. Le risque de réentrance `AudioQueueEnqueueBuffer` sous le verrou PCM reste ouvert.
- **Blocages hérités :** 5 contrôles R28 OPEN ; 9 constats R27 OPEN ; 15 obligations R23 OPEN ; 7 constats R24 OPEN ; 11 portes du Bureau OPEN / zéro résolue. Les tests textuels ne prouvent aucune race.
- **Cible de test Mac Intel non attestée :** 577 Python, 33 assertions natives C, 156 sources SHA-256, 20 rapports SHA-256, compilation R29 uniquement non liée, audit `nm` de l'exécutable non émetteur.
- **Gouvernance :** `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R29 FIX1 — Réparation de l'infrastructure de tests sans effet sur les sorties

- Témoin réel Mac Intel du 16 novembre 2026 : **intégrité 156 sources PASS**, audit R29 PASS, objets C non liés PASS, **33 assertions natives C PASS**, binaire non émetteur PASS ; **393 tests Python OK**, puis arrêt `TypeError: 'str' object is not callable`.
- Cause avérée : `tests/test_r29_admission_integration_review.py` donnait une chaîne à `cls.run`, masquant `unittest.TestCase.run`. Aucune preuve de race reproduite, aucune défaillance CoreAudio déclenchée.
- Correction FIX1 : renommer `cls.run` / `self.run` en `cls.runner` / `self.runner`, ajouter au lanceur R29 un précontrôle AST fail-closed empêchant toute nouvelle affectation `cls.run` ou `self.run` dans la classe de test R29 ; nouveau manifeste épinglé, aucune modification du C.
- **Statut :** FIX1_SOURCE_CANDIDATE ; MAC_INTEL_FULL_REPLAY_PENDING ; 577 tests Python ciblés, 33 C, 156 sources, 20 rapports du Bureau. `GEN_R29_MAC_INTEL_SOFTWARE` n'est PAS PASS à ce stade.
- Obligations inchangées : 7 constats R29 OPEN, 5 contrôles R28 OPEN, 9 constats R27 OPEN, 15 preuves R23 OPEN, 7 constats R24 OPEN, 11 portes Bureau OPEN/0 résolue. P0.01 IN_PROGRESS. PR #1 DRAFT, sans fusion.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R30 — Independent CoreAudio Callback Quiescence & Queue Ownership Adversarial Review

- **Référence réellement exécutée :** GEN-R29 FIX1 Mac Intel = 577 Python PASS, 33 C natives PASS, 156 sources intègres PASS, 20 rapports SHA-256 PASS ; aucune certification OS/physique.
- **Découverte prioritaire :** candidat C R29, après `AudioQueueStart`, branche `closed_and_empty == false` qui retourne avec quarantaine sans `AudioQueueStop` ni `AudioQueueDispose`. **CRITICAL — jamais activer**, la quarantaine n'est pas une coupure matérielle.
- **R30 :** audit indépendant source-only de la quiescence, durée de vie `userdata`, `ctx->queue`, callbacks, listeners, `AudioQueueEnqueueBuffer`, dispose failures et garanties C11 ; **12 constats (2 critiques) OPEN_NOT_PROVEN**, 20 contrôles Python statiques.
- **Aucune modification du code C** : backend original, C R26/R29 et portail R28 identiques ; objets compilés séparément, aucun backend de sortie lié au CLI. Aucun callback CoreAudio, simulation scientifique, émission physique ou test biologique.
- **Bureau :** 7 constats R29 OPEN, 5 R28 OPEN, 9 R27 OPEN, 15 R23 OPEN, 7 R24 OPEN et 11 portes original Bureau OPEN/0 résolue. Aucune signature indépendante.
- **Validation attendue, non attestée :** 597 tests Python, 33 assertions C, 162 sources SHA-256, 22 rapports de revue SHA-256 ; PR #1 DRAFT, pas de fusion.
- `GEN_R30_SOURCE_REVIEW=PUBLISHED`; `GEN_R30_MAC_INTEL=PENDING`; `C11_RACE_FREEDOM=NOT_PROVEN`; `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN`; `POST_START_SHUTDOWN_SAFETY=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R31 — Independent Critical Shutdown Path Remediation & Fail-Closed Ownership Design

- **Référence :** GEN-R30 validé logiciellement sur Mac Intel (597 Python, 33 C, 162 sources SHA-256, 22 rapports SHA-256 PASS), mais 12 constats source ouverts dont deux critiques ; aucun acquittement C11/OS.
- **Changement limité :** nouveau `generator/candidates/acoustic_macos_r31.c` isolé, dérivé de R29. La phase de shutdown tente `AudioQueueStop(ctx->queue,true)` **avant le retour sur admission encore active**, et la branche `OSStatus!=noErr` conserve une quarantaine sans disposer ni libérer. **Cette source n'est jamais liée, chargée ou exécutée** ; le moteur original, R26, R29 et R28 restent inchangés.
- **Limite critique :** tentative de stop réussie ou échouée **ne démontre pas** l'arrêt acoustique physique ou la fin de tous les callbacks ; un échec peut laisser une file active. Ne pas promouvoir les risques `Q30_02` et `Q30_12` en résolus.
- **Bureau :** 8 nouvelles obligations R31 OPEN, dont 2 CRITICAL. R30 12 OPEN (2 CRITICAL), R29 7 OPEN, R28 5 OPEN, R27 9 OPEN, R23 15 OPEN, R24 7 OPEN, et 11 portes historiques OPEN / 0 résolue. Aucun certificat ni signature.
- **Validation Mac Intel attendue, non acquise :** 617 tests Python, 33 assertions C, 169 sources SHA-256, 24 dossiers R20–R31 SHA-256 ; audit `nm` et binaire non émetteur maintenus.
- **Statut :** `GEN_R31_SOURCE_CANDIDATE=PUBLISHED` ; `GEN_R31_MAC_INTEL=PENDING`; `POST_START_SHUTDOWN_SAFETY=NOT_PROVEN`; `PHYSICAL_STOP=NOT_PROVEN`; `C11_RACE_FREEDOM=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`; PR #1 DRAFT, non fusionnée.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R31 FIX1 — Normalisation fail-closed des exceptions de l'auditeur

- **Témoin réel Mac Intel du 16 novembre 2026 :** lanceur SHA-256 PASS ; 169/169 sources PASS ; audit `R31_CRITICAL_SHUTDOWN_REVIEW=PASS` ; C31 compilé **non lié** ; 33/33 assertions C natives ; `nm` non émetteur PASS. Suite Python exécutée : `Ran 617 tests in 15.539s` puis **`FAILED (errors=4)`**. Aucune certification logicielle R31, aucun dossier final de 24 rapports.
- **Cause racine :** les quatre mutations ciblées retirent volontairement des motifs C ; dans `observe()`, un `piece.index()` non protégé déclenchait `ValueError`, alors que `tests/test_r31_critical_shutdown_review.py` exige `R31Error`.
- **FIX1 :** neuf ancrages utilisent `anchored_index()` avec `require()`, renvoyant une erreur contractuelle `R31Error` sur source inattendue. **Les tests adversariaux restent intacts**, aucune tolérance ajoutée pour `ValueError` ; aucun candidat C ou backend original modifié.
- **Répétition Mac Intel nécessaire :** objectif non attesté de 617/617 Python, 33/33 C, 169/169 fichiers SHA-256 et 24 rapports SHA-256 ; nouveaux journaux distincts de la tentative initiale.
- **Bureau :** R31 8 OPEN (2 CRITICAL) ; R30 12 OPEN (2 CRITICAL) ; R29 7 OPEN ; R28 5 OPEN ; R27 9 OPEN ; R23 15 OPEN ; R24 7 OPEN ; portes 11 OPEN / 0 résolue. `C11_RACE_FREEDOM=NOT_PROVEN`, `PHYSICAL_STOP=NOT_PROVEN`, `GEN_R31_FIX1_MAC_INTEL=PENDING`. PR #1 DRAFT, pas de fusion.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R32 — Independent Failed-Stop Containment & CoreAudio Ownership Safety Review

- **Point de départ :** GEN-R31 FIX1 Mac Intel logiciel PASS (617 Python, 33 assertions C, 169 fichiers source, 24 rapports SHA-256) ; aucune preuve de sûreté CoreAudio active.
- **Périmètre :** revue adversariale du candidat C31 **sans modification C ni intégration**. L'échec d'`AudioQueueStop(ctx->queue,true)` garde la file et le contexte en quarantaine mais ne prouve ni arrêt acoustique ni innocuité physique ; ne pas ajouter un repli `AudioQueueDispose` forcé ou un retry sans garanties OS.
- **Livrables :** auditeur source C11/OSStatus R32, **10 nouveaux constats OPEN_NOT_PROVEN (2 CRITICAL)**, 20 tests de non-régression lexicaux, trois dossiers B07/B09/B10, un runner Mac Intel et une nouvelle chaîne de 26 rapports SHA-256 R20–R32. Aucun callback CoreAudio, aucun test de race simulée, aucun instrument ni émission.
- **Constats non résolus hérités :** R31 8 OPEN (2 CRITICAL), R30 12 OPEN (2 CRITICAL), R29 7 OPEN, R28 5 OPEN, R27 9 OPEN, R23 15 OPEN, R24 7 OPEN, 11 portes Bureau OPEN/0 résolue.
- **Validation cible, non attestée :** 637 tests Python, 33 assertions natives C, 175 sources intègres, 26 rapports SHA-256 ; binaire `output_hard_denied.c` avec audit `nm` non émetteur. PR #1 DRAFT, non fusionnée.
- **États :** `GEN_R32_SOURCE_REVIEW=PUBLISHED`; `GEN_R32_MAC_INTEL=PENDING`; `FAILED_OS_STOP=NOT_TESTED`; `PHYSICAL_STOP=NOT_PROVEN`; `CALLBACK_QUIESCENCE=NOT_PROVEN`; `C11_RACE_FREEDOM=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R33 — Independent CoreAudio Failure-State Ownership & Safe-Abandonment Contract Design

- **Base Mac Intel attestée :** GEN-R32 637/637 Python, 33/33 assertions C, 175/175 sources SHA-256 et 26/26 rapports SHA-256 PASS ; validation logicielle seulement, aucune sûreté OS/physique certifiée.
- **Choix du Bureau :** ne pas créer un correctif C prétendument sûr sur les retours d'erreur `AudioQueueStop`/`AudioQueueDispose`. À la place, formaliser les dix situations de propriété (`owner_ctx` avant/après publication, queue OS possiblement active/invalide, listeners et callbacks) et distinguer conservation mémoire, validité de handle et coupure physique.
- **Nouveaux livrables :** `audits/r33_failure_state_ownership_contract.py`, 12 constats **OPEN_NOT_PROVEN (3 CRITICAL)**, `tests/test_r33_failure_state_ownership_contract.py` (20 contrôles source-only), matrice d'abandon sûr, revue B07/B09/B10, `RUN_GEN_R33_MAC_INTEL.command` et chaîne privée R20–R33 de 28 rapports SHA-256.
- **Aucun changement C** : code original, candidats R26/R29/R31 et unité atomique R28 byte-identical. Aucune activation CoreAudio, aucune simulation scientifique, aucun matériel ou émission.
- **Risques hérités :** R32 10 OPEN (2 CRITICAL) ; R31 8 OPEN (2 CRITICAL) ; R30 12 OPEN (2 CRITICAL) ; R29 7 OPEN ; R28 5 OPEN ; R27 9 OPEN ; R23 15 OPEN ; R24 7 OPEN ; 11 portes Bureau OPEN / 0 résolue.
- **Cible Mac Intel R33, non encore observée :** 657 Python, 33 C, 181 sources épinglées, 28 rapports SHA-256, objets de sortie compilés non liés, CLI non émetteur `nm` PASS.
- **Gouvernance :** `GEN_R33_SOURCE_CONTRACT=PUBLISHED`, `GEN_R33_MAC_INTEL=PENDING`, `C11_RACE_FREEDOM=NOT_PROVEN`, `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`, `BUREAU_CERTIFICATION=PENDING`, PR #1 DRAFT/non fusionnée.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R34 — Independent Callback Userdata Lifetime & OS Ownership Proof Review

- **Base Mac Intel attestée :** GEN-R33 = 657 Python PASS, 33 assertions C natives PASS, 181/181 sources SHA-256 PASS, 28/28 rapports SHA-256 PASS ; validation exclusivement logicielle et non émettrice.
- **Constat prioritaire :** `output_callback` et `queue_running_listener` doivent déréférencer `ctx->queue_admission` avant de pouvoir accepter/rejeter l'admission C11 ; les compteurs de callbacks ne recensent que les entrées après le gate. Fermer le gate et observer zéro bail ne prouve pas une quiescence de l'OS.
- **Approche :** auditeur indépendant SHA-pinné R34, 14 obligations **OPEN_NOT_PROVEN (4 CRITICAL)**, 11 phases documentaires de lifetime, 20 tests source-only, preuves B07/B09/B10, contrat Apple AudioQueueDispose/Stop/RemovePropertyListener classé selon succès/erreur et nouvelle chaîne de 30 rapports SHA-256.
- **Périmètre immuable :** aucune modification des sources C originales ou candidates R26/R29/R31/R28 ; aucun callback CoreAudio réel, aucune simulation scientifique, aucune émission et aucune exposition biologique. Le binaire conserve `output_hard_denied.c` et l'audit `nm`.
- **Risques anciens inchangés :** R33 12 OPEN (3 CRITICAL), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 et 11 portes historiques du Bureau OPEN/0 résolue. Aucune signature externe.
- **Objectifs Mac Intel, encore PENDING :** 677 Python, 33 C, 187 sources intègres et 30 rapports SHA-256, avec compilation candidate `COMPILED_UNLINKED`.
- **Gouvernance :** `GEN_R34_SOURCE_REVIEW=PUBLISHED`; `GEN_R34_MAC_INTEL=PENDING`; `C11_RACE_FREEDOM=NOT_PROVEN`; `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN`; `USERDATA_LIFETIME=NOT_PROVEN`; `PHYSICAL_CUTOFF=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`; PR #1 DRAFT et non fusionnée.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R35 — Independent Pre-Admission Callback Lifetime & OS Contract Evidence Review

- **Base réelle Mac Intel** : GEN-R34 logiciel PASS (677/677 Python, 33/33 assertions natives C, 187/187 sources SHA-256, 30/30 rapports SHA-256) ; aucune validation physique ou CoreAudio active.
- **Problème** : l'OS livre `userdata` aux callbacks et ces fonctions accèdent à `ctx->queue_admission` avant toute admission atomique ; la fermeture du gate C11 ne démontre pas qu'aucune entrée tardive OS ne puisse encore accéder au contexte.
- **Revue documentaire Apple indépendante** du 16 novembre 2026 : **9 catégories** distinguant synchronie de `AudioQueueStop(true)`, disposition `AudioQueueDispose(true)` et absence de callbacks **après disposition**, matching `userdata` sur listener/remove, et **absence de preuve sur les appels `OSStatus` échoués**. Les pages Apple sont des URLs publiques vivantes, non des certificats ou copies immuables.
- **Livrables** : audit `r35_pre_admission_os_contract_review.py` avec **12 obligations ouvertes (4 CRITICAL)** et deux ancrages C31 SHA-pinnés par obligation ; 13 phases source, 20 tests Python source-only, matrice de contrat API, décision Bureau B07/B09/B10, runner Mac Intel, revue propriétaire SHA-256 de 32 rapports R20–R35.
- **Périmètre inviolable** : aucun changement C original, candidats R26/R29/R31 ou portail R28 ; aucun backend CoreAudio lié ou exécuté, aucun callback OS ou mesure, aucune simulation scientifique.
- **Risques hérités inchangés** : R34 14 OPEN (4 CRITICAL), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 et les 11 portes historiques Bureau OPEN / 0 résolue.
- **Cibles de validation Mac Intel NON attestées** : 697 tests Python, 33 assertions natives C, 193 fichiers source SHA-256, 32 rapports SHA-256 ; CLI `output_hard_denied.c`, candidates `COMPILED_UNLINKED`, audit `nm` obligatoire.
- **Décision** : `GEN_R35_SOURCE_REVIEW=PUBLISHED` ; `GEN_R35_MAC_INTEL=PENDING` ; `PRE_ADMISSION_USERDATA_LIFETIME=NOT_PROVEN` ; `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN` ; `C11_RACE_FREEDOM=NOT_PROVEN` ; `PHYSICAL_CUTOFF=NOT_PROVEN` ; `BUREAU_CERTIFICATION=PENDING`. PR #1 DRAFT, pas de fusion.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R36 — Independent Pre-Admission Lifetime Containment Architecture & Proof-Gate Design

- **Témoin antérieur Mac Intel réel :** GEN-R35 logiciel PASS (697/697 Python, 33/33 assertions natives C, 193/193 sources SHA-256 et 32/32 rapports SHA-256), mais sûreté OS/C11 et physique non prouvée.
- **Choix d'architecture concrète :** candidat C11 `generator/candidates/r36_stable_userdata_anchor.c` **isolé, non lié, non exécuté** : `userdata` serait une ancre statique unique et non réutilisable, avec propriétaire atomiquement publié et conservé jusqu'à la fin du processus. Cycle documentaire/atomique `EMPTY→PREPARED→EXPOSED→SEALED` irréversible ; admission compare le pointeur au jeton statique avant de lire le propriétaire.
- **Limite explicite :** aucune insertion dans C31 ; ses callbacks passent toujours `ctx` directement à CoreAudio. L'ancre C36 n'est **pas** une preuve de quiescence OS, d'appariement des callbacks, de *happens-before* global, de validité d'alias propriétaires ou d'arrêt matériel.
- **Livrables :** auditeur `r36_static_anchor_proof_gate.py` (12 nouveaux constats **OPEN_NOT_PROVEN, 4 CRITICAL**), 20 tests lexicaux, documentation indépendante B07/B09/B10 et matrice adversariale, compilation C36 `-c` sans liaison, binaire CLI `output_hard_denied.c` et 34 rapports privés SHA-256 R20–R36 après réussite de toutes les étapes.
- **Périmètre immuable :** code original, candidats C R26/R29/R31 et portail R28 inchangés ; zéro appel CoreAudio actif, simulation, émission acoustique/EM ou essai biologique.
- **Risques hérités ouverts :** R35 12 (4 CRITICAL), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 et **11 portes Bureau OPEN / 0 résolue**.
- **Cibles Mac Intel R36, toujours PENDING :** 717 Python, 33 assertions C natives, 200 sources intègres et 34 rapports SHA-256 ; signe `R36_STABLE_ANCHOR_OBJECT=COMPILED_UNLINKED`.
- **Verrous :** `GEN_R36_SOURCE_CANDIDATE=PUBLISHED`, `GEN_R36_MAC_INTEL=PENDING`, `R36_REAL_OS_INTEGRATION=NO`, `USERDATA_PRE_ADMISSION_LIFETIME_IN_PRODUCTION=NOT_PROVEN`, `C11_RACE_FREEDOM=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`, `BUREAU_CERTIFICATION=PENDING`. PR #1 DRAFT et non fusionnée.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


### GEN-R36 FIX1 — incident réel Mac Intel et correction locale de l'auditeur

- **Journal propriétaire du 16/11/2026 :** 200/200 fichiers source SHA-256 PASS ; ancre statique C36 SHA-256 PASS ; 33/33 assertions natives C PASS ; C36 et C31 `COMPILED_UNLINKED` ; `R36_STATIC_ANCHOR_REVIEW=PASS` ; résultat intégral **`Ran 717 tests in 31.965s` → `FAILED (errors=1)`**. **34 rapports SHA-256 finaux NON PRODUITS** par le lanceur en arrêt `set -euo pipefail`.
- **Racine unique :** test mutation `test_mutation_owner_early_read_rejected` remplace `*owner_out=NULL;` ; l'auditeur `observe` tentait `enter.index(...)` sans contrôler l'ancrage, laissant un `ValueError` brut plutôt que le `R36Error` attendu.
- **FIX1 :** vérifier explicitement cinq ancrages d'admission avant les appels `.index()` ; transformer cette mutation en rejet contrôlé `R36Error` ; conserver intégralement les tests existants et les 12 constats R36 (4 CRITICAL).
- **Périmètre :** aucun changement C (ancre C36 comprise), aucune liaison ou émission ; Manifeste SHA-256 rescéllé pour le seul auditeur modifié, README et RoadMap.
- **Gouvernance :** `GEN_R36_INITIAL_MAC_INTEL=FAIL_1_TEST_ERROR` ; `GEN_R36_FIX1_SOURCE=PUBLISHED` ; `GEN_R36_FIX1_MAC_INTEL=PENDING` ; `BUREAU_GATES=11_OPEN` ; `NEVER_SIMULATION=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`. PR #1 reste DRAFT, non fusionnée.


## GEN-R37 — Independent Static-Anchor Integration Feasibility & C11 Ownership Proof Review

- **Témoin Mac Intel antérieur réel :** GEN-R36 FIX1 PASS (717/717 Python, 33/33 assertions C natives, 200/200 sources SHA-256, 34/34 rapports SHA-256), sans preuve de sécurité C11/OS/physique.
- **Architecture proposée, sans intégration OS :** nouveau candidat `generator/candidates/r37_callback_lease_adapter.c`, non lié, non exécuté. Il propose deux entrées séparées (sortie et listener), un `FM37Lease` local à la pile du callback avec `UNUSED → ACTIVE → FINISHED`, ancre R36 une seule fois, et délégation des admissions/sorties à `fm36_try_enter` / `fm36_leave` ; aucune allocation ou libération du propriétaire.
- **Limitations prouvées par inspection :** C31 passe encore `ctx` aux deux callbacks, C37 n'est pas un ABI CoreAudio, les alias du propriétaire peuvent être libérés hors du module, le bail non atomique ne doit jamais être partagé, toutes les sorties et exceptions ne sont pas qualifiées, et `seal` ne garantit aucun arrêt matériel.
- **Livrables :** auditeur `r37_adapter_ownership_proof_review.py` SHA-pinné (**14 nouvelles obligations ouvertes, 4 CRITICAL**) ; six contrats d'intégration ; 20 tests source-only dont cinq mutations ; trois documents B07/B09/B10 ; compilation `clang -c` séparée des candidats R31/R36/R37 ; `nm` du CLI hard-denied ; génération conditionnelle de 36 rapports SHA-256 R20–R37.
- **Périmètre :** aucun changement du moteur C d'origine, R31/R36, autres candidats ou chaîne d'émission ; aucun callback CoreAudio réel ni simulation scientifique, émission acoustique/EM ou exposition biologique.
- **Obligations encore ouvertes :** R36 12 (4 CRITICAL), R35 12 (4), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 ; **Bureau historique 11 OPEN / 0 résolue**.
- **Cibles Mac Intel, PENDING :** 737 Python, 33 C, 207 sources SHA-256 et 36 rapports SHA-256. `GEN_R37_SOURCE_CANDIDATE=PUBLISHED` ; `GEN_R37_MAC_INTEL=PENDING` ; `GEN_R37_REAL_OS_INTEGRATION=NO` ; `OWNER_LIFETIME=NOT_PROVEN`; `C11_HAPPENS_BEFORE=NOT_PROVEN`; `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN`; `PHYSICAL_CUTOFF=NOT_PROVEN` ; `BUREAU_CERTIFICATION=PENDING`.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`. PR #1 DRAFT, non fusionnée.


## GEN-R38 — Independent Callback Owner-Alias & Exit-Path Completeness Audit

- **Base réellement attestée :** GEN-R37 Mac Intel logiciel PASS (737 Python, 33 assertions natives C, 207 fichiers source SHA-256, 36 rapports SHA-256), sans certification de sûreté.
- **Analyse nouvelle :** inventaire statique de **12 relations documentaires d'alias** entre `owner_ctx`, `ctx`, les deux `userdata` CoreAudio, `ptr/data`, `ctx->queue`, l'ancre R36 et le bail R37. Comptage des **2 sites `free(owner_ctx)` prépublication / 0 postpublication** dans le candidat C31 et reconnaissance de `gate_leave` dans output/listener.
- **Verdict conservateur :** **18 constats ouverts (5 critiques)**, y compris absence de propriété exclusive prouvée, première déréférence de `ctx` avant admission, manque d'appariement `fm37_finish` par vrai callback et absence de certification CoreAudio/physique. Le comptage lexical ne prouve pas que tous les chemins ou alias externes sont connus.
- **Livrables :** `audits/r38_owner_alias_exit_audit.py`, `tests/test_r38_owner_alias_exit_audit.py` (20 tests source-only et quatre mutations de chaînes), matrice d'alias, revue Bureau B07/B09/B10, obligations adversariales, launcher `RUN_GEN_R38_MAC_INTEL.command` avec chaîne de preuves R16–R37 et 38 rapports SHA-256 R20–R38 conditionnels.
- **Périmètre inviolable :** aucun fichier C modifié, pas de liaison/exécution des candidats R31/R36/R37, binaire CLI hard-denied ; aucune simulation scientifique, émission acoustique/EM ni exposition biologique.
- **Obligations héritées non déchargées :** R37 14 OPEN (4 CRITICAL), R36 12 (4), R35 12 (4), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 ; Bureau historique **11 OPEN / 0 résolue**.
- **Objectifs Mac Intel non encore attestés :** 757 Python, 33 assertions C natives, 213 sources épinglées SHA-256, 38 rapports contrôlés SHA-256 ; candidat objet `COMPILED_UNLINKED`.
- **Gouvernance :** `GEN_R38_SOURCE_AUDIT=PUBLISHED`; `GEN_R38_MAC_INTEL=PENDING`; `CALLBACK_OWNER_ALIAS_LIFETIME=NOT_PROVEN`; `CALLBACK_EXIT_COMPLETENESS=NOT_PROVEN`; `C11_RACE_FREEDOM=NOT_PROVEN`; `COREAUDIO_QUIESCENCE=NOT_PROVEN`; `PHYSICAL_CUTOFF=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`; PR #1 reste DRAFT, non fusionnée.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R39 — Independent Owner-Lifetime Enforcement & Callback Exit Contract Remediation Design

- **Témoin antérieur réel du propriétaire** : GEN-R38 Mac Intel PASS logiciel (757/757 Python, 33/33 assertions natives C, 213/213 fichiers source SHA-256, 38/38 rapports SHA-256), sans preuve de sûreté OS/C11 ou physique.
- **Correction isolée, non intégrée** : nouveau candidat `generator/candidates/r39_owner_lifetime_exit_ticket.c` avec ticket C11 `FM39Lease` et CAS de terminaison `ACTIVE→FINISHED` avant `fm36_leave`. Publication des pointeurs après admission statique R36 et avant état ACTIVE en release. Le module empêche au plus une double sortie pour **un ticket vivant, initialisé et non copié** ; cette garantie locale **AT-MOST-ONCE n'est PAS une garantie EXACTLY-ONCE**, une preuve d'owner lifetime ni un mécanisme de récupération des chemins d'erreur OS.
- **Périmètre non régressif** : C31 et ses callbacks OS ne changent pas (`userdata=ctx`), candidats C36/C37 inchangés ; C39 est compilé **en objet non lié et jamais exécuté**, aucune API AudioQueue, émission, simulation scientifique ni test biologique.
- **Audit indépendant R39** : `r39_owner_lifetime_exit_ticket_review.py`, **16 nouvelles obligations OPEN (4 CRITICAL)**, 32 preuves source SHA-pinnées, six contrats documentaires, chaîne R16–R38 de preuves recalculée, 20 tests Python source-only dont quatre mutations adversariales, trois matrices Bureau B07/B09/B10, runner `RUN_GEN_R39_MAC_INTEL.command`.
- **Portes de sécurité héritées** : R38 18 OPEN (5 CRITICAL), R37 14 (4), R36 12 (4), R35 12 (4), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 ; Bureau historique **11 OPEN / 0 résolue**.
- **Cibles de validation propriétaire Mac Intel, PENDING** : 777 tests Python, 33 assertions natives C, 220 sources SHA-256 et 40 rapports SHA-256 R20–R39. Aucun `GEN_R39_MAC_INTEL_SOFTWARE=PASS` tant que le journal natif réel n'est pas reçu.
- **Décision** : `GEN_R39_CANDIDATE_SOURCE=PUBLISHED`, `GEN_R39_MAC_INTEL=PENDING`, `OWNER_LIFETIME_IN_PRODUCTION=NOT_PROVEN`, `CALLBACK_EXACTLY_ONCE=NOT_PROVEN`, `C11_RACE_FREEDOM=NOT_PROVEN`, `OS_CALLBACK_QUIESCENCE=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`, `BUREAU_CERTIFICATION=PENDING`. PR #1 reste **DRAFT, non fusionnée**.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R40 — Independent Ticket Ownership, Copy Prevention & Completion Coverage Review

- **Baseline réelle Mac Intel :** GEN-R39 logiciel PASS (777 tests Python, 33 assertions C natives, 220 sources SHA-256, 40 rapports SHA-256), sans certification de sûreté C11/OS/physique.
- **Candidat C11 concret, source-only et jamais exécuté** : `generator/candidates/r40_opaque_ticket.h` + `.c`. Le header définit seulement un type incomplet `FM40Ticket`, la structure et **4 slots statiques jamais recyclés** demeurent privés à l'implémentation. Les clients C correctement typés ne peuvent copier le ticket **par valeur**, mais peuvent copier des pointeurs ; cast/mémoire incorrecte et alias `owner` restent hors garantie. **4 tickets par processus ne conviennent pas aux callbacks CoreAudio non bornés.**
- **Terminaison candidate :** `fm40_begin` CAS `UNUSED→RESERVED`, `fm36_try_enter`, publication `ACTIVE` ; `fm40_complete` vérifie l'identité du pointeur avant de le déréférencer et utilise CAS `ACTIVE→FINISHED` avant un seul `fm36_leave`. Garantie locale **AT-MOST-ONCE** uniquement ; `EXACTLY_ONCE=NOT_PROVEN`, `OWNER_LIFETIME=NOT_PROVEN`.
- **Preuves adversariales :** `r40_ticket_copy_completion_review.py` (**18 OPEN, 5 CRITICAL**), 36 ancrages SHA-256, 6 contrats ; `test_r40_ticket_copy_completion_review.py` (20 nouveaux tests source-only et 4 mutations) ; trois documents B07/B09/B10 ; `RUN_GEN_R40_MAC_INTEL.command` avec **vrai test négatif de compilation C** vérifiant la non-instanciabilité du type incomplet.
- **Invariants :** candidats C31/C36/C37/C39 et backend source inchangés ; C40 objet `clang -c` non lié, non chargé, non exécuté ; CLI `output_hard_denied`, symboles CoreAudio émetteurs non liés, aucune émission ou simulation scientifique.
- **Portes historiques non levées :** R39 16 OPEN (4 CRITICAL), R38 18 (5), R37 14 (4), R36 12 (4), R35 12 (4), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 ; **Bureau historique 11 OPEN / 0 résolue**.
- **Validation native future (PENDING) :** 797 tests Python, 33 assertions C natives, 228 SHA sources, 42 rapports SHA-256 R20–R40, C31/C36/C37/C39/C40 `COMPILED_UNLINKED`, rejet du type opaque par `clang`.
- **Décision :** `GEN_R40_SOURCE_REVIEW=PUBLISHED`, `GEN_R40_MAC_INTEL=PENDING`, `COPY_BY_VALUE_TYPED_CLIENT=BLOCKED_CANDIDATE`, `POINTER_ALIASING=NOT_PREVENTED`, `CALLBACK_EXIT_COMPLETENESS=NOT_PROVEN`, `C11_RACE_FREEDOM=NOT_PROVEN`, `OS_CALLBACK_QUIESCENCE=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`, `BUREAU_CERTIFICATION=PENDING`. PR #1 DRAFT non fusionnée.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.


## GEN-R41 — Independent Ticket Capacity, Pointer Aliasing & Failure-Path Containment Review

- **Baseline propriétaire réelle :** GEN-R40 Mac Intel PASS logiciel (797/797 Python, 33 assertions natives C, 228/228 sources et 42/42 rapports SHA-256), sans certification CoreAudio/C11/physique.
- **Nouveaux candidats C11 isolés** : `generator/candidates/r41_index_ticket.h` et `.c`. L'API retourne un indice de slot `FM41TicketRef` à la place d'un `FM40Ticket*`. Cette représentation évite d'exposer l'adresse du slot mais **l'indice est copiable, falsifiable et n'est pas une capacité sécurisée**.
- **Capacité et erreurs** : 4 slots statiques à usage unique, jamais recyclés, saturation refusée avec masque de faute persistant `FM41_FAULT_CAPACITY`. Un masque `atomic_uint` enregistre d'autres échecs locaux (admission, owner nul, index invalide, doublon de sortie, `leave`, inscription, seal). Contrôle du masque avant/après la réservation, mais pas de fermeture atomique avec les autres callbacks ; ce registre n'est **pas** un arrêt CoreAudio.
- **Contrat de sortie** : borne d'indice contrôlée avant accès, CAS `ACTIVE→FINISHED`, `fm36_leave` au plus une fois par slot. **EXACTLY_ONCE=NOT_PROVEN** (appel de fin manquant ou falsifié). Alias `owner_out` externe et mémoire C11 globale non prouvés. Quatre tickets à vie sont volontairement **incompatibles avec un flux OS non borné**.
- **Livrables R41** : `audits/r41_capacity_alias_failure_review.py` (**19 OPEN, dont 5 CRITICAL**, 38 témoins SHA-pinnés, six contrats), `tests/test_r41_capacity_alias_failure_review.py` (20 nouveaux tests source-only, trois mutations), trois documents B07/B09/B10, `RUN_GEN_R41_MAC_INTEL.command` compilant C41 `clang -c` en objet non lié, audit `nm`, binaire CLI hard-denied et 44 rapports SHA conditionnels.
- **Aucune régression de périmètre** : aucun changement du backend original ou C31/C36/C37/C39/C40, aucune liaison ni exécution de leur code, aucun appel CoreAudio actif, aucune simulation scientifique ni émission physique/essai humain ou biologique.
- **Portes de sécurité** : R41 19 OPEN (5 CRITICAL), R40 18 (5), R39 16 (4), R38 18 (5), R37 14 (4), R36 12 (4), R35 12 (4), R34 14 (4), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7 ; Bureau historique **11 OPEN / 0 résolue**. Les registres se recoupent.
- **Objectifs Mac Intel à confirmer par journal réel :** 817 tests Python, 33 assertions C natives, 236 sources SHA-256 et 44 rapports SHA-256 ; C41 `COMPILED_UNLINKED` et symboles émetteurs `NOT_LINKED`.
- **Décision de gouvernance** : `GEN_R41_SOURCE_CANDIDATE=PUBLISHED`, `GEN_R41_MAC_INTEL=PENDING`, `INDEX_TICKET_AUTHENTICITY=NOT_PROVEN`, `OWNER_LIFETIME_IN_PRODUCTION=NOT_PROVEN`, `CALLBACK_EXACTLY_ONCE=NOT_PROVEN`, `C11_RACE_FREEDOM=NOT_PROVEN`, `OS_CALLBACK_QUIESCENCE=NOT_PROVEN`, `PHYSICAL_CUTOFF=NOT_PROVEN`, `BUREAU_CERTIFICATION=PENDING`, PR #1 DRAFT et non fusionnée.
- `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
