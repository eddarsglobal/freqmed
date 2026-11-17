# FREQMED — GEN-R29 Independent C11 Admission Integration & Queue Ownership Proof Review

**Source Mac Intel réellement attestée : GEN-R28, 557 tests Python, 33 assertions C natives, 150 fichiers SHA-256, 18 rapports vérifiés ; aucun callback CoreAudio actif, aucune émission physique et aucune simulation scientifique.**

## Un nouveau candidat C isolé, pas une autorisation de sortie

`candidates/acoustic_macos_r29.c` part du C isolé de GEN-R26. Il incorpore, uniquement lors de sa propre compilation, les primitives du portail C11 vérifiées sur GEN-R28, par `#include "r28_callback_admission_gate.c"`. Le backend original `src/acoustic_macos.c`, le C candidat R26 et le composant R28 restent inchangés ; R29 n'est pas lié, chargé ni exécuté.

Changements concrets : un `FMR28AdmissionGate` est ajouté au contexte ; il est initialisé avant `AudioQueueNewOutput`. Les callbacks de sortie et listeners tentent l'admission **avant l'accès aux champs d'état et à la file**. Un refus termine leur chemin sans utilisation de `ctx->queue`. Les callbacks admis libèrent exactement une fois le bail en chemin nominal. Le contrôleur ferme les admissions à l'échec de création, au rejet de liaison et avant le nettoyage final. Si le portail fermé n'est pas vide, il renonce à disposer de la file et impose une quarantaine permanente.

Cela introduit une frontière **source-only** entre accès acceptés et phase de disposition, mais **ne résout pas** l'OS userdata pré-admission, les erreurs CoreAudio ou l'absence de races. Le contrôleur dispose d'une propriété de phase unithread **supposée mais non démontrée** ; cette dernière doit être reliée explicitement aux callbacks et aux appels `AudioQueueStop`, `AudioQueueRemovePropertyListener` et `AudioQueueDispose`.

## Le modèle C11 et les garanties OS doivent rester séparés

Le protocole de R28 emploie un compteur/biseau fermé dans un même objet atomique. Des opérations acquire/release peuvent établir une relation happens-before **si** la lecture observe l'écriture ou la séquence de libération correspondante ; l'auditeur textuel ne démontre pas ce point sur tous les chemins. Un callback arrive avec un userdata fourni par CoreAudio : il doit être valide **avant** la première instruction atomique ; aucune fermeture logicielle ne prolonge sa durée de vie a posteriori.

Apple décrit `AudioQueueDispose(queue,true)` comme synchrone pour une disposition réussie et documente que la file libérée ne peut plus être utilisée et qu'elle ne rappellera plus de callback. La conduite à tenir en cas d'OSStatus d'erreur et l'interaction avec des listeners déjà en cours restent à qualifier séparément. Références : https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29 et https://en.cppreference.com/c/atomic/memory_order .

Le candidat conserve `AudioQueueEnqueueBuffer` sous `pcm_writer_gate` (risque AD02), avec des incertitudes de réentrance, de budget de temps réel et de contention. Dans une situation d'erreur, choisir de conserver la file OS sans disposition **n'est pas une preuve de coupure physique** ; c'est précisément pourquoi ce C ne peut être activé.

## Sept constats nouveaux et blocages hérités

| ID | Priorité | Bureau | Preuve manquante |
|---|---|---|---|
| I29-01 | HIGH | B07 | Validité du userdata avant admission, y compris après fermeture |
| I29-02 | HIGH | B07 | Quiescence OS réelle, indépendamment de closed-and-empty |
| I29-03 | HIGH | B09 | Happens-before sur tous les accès à queue et aux buffers |
| I29-04 | HIGH | B07 | Erreurs de retrait de listener, de stop et de disposition |
| I29-05 | HIGH | B09 | Réentrance `AudioQueueEnqueueBuffer` et temps réel |
| I29-06 | HIGH | B10 | Quarantaine sans disposition, fuite de ressources OS et arrêt |
| I29-07 | HIGH | B09 | Appariement enter/leave, underflow, propriété lock-free |

Tous sont **OPEN_NOT_PROVEN**, sans race reproduite. Les 5 contrôles R28, 9 risques R27, 15 obligations R23, 7 lacunes R24 et 11 portes du Bureau restent ouverts. Le succès d'un audit source ne prouve pas la sûreté du code.

## Contrôles et preuve Mac Intel

`RUN_GEN_R29_MAC_INTEL.command` doit reprendre la chaîne R16–R28 contre l'archive originale R19 en lecture seule, ajouter le rapport R29, compiler le candidat C29 en objet isolé avec `clang -c` et conserver R26, R28 et les cinq objets existants non liés. Le binaire de test doit conserver `output_hard_denied.c`, l'allowlist et l'audit `nm`. Les 20 tests Python supplémentaires restent statiques, mutation textuelle uniquement, sans simulation scientifique.

**Cible Mac Intel : 577 Python, 33 C, 156 fichiers épinglés, 20 rapports R20–R29 vérifiés SHA-256. Il s'agit de résultats attendus, pas encore d'un témoin Mac GEN-R29.**

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
