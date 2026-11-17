# FREQMED GEN-R40 — Bureau B07/B09/B10 : revue indépendante

**Verdict maximal : `OPAQUE_PRIVATE_TICKET_CANDIDATE_REVIEWED_COMPLETION_AND_OS_PROOFS_OPEN`.** Aucun procès-verbal de certification physique, C11 générale ou Apple CoreAudio.

### B07 — appels OS et callbacks tardifs

**OP40_01 et OP40_04 : CRITICAL OPEN.** Le candidat C31 transmet encore `ctx` à `AudioQueueNewOutput` et au listener. Aucun de C36/C37/C39/C40 n'a été raccordé aux vrais callbacks. Aucun témoin d'arrêt/disposition échoué ni de quiescence du système n'existe ici. Aucun couplage OS ni exécution de callback.

### B09 — copies, alias et complétude

**OP40_02 et OP40_03 : CRITICAL OPEN.** L'opacité cache la définition et rend la copie **par valeur** d'un ticket illégale pour un appelant C correctement typé, ce qui sera contrôlé par un véritable `clang -fsyntax-only` avec erreur attendue. En revanche, l'appelant peut toujours recopier les pointeurs `FM40Ticket*` ou `owner_out`, tenter des accès par cast, omettre complètement `fm40_complete`, ou violer l'obligation de garder `owner` vivant. Une capacité statique bornée à quatre **admissions de durée de vie** ne suffirait pas aux callbacks CoreAudio réels.

Le CAS garantit seulement un **au-plus-une-fois** local pour un slot valide et vivant ; il ne démontre pas que chaque entrée aura une sortie. `fm36_leave` peut échouer après l'état terminal. Les autres champs du contexte `ctx` et les parcours d'erreur OS exigent leurs propres preuves C11.

### B10 — sécurité matérielle

**OP40_05 : CRITICAL OPEN.** Compilation `clang -c`, test négatif de typage C, analyse `nm`, assertions logicielles et SHA-256 ne constituent aucune mesure d'émission ni une preuve de coupure physique. Aucun instrument EM/acoustique n'est piloté. Aucun essai humain ou biologique.

| Ensemble | Obligations ouvertes |
|---|---|
| GEN-R40 | **18 OPEN, 5 CRITICAL** |
| GEN-R39 | 16 OPEN, 4 CRITICAL |
| GEN-R38 | 18 OPEN, 5 CRITICAL |
| GEN-R37 | 14 OPEN, 4 CRITICAL |
| GEN-R36 / R35 / R34 | 12 / 12 / 14 |
| GEN-R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 |
| GEN-R29 / R28 / R27 | 7 / 5 / 9 |
| R23 / R24 | 15 / 7 |
| Bureau historique | **11 OPEN / 0 résolue** |
| Certificat C11 global | **NOT_PROVEN** |
| Intégration CoreAudio | **NO** |
| Quiescence / arrêt physique | **NOT_PROVEN** |
| Signatures indépendantes | **NONE** |

Les comptes sont des registres qui se recoupent ; **ne pas additionner** comme défauts indépendants.

**Cibles Mac Intel R40 (PENDING) : 797 Python, 33 C natives, 228 fichiers SHA-256 et 42 rapports SHA-256.** PR #1 doit rester DRAFT et non fusionnée ; aucun objet C31/C36/C37/C39/C40 lié au binaire émetteur.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
