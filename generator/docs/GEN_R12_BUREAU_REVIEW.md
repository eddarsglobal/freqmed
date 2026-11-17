# GEN-R12 — Bureau : revue indépendante requise (AUCUNE CERTIFICATION)

**B09 — Architecture / cyber / code :**
- Vérifier chaque voie d'entrée/sortie des callbacks, y compris les erreurs.
- Auditer la barrière `shutdown_in_progress`, `atomic_flag` PCM et les compteurs atomiques en regard des règles réelles de CoreAudio.
- Analyser une éventuelle durée de vie incorrecte du `AcousticContext` local si `AudioQueueDispose(true)` retourne une erreur ou si les callbacks survivent à la libération.
- Vérifier l'absence de chemin permettant à `AudioQueueStart` ou à l'EM de se lier au binaire non émetteur.
- Tests structurels et compilation : pas une preuve de race freedom.

**B04/B07 — Acoustique :** aucune sortie physique, aucun transducteur ni niveau de pression/frequence acoustique vérifiés. Aucune caractérisation de temps d'arrêt.

**B05/B06 — EM/instrumentation :** le contrat documentaire GEN-R11 reste `PRESENT_UNVERIFIED` au maximum et `fm_em_hardware_qualified_in_r11` refuse toujours la qualification. Aucun instrument réel qualifié, aucun protocole envoyé et aucune interface ouverte.

**B10 — Sécurité :** aucun banc non biologique autorisé, aucun coupe-circuit physique indépendant certifié, aucun usage biologique ou médical.

**RoadMapGuardian :** P0.01 IN_PROGRESS, G0–G7 inchangés, PR #1 DRAFT, `main` inchangée. Les travaux GEN-R12 sont de simples candidats logiciels hors admission de matériel.

`GEN_R12_SOFTWARE_WITNESS=PENDING` · `BUREAU_CERTIFICATION=PENDING` · `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
