# FREQMED GEN-R35 — Independent Pre-Admission Callback Lifetime & OS Contract Evidence Review

**Départ : GEN-R34 témoin propriétaire Mac Intel PASS : 677 tests Python, 33 assertions natives C, 187 fichiers source SHA-256, 30 rapports SHA-256.** Ce sont des preuves **logicielles et non émettrices**. Aucun callback CoreAudio réel ou résultat OS d'échec n'a été observé.

## Problème de preuve prioritaire

`output_callback(void *ptr,...)` et `queue_running_listener(void *data,...)` convertissent le pointeur OS en `AcousticContext *ctx`, vérifient `ctx != NULL`, puis évaluent `&ctx->queue_admission` à travers `fm_r28_gate_try_enter`. **Une conversion de pointeur n'est pas une déréférence ; l'accès au membre l'est.** Le portail atomique requiert donc lui-même que `ctx` soit vivant avant l'admission. Ni son état fermé, ni le compteur de callbacks admis égal à zéro ne prouvent que l'OS n'entrera plus avec le même `userdata`.

## Ce que les contrats publics Apple établissent — et leurs limites

Contrats consultés le **16 novembre 2026** via les pages officielles Apple (URLs vivantes, **non archivées ni épinglées** dans ce jalon) :

- `AudioQueueStop(queue, true)` : arrêt immédiat/synchrone demandé ; `false` est asynchrone et les callbacks peuvent se poursuivre pendant la vidange. Le matériel audio associé ne s'arrête que s'il n'est pas utilisé par d'autres services. **Un appel échoué ne certifie pas un arrêt physique.**
- `AudioQueueDispose(queue, true)` : disposition immédiate/synchrone, destruction des ressources et indication qu'aucun callback de cette queue n'est invoqué **après la disposition**. Une postcondition de succès ne doit **jamais** être attribuée à un `OSStatus` non nul.
- `AudioQueuePropertyListenerProc` : reçoit le `inUserData` transmis lors de l'enregistrement. `AudioQueueRemovePropertyListener` exige les mêmes arguments de sélection, notamment `userdata`. Ces pages publiques ne prouvent pas, à elles seules, l'exclusion d'une entrée OS avant `try_enter` sur **tous** les chemins d'échec.
- Les pages consultées ne constituent **pas** un théorème de *happens-before* C11, une preuve d'ordre interthreads, une mesure de coupure ou une garantie de durée de vie des callbacks déjà en cours sur des appels échoués.

Références exactes :
1. https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
2. https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
3. https://developer.apple.com/documentation/audiotoolbox/audioqueuepropertylistenerproc
4. https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

## Livrables concrets

- `audits/r35_pre_admission_os_contract_review.py` : **9 catégories de preuves documentaires Apple**, **13 phases source documentaires**, **12 nouvelles obligations `OPEN_NOT_PROVEN` (4 critiques)** ; deux ancrages SHA-pinnés du C31 par constat et recalcul de toute la chaîne de provenance R16–R34.
- `tests/test_r35_pre_admission_os_contract_review.py` : **20 tests source-only**, dont quatre mutations textuelles adversariales, conservation des C historiques, audit de non-liaison et vérification de l'archive propriétaire R19.
- `RUN_GEN_R35_MAC_INTEL.command` : auditeur indépendant, binaire `output_hard_denied.c` avec `nm`, candidats C compilés mais **non liés**, garde `unittest.TestCase.run`, puis dossier privé de **32 rapports R20–R35 avec SHA-256** uniquement après réussite de la suite.
- `docs/GEN_R35_BUREAU_REVIEW.md` et `docs/GEN_R35_APPLE_OS_CONTRACT_MATRIX.md` : gouvernance B07/B09/B10 et preuve API vs preuve C11.

**Aucun fichier C n'est modifié.** Aucun automate de callback, nouvelle fonction d'émission, simulation scientifique, test humain/biologique ou instrument physique.

**Objectifs Mac Intel GEN-R35, non encore exécutés :** 697 tests Python ; 33 assertions C ; 193 sources SHA-256 ; 32 rapports SHA-256. Tout PASS éventuel restera une validation logicielle, **jamais** une autorisation de publication/émission.

Conserver ouverts : R34 14 (4 CRITICAL), R33 12 (3), R32 10 (2), R31 8 (2), R30 12 (2), R29 7, R28 5, R27 9, R23 15, R24 7, Bureau **11 OPEN / 0 résolue**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
