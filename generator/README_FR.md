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
