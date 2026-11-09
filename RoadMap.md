# RoadMap.md — FREQMED : plateforme de recherche par mesures physiques réelles

**Version :** 0.3.3 — P0.01-R1, ouverture de l'audit documentaire des instruments réels
**Date :** 2026-11-09  
**Nom :** FREQMED (nom de travail, sans promesse médicale)  
**Mission :** développer une plateforme multilingue et multiplateforme de **mesure, acquisition, analyse et traçabilité de phénomènes acoustiques et électromagnétiques réels**. Rechercher, uniquement dans des cadres expérimentaux autorisés, s'il existe des effets physiquement et biologiquement reproductibles différents entre tissus pathologiques et tissus sains.  
**Nature du produit :** instrument logiciel de recherche empirique ; ni outil de diagnostic, ni traitement, ni dispositif d'exposition médicale.  
**Budget logiciel :** **0 CHF / EUR / USD** ; uniquement des composants open source, légalement réutilisables et redistribuables, sans licence payante, abonnement, API ou service propriétaire requis.  
**Gouvernance :** un seul `RoadMap.md`, progression séquentielle, statut `PENDING → IN_PROGRESS → TESTING → CERTIFIED` ; une validation logicielle ne prouve jamais l'efficacité clinique.  
**État :** `P0.00=CERTIFIED_GOVERNANCE_ONLY / P0.01=IN_PROGRESS_DOCUMENTARY_ONLY / CLINICALLY_VALIDATED=NO / PRODUCTION=NOT_AUTHORIZED`.

## 0. CONSTITUTION — RÈGLE ABSOLUE : « JAMAIS DE SIMULATION »

**Décision explicite du propriétaire (2026-11-09, P0.00-R1) : `NEVER_SIMULATION=ENFORCED`.** Cette règle prime sur toute architecture, toute bibliothèque et tout jalon antérieur.

### 0.1 Interdictions absolues pour FREQMED

1. **Aucune simulation** acoustique, électromagnétique, thermique, cellulaire, tissulaire ou clinique : pas de solveur de propagation, modèle virtuel d'exposition, jumeau numérique, scénario de patient virtuel ou résultat de champ calculé présenté comme étude du réel.
2. **Aucune donnée fabriquée** pour représenter un phénomène mesuré : pas de faux capteurs, faux spectres, fausses expériences, démonstrations imitant une mesure, résultats inventés, données synthétiques d'effet cellulaire ou contrôles biologiques fictifs.
3. **Aucune substitution du mesuré par le calculé :** une prédiction, un ajustement mathématique ou une visualisation ne devient jamais une preuve expérimentale. L'affichage d'une courbe ne doit utiliser que des données réellement acquises et identifiées comme telles.
4. **Aucun mode “simulation”, même caché, de secours ou pédagogique**, ni commutateur permettant de contourner les règles ci-dessus. Les composants logiciels destinés principalement à la simulation physique ne seront pas intégrés au périmètre actuel.
5. Toute violation déclenche `GUARDIAN=BLOCK`. Une demande de revenir à la simulation exigerait une modification explicite de cette règle par le propriétaire et une nouvelle revue du périmètre : aucun jalon ne peut l'autoriser silencieusement.

### 0.2 Ce qui reste autorisé : réel, vérifiable et sûr

- Analyse documentaire et revue de publications, en distinguant faits reproductibles, hypothèses et limites.
- **Acquisition de mesures réelles** à partir d'instruments correctement identifiés et, quand une précision physique est revendiquée, étalonnés (oscilloscope, analyseur de spectre, capteur acoustique, instrumentation de champ, etc.). Aucune compatibilité n'est présumée avant essai.
- Opérations de traitement des **données réellement mesurées** : unités physiques, filtres, transformée de Fourier, statistiques descriptives, incertitudes et graphiques étiquetés « MESURE RÉELLE ». L'analyse n'est pas une simulation de phénomène biologique.
- Vérification de fichiers, tests de licence, de sécurité, d'intégrité, de performances et de traductions. Les autotests purement informatiques ne doivent jamais être présentés comme essais physiques ou biologiques.
- **Génération de hertz réelle** uniquement dans une étape future de banc *non biologique*, avec instrument physique adapté, mesures indépendantes et contrôle de sécurité autorisé ; une consigne numérique ou un export audio seul n'est **pas** une fréquence physiquement vérifiée. Aucun pilote d'émission n'est autorisé à ce stade.
- Les expériences sur cellules, organismes ou humains ne sont **pas autorisées** par cette RoadMap ; elles demanderaient une institution compétente et des autorisations éthiques, biologiques, réglementaires et de sécurité distinctes, avant toute exposition.

