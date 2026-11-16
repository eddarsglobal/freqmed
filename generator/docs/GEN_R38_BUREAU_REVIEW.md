# FREQMED GEN-R38 — Independent Bureau B07/B09/B10 Owner-Alias Exit Audit

**Verdict maximum : `OWNER_ALIAS_EXIT_PATHS_MAPPED_RUNTIME_LIFETIME_NOT_PROVEN`.**

### B07 : durées de vie OS et mémoire pré-admission

`AL38_01`, `AL38_02`, `AL38_04` sont **CRITICAL / OPEN_NOT_PROVEN**. Le code C31 continue de remettre `ctx` directement à `AudioQueueNewOutput` et au listener ; la première évaluation de `ctx->queue_admission` précède le bail. Les erreurs d'arrêt, de disposition et de désinstallation listener n'ont pas de postcondition de quiescence suffisamment établie dans cette revue.

### B09 : propriété, alias, C11 et chemins d'issue

`AL38_03` est **CRITICAL / OPEN_NOT_PROVEN** : une ancre statique ne peut interdire qu'un alias externe libère son contexte. Le contrôle de sortie C31 est un dénombrement de points de passage **textuels**, pas une analyse de programme formelle, et n'établit aucune preuve temporelle de quiescence OS. Le bail local C37 n'est pas atomique, sa bonne initialisation et son appariement `enter/finish` restent externes au module. `ctx->queue` partage un accès non atomique entre chemins sans preuve C11 générale.

### B10 : sûreté physique

`AL38_05` est **CRITICAL / OPEN_NOT_PROVEN** : aucune vérification instrumentale de l'arrêt physique, aucun droit d'émettre. La publication de résultats de tests `nm` et SHA-256 ne doit jamais être interprétée comme une mesure matérielle.

| Porte | Statut |
|---|---|
| GEN-R38 | **18 OPEN, dont 5 CRITICAL** |
| GEN-R37 | 14 OPEN, 4 CRITICAL |
| GEN-R36 | 12 OPEN, 4 CRITICAL |
| GEN-R35 | 12 OPEN, 4 CRITICAL |
| GEN-R34 | 14 OPEN, 4 CRITICAL |
| GEN-R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 OPEN |
| R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN / 0 résolue** |
| C31/C36/C37 unifiés | **NON** |
| Preuve `userdata` réel | **NOT_PROVEN** |
| Baux réellement appariés | **NOT_PROVEN** |
| Libération sûre des alias | **NOT_PROVEN** |
| Quiescence CoreAudio | **NOT_PROVEN** |
| Arrêt physique | **NOT_PROVEN** |

**Aucune signature indépendante n'est émise. Aucune certification logicielle de concurrence ou matérielle.** L'audit R38 est un outil de recensement et de veto, pas un mécanisme de correction en production.

**Objectifs propriétaires Mac Intel en attente :** 757 Python, 33 assertions C natives, 213 sources SHA-256, 38 rapports SHA-256. PR #1 **DRAFT, non fusionnée**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
