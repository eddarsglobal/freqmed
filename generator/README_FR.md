# FREQMED GEN-R8 — Correction du cycle de lecture du générateur acoustique

**Mission : développer un système qui GÉNÈRE réellement des fréquences acoustiques et électromagnétiques à travers le matériel approprié.** Le Bureau est responsable des recherches scientifiques, de la sûreté et de la certification ; le développement code porte sur les générateurs. Design Windows 11 × macOS conservé.

## GEN-R7 : preuve Mac Intel reçue le 13 novembre 2026

**134/134 tests PASS**, compilation Mac Intel, 33/33 assertions C, audit `nm` PASS, sans aucune émission. L’inventaire IOKit sur ce Mac a observé 10 entrées USB, 23 interfaces USB, 4 nœuds série d’appel, **0 interface USBTMC**. Il ne prouve la présence d'aucun générateur EM qualifié.

## GEN-R8 : défaut logiciel du moteur de sortie acoustique corrigé dans le source

Le module CoreAudio source `src/acoustic_macos.c` pouvait auparavant arrêter immédiatement la file audio après **mise en file du dernier échantillon**, sans confirmer que la file avait terminé sa lecture. Le code est désormais préparé pour :

1. Mémoriser atomiquement l’état de démarrage, de fin d’envoi, de demande de vidange et d’arrêt réel de la file.
2. Employer `AudioQueueStop(queue, false)` **uniquement après la mise en file du dernier échantillon et le démarrage effectif**, pour laisser jouer les tampons déjà en file.
3. Observer la fin de lecture réelle du point de vue de CoreAudio via `AudioQueueAddPropertyListener(..., kAudioQueueProperty_IsRunning, ...)` et `AudioQueueGetProperty`.
4. **Réserver `AudioQueueStop(queue, true)` à une erreur, une dérive du routage ou l’expiration du watchdog** ; cette coupure logicielle ne remplace pas un coupe-circuit matériel.
5. Protéger les états partagés de callback avec des variables atomiques, et conserver l’UID du périphérique strictement en mémoire.

**AUCUNE ÉMISSION PHYSIQUE dans GEN-R8.** Le backend capable de générer des échantillons PCM pour une sortie CoreAudio est toujours un fichier source **compilé mais NON LIÉ** au programme. La commande `selftest` compile des objets isolés, analyse les symboles de l’exécutable, exécute les tests logiciels, et ne lance ni son, ni RF, ni champ EM. Aucune simulation de phénomènes physiques ni faux relevé ne sont utilisés.

### Mac Intel

`bash RUN_GEN_R8_MAC_INTEL.command selftest`

`bash RUN_GEN_R8_MAC_INTEL.command probe` — lecture seule de la sortie audio macOS.

`bash RUN_GEN_R8_MAC_INTEL.command em-discover` — lecture seule de l’inventaire IOKit réel.

Le lanceur écrit uniquement ses objets temporaires sous `~/Downloads`, **n’installe aucune application, notamment pas dans `~/Applications`**. Aucune modification d’autres dépôts, aucune dépendance payante. Code Apache-2.0 ; CoreAudio/IOKit sont des dépendances du système Apple et non du code FOSS.

### Limites du stade R8

La fin indiquée par AudioQueue n’est pas une preuve indépendante de pression acoustique, de fréquence produite physiquement ou d’absence de danger. Le callback, les périphériques et les latences restent à qualifier par le Bureau avec de vrais bancs non biologiques. Le générateur EM ne peut avancer vers son pilote sans un **équipement réel identifié**, un protocole exact, un contrôle d'arrêt indépendant et les autorisations applicables.

**GEN-R8 = CANDIDATE_CODE_READY_FOR_MAC_REVIEW**, pas une certification du Bureau.

