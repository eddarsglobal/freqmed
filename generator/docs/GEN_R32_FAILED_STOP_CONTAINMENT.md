# FREQMED GEN-R32 — Independent Failed-Stop Containment & CoreAudio Ownership Safety Review

**Référence propriétaire réellement attestée : GEN-R31 FIX1, 617/617 Python, 33/33 assertions natives C, 169/169 fichiers SHA-256, 24/24 rapports SHA-256.** Cette validation concerne exclusivement des outils non émetteurs, sans preuve OS/C11 ni mesure physique.

## Pourquoi GEN-R32 ne modifie pas le candidat C31

Dans `candidates/acoustic_macos_r31.c`, le contrôleur ferme d'abord les admissions C11, puis tente `AudioQueueStop(ctx->queue,true)`. En cas de `OSStatus != noErr`, il enregistre un défaut, met le processus en quarantaine et retourne **sans disposer la file**. Cette branche évite une libération de mémoire ambiguë, mais ne prouve **aucun arrêt de la file ni du matériel**.

Un simple nouveau code de repli, une répétition de `AudioQueueStop`, une fermeture du gate atomique, un `AudioQueueDispose` forcé ou un arrêt du processus ne peuvent pas être présentés comme une solution sûre en l'absence de contrat OS et de qualification instrumentale. GEN-R32 est donc une **revue adversariale source-only**, pas un nouveau correctif C prétendument sûr.

La documentation Apple indique que `AudioQueueStop(queue,true)` est synchrone lorsque l'arrêt réussit. Elle ne documente pas de garantie de coupure après un échec quelconque. `AudioQueueDispose(queue,true)` concerne la libération de la file et des buffers, mais les garanties nécessaires en cas de retour d'erreur, y compris listeners et callbacks déjà actifs, restent à établir indépendamment. Les codes comme `kAudioQueueErr_InvalidRunState` et `kAudioQueueErr_QueueInvalidated` doivent être examinés sans attribuer des postconditions non documentées.

Sources officielles :
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audio-queue-services

## Travail livré

1. `audits/r32_failed_stop_ownership_review.py` : audit source C11/OSStatus qui réexamine la branche d'échec, les usages `ctx->queue`, l'admission tardive, les erreurs de retrait de listener et la disposition. **10 constats, dont 2 CRITICAL**, tous `OPEN_NOT_PROVEN`, deux ancrages de source C31 exacts et SHA-256 par constat. Recalcule la chaîne R16–R31 issue de l'archive R19 originale.
2. `tests/test_r32_failed_stop_ownership_review.py` : **20 nouveaux tests** des invariants source, de la non-liaison, de l'intégrité, des mutations textuelles et du dossier propriétaire. Aucune exécution de callback, aucune simulation scientifique.
3. `RUN_GEN_R32_MAC_INTEL.command` : lanceur qui reprend les audits et tests R16–R31, ajoute R32, garde le C31 en objet isolé `clang -c`, maintient l'audit `nm` du CLI non émetteur et produit **26 rapports R20–R32 SHA-256** après réussite seulement.
4. `docs/GEN_R32_BUREAU_REVIEW.md` et `docs/GEN_R32_FAILURE_CASE_MATRIX.md` : décision B07/B09/B10 et plan précis des obligations.

**Aucun C de production ni candidat C R26/R29/R31, ni portail R28, n'est modifié.** PR #1 maintenue DRAFT, sans fusion.

## Verdict possible, strictement limité

Un résultat `R32_FAILED_STOP_OWNERSHIP_REVIEW=PASS` signifie que l'audit a correctement consigné et vérifié ses **lacunes toujours ouvertes**. Il ne signifie ni race freedom, ni durée de vie de userdata démontrée, ni quiescence CoreAudio, ni arrêt physique après échec d'OSStatus.

**Cibles Mac Intel R32 (non exécutées à ce jour) : 637 tests Python, 33 assertions natives C, 175 fichiers SHA-256 et 26 rapports SHA-256.**

Les obligations antérieures restent intégralement ouvertes : R31 8 (2 critiques), R30 12 (2 critiques), R29 7, R28 5, R27 9, R23 15, R24 7, Bureau 11 (zéro résolue).

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
