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
- 2026-11-13 : GEN-R15 FIX1 candidat : trois assertions historiques de `AudioQueueDispose` adaptées aux branches sûres (erreur conserve la référence, succès seul confirme disposal), **aucune modification du backend acoustique ou EM** ; retest Mac Intel **295/295 attendu, non encore attesté** ; Bureau PENDING, P0.01 IN_PROGRESS, interdiction permanente de simulation et d'émission.

- 2026-11-09 : P0.00-R4 gouvernance initiale certifiée ; **l'ancien P0.01 est un audit documentaire, pas une certification du nouveau générateur**.
- 2026-11-10/12 : séries documentaires R2–R28 ; UI V4/V5 ; moteurs candidats R29–R32 en dehors de la branche officielle.
- 2026-11-12 : correction impérative de mission par le propriétaire : **FREQMED = générateurs physiques acoustique ET EM**, recherche scientifique sous Bureau. La présente refonte ne crée aucune autorisation d'émission.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