`NEVER_SIMULATION=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R9 — Propriété des callbacks et arrêt (candidat non émetteur)

Le callback CoreAudio ne demande plus lui-même la vidange de la file. La boucle de commande détient cette responsabilité et le nettoyage supprime le listener avant la libération synchrone, en remontant les erreurs. Le backend reste compilé comme objet isolé sans liaison à l'exécutable.

Commande Mac Intel GEN-R9 : 175/175 tests PASS et 33/33 assertions C PASS, preuve propriétaire reçue le 13 novembre 2026, sans émission.

Le Bureau n'a pas certifié R9. Émission acoustique/EM, simulation, exposition biologique et production : interdites.

## GEN-R10 — Récupération sur erreur et extinction (code candidat)

Le générateur acoustique source refuse les tampons PCM invalides et n'interprète plus un échec d'enfilement comme une fin réussie. Le watchdog exploite une horloge monotone réelle en plus d'une borne d'itérations; l'état de fin normale est refusé en présence de défaut. La procédure de nettoyage R9 demeure.

`bash RUN_GEN_R10_MAC_INTEL.command selftest` compile les objets de backend non reliés, vérifie l'absence de symboles d'émission dans l'exécutable puis lance les tests. Aucune activation acoustique/EM. Le matériel EM reste non qualifié. GEN-R10 a été vérifié sur Mac Intel le 13 novembre 2026 : 195/195 tests Python, 33/33 assertions C, intégrité et audit non émetteur PASS. L'examen du Bureau reste en attente.

## GEN-R11 — Intégrité des états d'arrêt et qualification documentaire EM (13 novembre 2026)

Le backend acoustique candidat conserve en mémoire la première cause de défaillance via une opération atomique; une barrière de fermeture interdit de nouvelles demandes de vidange à partir du nettoyage. Les callbacks/listeners ne peuvent déclarer une fin normale lorsqu'une défaillance a été enregistrée. La gestion des tampons et l'horloge monotone GEN-R10 sont conservées.

Le sous-système EM possède désormais une validation **de la forme des dossiers** fabricant/protocole/coupure/métrologie, compilée comme objet isolé. Un document même bien formé est toujours **NON VÉRIFIÉ** : aucun équipement EM n'est déclaré qualifié et aucune commande n'est envoyée.

Commande Mac Intel source-only : `bash RUN_GEN_R11_MAC_INTEL.command selftest`.
Résultats attendus : 215 tests Python (195 précédents + 20 nouveaux), 33 assertions C et cinq objets source isolés non liés. Les résultats restent **à confirmer sur le Mac du propriétaire**. Aucun appareil n'est installé ni émis.

GEN-R11 est un **candidat de développement**, pas une certification du Bureau. P0.01 reste IN_PROGRESS ; PR #1 DRAFT, `main` inchangée. `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R12 — Audit de durée de vie des callbacks CoreAudio (candidat non émetteur)

GEN-R11 FIX1 a été vérifié sur le Mac Intel du propriétaire, le 13 novembre 2026 : **215/215 tests Python PASS et 33/33 assertions C PASS** ; cinq objets de backend compilés mais non liés. La certification scientifique du Bureau demeure en attente.

GEN-R12 ajoute des compteurs d'activité atomiques pour les callbacks et listeners, un verrou exclusif d'écriture PCM qui signale les chevauchements comme erreurs, ainsi qu'une confirmation de libération CoreAudio et un contrôle final des callbacks encore actifs. Aucun résultat des tests Mac GEN-R12 n'est encore attesté. Les compteurs ne prouvent pas l'absence de races ou d'accès après libération en cas d'erreur OS.

Lancement source-only sur Mac Intel : `bash RUN_GEN_R12_MAC_INTEL.command selftest`. Cible : **235 tests Python** (215 historiques et 20 nouveaux), **33 assertions natives C**, cinq objets isolés non reliés, audit de symboles non émetteurs. Le générateur EM ne comporte aucun équipement qualifié ou commande matérielle autorisée.

