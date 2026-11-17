# FREQMED GEN-R36 — Bureau B07/B09/B10 Architecture & Proof Gate

**Verdict maximal : `STATIC_LIFETIME_ANCHOR_CANDIDATE_REVIEWABLE_NOT_INTEGRATED_NOT_CERTIFIED`.**

## Autorité B07 — frontière OS ↔ C11

**SA36_01, SA36_02, SA36_03 CRITICAL, OPEN_NOT_PROVEN.** Le C31 réel remet encore le contexte `ctx` directement aux APIs CoreAudio. Le candidat R36 remettrait plutôt une ancre statique, mais aucune API OS n'y est raccordée. Aucune garantie CoreAudio n'est revendiquée pour les erreurs `AudioQueueStop`, `AudioQueueDispose`, `AudioQueueNewOutput` et les listeners.

L'ancre statique permettrait en principe de déplacer **le premier accès de callback** vers une adresse dont la durée de vie est celle du processus, sans libérer l'allocation du contexte. Mais cela reste un **contrat architectural candidat**, non un résultat de callback réel.

## Autorité B09 — modèle mémoire et alias

**SA36_05–SA36_09 HIGH, OPEN_NOT_PROVEN.** Il faut prouver le maintien effectif du propriétaire, y compris sur toutes les erreurs ; le module atomique ne peut contrôler des `free` ailleurs. Le compteur `admitted` peut inclure un callback déjà engagé lorsque `seal` arrive ; son zéro n'exclut pas une nouvelle entrée OS. `fm36_leave` ne possède pas de jeton propre à chaque appel, donc le contrat d'appariement par callback est une obligation non déchargée. La publication exige un modèle happens-before complet à l'échelle de l'intégration, absent en R36.

Un seul slot est volontairement impossible à réutiliser. L'épuisement doit produire un refus complet, **pas** une allocation d'urgence, un second slot non audité ou une réouverture.

## Autorité B10 — sûreté physique

**SA36_04 CRITICAL, OPEN_NOT_PROVEN** : l'ancre et sa mise en quarantaine n'ont aucun pouvoir d'arrêt d'un appareil. **SA36_12 HIGH** : les preuves source C11, `clang -c` et l'audit `nm` ne sont pas des mesures d'émission ni des qualifications biologiques.

| Ensemble | Statut |
|---|---|
| GEN-R36 | **12 OPEN, dont 4 CRITICAL** |
| GEN-R35 | 12 OPEN, dont 4 CRITICAL |
| GEN-R34 | 14 OPEN, dont 4 CRITICAL |
| GEN-R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 OPEN |
| R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN, 0 résolue** |
| Intégration du module R36 au C31 | **NON** |
| Preuve de vie `userdata` en production | **NOT_PROVEN** |
| Preuve OS des callbacks tardifs | **NOT_PROVEN** |
| Preuve C11 globale | **NOT_PROVEN** |
| Preuve de coupure physique | **NOT_PROVEN** |
| Signatures indépendantes | **NONE** |

**Cibles R36 Mac Intel : 717 Python, 33 C, 200 fichiers source SHA-256, 34 rapports SHA-256** ; valeurs PENDING avant journal utilisateur.

Conserver PR #1 DRAFT et non fusionnée ; aucune activation du backend source C, aucune émission ou simulation scientifique.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
