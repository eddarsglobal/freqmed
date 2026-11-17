# FREQMED GEN-R43 — Bureau indépendant B07/B09/B10

**Verdict maximal documentaire : `LOCAL_PUBLICATION_CAS_REVIEWED_OS_AUTHENTICITY_CAPACITY_UNPROVEN`.** Aucune signature d'un certificateur indépendant, aucun essai Apple/CoreAudio, aucune mesure physique.

### B07 — état OS et quiescence

**G43_01 et G43_06 : CRITICAL OPEN.** Le C31 réel transmet encore un `ctx` dynamique à la sortie CoreAudio et au listener. C43 n'est ni branché sur le callback Apple ni exécuté. Une fermeture `fm43_gate` n'appelle pas `AudioQueueStop` et ne prouve pas l'arrêt des callbacks, la réussite de `Dispose` ou la coupure d'une sortie physique.

### B09 — publication, identité et mémoire

**G43_02, G43_03, G43_04 et G43_05 : CRITICAL OPEN.** L'autorisation d'admission possède désormais un CAS sur le même mot atomique que CLOSED ; cela ordonne correctement la **décision locale** par rapport à la fermeture. La publication du pointeur au consommateur vient **après le CAS** et peut encore arriver après une fermeture concurrente : **problème d'exposition post-close NON RÉSOLU**.

Le C43 lie l'adresse opaque du ticket à `userdata` lors de `complete`, mais ne prouve aucune authenticité : les deux pointeurs sont copiables s'ils deviennent connus. Le module ne contrôle pas les alias externes ni les `free` d'`owner`. Les quatre slots non recyclés et les permis consommés à vie ne permettent aucun flux de callbacks non borné. L'absence de `complete`, les erreurs de `fm36_leave` et la liberté des races C11 du contexte partagé restent ouvertes.

### B10 — sécurité matérielle

`clang -c`, `nm`, tests Python, SHA-256 et audits source démontrent uniquement des propriétés logicielles de l'environnement de test. Ils n'établissent aucune sûreté instrumentale, aucun arrêt physique, aucune conformité médicale. Aucun essai humain ou biologique ni aucune simulation scientifique.

| Ensemble | État |
|---|---|
| GEN-R43 | **21 OPEN, dont 6 CRITICAL** |
| GEN-R42 | 20 OPEN, 6 CRITICAL |
| GEN-R41 | 19 OPEN, 5 CRITICAL |
| GEN-R40 | 18 OPEN, 5 CRITICAL |
| GEN-R39 | 16 OPEN, 4 CRITICAL |
| GEN-R38 | 18 OPEN, 5 CRITICAL |
| R37/R36/R35/R34 | 14/12/12/14 OPEN |
| R33/R32/R31/R30 | 12/10/8/12 OPEN |
| R29/R28/R27 | 7/5/9 OPEN |
| R23/R24 | 15/7 OPEN |
| Bureau historique | **11 OPEN, 0 résolue** |
| Callback CoreAudio réel intégré | **NON** |
| Sortie externe interdite après fermeture | **NOT_PROVEN** |
| Identité authentifiée | **NOT_PROVEN** |
| Quiescence / coupure physique | **NOT_PROVEN** |

**R43 propriétaire Mac Intel : PENDING.** Cibles 857 tests Python, 33 assertions C, 252 sources SHA-256, 48 rapports SHA-256. Ne pas qualifier GEN-R43 comme validé sur Mac sans journal.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