**AUCUNE ÉMISSION PHYSIQUE.** `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R12 FIX1 — Régression des tests hérités (13 novembre 2026)

Le premier lancement réel Mac Intel de GEN-R12 (`c2c5dd39778ae40d1c44d93faddeda420ebf559c`) a confirmé l'intégrité de 70 fichiers, la compilation native des cinq objets isolés, les 33/33 assertions C et l'audit de symboles non émetteurs. La suite Python a compté **235 tests, 3 FAIL** uniquement parce que les tests R9, R10 et R11 attendaient l'ancienne formulation exacte de `AudioQueueDispose(...,true)`. Les 20 nouveaux tests R12 ont réussi.

**FIX1** conserve le backend sans modification : les trois assertions historiques vérifient désormais le contrat renforcé — `AudioQueueDispose(...,true)`, mémorisation de `FM_FAULT_DISPOSAL` lors d'une erreur, `err=1`, confirmation `dispose_confirmed=1` uniquement lors d'un retour réussi, puis refus de succès sans confirmation. L'ordre de retrait du listener avant libération reste testé.

La correction GEN-R12 FIX1 a été exécutée sur le Mac Intel : **235/235 tests Python PASS et 33/33 assertions natives C PASS**, cinq objets isolés, aucune émission. Cet état ne vaut pas certification du Bureau. Les compteurs de callbacks ne prouvent pas l'absence de races mémoire ni la sécurité en cas de libération CoreAudio échouée. **Sorties physiques toujours interdites**, `NEVER_SIMULATION=ENFORCED`, `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R13 — CoreAudio Context Lifetime & Failed-Disposal Containment (candidat)

Le contexte de callback n'utilise plus la pile : le stockage alloué avec `calloc` reste valide après le retour de fonction si la durée de vie du contexte CoreAudio est incertaine. Un verrou atomique de processus interdit toute seconde session concurrente ; en cas d'échec de construction ou de disposition de la file, la mémoire est délibérément conservée en quarantaine et les nouvelles sessions refusées. Un contexte n'est libéré que si la disposition synchrone a réussi **et** les deux compteurs de callbacks/listeners sont nuls. L'alias source temporaire `#define ctx (*owner_ctx)` est documenté comme une dette de lisibilité à auditer ; aucune fonction d'émission n'est activée.

Sur Mac Intel : `bash RUN_GEN_R13_MAC_INTEL.command selftest` (code source compilé uniquement en objets isolés, binaire utilisateur non émetteur). **Cible : 255 tests Python (235+20) et 33 assertions C**. GEN-R13 a été exécuté le 13 novembre 2026 sur Mac Intel : **255/255 tests Python PASS, 33/33 assertions C PASS**, sans sortie physique. Les garanties de comportement CoreAudio actif, de coupure matérielle et de certification du Bureau restent absentes.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R14 — Explicitation de la propriété mémoire CoreAudio (candidat non émetteur)

La révision GEN-R13 a été vérifiée sur Mac Intel : **255/255 tests Python**, **33/33 assertions C**, cinq objets compilés séparément et sortie interdite. GEN-R14 supprime le macro-alias temporaire `#define ctx (*owner_ctx)` / `#undef ctx` au profit du pointeur explicite `AcousticContext *ctx=owner_ctx` et de tous les accès `ctx->membre`. Le contexte continue d'être alloué sur tas, quarantainé et conservé lors d'une disposition CoreAudio incertaine. Les refus de session concurrente, barrières d'arrêt, compteurs de callbacks et permissions physiques restent inchangés.

Neuf fichiers de tests historiques R3–R13 ont été actualisés pour vérifier les nouvelles expressions au lieu de l'ancien alias. Vingt nouveaux tests R14 vérifient les chemins de propriété et de libération. **Validation propriétaire Mac Intel du 13 novembre 2026 : 275/275 tests Python et 33/33 assertions C PASS**, sans émission ; certification du Bureau toujours en attente. Le runner `RUN_GEN_R14_MAC_INTEL.command` ne relie aucun backend acoustique ou EM à l'exécutable et n'autorise aucune émission, simulation ou exposition biologique.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R15 — Audit exhaustif des chemins d'échec CoreAudio et propriété des ressources

La révision GEN-R14 a passé sur Mac Intel 275/275 tests Python et 33/33 assertions natives C ; les objets des moteurs restent séparés du programme non émetteur.

GEN-R15 renforce les chemins d'échec :
- Seconde lecture atomique de `fm_context_quarantined` **après** la réservation de session, avec restitution de la réservation si elle est empoisonnée.
- Quand le binding de route est refusé, un retour de disposition réussi ne suffit plus pour libérer la mémoire : les compteurs des deux types de callbacks doivent être nuls.
- Un échec d'inscription de listener est traité comme **état incertain**, avec cause de défaut `FM_FAULT_LISTENER_REGISTRATION`.
- Un échec de retrait de listener déclenche `FM_FAULT_LISTENER_REMOVAL` ; même une disposition synchrone annoncée comme réussie n'autorise plus à libérer ce contexte.
- En cas d'échec de `AudioQueueDispose`, la référence `ctx->queue` est conservée avec le contexte en quarantaine ; aucun réarmement ou réessai automatique n'est proposé.
- La libération complète exige la disposition confirmée, l'absence d'incertitude de listeners et zéro callback actif.

