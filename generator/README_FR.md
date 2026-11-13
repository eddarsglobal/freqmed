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

Neuf fichiers de tests historiques R3–R13 ont été actualisés pour vérifier les nouvelles expressions au lieu de l'ancien alias. Vingt nouveaux tests R14 vérifient les chemins de propriété et de libération. **Cible Mac Intel : 275 tests Python et 33 assertions C, toujours en attente de preuve**. Le runner `RUN_GEN_R14_MAC_INTEL.command` ne relie aucun backend acoustique ou EM à l'exécutable et n'autorise aucune émission, simulation ou exposition biologique.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
