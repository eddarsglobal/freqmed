# Bureau FREQMED — GEN-R65 : rapport d'ingénierie (non certifiant)

**Objet :** préparation PCM numérique par segments ≤256 trames, sous les verrous R58–R64. Pas de nouvelle autorisation de banc, pas d'émission.

## Règles de décision

- **B07 Acoustique/DSP :** comparer C R65 au générateur de consignes C R63 ; vérifier fréquence, durée, enveloppe et continuité des segments ; aucun niveau acoustique physique déduit.
- **B08 Logiciel scientifique :** vérifier 256 trames max, intégralité du nombre de trames, ordre et parité des échantillons, arrêt en défaut et effacement mémoire.
- **B09 Architecture/sécurité/UX :** liaison R59/R60/R61/R62 vérifiée avant et après, API localhost POST authentifiée, aucune identité UID ou tampon dans la réponse, dix langues, application OFF au démarrage.
- **B10 Sûreté :** sortie réelle `HARD_DENIED`, audio playback `NOT_PERFORMED`, interdiction biologique et de production, STOP logiciel ne vaut pas arrêt physique certifié.
- **B04 Métrologie acoustique :** `NOT_EVALUATED` ; aucun transducteur qualifié, instrument étalonné ou mesure de pression acoustique fourni.

Ces cinq entrées constituent une **revue par fonctions** sur le code et les preuves du développeur, pas une certification indépendante de titulaires identifiés.

## État scientifique

`P0.01=IN_PROGRESS_REBASE_REVIEW`; `P0.02=PENDING`; `P1.01=PENDING`; `P1.02=PENDING`. Les validations numériques GEN-R65 ne modifient pas ces états. `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`; `NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED` (CoreAudio plateforme Apple non FOSS).

## Evidence d'ingénierie

Tests nouveaux : 50 tests C/FFI/API, dont équivalence float32 sur 22050 trames et tests de fail-closed sur mutations de la commande. Suite exécutée sur Linux : **692/692 tests PASS, 0 ignoré**, 20 modules en processus Python isolés, dont les **642 cas hérités** et 50 tests nouveaux R65. Sur Mac Intel, compilation Apple/CoreAudio et parcours Safari **EN ATTENTE**. Le runner exploite au plus quatre processus isolés pour borner les régressions historiques. Le kit a un manifeste SHA256 et un ZIP SHA256 externe distincts.

**Verdict :** `CANDIDATE_CODE_READY_FOR_MAC_INTEL_EVALUATION`; pas `CERTIFIED`, aucune fusion GitHub autorisée par ce rapport.

## Résultat du développeur au 23 novembre 2026

`GEN_R65_SOFTWARE_TESTS=692_SUCCESS_SKIPPED_0` sur environnement Linux. L’archive sera testée après extraction neuve. Aucun banc, aucun générateur physique, aucune mesure acoustique, aucune simulation scientifique. Une revue par fonctions du Bureau n’est pas une décision de certification.