Les **20 nouveaux tests GEN-R15** ciblent ces choix, plus le refus effectif des commandes `emit`, `arm`, `play` et `transmit`. Premier témoin Mac Intel : **295 tests exécutés, 292 PASS et 3 FAIL hérités R9/R10/R11**, alors que compilation isolée, 33/33 assertions natives C, 82 fichiers intègres et audit de symboles PASS. **GEN-R15 initial NON VALIDÉ.** Voir `docs/GEN_R15_FAILURE_PATH_OWNERSHIP_AUDIT.md` et `docs/GEN_R15_BUREAU_REVIEW.md`.

Le binaire exécutable reste hard-denied et ne relie jamais `acoustic_macos.c`. Ces travaux n'ont aucune valeur de preuve de sortie, de sécurité sous charge ou de coupure matérielle.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R15 FIX1 — Assertions de disposition CoreAudio non fragiles (13 novembre 2026)

Le premier journal Mac Intel R15 a montré trois échecs dans les seuls tests hérités R9, R10, R11 : leurs regex imposaient une juxtaposition de `err=1;` et `} else {`, mais un commentaire de rétention a été ajouté dans la branche d'erreur. Ce constat ne modifie pas les protections du backend.

FIX1 modifie **uniquement les trois tests historiques**, le présent README, la RoadMap et le manifeste de fichiers. Les assertions inspectent désormais les branches de `AudioQueueDispose(ctx->queue,true)` : lors d'un échec, mémorisation de `FM_FAULT_DISPOSAL`, `err=1` et maintien de la référence de file ; uniquement lors du succès, `dispose_confirmed=1` et `ctx->queue=NULL`. Le test est sensible à une régression réelle mais indépendant des commentaires ou espaces. Nombre total inchangé : **295 tests**.

**GEN-R15 FIX1 validé le 13 novembre 2026 sur Mac Intel : 295/295 tests Python PASS, 33/33 assertions natives C PASS, 82/82 fichiers intègres, backend isolé non lié et aucune émission.** La certification du Bureau reste PENDING. Aucun backend physique, générateur EM, protocole matériel, autorisation, simulation ou production n'est modifié.

## GEN-R16 — CoreAudio Ownership Evidence & Static Concurrency Audit (candidat)

GEN-R15 FIX1 a été validé logiciellement sur Mac Intel : **295/295 tests Python, 33/33 assertions C PASS**. GEN-R16 ajoute un auditeur autonome FOSS avec Python standard uniquement : `audits/r16_ownership_static_audit.py`. Il lit **uniquement les vraies sources C**, tokenise les branches en ignorant les commentaires, classe les quatre sites de libération de `owner_ctx`, vérifie le contrôle de la quarantaine et les transitions d'arrêt, puis écrit un **rapport JSON auditable** hors de la source officielle, dans le dossier temporaire du runner.

Les **20 nouveaux tests GEN-R16** valident les résultats et les limites du rapport. Le runner `RUN_GEN_R16_MAC_INTEL.command` exécute l'audit statique avant compilation des objets natifs isolés et échoue sans poursuivre si le verdict est défavorable. **Validation réelle propriétaire GEN-R16 Mac Intel (13 novembre 2026) : 315/315 tests Python PASS, 33/33 assertions natives C PASS et audit statique 25/25 PASS.** L'objet acoustique reste compilé mais non lié ; Bureau PENDING.

Ce n'est **pas** une preuve formelle de concurrence C11, de sûreté du callback CoreAudio actif, de coupure matérielle ou de performance médicale. Le rapport annonce explicitement les incertitudes. Le backend acoustique et les pilotes EM restent non liés à l'exécutable et aucune simulation ni émission n'est autorisée.

Documentation : `docs/GEN_R16_STATIC_OWNERSHIP_EVIDENCE.md` et `docs/GEN_R16_BUREAU_REVIEW.md`.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R17 — Robustesse et vérification indépendante des preuves (candidat source-only)