**Définition opérationnelle :** `REAL_MEASUREMENT_REQUIRED`. Chaque acquisition doit porter une source instrumentale, un horodatage, une unité, un protocole, une configuration matérielle, un état d'étalonnage, une traçabilité et une incertitude. Les données de démonstration non mesurées sont refusées.

### 0.3 Scientifique : constat ≠ traitement

Les ultrasons et champs électromagnétiques peuvent interagir avec les cellules ou tissus dans certaines conditions documentées ; ce constat ne prouve **aucune fréquence unique pour un cancer**, ni une destruction sélective sans dommages, ni une indication thérapeutique. La fréquence en Hz ne suffit pas : pression, intensité, champ, géométrie, dose, durée et conditions expérimentales comptent. Toute affirmation de sélectivité malade/sain exige des comparaisons expérimentales réelles, contrôles négatifs, quantification des dommages hors cible, réplicats indépendants et validation appropriée. Aucun protocole thérapeutique n'est livré.

## 1. Gouvernance et licence — sans frais et sans privilège clinique

### 1.1 Politique stricte 100 % FOSS et budget zéro

- Les logiciels intégrés doivent être gratuits à utiliser et à redistribuer, **sous licence open source explicite** et compatible (MIT, BSD, Apache-2.0, ISC, etc., après examen). « Sans licence payante » ne veut pas dire « sans licence juridique » : un dépôt sans licence explicite est **BLOCKED**.
- Audit obligatoire : dépôt officiel, version et commit, texte de licence, dépendances transitives, exécutables, actifs, SBOM, notices et possibilité de build/utilisation locale sans compte payant ni service cloud requis.
- Les logiciels libres sous GPL/LGPL restent juridiquement open source et gratuits ; leur intégration est toutefois suspendue par préférence architecturale tant que leur compatibilité et obligations n'ont pas été examinées. Ne jamais les qualifier de « payants ».
- `GSAP` et `MATLAB` sont exclus de la pile : le premier n'est pas sous une licence open source sans restriction, le second est propriétaire. `FL Studio` peut être connu du propriétaire mais n'est ni intégré ni requis. Aucun outil de simulation physique (par exemple `MFEM`, `Meep`, `openEMS`, `k-Wave`, `scikit-fem`) ne constitue un candidat d'intégration au produit sous la règle R1, quelle que soit sa licence.
- **Réalisme plateforme :** macOS, Windows et iOS comprennent des dépendances système propriétaires ; aucun build natif n'est annoncé « intégralement FOSS » sans preuve. Une interface web/PWA peut constituer une distribution candidate sans boutique ; la publication App Store/TestFlight payante est exclue par budget zéro. Tout blocage de plateforme doit être documenté.

### 1.2 Guardian / certification

- Un seul fichier officiel `RoadMap.md` et **28 jalons stables**. À chaque jalon : ID, responsable, critères d'acceptation, tests, statut et traces SHA-256/version.
- Aucun jalon ne s'ouvre avant certification de son prédécesseur. `P0.01` reste bloqué tant que `P0.00` n'est pas **CERTIFIED**.
- `BLOCK` pour toute simulation, donnée expérimentale inventée, bibliothèque sans droits compatibles, coût obligatoire, contournement des autorisations, allégation de guérison ou tentative de pilotage d'exposition biologique/humaine.
- `REMEDIATE` pour manque de preuves de mesures, chaîne d'étalonnage, protocole, incertitude, reproductibilité, droits, qualité ou sécurité.
- `PASS` peut valider un contrôle documentaire/logiciel ou une mesure physique selon preuves disponibles ; il ne certifie jamais un traitement médical.
- Une analyse automatisée, même par IA, ne remplace pas une revue compétente en sécurité, biologie, clinique ou éthique lorsque nécessaire.
- **P0.00-R1 :** le propriétaire a demandé l'interdiction de simulation ; les tests documentaires de la version précédente ont PASS sur Mac Intel. **Il n'a pas encore certifié l'ensemble de la charte amendée.** Pas de signature présumée, pas d'avancement automatique.

