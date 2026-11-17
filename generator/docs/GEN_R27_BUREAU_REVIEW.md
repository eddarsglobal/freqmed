# FREQMED — Bureau GEN-R27 : audit adversarial C11 et propriété du contexte

**Verdict maximal proposé : `ADVERSARIAL_GAPS_CONFIRMED_NO_RUNTIME_SAFETY_PROOF`.** Il s'agit d'un audit du code C isolé, non d'une preuve de sûreté ni d'une autorisation de sortie.

### Mandats d'examen

**B09 — Concurrence C11 (priorité haute).** Vérifier que le nouveau `pcm_writer_gate` protège effectivement les champs PCM non atomiques, mais aussi que le contrôleur ne peut pas invalider `ctx->queue` pendant qu'un callback utilise `fill_audio`. Qualifier les accès à la file et aux buffers, l'appel `AudioQueueEnqueueBuffer` dans la section critique, les conséquences d'une réentrance et les garanties du modèle mémoire. **Le succès d'un test textuel ne prouve pas un happens-before.**

**B07 — Durée de vie et callbacks CoreAudio (priorité haute).** Clarifier les contrats distincts de `AudioQueueNewOutput`, `AudioQueueRemovePropertyListener` et `AudioQueueDispose(queue,true)`, y compris le retour d'erreur. Exiger une preuve de fin de toutes les entrées callback/listener avant tout changement pouvant rendre `queue` invalide. Les compteurs d'activité enregistrent des entrées et sorties, mais une lecture zéro ne garantit pas l'absence d'une nouvelle entrée.

**B10 — Échec système et propriété des ressources (priorité haute).** Le correctif GEN-R26 conserve le tas après publication et condamne le processus. Une telle stratégie réduit un risque de `free` prématuré, mais laisse l'OS potentiellement propriétaire de ressources non libérées ; établir une borne mémoire/queue et une politique de destruction du processus. Conserver le tas **n'est pas** prouver qu'une queue disposée reste exploitable.

### Portes et non-régression

| Objet | Verdict GEN-R27 |
|---|---|
| Modifications au C historique `src/acoustic_macos.c` | **0** |
| Modifications au candidat C isolé GEN-R26 | **0 nouvelles** |
| GEN-R26 : trois corrections dans la source isolée | Maintenues, non intégrées |
| Constats adversariaux GEN-R27 | **9 OPEN_NOT_PROVEN** |
| Obligations de preuve GEN-R23 | 15 OPEN |
| Lacunes GEN-R24 | 7 OPEN |
| Portes de certification du Bureau | **11 OPEN, 0 résolue** |
| Race C11 reproduite | Non |
| Quiescence des callbacks CoreAudio | NOT_PROVEN |
| Échec réel de `AudioQueueDispose` | NOT_TESTED |
| Signature indépendante | NONE |
| Émission ou expérience physique | NOT_AUTHORIZED |

Les vingt nouveaux tests adversariaux ne sont que des tests sur texte source et intégrité. La suite complète visée est **537/537 Python, 33/33 assertions natives C et 144/144 sources intègres**, dossier de seize rapports R20–R27 avec SHA-256 après réussite réelle. `main` ne doit pas être modifiée ; la PR reste **DRAFT**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