GEN-R16 a été validé sur le Mac Intel du propriétaire : **315/315 tests Python PASS**, **33/33 assertions C PASS**, **25/25 contrôles de propriété mémoire PASS**, avec les cinq objets natifs isolés non liés et aucune émission acoustique ou EM. GEN-R17 renforce la confiance dans les preuves, sans changer les moteurs de sortie.

L'outil `audits/r17_evidence_verifier.py` est **indépendant de l'auditeur R16** : il recalcule les SHA-256 de tous les fichiers du générateur, refuse les chemins et champs JSON inattendus, contrôle les 25 identifiants obligatoires et les risques non résolus, puis revérifie les deux API publiques de sortie et la liste explicite des fichiers C liés à l'exécutable non émetteur. Il écrit un second JSON, avec SHA-256 des sources, auditeurs, runner et rapport R16. **Ce n'est pas une signature externe ni une certification de sûreté.**

Les **20 nouveaux tests R17** vérifient également la détection des preuves falsifiées et des régressions source dans des copies isolées temporaires : aucune mutation de la source officielle, aucun code émetteur exécuté et aucune simulation scientifique. La compilation et les tests natifs demeurent inchangés dans leur domaine de sûreté.

**GEN-R17 validé logiciellement le 14 novembre 2026 sur Mac Intel : 335/335 tests Python PASS, 33/33 assertions natives C PASS, 25/25 contrôles statiques PASS, deux JSON vérifiés et 92/92 fichiers intègres.** Bureau PENDING. Voir `docs/GEN_R17_EVIDENCE_INDEPENDENT_VERIFICATION.md` et `docs/GEN_R17_BUREAU_REVIEW.md`.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R18 — Renforcement de la chaîne de preuves & couverture des chemins de sortie

Le journal du propriétaire du **14 novembre 2026** atteste GEN-R17 logiciel sur Mac Intel : **335/335 tests Python, 33/33 assertions C, 25/25 contrôles R16, vérificateur R17 PASS**, 92 sources intègres, backend CoreAudio/EM compilé isolément et non lié, aucune émission.

GEN-R18 ajoute `audits/r18_control_flow_envelope.py`, un analyseur lexical borné des vraies sources C : il classe **13 retours**, **4 libérations `free(owner_ctx)`**, **6 restitutions atomiques du verrou de session**, le nombre et l'ordre des API CoreAudio et l'absence de réouverture de la quarantaine. Il confirme que chaque retour anticipé reste un refus, qu'aucune nouvelle libération de contexte n'apparaisse et que toutes les sorties après publication OS restent entourées de leurs protections de source.

Le runner `RUN_GEN_R18_MAC_INTEL.command` produit trois rapports JSON séparés : R16 source, R17 vérification de l'intégrité et R18 graphe lexical des exits. GEN-R18 relie cryptographiquement les SHA-256 des trois documents et du manifeste et vérifie l'allowlist des six sources C du **runner R18 courant**. Les **20 tests Python supplémentaires** incluent des régressions détectées sur des modifications **en mémoire** des sources ; aucun exécutable modifié n'est lancé. L'analyse lexicale ne prouve ni l'intégralité du contrôle-flow C ni l'absence de race CoreAudio.

**Validation réelle GEN-R18 sur Mac Intel, 14 novembre 2026 : 355/355 tests Python PASS, 33/33 assertions C PASS, audit R16/R17/R18 PASS et 97/97 sources intègres, objets CoreAudio/EM non liés.** La certification du Bureau reste PENDING. Aucun changement des modules `src/`, aucune simulation scientifique, aucune activation de sortie ou nouvel instrument.

Voir `docs/GEN_R18_CONTROL_FLOW_EVIDENCE.md` et `docs/GEN_R18_BUREAU_REVIEW.md`.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R19 — Adversarial Static Audit & Evidence Preservation

Le témoin réel GEN-R18 a passé sur Mac Intel : **355/355 tests Python**, **33/33 assertions C**, **25/25 contrôles R16**, vérificateur R17 et audit R18 PASS, **97/97 fichiers intègres**, sans sortie physique. Le moteur CoreAudio reste **compilé en objet isolé, non lié, jamais exécuté**.

