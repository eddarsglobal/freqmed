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
