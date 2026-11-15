# FREQMED GEN-R26 — Première remédiation C11 native isolée

## Source de vérité et séparation physique

Baseline réellement observée sur Mac Intel le **15 novembre 2026** : GEN-R25, commit `646403a02ac9664b97c3fce954cbcf69415cee8e`, **497/497 Python PASS**, **33/33 assertions natives C PASS**, **133/133 fichiers SHA-256 PASS**, douze rapports R20–R25 SHA-256 vérifiés. Neuf remédiations `PROPOSED_NOT_APPLIED` ; quinze obligations R23, sept risques R24 et onze portes du Bureau restent OPEN.

GEN-R26 crée une **nouvelle source C native complète**, `generator/candidates/acoustic_macos_r26.c`, dérivée de `generator/src/acoustic_macos.c` par **exactement trois remplacements limités et un en-tête de restriction**. Le C original, épinglé depuis R19, reste **strictement intact** ; les anciens audits R16–R25 et la PR #1 restent non certifiants. Ce C est un **candidat natif de conception**, pas un programme autorisé à piloter CoreAudio.

## Les trois modifications concrètes et leurs limites

| Candidat | Modification réellement présente dans `candidates/` | Risque encore ouvert |
|---|---|---|
| **R26_PCM_CONTROLLER_SHARED_GATE** | Le contrôleur acquiert `pcm_writer_gate` avec `memory_order_acquire` avant `fill_audio(ctx,b)`, puis le libère avec `memory_order_release`. Le callback conserve le même drapeau et son contrôle de chevauchement. Une contention du contrôleur verrouille la séquence en échec | Cette participation réciproque ne démontre pas le moment réel de publication des userdata, l'admission des callbacks, ni l'absence d'un interleaving non audité. Il ne faut pas utiliser un verrou bloquant ou non borné dans un callback temps réel |
| **R26_BIND_ERROR_RETAIN_USERDATA** | Après rejet de la liaison de la route, même si `AudioQueueDispose(...,true)` rapporte le succès, le contexte déjà publié dans `AudioQueueNewOutput` est conservé et `fm_context_quarantined` est verrouillé | Ne prouve pas qu'aucun callback ne survit ni que tous les retours OSStatus sont correctement qualifiés ; le tas peut rester alloué jusqu'à la terminaison du processus |
| **R26_PUBLISHED_CONTEXT_FAIL_CLOSED** | Le chemin de fermeture terminal conserve tout contexte publié : plus de `free(owner_ctx)` après publication, retour `-1`, quarantaine du processus. Les deux seuls `free(owner_ctx)` restants précèdent toute création de queue | Cette conception abandonne le résultat de succès, peut retenir la mémoire de façon permanente et ne garantit pas l'arrêt ou l'absence de race des callbacks et listeners |

Ces modifications sont un point de départ volontairement conservateur. **GEN-R26 ne clôt aucune preuve C11 ou CoreAudio** ; il ne livre ni un remède prêt à être utilisé, ni une preuve de performance ou d'absence d'inversion de priorité en temps réel. Aucun comportement d'échec `AudioQueueDispose` n'est testé sur un véritable périphérique.

## Conditions techniques de contrôle

`audits/r26_isolated_patch_gate.py` reconstruit le fichier candidat par application *octet pour octet* des trois modifications au C original épinglé. Il rejette toute autre altération, tout changement de SHA du C historique et toute modification de l'allowlist du binaire. Il recalculera également le rapport R25 à partir de la chaîne réelle R16–R24 et de l'archive R19 en lecture seule.

Le lanceur `RUN_GEN_R26_MAC_INTEL.command` compile `candidates/acoustic_macos_r26.c` **avec `clang -c`, dans un objet distinct uniquement, sans éditeur de liens et sans chargement**. Il reconduit les cinq objets acoustiques/EM existants compilés et non liés, les 33 assertions C et l'exécutable séparé où `output_hard_denied.c` refuse l'émission. Les **20 tests supplémentaires** sont textuels et documentaires ; ils ne simulent pas les appels CoreAudio, des threads ou des mesures scientifiques. Le dossier privé de 14 rapports R20–R26 est créé seulement après réussite de l'ensemble.

**Cibles d'exécution Mac Intel (non encore attestées) : 517/517 Python, 33/33 C, 139/139 empreintes, compilation candidate `COMPILED_UNLINKED`, 14 rapports SHA-256 PASS.** Trois corrections sont effectivement présentes *dans la source candidate isolée* ; **zéro correction est appliquée à `generator/src/acoustic_macos.c` ou à l'exécutable**.

## Règles de décision

Les 15 obligations de preuve R23 restent OPEN et non acquittées, sept constats R24 OPEN, neuf remédiations R25 non fusionnées, onze portes Bureau OPEN/0 résolue. Les fonctions B07 (CoreAudio), B09 (C11) et B10 (gouvernance) doivent encore contrôler indépendamment l'architecture, l'impact mémoire de la quarantaine, tous les accès non atomiques, le retrait des listeners, le modèle happens-before et le contrat OS de libération. **Aucune signature indépendante n'est présumée.**

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