GEN-R19 renforce les preuves sans modifier les modules `src/`. `audits/r19_adversarial_source_audit.py` ajoute **13 contrats adversariaux** sur les vraies sources C : empreintes strictes des deux backends, refus des préprocesseurs et chargements dynamiques non classés, cinq conditions exactes de quiescence, accounting des callbacks et écouteurs, verrou PCM, état atomique de quarantaine et maintien des 13 retours / 4 `free` / 6 releases R18. Le runner exécute R16 → R17 → R18 → R19 **avant toute compilation native de tests**, avec échec fermé si une preuve échoue. La liste des six fichiers C du binaire est vérifiée, et aucune sortie acoustique/EM n'est liée.

`audits/r19_evidence_archive.py` **recalcule les quatre preuves JSON réelles** après le selftest complet du Mac, revalide les octets du manifeste source, puis les copie dans `~/Downloads/FREQMED_GEN_R19_EVIDENCE_*` avec permissions `0700/0600`. Une archive contient les quatre rapports, `KIT_SHA256SUMS.txt`, `EVIDENCE_INDEX.json`, `EVIDENCE_SHA256SUMS.txt`, le commit exact apporté par le bootstrap épinglé et des empreintes vérifiables. Une altération ultérieure par rapport à ces hashes est détectée ; **l'archive n'est ni immuable, ni signée par un tiers, ni horodatée par une autorité externe**.

Les **20 nouveaux tests GEN-R19** utilisent des modifications de texte ou JSON seulement sur des copies logicielles temporaires : aucune mesure scientifique simulée, aucune sortie physique activée. **GEN-R19 validé logiciellement le 14 novembre 2026 sur Mac Intel : 375/375 tests Python PASS, 33/33 assertions natives C PASS, quatre audits R16–R19 PASS, 103/103 fichiers intègres et archive R19 créée puis vérifiée.** Bureau PENDING.

Voir `docs/GEN_R19_ADVERSARIAL_STATIC_AUDIT.md` et `docs/GEN_R19_BUREAU_REVIEW.md`. Bureau certification PENDING, RoadMap P0.01 IN_PROGRESS, PR #1 DRAFT sans fusion dans main.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R20 — Independent Evidence Reverification & Bureau Readiness

Le témoin GEN-R19 du 14 novembre 2026 confirme **375/375 tests Python**, **33/33 assertions C**, **13 contrôles adversariaux R19**, **103/103 sources intègres**, archive locale des quatre JSON créée et vérifiée. Aucun backend d'émission n'était lié ou exécuté.

GEN-R20 fournit `audits/r20_bureau_archive_review.py` et **20 nouveaux tests**, pour revérifier **l'archive R19 réelle sans jamais la modifier**. Le vérificateur exige le SHA-256 de l'ancien manifeste `c80091fd6d22e8e8bef076b4565f5640be70c53268c4238aa8d264b1207dfb28` et le commit R19 exact `e77b1ff47a0748d4e91118a865e2681680fd9c31`, pas ceux de R20. Il recalcule et croise les liens de SHA, schémas, limites, comptages et invariants de quatre preuves R16–R19 et l'état du backend.

Le runner `RUN_GEN_R20_MAC_INTEL.command` exige `FREQMED_GEN_R19_ARCHIVE_DIR` avec le dossier privé R19 existant. Après vérification, il compile seulement les objets natifs isolés et exécute la suite logicielle. Un **nouveau dossier privé R20** n'est créé qu'après le succès intégral, contenant le JSON de revérification, la grille de revue du Bureau et leurs SHA-256. Aucune modification de l'archive R19.

**GEN-R20 validé logiciellement le 14 novembre 2026 sur Mac Intel : 395/395 tests Python PASS, 33/33 assertions natives C PASS, archive R19 (103 fichiers et 4 JSON) revérifiée et 108/108 fichiers du générateur intègres.** La certification du Bureau reste PENDING. Les décisions restent `REVIEWABLE_NOT_CERTIFIED`, `BUREAU_CERTIFICATION=PENDING` et `RoadMap P0.01=IN_PROGRESS`. L'archive R19 reste modifiable par son propriétaire ; aucun certificat tiers ou contrôle matériel réel n'a été produit.

