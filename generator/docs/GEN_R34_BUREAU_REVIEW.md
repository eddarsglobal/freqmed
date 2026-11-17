# FREQMED GEN-R34 — Independent Bureau B07/B09/B10 Userdata Lifetime Review

**Verdict maximal : `USERDATA_LIFETIME_OBLIGATIONS_MAPPED_OS_C11_PROOF_OPEN`.** Le succès d'un audit du code ne ferme aucune obligation.

### B07 : callback et listener avant `try_enter`

`UD34_01` et `UD34_02` sont **CRITICAL / OPEN_NOT_PROVEN** : les expressions `&ctx->queue_admission` exigent un contexte C encore valide au moment où CoreAudio appelle le callback. Le gate atomique ne peut pas assurer sa propre durée de vie. Les fonctions `AudioQueueNewOutput` et `AudioQueueAddPropertyListener` qui reçoivent `userdata` et leurs échecs nécessitent un contrat OS ou une preuve externe d'exclusion des callbacks tardifs.

`UD34_04` est **CRITICAL / OPEN_NOT_PROVEN** : un retour `AudioQueueDispose != noErr` ne garantit ni file valide ni file détruite. Le fait que le code ne libère pas `owner_ctx` n'établit pas la sûreté de `AudioQueueRef`.

### B10 : arrêt physique

`UD34_03` est **CRITICAL / OPEN_NOT_PROVEN** : un échec d'`AudioQueueStop` n'est pas une coupure acoustique démontrée. Une session en quarantaine peut encore avoir des ressources OS possiblement actives. Aucune activation physique ou biologique n'est autorisée.

### B09 : C11, compteurs, file et PCM

`UD34_08`–`UD34_13` sont ouverts : les compteurs incrémentés après admission ne recensent pas l'entrée pré-admission ; `closed_and_empty` est un prédicat C11, pas une preuve de quiescence OS ; `ctx->queue=NULL` demeure non atomique, et `AudioQueueEnqueueBuffer` doit encore être qualifié face à la concurrence avec stop/dispose.

| Porte | Statut |
|---|---|
| GEN-R34 | **14 OPEN / 4 CRITICAL** |
| GEN-R33 | **12 OPEN / 3 CRITICAL** |
| GEN-R32 | 10 OPEN / 2 CRITICAL |
| GEN-R31 | 8 OPEN / 2 CRITICAL |
| GEN-R30 | 12 OPEN / 2 CRITICAL |
| GEN-R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN / 0 résolue** |
| Preuve lifetime `userdata` | **NOT_PROVEN** |
| Quiescence OS | **NOT_PROVEN** |
| Arrêt physique | **NOT_PROVEN** |
| Signatures externes | **NONE** |

**Gouvernance :** aucun code C original ou candidat modifié, aucun callback lancé, PR #1 **DRAFT et non fusionnée**. Le jalon GEN-R34 vise uniquement l'audit source et le témoin Mac Intel (677 Python, 33 assertions C, 187 fichiers SHA-256 et 30 rapports SHA-256). Aucune certification ni passage en production.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
