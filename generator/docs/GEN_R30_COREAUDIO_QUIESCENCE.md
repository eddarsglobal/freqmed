# FREQMED — GEN-R30 Independent CoreAudio Callback Quiescence & Queue Ownership Adversarial Review

**Baseline propriétaire vérifiée : GEN-R29 FIX1, Mac Intel, 577/577 Python, 33/33 C, 156/156 sources SHA-256, 20/20 rapports SHA-256.** Commit de départ `0b64a66bcedd2dfc5d851933213d5ac68b50f31f`. Témoin logiciel réussi, sans permission physique et sans preuve formelle C11/OS.

## Observation prioritaire — retour précoce après démarrage de file

Le candidat isolé `candidates/acoustic_macos_r29.c` appelle `AudioQueueStart(ctx->queue,NULL)` avant sa fermeture finale. Si `fm_r28_gate_closed_and_empty(&ctx->queue_admission)` est faux lors de la fermeture, le contrôleur **retourne -1 avant** `AudioQueueStop(ctx->queue,true)`, `AudioQueueRemovePropertyListener` et `AudioQueueDispose`. Sa mise en quarantaine logicielle interdit une nouvelle session mais ne prouve **aucun arrêt de la file précédemment démarrée**. Le caractère potentiellement critique de ce chemin interdit toute activation ; un risque n'est pas une race reproduite.

Ce cas n'est pas corrigé au jalon R30 : il est documenté avec ses lignes et SHA-256 dans une nouvelle revue adversariale. Le binaire public lie toujours `output_hard_denied.c`, **jamais le candidat R29**.

## Séparation stricte des garanties

1. **C11** : les opérations acquire/release du portail d'admission doivent être reliées à l'ensemble des accès `ctx->queue`, aux PCM et aux sorties anticipées. Une lecture `closed_and_empty` ne prouve que le compteur atomique au moment lu et sous ses préconditions, pas la quiescence de l'OS.
2. **CoreAudio** : `AudioQueueStop(queue,true)` demande un arrêt synchrone. `AudioQueueDispose(queue,true)` est décrit comme synchrone ; sa documentation dit aussi que la queue n'est plus utilisable et ne rappelle plus les callbacks après disposition. Le traitement de `OSStatus` d'échec, la durée de vie de callbacks déjà entrés et des listeners doivent être explicitement qualifiés.
3. **Physique** : ni arrêt logiciel, ni échec d'une API CoreAudio, ni quarantaine mémoire n'établissent à eux seuls un arrêt acoustique mesuré. Le candidat ne doit pas être activé. Aucune simulation, aucune émission et aucun test biologique.

Sources Apple vérifiées :
- `AudioQueueStop` : https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
- `AudioQueueDispose` : https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
- `AudioQueueRemovePropertyListener` : https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

## Audit ajouté

`audits/r30_coreaudio_quiescence_adversarial.py` examine les fonctions existantes `fill_audio`, `queue_running_listener`, `output_callback` et `acoustic_output_impl`, attribue **12 constats**, dont **2 critiques**, tous `OPEN_NOT_PROVEN`, et émet deux ancrages du candidat C SHA-256 par constat. Il recalcule le rapport R29 et la chaîne historique R16–R29 avant de produire un JSON et un Markdown privés.

`tests/test_r30_coreaudio_quiescence_adversarial.py` ajoute **20 tests Python** ; ils testent les invariants de source, le caractère visible du chemin critique, la conservation des blocages et des mutations **textuelles uniquement**. Aucun callback n'est activé ni injecté : il n'y a aucune simulation scientifique et aucune preuve de concurrence acquittée.

Le lanceur Mac Intel compile uniquement les objets C déjà approuvés comme **COMPILED_UNLINKED** (R26, R28, R29, cinq backends), conserve `nm` sur le binaire non émetteur et la preuve originale R19 en lecture seule. Après réussite complète seulement, il génère **22 rapports R20–R30** et vérifie leurs SHA-256.

**Cibles Mac Intel GEN-R30 non encore exécutées : 597 tests Python, 33 assertions C, 162 fichiers source SHA-256, 22 rapports SHA-256.** Aucun succès natif GEN-R30 n'est affirmé avant le journal Mac.

## Gouvernance

- `GEN_R29_FIX1_MAC_INTEL_SOFTWARE=PASS` ; `GEN_R30_MAC_INTEL=PENDING`.
- R30 : **12 constats OPEN_NOT_PROVEN**, 2 **CRITICAL**.
- R29 : 7 ouverts ; R28 : 5 ; R27 : 9 ; R23 : 15 ; R24 : 7 ; Bureau : **11 ouverts / 0 résolue**.
- `C11_RACE_FREEDOM=NOT_PROVEN`, `CALLBACK_QUIESCENCE=NOT_PROVEN`, `POST_START_SHUTDOWN_SAFETY=NOT_PROVEN`.
- PR #1 **DRAFT**, pas de fusion, aucune production ni équipement activé.
- `NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