Voir `docs/GEN_R20_EVIDENCE_REVERIFICATION.md` et `docs/GEN_R20_BUREAU_READINESS.md`. `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R20 FIX1 — Python SyntaxWarning cleanup (candidat, aucune sortie)

Le journal propriétaire GEN-R20 sur Mac Intel montre quatre répétitions de `SyntaxWarning: invalid escape sequence` dans `audits/r20_bureau_archive_review.py`, sur deux chaînes de présentation Markdown autour du SHA de commit R19. Les contrôles logiciels GEN-R20 ont réussi malgré ces avertissements. FIX1 retire exactement les deux échappements antislash devant l'accent grave Markdown, sans changement de logique, d'archive ou de code natif de sortie.

Deux tests sont ajoutés à `tests/test_r20_bureau_readiness.py` : compilation de l'auditeur sous `SyntaxWarning` et `DeprecationWarning` configurés comme erreurs, et vérification du Markdown du commit sans antislash. Cible **397 tests Python (395+2) + 33 assertions C natives** sur Mac Intel. `RUN_GEN_R20_MAC_INTEL.command` reste inchangé ; le bootstrap FIX1 épingle le nouveau commit et le manifeste des 108 sources, vérifie l'archive historique R19 en lecture seule, puis lance tous les tests non émetteurs. FIX1 est **PENDING** jusqu'au journal Mac Intel.

Aucune modification de `generator/src/` ni de l'archive R19 conservée. `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R21 — Bureau Evidence Gap Review (candidat)

Le propriétaire a exécuté GEN-R20 FIX1 sur Mac Intel au commit `0812ac4a3756e795ba411ffe61a52f7f6f32e130` : **397/397 Python PASS**, **33/33 assertions natives C PASS**, **108/108 sources intègres**, `R20_ORIGINAL_R19_ARCHIVE_REVERIFICATION=PASS` (103 sources historiques, quatre rapports), warnings Python précédents non reproduits. Les backends de sortie sont restés non liés et la sortie physique bloquée.

GEN-R21 introduit `audits/r21_bureau_evidence_gaps.py`, `tests/test_r21_evidence_gaps.py`, le runner `RUN_GEN_R21_MAC_INTEL.command` et deux documents spécialisés. **Onze portes documentées, zéro levée** : chaque ligne relie la lacune R20 à un B01–B10 responsable, à une ligne de code/document réellement épinglée et à la preuve indépendante manquante. Les cinq rapports courants R16–R20 sont recomparés aux sources et à l'archive R19 d'origine en lecture seule. La documentation ne prétend pas disposer de preuves matérielles, de mesures ou de signatures indépendantes.

Cible de validation **417 tests Python (397+20) et 33 assertions C**, **113 fichiers générateur épinglés**. Le dossier privé du Bureau sera produit **après succès natif seulement**, avec quatre rapports JSON/Markdown R20/R21 et leurs empreintes SHA-256. **Mac Intel GEN-R21 PASS (417/417 Python, 33/33 C, 113/113 sources, 11 portes OPEN)** ; `EVIDENCE_GAPS_MAPPED_NOT_CERTIFIED`, `RoadMap P0.01=IN_PROGRESS`, `BUREAU_CERTIFICATION=PENDING`.

Voir `docs/GEN_R21_EVIDENCE_GAPS.md` et `docs/GEN_R21_BUREAU_REVIEW.md`. `NEVER_SIMULATION=ENFORCED`, `ZERO_COST_FOSS=ENFORCED`, `ACOUSTIC_OUTPUT=LOCKED`, `EM_OUTPUT=LOCKED`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R22 — Independent C11 & CoreAudio Lifetime Review

**Base attestée sur Mac Intel : GEN-R21 PASS**, source `01db479705fc39b5b8d72c60845c3a6d29c5c0d8`. Les **417 tests Python et 33 assertions C** ont réussi ; 113 fichiers SHA-256 PASS ; les onze portes du Bureau sont encore ouvertes et le dossier R21 a été conservé avec empreintes.

