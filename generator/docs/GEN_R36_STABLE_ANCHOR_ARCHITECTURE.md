# FREQMED GEN-R36 — Independent Pre-Admission Lifetime Containment Architecture

**Baseline réellement attestée le 16 novembre 2026 : GEN-R35 Mac Intel, 697/697 tests Python, 33/33 assertions natives C, 193/193 sources SHA-256, 32/32 rapports SHA-256.** Un succès logiciel ne certifie ni OS/CoreAudio, ni race freedom C11, ni matériel.

## Décision : un seul jeton statique de durée de vie du processus

Le candidat isolé **`candidates/r36_stable_userdata_anchor.c`** est un module C11 concret qui pourrait, dans une **future révision indépendante**, remplacer le `userdata=ctx` du C31 par l'adresse d'une ancre statique `fm36_anchor`. **Il n'est ni intégré, ni lié, ni chargé ni exécuté** en R36. Il ne contient aucun appel `AudioQueue*`, aucun code d'émission ni thread autonome.

La structure `FM36StableAnchor` contient : `atomic_uint phase`, `_Atomic(void *) owner`, `atomic_uint admitted`. Elle et son `atomic_flag fm36_one_shot_claim` ont une durée de vie statique en C11.

1. `fm36_prepare_once(owner,&userdata)` : revendique **une seule fois** l'ancre, publie le propriétaire avec les accès atomiques C11, puis remet une adresse d'ancre **stable jusqu'à la fin du processus**, distincte de `owner`.
2. `fm36_mark_exposed(userdata)` : transition atomique unique `PREPARED → EXPOSED`. **Hypothèse obligatoire** pour une future intégration : effectuer cette transition **avant** de remettre l'adresse à l'OS ; après cette revendication, `owner` ne pourra plus être libéré, **même si la création de la queue échoue**.
3. `fm36_try_enter(userdata,&owner)` : compare d'abord le pointeur `userdata` à l'adresse statique, sans le déréférencer ; consulte ensuite la phase, incrémente le compteur, relit la phase et récupère le contexte par une lecture atomique. Il refuse les admissions tardives après fermeture ; un callback admis peut toutefois se trouver en concurrence avec `seal`.
4. `fm36_leave(userdata)` : CAS décrémentant le compteur tant que sa valeur est positive ; ce compteur ne prouve pas l'appariement par callback ni la fin des entrées OS.
5. `fm36_seal(userdata)` : transition irréversible `PREPARED/EXPOSED → SEALED`, aucun `free`, aucun effacement de propriétaire, aucune réinitialisation et **aucun recyclage**.

**Coût accepté :** la session unique doit être refusée si le slot a déjà servi. Le propriétaire mémoire doit rester alloué jusqu'à la fin du processus. Une fuite bornée à **au plus un propriétaire par processus si le contrat appelant est respecté** est préférable ici à une libération pouvant rendre `userdata` invalide, mais cette politique n'est pas une démonstration de sûreté globale et n'implique aucun arrêt physique.

## Ce que GEN-R36 ne résout pas

- Le vrai C31 continue de passer `ctx` directement à `AudioQueueNewOutput` et `queue_running_listener`. **La protection proposée n'est pas dans le chemin CoreAudio réel**.
- Une ancre statique ne démontre ni l'état d'une file OS après échec `AudioQueueStop` ou `AudioQueueDispose`, ni la terminaison des callbacks déjà admis.
- La validité du `owner` retourné repose sur une obligation **externe** de ne jamais le libérer après préparation ; le module ne contrôle pas tous les alias du propriétaire.
- La double lecture de phase et le comptage atomique n'établissent ni ordonnanceur temps réel sûr, ni happens-before de l'ensemble des données du contexte, ni un appariement exact `enter/leave` en présence d'un code appelant erroné.
- Même un processus mis en quarantaine peut ne pas démontrer la coupure d'un périphérique physique.

## Livrables et statut

- Candidat C11 concret, standalone, **compilé en objet indépendant** par `RUN_GEN_R36_MAC_INTEL.command`, mais **jamais lié** au binaire.
- Audit `audits/r36_static_anchor_proof_gate.py`, 12 obligations `OPEN_NOT_PROVEN` dont 4 CRITICAL ; ancrages source C31/C36 et chaînes de preuve recomputées R16–R35.
- `tests/test_r36_static_anchor_proof_gate.py`, **20 nouveaux tests statiques**, sans simulation scientifique ni invocation CoreAudio.
- `docs/GEN_R36_BUREAU_PROOF_GATES.md` et `docs/GEN_R36_ADVERSARIAL_INTEGRATION_MATRIX.md`.
- **Cibles R36 Mac Intel, non encore attestées : 717 tests Python, 33 assertions natives C, 200 sources SHA-256, 34 rapports du Bureau SHA-256.**

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