## 2. Bureau de compétences et références scientifiques


Ces responsabilités restent **à pourvoir** ; les chercheurs cités ailleurs ne sont pas membres du projet. Une revue indépendante et qualifiée sera nécessaire avant toute expérimentation biologique ou humaine, sous autorisations séparées.

| Code | Discipline / owner role | Core duty | Status |
|---|---|---|---|
| B01 | Clinical oncology + neuro-oncology | Indications, comparators, meaningful clinical endpoints and contraindications | UNFILLED |
| B02 | Pathology, cancer cell biology, molecular biology | Diseased vs healthy phenotype definitions; biomarkers and controls | UNFILLED |
| B03 | Biophysics + mechanobiology | Forces, receptors, cell responses; causal tests and negative controls | UNFILLED |
| B04 | Métrologie acoustique et ultrasons | Propagation et cavitation mesurées sur banc non biologique autorisé ; étalonnage et sécurité | UNFILLED |
| B05 | Métrologie électrique et électromagnétique | Mesures instrumentales réelles, étalonnage et sécurité sur banc non biologique ; aucun solveur ni émission libre | UNFILLED |
| B06 | Imagerie et métrologie instrumentale | Images réellement acquises, étalonnage spatial et références physiques non biologiques | UNFILLED |
| B07 | Acoustics + digital signal processing | Waveforms, spectral accuracy, spectral artefacts and calibration | UNFILLED |
| B08 | Analyse de données réelles et logiciel scientifique | Vérification numérique de relevés instrumentaux, statistiques et incertitudes ; aucun solveur de simulation | UNFILLED |
| B09 | Multiplatform software + cyber/privacy + UX/i18n | App architecture, security, accessibility, 10 locales | UNFILLED |
| B10 | Safety/regulatory quality + ethics/biostatistics | Risk management, preregistration, study design, review gates | UNFILLED |

### 2.1 Publicly documented scientific references (NOT project members)

These are **literature and expertise references** only. No endorsement, partnership, invitation accepted, personal participation, or medical validation is implied. Affiliation information should be refreshed before any outreach.