GEN-R22 approfondit trois lacunes : `C11_CALLBACK_RACE_FREEDOM`, `ACTIVE_COREAUDIO_LIFETIME`, `FAILED_OS_DISPOSAL_BEHAVIOR`. L'auditeur `audits/r22_coreaudio_lifetime_review.py` réalise **17 observations statiques bornées** sur la véritable source CoreAudio épinglée, puis émet **trois constats de risque explicitement non résolus**. Sont considérés : accès non atomiques au PCM, ordre acquire/release et chemin contrôleur, callbacks éventuellement tardifs après lecture de compteurs à zéro, statut de dispose synchrone et échec réel non observé. Le cas de succès d'`AudioQueueDispose(..., true)` est documenté par Apple comme synchrone et n'appelant plus de callbacks pour la queue libérée ; cela ne vaut pas qualification des erreurs ou preuve C11.

Le nouveau runner `RUN_GEN_R22_MAC_INTEL.command` garde les sorties acoustiques et EM non liées, le Guardian fermé et **l'archive historique R19 en lecture seule**. Il recalcule les preuves R16–R21 avant R22, puis les 33 assertions C et la suite Python complète. **20 tests Python** d'analyse des sources sont ajoutés, aucun appel actif à CoreAudio ni simulation physique. Le dossier privé R22 inclura les six fichiers R20/R21/R22 JSON/Markdown et leur manifeste SHA-256 uniquement après PASS.

**Cible Mac Intel : 437 Python (417+20), 33 C, 118 sources**, 17 observations statiques, trois risques non prouvés, onze portes ouvertes. **GEN-R22 MAC INTEL PASS (437/437 Python, 33/33 C, 118/118 sources, 17 observations statiques, 3 risques OPEN)**, `REVIEW_REQUIRED_NO_EMISSION`, Bureau PENDING, RoadMap P0.01 IN_PROGRESS.

Voir `docs/GEN_R22_C11_COREAUDIO_REVIEW.md` et `docs/GEN_R22_BUREAU_REVIEW.md`. `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.

## GEN-R23 — C11 Happens-Before & Callback Quiescence Proof Obligations (candidat)

**Témoin GEN-R22 réel sur Mac Intel, 15 novembre 2026 : 437/437 Python PASS, 33/33 C PASS, 118/118 sources SHA-256 PASS**, rapports R20–R22 (six fichiers) SHA-256 vérifiés, onze portes du Bureau ouvertes, zéro certifiée, aucune émission.

GEN-R23 introduit un registre de **15 obligations de preuve non acquittées** : cinq pour les relations happens-before entre le contrôleur, les callbacks et les champs PCM non atomiques ; cinq pour la durée de vie de userdata et la quiescence des callbacks ; cinq pour les retours d'erreur de `AudioQueueDispose`, des listeners et la quarantaine du processus. Les **30 références de source** (deux par obligation) sont contrôlées sur le véritable C natif et le manifeste courant. `audits/r23_happens_before_obligations.py` recalcule le JSON R22 à partir des rapports R16–R21 et de l'archive R19 inchangée, et conserve les trois premières portes `NOT_PROVEN/NOT_TESTED/NOT_TESTED`.

La maintenance de compatibilité R22 autorise désormais les manifests `>=118` fichiers, sans changer les 17 observations de GEN-R22 ni le témoin Mac historique. GEN-R23 ajoute **20 tests Python** de contrôle des obligations, mutations de source et fail-closed ; le lanceur `RUN_GEN_R23_MAC_INTEL.command` garde les cinq objets CoreAudio/EM **non liés**, les **33 assertions natives C**, le binaire sans émission, puis produira huit rapports JSON/MD R20–R23 avec leur SHA-256 après succès. Le code natif dans `generator/src/` demeure inchangé.

**Cible Mac Intel GEN-R23 : 457/457 Python (437+20), 33/33 C, 123 sources**, 15 obligations OPEN, aucune acquittée, 11 portes Bureau OPEN. `GEN_R23_MAC_INTEL=PENDING`, `PROOF_OBLIGATIONS_OPEN_NO_EMISSION`. P0.01 IN_PROGRESS ; Bureau PENDING ; zéro coût FOSS et aucune simulation scientifique ou émission.

Documents : `docs/GEN_R23_HAPPENS_BEFORE_PROOF_OBLIGATIONS.md` et `docs/GEN_R23_BUREAU_REVIEW.md`.
