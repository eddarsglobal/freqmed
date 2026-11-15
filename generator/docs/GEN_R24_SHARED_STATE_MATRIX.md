# FREQMED GEN-R24 — Independent C11 Shared-State Matrix

## Point de départ réel

Le 15 novembre 2026, le propriétaire a exécuté GEN-R23 Mac Intel sur le commit `e52a18b39c4e29203fef23c3a63c4537317794a5` : **457/457 Python PASS**, **33/33 assertions C natives PASS**, **123/123 fichiers source SHA-256 PASS** ; 15 obligations de preuve R23 restées ouvertes, 11 portes du Bureau non résolues, huit rapports JSON/Markdown contrôlés SHA-256. Le programme de validation n'a activé aucune sortie.

## Inventaire source réellement ancré

L'auditeur `audits/r24_shared_state_contract_audit.py` réexamine le fichier `src/acoustic_macos.c`, dont les octets sont identiques à la source épinglée R19. Sa matrice répertorie **19 champs déclarés `AcousticContext`**, dont **7 champs non atomiques et 12 atomiques**, et **112 occurrences syntaxiques de références `ctx->...` ou `owner_ctx->...`**. Chaque occurrence possède une ligne et une fonction réellement trouvées dans le C, sous SHA-256 vérifié. L'inventaire refuse un champ inconnu, un champ supprimé, une variation non revue du nombre d'occurrences ou un accès hors d'une fonction connue.

| Champ non atomique | Références lexicales | Risque à examiner |
|---|---:|---|
| `queue` (`AudioQueueRef`) | 13 | Propriété et durée de vie interfonctions, disposition et réutilisation par les callbacks |
| `phase` | 4 | Champ PCM modifié dans `fill_audio` appelé depuis le contrôleur et un callback |
| `phase_step` | 2 | Initialisé par le contrôleur, lu dans `fill_audio` |
| `normalized_level` | 2 | Initialisé par le contrôleur, lu dans `fill_audio` ; pas une mesure physique |
| `frames_written` | 4 | Compteur PCM non atomique modifié dans `fill_audio` |
| `total_frames` | 5 | Initialisé par le contrôleur, consulté dans `fill_audio` |
| `fade_frames` | 7 | Valeur de rampe PCM consultée dans `fill_audio` |

Les 12 autres champs sont déclarés avec `atomic_int`, `atomic_uint` ou `atomic_flag` : `last_frame_enqueued`, `failed`, `stop_requested`, `queue_started`, `queue_stopped`, `graceful_drain_requested`, `shutdown_in_progress`, `first_fault_reason`, `active_output_callbacks`, `active_property_listeners`, `dispose_confirmed` et `pcm_writer_gate`.

**Attention au mot « exhaustif » :** l'inventaire est exhaustif **pour les 112 expressions syntaxiques `ctx->champ` de cette source épinglée**, pas pour tous les accès mémoire possibles en C, les pointeurs aliasés par les API système, la mémoire des buffers AudioQueue ou les interleavings du système d'exploitation. L'extraction des fonctions utilise un scanner d'accolades borné ; ce n'est pas un parseur C complet, ni un analyseur de races.

## Onze appels AudioQueue directs relevés

`AudioQueueNewOutput` (1), `AudioQueueAddPropertyListener` (1), `AudioQueueRemovePropertyListener` (1), `AudioQueueDispose` (2), `AudioQueueStart` (1), `AudioQueueStop` (2), `AudioQueueGetProperty` (1), `AudioQueueAllocateBuffer` (1) et `AudioQueueEnqueueBuffer` (1). Cette surface ne comprend pas les API invoquées indirectement par des modules auxiliaires, lesquelles conservent leurs propres audits R16–R23.

## Contrats de référence externes — limites explicites

- **Apple AudioQueueDispose** — https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose : `inImmediate=true` demande une disposition synchrone ; après disposition, l'API n'invoque plus de callbacks de cette file. L'audit ne déduit **aucune preuve** du comportement après un retour d'erreur ou de l'achèvement de toutes les opérations mémoire C11 du programme.
- **Apple AudioQueueRemovePropertyListener** — https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener : supprime l'inscription du listener désigné et renvoie un `OSStatus`. Cette page n'établit pas à elle seule une garantie que tous les callbacks du listener déjà en cours sont terminés avant le retour.
- **Apple AudioQueueNewOutput** — https://developer.apple.com/documentation/audiotoolbox/audioqueuenewoutput : création de la file avec callback et userdata. L'audit ne suppose pas la publication sûre et l'ordre d'exécution de tous les callbacks après `AudioQueueStart` sans justification supplémentaire.
- **C11 memory_order** — https://en.cppreference.com/w/c/atomic/memory_order : une relation acquire/release n'est pas une preuve générale que des écritures non atomiques et tous les callbacks sont convenablement ordonnés.

Ces contrats sont des **sources normatives/documentaires**, non des mesures physiques, preuves de mémoire formelle ou reproductions d'erreurs OS.

## Sept constats du Bureau encore ouverts

`SH01_NONATOMIC_PCM_CONTROLLER_CALLBACK`, `SH02_NONATOMIC_QUEUE_REFERENCE_LIFETIME`, `SH03_ATOMIC_COUNTER_ENTRY_WINDOW`, `SH04_LISTENER_REMOVAL_QUIESCENCE`, `SH05_SUCCESSFUL_DISPOSAL_LIMIT`, `SH06_DISPOSAL_ERROR_HEAP_RETENTION` et `SH07_C11_RELEASE_ACQUIRE_LIMIT`. Chacun est relié à une des trois premières portes R20/R23 du Bureau, chacune toujours non certifiée.

GEN-R24 conserve **15 obligations de preuve GEN-R23 OPEN/0 acquittée** et **11 portes du Bureau OPEN/0 résolue**. La preuve de non-concurrence mémoire, la quiescence réelle et le comportement d'erreur `AudioQueueDispose` restent `NOT_PROVEN / NOT_PROVEN / NOT_TESTED`.

## Mise en œuvre et validation

Le nouveau runner `RUN_GEN_R24_MAC_INTEL.command` recalcule les preuves R16–R23 (archive R19 originale en lecture seule), puis établit la matrice R24 avant de compiler les cinq objets candidats acoustique/EM **isolés et non liés**. Il conserve les 33 assertions natives C, le lien du binaire hard-denied et l'audit `nm`. La suite Python doit inclure **20 nouveaux tests** GEN-R24, dont le refus de champs ou d'appels API non revus.

Après réussite réelle des tests Mac Intel seulement, il créera un dossier privé avec **10 rapports JSON/Markdown R20–R24** et un manifeste SHA-256. Le dossier R19 existant n'est jamais modifié.

**Cible Mac Intel : 477/477 Python, 33/33 C et 128/128 sources intègres ; validation GEN-R24 encore PENDING.**

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
