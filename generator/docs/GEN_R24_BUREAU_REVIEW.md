# FREQMED GEN-R24 — Bureau B07 / B09 / B10 : matrice partagée et contrats CoreAudio

**Verdict maximal : SHARED_STATE_MAPPED_CONTRACT_GAPS_OPEN.** Un PASS logiciel ne constitue aucune preuve de race freedom C11, de quiescence OS ni de sécurité physique.

## Avis technique provisoire fondé sur le code, pas certification

**B09 — Concurrence mémoire C11 :** la source épinglée possède 19 champs de contexte, 12 déclarations atomiques et sept champs non atomiques. Le contrôleur et le callback appellent tous les deux `fill_audio`, qui modifie `phase` et `frames_written`. Le verrou atomique `pcm_writer_gate` protège une portion du callback, pas l'intégralité des appels du contrôleur. Une justification formelle ou une modification C séparément examinée serait nécessaire avant la fermeture de cette lacune.

**B07 — API et durée de vie macOS :** `AudioQueueDispose(queue,true)` est documenté comme synchrone et la file libérée cesse d'invoquer les callbacks, mais aucun témoin d'échec réel de disposition n'a été établi. `AudioQueueRemovePropertyListener` ne démontre pas à lui seul l'attente des callbacks déjà en cours. Les compteurs atomiques incrémentés seulement à l'entrée du callback ne remplacent pas une barrière d'admission OS.

**B10 — Contention et publication :** le code refuse l'émission et conserve des pointeurs/contextes en quarantaine lorsque la disposition est incertaine. Il doit encore être démontré qu'aucune voie de réadmission, race C11 ou réclamation erronée de sécurité n'est possible en conditions réelles. La quarantaine n'est pas une coupure matérielle physique.

## Contrôles et preuves attendus

Le nouveau dossier GEN-R24 doit livrer : matrice exacte des 19 champs et 112 références `ctx->`, fonctions et numéros de lignes, inventaire des 11 appels AudioQueue directs, quatre contrats externes avec limitations explicites, sept constats supplémentaires encore ouverts, chaîne des rapports R16–R23 recalculée et dix fichiers de sortie R20–R24 avec manifeste SHA-256 vérifié.

**Condition logicielle du candidat :** 477 tests Python et 33 assertions natives C, sans backend de sortie lié. **Condition de certification : aucune acquittée** ; 15 obligations GEN-R23, sept nouveaux constats R24 et 11 portes Bureau restent ouverts. Pas de signatures indépendantes inventées, pas d'expérience active, pas de mesures acoustiques/EM ni de simulation scientifique.

**Règles permanentes :** `RoadMap P0.01=IN_PROGRESS`, `BUREAU_CERTIFICATION=PENDING`, `NEVER_SIMULATION=ENFORCED`, `ZERO_COST_FOSS=ENFORCED`, `ACOUSTIC_OUTPUT=LOCKED`, `EM_OUTPUT=LOCKED`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`.
