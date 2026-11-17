# FREQMED GEN-R39 — Bureau B07/B09/B10 : Owner Lifetime & Exit Ticket

**Verdict maximal : `AT_MOST_ONCE_EXIT_CANDIDATE_REVIEWED_EXACTLY_ONCE_AND_OS_PROOFS_OPEN`.** Il ne s'agit pas d'un procès-verbal d'homologation.

### B07 — frontière OS / durée de vie

`LT39_01 CRITICAL` : C31 remet encore le `ctx` heap aux vrais callbacks ; la solution C39 n'est ni un callback ABI Apple ni intégrée. `LT39_04 CRITICAL` : les postconditions OS après échec de Stop/Dispose et l'arrêt physique ne sont pas démontrés. C39 ne résout aucun chemin OS de production, n'émet aucun signal et ne reçoit aucune invocation de CoreAudio.

### B09 — propriétaire, ticket et relation C11

`LT39_02 CRITICAL` : le ticket ne détient **pas** l'exclusivité ni la durée de vie des alias mémoire de `owner`. Il suppose l'immortalité contractuelle de l'allocation après `fm36_prepare_once`.

`LT39_03 CRITICAL` : le CAS de `fm39_complete_at_most_once` garantit seulement qu'un ticket vivant ne décrémente **pas plus d'une fois**. Il n'existe aucune preuve qu'un callback réel appellera `complete` ou que tous les chemins d'erreur garantissent la sortie.

Hypothèses non déchargées : initialisation correcte de chaque `FM39Lease`, absence de copie et de réinitialisation, stabilité de sa mémoire face aux appels concurrents, conservation des alias d'owner, appariement de chaque callback, absence de double admission, cohérence globale des champs PCM et `ctx->queue`, erreur `fm36_leave` qui laisse `FINISHED` terminal.

### B10 — aucun résultat physique

Une preuve `clang -c`, `nm`, SHA-256 et tests Python ne démontre ni production sûre, ni coupure d'un appareil, ni conformité biomédicale. Zéro mesure, zéro émission autorisée, zéro essai humain ou biologique.

| Ensemble de preuves | État |
|---|---|
| R39 | **16 OPEN, 4 CRITICAL** |
| R38 | 18 OPEN, 5 CRITICAL |
| R37 | 14 OPEN, 4 CRITICAL |
| R36 / R35 / R34 | 12 / 12 / 14 OPEN |
| R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 OPEN |
| R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN, 0 résolue** |
| Liaison C39 à l'exécutable | **INTERDITE** |
| C31 réécrit pour ancre statique | **NON** |
| Garantie at-most-once locale | **CANDIDATE SOURCE** |
| Garantie exactly-once globale | **NOT_PROVEN** |
| Propriétaire pré-admission vivant | **NOT_PROVEN** |
| Quiescence CoreAudio | **NOT_PROVEN** |
| Arrêt physique | **NOT_PROVEN** |

**Cibles Mac Intel R39 non attestées : 777 tests Python, 33 assertions C natives, 220 sources et 40 rapports SHA-256.** Le Bureau ne délivre aucune signature ni autorisation d'intégration, d'exposition biologique ou d'émission.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