| Branch | Reference | Why study their work | Source |
|---|---|---|---|
| Clinical oncology / neuro-oncology / TTFields | **Prof. Roger Stupp** (Northwestern) | Randomized clinical studies and tumor-treating-fields evidence | [R01](https://www.neurology.northwestern.edu/faculty/profile.html?xid=37377) |
| Oncology / cancer immunology | **Prof. Elizabeth M. Jaffee** (Johns Hopkins) | Tumour microenvironment and cancer immunology | [R02](https://prescancerpanel.cancer.gov/members/jaffee) |
| Quantitative pathology | **Prof. David L. Rimm** (Yale) | Biomarkers, microscopy, pathological measurement and reproducibility | [R03](https://medicine.yale.edu/profile/david-rimm/) |
| Cellular mechanobiology / neuroscience | **Prof. Ardem Patapoutian** (Scripps) | PIEZO mechanosensitive channels and how cells detect mechanical forces | [R04](https://www.scripps.edu/faculty/patapoutian/) |
| Histotripsy / biomedical engineering | **Prof. Zhen Xu** (University of Michigan) | Image-guided tissue disruption through acoustic cavitation | [R05](https://bme.umich.edu/people/xu-zhen/) |
| Biomedical ultrasonics / drug delivery | **Prof. Constantin Coussios** (Oxford) | Therapeutic ultrasound, ultrasound-triggered delivery, translational devices | [R06](https://eng.ox.ac.uk/people/constantin-coussios) |
| MRI-guided focused ultrasound / neuro applications | **Prof. Kullervo Hynynen** (University of Toronto) | Focused ultrasound fields, targeting and imaging-guided interventions | [R07](https://medbio.utoronto.ca/faculty/hynynen) |
| Molecular imaging / radiology | **Prof. Katherine Ferrara** (Stanford) | Quantitative imaging and targeted delivery under ultrasound | [R08](https://med.stanford.edu/profiles/katherine-ferrara) |
| Acoustic cavitation / physical acoustics | **Prof. Timothy Leighton** (Southampton) | Bubble physics, sound–matter interaction, experimentally verified effects | [R09](https://www.southampton.ac.uk/engineering/research/impact/bubble_acoustics.page) |
| Digital signal processing / audio | **Prof. Julius O. Smith III** (Stanford, emeritus) | Audio synthesis, signal theory, numerical DSP | [R10](https://music.stanford.edu/people/julius-smith) |
| Real-time sound programming | **Prof. Miller Puckette** (UC San Diego, emeritus) | Max and Pure Data, programmable audio systems | [R11](https://msp.ucsd.edu/bio.htm) |
| Audio signal processing / scientific programming | **Prof. Brian McFee** (NYU) | Audio features, open-source `librosa`, scientific validation | [R12](https://steinhardt.nyu.edu/people/brian-mcfee) |
| Biomedical signals / scientific computing | **Dr. Alexandre Gramfort** (research scientist; formerly Inria) | Biosignals, scientific software, MNE-Python and machine learning | [R13](https://alexandre.gramfort.net/) |
| Identification de systèmes à partir de mesures | **Prof. Steven L. Brunton** (University of Washington) | Travaux de référence uniquement ; aucun simulateur ni modèle de phénomène à intégrer | [R14](https://www.me.washington.edu/facultyfinder/steve-brunton) |

**Open scientific questions ≠ demonstrated “undetermined powers.”** Maintain a *Hypothesis Registry* listing negative results, unsupported ideas, confidence levels, competing mechanisms and falsifiable predictions. Never label an unknown effect as confirmed.

## 3. Architecture de mesure expérimentale (sans simulation)

### 3.1 Modules, tous soumis aux gates

1. **Evidence Desk :** recensement des publications, bibliographies, contradictions, résultats négatifs et statut des preuves.
2. **Instrument Capture :** lecture et traçabilité de fichiers et flux issus de vrais instruments (connexion aux instruments **désactivée** avant validation matérielle et de sécurité).
3. **Signal Measurement & Analysis :** analyse de signaux effectivement acquis, affichage temporel/spectral, calcul d'unités et métrologie ; jamais de courbe présentée comme mesurée sans source réelle.
4. **Experimental Record :** protocole et conditions réels, étalonnage, contrôles et incertitudes, comparaison de sessions sans inventer des effets biologiques.
5. **Independent Validation Guardian :** preuves SHA-256, qualité, licence, revue, sécurité, conformité des données, verrouillage des fonctionnalités d'exposition.

**Plan de génération physique de fréquences :** module futur uniquement pour un banc instrumenté non biologique, après sécurité et contrôle indépendants. Les haut-parleurs, électrodes, transducteurs ultrasonores et émetteurs RF ne seront pas pilotés dans les phases actuelles. Les formes d'onde numériques ne sont pas assimilées à des champs ou pressions effectivement produits.

### 3.2 Candidats technologiques — audit restant à faire

| Domaine | Candidats FOSS à auditer, **aucun adopté** | Limites |
|---|---|---|
| Web/PWA | React, D3, Three.js, React Flow (packages open source seulement) | Licences de tous les actifs et dépendances ; aucune courbe fictive |
| Coque desktop | Tauri 2 | Dépendances SDK propriétaires éventuelles et faisabilité hors frais |
| Données de mesure | SQLite (domaine public), CSV, JSON, WAV et bibliothèques FOSS de lecture | Métadonnées instrumentales et provenance obligatoires |
| Analyse sur **mesures réelles** | NumPy/SciPy, RustFFT, librosa selon utilité réelle | Interprétation limitée aux mesures ; vérification numérique distincte d'une preuve physique |
| Connexion instrumentale future | Bibliothèques et pilotes à découvrir sous licences compatibles | **BLOCKED** jusqu'au banc réel, protocole, sécurité et preuve de compatibilité |
| Solveurs et simulateurs | **Aucun** | **EXCLUDED_BY_NEVER_SIMULATION** indépendamment du statut FOSS |

**Audit P0.01 antérieur :** `P0_01_AUDIT_OSS.md` / `P0_01_COMPONENT_INVENTORY.csv` (version 0.2.0) constituent des **archives documentaires non applicables aux choix d'intégration R1**. Leur classement de 15 candidats est **supplanté** par le nouveau périmètre ; un audit actualisé des composants de mesure doit être réalisé et vérifié avant toute adoption.

### 3.3 Langues et accessibilité

**10 UI locales :** `en` (défaut), `fr`, `de`, `ar` (RTL), `es`, `pt`, `hr`, `it`, `zh`, `ko`. Les valeurs physiques restent invariantes entre traductions ; équivalences de mots, de décimales et d'unités testées.

### 3.4 Chaîne de preuve pour chaque mesure

`measurement_id`, type d'instrument, marque/modèle si disponible, numéro d'identification non sensible, date/heure, méthode d'acquisition, capteur, gamme/limites, état d'étalonnage, paramètres de capture, unité, débit d'échantillonnage, incertitude, référence de protocole, contrôles, fichier brut original et empreinte SHA-256. Une mesure non vérifiable peut être archivée comme **non qualifiée**, jamais présentée comme validation.

## 4. RoadMap — 28 jalons, ordre strict

### P0 — Fondation et audit

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| **P0.00** | Charte et gouvernance R4 | Constitution **JAMAIS DE SIMULATION**, FOSS zéro coût, dix langues, sécurité, bureau et règle de certification cohérents | Contrôle Mac Intel sur commit R3 et décision explicite du propriétaire ; aucun aval clinique | B09+B10 / Owner | **CERTIFIED — GOVERNANCE_ONLY** |
| P0.01 | Ré-audit des technologies de **mesure réelle** | Inventaire documenté : provenance, licence gratuite et compatible, dépendances transitives, faisabilité instruments et Mac Intel ; aucun solveur retenu | SBOM, scan droits, étude sans installation payante, rapport d'écarts | B05+B07+B09 | **IN_PROGRESS — DOCUMENTARY_ONLY_R1** |
| P0.02 | Bibliographie critique et résultats expérimentaux | ≥30 sources vérifiables, mécanismes séparés des hypothèses, limites et résultats négatifs inclus | Sources/DOI contrôlés, revue critique, absence d'allégations indues | B01+B02+B03+B10 | PENDING |
| P0.03 | Sécurité et cadre d'usage non médical | Pas d'exposition humaine ou biologique, pas de commande d'émetteurs, registre risques/permissions | Audit de fonctions et dispositifs, contrôle des permissions, BLOCK sur contournement | B01+B04+B05+B10 | PENDING |
| P0.04 | Première question de mesure réelle | Choisir un phénomène **non biologique** objectivement mesurable, témoins physiques et équipement disponible ; pas d'étude tissulaire non autorisée | Faisabilité instrumentale et protocole de métrologie | B04+B05+B07 | PENDING |

### P1 — Spécification de métrologie

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P1.01 | Unités physiques et métadonnées | Hz, Pa, V/m, durée, mesure/étalonnage/incertitude définis, sans nombres arbitraires assimilés à des données | Tests dimensionnels et conformité aux métadonnées de vrais relevés | B05+B07+B08 | PENDING |
| P1.02 | Chaîne de mesure et plan d'étalonnage | Instruments et capteurs documentés ; limites, bande passante, précision et risques connus | Preuves de calibration et contrôle indépendant ou état NON_QUALIFIÉ | B04+B05+B07 | PENDING |
| P1.03 | Provenance et confidentialité | Conservation des données **brutes mesurées**, sources autorisées, droits d'usage et aucun identifiant patient | Hash, contrôle fichiers bruts, rejet de métadonnées manquantes | B06+B09 | PENDING |

### P2 — Studio de données de mesures réelles

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P2.01 | Import de vraies acquisitions | Import WAV/CSV/JSON de capture réelle seulement, label mesure/non qualifiée, aucune génération fictive | Import et vérification d'au moins un fichier d'instrument réel avec SHA | B07+B09 | PENDING |
| P2.02 | Analyses et graphiques fondés sur les relevés | Spectres FFT, temporel, amplitude, unités, chaîne de mesure et incertitude en affichage | Recalcul indépendant sur fichier acquis réel ; zéro écran de faux résultats | B07+B08+B09 | PENDING |
| P2.03 | Interface locale en dix langues | Parcours adapté aux cinq cibles quand techniquement réalisable sans coût et sans SDK obligatoire non autorisé | Tests accessibilité, traduction et chaîne métrologique sur chaque build disponible | B09 | PENDING |

### P3 — Vérifications instrumentales réelles non biologiques

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P3.01 | Mesure acoustique sur banc non biologique | Au moins une acquisition instrumentée autorisée ; préciser capteur, spectre réel, limite et incertitude | Journal instrument, source brute, contrôle et répétition indépendante | B04+B07+B08 | PENDING |
| P3.02 | Mesure électrique/EM sur banc non biologique | Aucune émission RF libre ; mesure instrumentée existante ou banc matériel autorisé avec protections | Preuve de configuration et de sécurité, relevés bruts, contrôle indépendant | B05+B08+B10 | PENDING |
| P3.03 | Qualité et comparabilité des mesures | Relier spectres et niveaux réels à conditions instrumentales, témoins non biologiques | Répétabilité, validité d'étalonnage, analyse d'incertitude | B04+B05+B08 | PENDING |

### P4 — Analyse scientifique de résultats empiriques

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P4.01 | Registre mécanismes et niveau de preuve | Chaque mécanisme renvoie aux publications, aux études expérimentales et aux contre-exemples ; aucun « Hz qui guérit » | Traçabilité et revue scientifique critique | B01+B02+B03 | PENDING |
| P4.02 | Comparaison de données réellement mesurées | Comparaison légitime de campagnes et de témoins physiques ; aucune inférence de sélectivité cellulaire sans expériences autorisées | Audit sources, biais, incertitude, résultat nul conservé | B02+B03+B08 | PENDING |
| P4.03 | Registre d'hypothèses testables sans générateur médical | Questions précises, falsification, variables mesurables, critères d'arrêt, aucun conseil thérapeutique | Critique indépendante et contrôle des allégations | B03+B08+B10 | PENDING |

### P5 — Qualification indépendante et audit

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P5.01 | Reproductibilité de mesures sur instrument réel | Acquisition répétée et revue par second opérateur/instrument si disponible ; seuils justifiés | Fichiers bruts, logs, calibration et rapport de répétabilité | B04+B05+B07+B08 | PENDING |
| P5.02 | Audit anti-tromperie et de sécurité | Rejet des preuves fictives, dérives de calibration, affirmations de guérison ou de sélectivité non étayées | Scénarios de sécurité documentaires, vérification des traces ; `BLOCK` | B01+B09+B10 | PENDING |
| P5.03 | Reproductibilité du logiciel et droits | SBOM, provenance, absence de télémétrie et de dépendances payantes ; aucune commande matérielle cachée | Build reproductible, audits de fichiers/deps, revue sécurité | B09+B10 | PENDING |

### P6 — Décision institutionnelle pour d'éventuelles expériences biologiques

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P6.01 | Question biologique et protocole soumis à revue | Hypothèse vérifiable, témoins sains/pathologiques et dommages hors cible, comité qualifié, plan statistique | Revue indépendante et dossier autorisations préalable | B01+B02+B03+B10 | PENDING |
| P6.02 | Dossier de sécurité et mesures sur banc passif | Inventaire matériel, incertitudes et analyse de risque ; pas d'exposition biologique | Preuve sur banc non biologique, revue sécurité | B04+B05+B06+B10 | PENDING |
| P6.03 | Porte d'autorisation des expériences sur matière biologique | Partenaire institutionnel, règles biosécurité/éthique et autorisations réglementaires écrites | Autorisations distinctes avant acte expérimental | B01+B02+B10 | **LOCKED** |

### P7 — Toute voie de dispositif ou recherche clinique ultérieure

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P7.01 | Classification réglementaire | Analyse du champ d'application selon territoire et de l'usage médical envisagé | Évaluation qualifiée et traçable | B10 | **LOCKED** |
| P7.02 | Sécurité du dispositif et qualité si applicable | Risques, cycle de vie, matériel, essais et conformité définis conformément au cas réel | Audits indépendants et conformité démontrée | B09+B10 | **LOCKED** |
| P7.03 | Décision d'investigation clinique | Études cliniques seulement si preuves et autorisations préalables suffisantes | Approbations institutionnelles et réglementaires | B01+B10 | **LOCKED** |

### P8 — Publication

| ID | Travail | Critères d'acceptation | Test et preuve | Responsable | Statut |
|---|---|---|---|---|---|
| P8.01 | Application de **mesures réelles uniquement** | Présenter données acquises et statut métrologique, sans simulation, prédiction thérapeutique ou commande d'émetteurs médicaux | Vérification sur fichiers réellement mesurés, audit sécurité/licences, 10 langues | B09+B10 | **LOCKED** |
| P8.02 | Produit médical éventuel | Requiert voie réglementaire distincte, preuves cliniques et autorisation explicite | Décision institutionnelle + réglementaire formelle | B01+B10 | **LOCKED / HORS PÉRIMÈTRE** |

### 4.1 Gates de sortie

- **G0 :** la charte R3 est approuvée explicitement par le propriétaire, puis vérifiée sur Mac Intel ; aucun franchissement avant certification.
- **G1 :** droits, instruments, données et références traçables ; aucune dépendance de simulation intégrée.
- **G2 :** le logiciel affiche uniquement des données physiques acquises, avec provenance et contrôle de métrologie.
- **G3 :** des mesures non biologiques, si autorisées et possibles, sont répétées indépendamment.
- **G4 :** une hypothèse biologique n'est jamais confondue avec un résultat clinique ; des données réelles sont exigées.
- **G5 :** revue scientifique, sécurité et licences indépendante de toute promesse de traitement.
- **G6 :** projet d'étude uniquement ; aucune autorisation automatique d'expérimentation biologique.
- **G7 :** toute voie clinique requiert les approbations et preuves réglementaires pertinentes.

## 5. Tests et blocages non négociables

1. `NO_SIMULATION`: absence de tout module d'émulation, jeu de données expérimental fabriqué, solveur et affichage non mesuré prétendant représenter le réel.
2. `REAL_DATA_ONLY`: tout spectre ou métrique physique visible possède un fichier brut issu d'un instrument, la provenance et l'unité adéquate.
3. `CALIBRATION_REQUIRED`: précision physique revendiquée interdite sans attestation de calibration ou incertitude indiquée.
4. `NO_MEDICAL_EXPOSURE`: aucun signal destiné à un patient, aucune exposition biologique ou humaine, aucune sortie vers électrodes, transducteurs thérapeutiques ou émetteurs RF.
5. `NO_CLINICAL_CLAIMS`: pas de traitement proposé ni de recommandation sur une fréquence pour une maladie.
6. `FOSS_ZERO_COST`: interdiction de logiciel/SDK/service commercial obligatoire ou de licence payante ; SBOM et droits transitifs vérifiés.
7. `NO_FABRICATED_MEASUREMENT`: données absentes = interface « données indisponibles » et jamais un exemple artificiel ressemblant à un résultat.
8. `TRACEABILITY`: conservation brute SHA-256, protocole, instruments et versions de logiciels.
9. `LOCALE_PARITY`: dix langues, arabe RTL ; unité et données physiques identiques entre traductions.
10. `SEQUENTIAL_GUARD`: aucune étape suivante avant `CERTIFIED` précédent ; revue humaine/institutionnelle spécialisée aux gates concernés.

## 6. P0.00-R1 — décision et exécution

**Base de provenance :** `RoadMap.md` v0.2.0, SHA-256 `fad5e2f7b9e416ead84c7b00beb865383f3caa5725ae11df450652f836f3d6c6`.  
**Amendement demandé :** interdiction permanente de simulation, remplacement de tous les livrables orientés simulation par des étapes empiriques de mesure réelle ; maintien de la politique FOSS à zéro coût, des dix langues et des 28 jalons.

**État de preuve historique :** la validation P0.00 v0.2.0 était `PASS`, sans certification. La v0.3.0 a ensuite passé R1 et R2 sur Mac Intel selon les journaux fournis par le propriétaire (R1 : 6/6 fichiers, 3/3 autotests ; R2 : 5 fichiers, 4/4 autotests). La nouvelle version R3 nécessite sa propre vérification locale.

**Décision restante :** revue du propriétaire sur le périmètre `NO_SIMULATION` et la charte actualisée avant `P0.00=CERTIFIED`. `P0.01` ne commence pas avant cette certification.

**Interdit actuellement :** pilotes matériels réels, émission ciblant le corps, expérimentation biologique, essais sur humains, validation thérapeutique, distribution en production.

## 7. Sources de recherche conservées (non affiliées)

- [S1] [FDA — champ de l'approbation de TTFields](https://www.fda.gov/news-events/press-announcements/fda-approves-first-its-kind-device-treat-pancreatic-cancer).
- [S2] [FDA PMA P250034](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id=P250034).
- [S3] [Focused Ultrasound Foundation — mécanismes](https://www.fusfoundation.org/the-technology/mechanisms-of-focused-ultrasound/).
- [S4] [US NCI — HIFU](https://www.cancer.gov/publications/dictionaries/cancer-terms/def/high-intensity-focused-ultrasound-therapy).
- [S5] [ISO 14971 — gestion des risques](https://www.iso.org/standard/72704.html).

**VERDICT DOCUMENTAIRE R3 :** `R3_REVIEW_REQUIRED`; `P000_CERTIFIED=NO`; `P001=BLOCKED_BY_P000`; `NEVER_SIMULATION=ENFORCED`; `PRODUCTION=NOT_AUTHORIZED`.


## 8. P0.00-R3 — Revue de cohérence avant certification

**2026-11-09 — correctif strictement documentaire :** fonctions B04, B05, B06 et B08 recentrées sur des mesures physiques réelles, suppression des responsabilités de simulation et clarification de la référence scientifique B14. Aucun composant, solveur ou générateur de signal n'est intégré.

**Preuves antérieures communiquées par le propriétaire :** R1 (6/6 fichiers et 3/3 autotests PASS) et R2 (5 fichiers et 4/4 autotests PASS), macOS Intel x86_64. Le journal R1 a été contrôlé avec SHA-256 `f461b548e6842ed34733461130bb417f9a2fb1736cfbac2c7c303fe3785c1334`. Les journaux sources ne sont pas archivés dans le dépôt GitHub. Le contrôle R3 sur Mac reste nécessaire.

**Décision :** « au suivant » autorise cette remédiation documentaire, **pas la certification de P0.00**. Le propriétaire doit approuver explicitement la charte amendée R3 après les vérifications.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `P0.00=IN_PROGRESS` ; `P0.01=BLOCKED_BY_P0.00` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## 9. P0.00-R4 — Certification documentaire de gouvernance

**Date UTC :** `2026-11-09T16:37:29+00:00`
**Vérification des sources :** Mac Intel, dépôt Git propre, branche main, remote GitHub vérifié, RoadMap Git blob `aaced45de14909dbe8628321278d500beda667a1`, commit `be2f743ef0960292ef405f032502d0977e22b43b`.
**Consentement :** approbation explicite du propriétaire par commande locale TTY `APPROVE_FREQMED_P000_GOVERNANCE_ONLY` (aucune signature personnelle ou expertise médicale prétendue).
**Périmètre :** certification de la charte et des contrôles documentaires uniquement. Elle n'atteste ni étalonnage, ni mesure physique, ni effet sur cellules, ni conformité médicale.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `P0.00=CERTIFIED_GOVERNANCE_ONLY` ; `P0.01=PENDING_ELIGIBLE_NOT_STARTED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.


## 10. P0.01-R1 — Audit documentaire des instruments réels

Ouverture de `P0.01=IN_PROGRESS_DOCUMENTARY_ONLY` le 9 novembre 2026, sur la base de P0.00 certifié. Sources et candidats documentés dans [docs/P0_01_R1_AUDIT_SCOPE.md](docs/P0_01_R1_AUDIT_SCOPE.md). **Aucune dépendance installée ou approuvée** ; contrôles Mac, licences transitives et moyens d'acquisition encore à vérifier.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
