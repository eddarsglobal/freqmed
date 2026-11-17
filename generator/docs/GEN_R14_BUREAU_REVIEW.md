# GEN-R14 — Dossier d'examen indépendant du Bureau (NON CERTIFIÉ)

**B09 — Architecture / sécurité :** examiner la suppression des macros, les types C11 et les pointeurs CoreAudio explicites, puis vérifier tous les chemins de `calloc`, de libération avant publication, d'échec de création de file, de rejet de binding, de `AudioQueueDispose` et de quarantaine. Une réussite de compilation et de tests structurels ne garantit pas que tous les callbacks se terminent avant la libération.

**B07 / B04 — DSP et acoustique :** le backend source est compilé mais jamais lié ou exécuté dans le binaire propriétaire. Aucune fréquence acoustique émise, durée de lecture physique, niveau de pression ou coupure indépendante vérifiés.

**B05 / B06 — EM :** le dossier de qualification GEN-R11 est documentaire et non autorisant. Aucun générateur EM réel identifié ni pilote actif, émission ou contrôle de port.

**B10 — Sûreté :** le verrou logiciel et une mise en quarantaine mémoire ne remplacent pas un arrêt physique indépendant, l'évaluation des risques, le protocole de banc non biologique ou l'autorisation explicite de tests matériels. Aucune exposition humaine, animale ou biologique.

**RoadMapGuardian :** P0.01 IN_PROGRESS, aucun ancien jalon certifié rétroactivement ; PR #1 demeure DRAFT, `main` inchangée. GEN-R13 attestation Mac Intel 255/255 Python et 33/33 C. GEN-R14 275/275 Python et 33/33 C visés mais NON encore exécutés sur le Mac du propriétaire.

`BUREAU_CERTIFICATION=PENDING` · `NEVER_SIMULATION=ENFORCED` · `ZERO_COST_FOSS=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
