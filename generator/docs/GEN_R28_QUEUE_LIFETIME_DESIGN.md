# FREQMED GEN-R28 — C11 Queue Lifetime & Callback Admission Remediation Design

**Baseline Mac réellement attestée : GEN-R27 537/537 Python, 33/33 C, 144/144 intégrités et 16/16 rapports SHA-256, sans émission.** Commit de référence : `01137691cd62460799ab23b9ca5c844926130297`. Neuf constats R27 ouverts, quinze preuves R23 non acquittées, sept risques R24 non résolus, onze portes du Bureau ouvertes.

## Nouvelle correction de conception, non intégrée

Une nouvelle unité C11 pure `candidates/r28_callback_admission_gate.c` définit cinq opérations : `init`, `try_enter`, `leave`, `close`, `closed_and_empty`. Elle ne contient **aucun appel CoreAudio** et reste compilée en objet indépendant, **sans liaison et sans chargement**. Elle n'est pas une modification du moteur original ni de `candidates/acoustic_macos_r26.c`. Le verrou PCM de R26 reste une question de revue.

Le mot atomique `state` comprend un bit terminal `FM_R28_CLOSED` et un compteur bas de leases acceptés. Le callback peut tenter **une unique CAS forte** `memory_order_acq_rel` ; sur concurrence ou fermeture, l'entrée est refusée. L'absence de boucle évite un spin non borné dans un callback, mais **ne prouve pas la performance temps réel**. Un utilisateur accepté doit obligatoirement effectuer un `leave` unique. Une mauvaise paire enter/leave pourrait provoquer un underflow : ce contrat **n'est pas prouvé en intégration**. L'état fermé ne se réouvre jamais.

Le contrôle `closed_and_empty` donne seulement une **condition C11 nécessaire**. Il ne prouve **ni l'arrêt des callbacks CoreAudio futurs, ni la validité de `AudioQueueRef`, ni la libération de la file par l'OS**. Avant tout `AudioQueueDispose`, il faudrait démontrer que tous les chemins utilisant queue/buffers ont acquis puis libéré un bail, que la fermeture interdit de nouvelles prises, que le contexte userdata reste vivant même pour une entrée tardive, et établir séparément les garanties de l'OS. Il est interdit d'invalider `ctx->queue` sur la seule lecture d'un compteur à zéro.

## Dossier du Bureau (tous OPEN_NOT_PROVEN)

| ID | Fonction | Obligation à acquitter |
|---|---|---|
| D28_01 | B07 | Userdata stable avant tout accès au portail atomique, y compris après la désinscription |
| D28_02 | B09 | Lease obligatoire pour chaque utilisation de queue/buffer ; preuve happens-before avant invalidation |
| D28_03 | B09 | CAS bornée, abandon fail-closed, absence de réentrance dangereuse et enveloppe temps réel |
| D28_04 | B07 | Contrats OSStatus/AudioQueueDispose, retrait listener, preuve de propriété avant libération |
| D28_05 | B10 | Limite des ressources retenues et fermeture irréversible du processus |

Cette unité **n'est pas raccordée au callback ou contrôleur réel** : elle démontre seulement qu'un contrat candidat est compilable. `AudioQueueEnqueueBuffer` reste situé dans la section PCM du candidat R26 ; AD02 demeure ouvert. L'échec réel de disposition OS n'a pas été testé.

Le lanceur Mac Intel `RUN_GEN_R28_MAC_INTEL.command` réexécute R16–R27 sur les vraies sources et l'archive R19 originale, puis compile **séparément** le nouveau C11. Le binaire CLI reste celui du refus de sortie et conserve l'audit `nm`. Vingt tests Python supplémentaires analysent uniquement les sources et des altérations de texte, sans simulation de threads ni de phénomène physique.

**Cible Mac : 557 tests Python, 33 assertions C, 150 fichiers épinglés, 18 rapports SHA-256. Ce ne sont pas des résultats Mac déjà obtenus.** GEN-R28 reste `PENDING_NATIVE_OWNER_VALIDATION`, Bureau `PENDING`, PR `DRAFT`, aucune fusion.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
