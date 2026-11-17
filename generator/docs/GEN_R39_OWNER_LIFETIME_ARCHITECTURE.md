# FREQMED GEN-R39 — Owner-Lifetime Enforcement & Callback Exit Contract Remediation Design

**Dernière preuve propriétaire Mac Intel : GEN-R38 logiciel PASS le 17 novembre 2026** — 757/757 tests Python, 33/33 assertions natives C, 213/213 sources SHA-256 et 38/38 rapports SHA-256. Ce sont des résultats logiciels sans émission, non une certification C11, OS ou physique.

## Correctif C11 proposé — candidat C39, non intégré

`candidates/r39_owner_lifetime_exit_ticket.c` est une **unité de traduction C11 réelle et isolée**, compilable `clang -c` mais **jamais liée, chargée ni exécutée**. Aucun `AudioQueue`, générateur, instrument EM, callback CoreAudio réel, simulation ou mesure n'y figure. Le vrai C31, la structure R36 et l'adaptateur R37 restent inchangés.

R38 avait recensé 12 relations d'alias et des sorties textuelles ; R39 transforme une partie du contrat d'appariement en **ticket atomique à sortie au plus une fois**. Un `FM39Lease` possède un `atomic_uint phase` et deux pointeurs `os_userdata/owner`, écrits après admission puis **jamais réécrits après publication**. Son cycle source est :

1. `FM39_LEASE_INITIALIZER` : un objet **distinct, vivant et initialisé une fois** (obligation du futur appelant).
2. `fm39_register_owner_once` : utilise `fm36_prepare_once` puis `fm36_mark_exposed` ; après revendication réussie, `owner` doit demeurer vivant jusqu'à la fin du processus, même si l'exposition échoue.
3. `fm39_enter_once` : CAS C11 `UNUSED→RESERVING`, admission par `fm36_try_enter`, publication des pointeurs immuables, puis `ACTIVE` en `memory_order_release`. Les échecs terminent en `REJECTED` ; sur owner nul après admission, sortie compensatrice `fm36_leave`.
4. `fm39_owner_if_active` : lecture `memory_order_acquire` et accès uniquement en `ACTIVE`. Cette synchronisation **locale au ticket** n'établit aucune preuve C11 des autres champs du contexte.
5. `fm39_complete_at_most_once` : CAS `ACTIVE→FINISHED`, puis **seul le gagnant** exécute `fm36_leave`. Une double sortie sur le même ticket encore valide peut donc être refusée même si deux appels sont concurrents. Cela ne garantit ni l'appel final, ni la libération correcte sur chaque erreur OS ; si `fm36_leave` échoue, l'erreur reste ouverte et `FINISHED` est terminal.
6. `fm39_seal_without_release` : délègue à `fm36_seal`, n'efface ni le propriétaire ni son jeton, et **ne prouve aucun arrêt physique**.

La correction obtenue est **strictement locale et conditionnelle** : pour un ticket C11 correctement initialisé, non copié, dont la mémoire reste vivante, un seul CAS `ACTIVE→FINISHED` peut réussir. Les trois conditions sont des **hypothèses externes**, non des faits vérifiés en production. La garantie **at-most-once** ne doit jamais être présentée comme **exactly-once**.

## Règles de gouvernance

Le code C31 continue d'envoyer `ctx` directement à `AudioQueueNewOutput` et au listener ; C36/C37/C39 **ne sont pas intégrés dans les callbacks**. La valeur du pointeur `owner` demeure sous le contrôle des alias externes ; aucun module C11 ne prouve qu'aucun autre composant ne puisse libérer l'allocation. La fin de callback, la quiescence CoreAudio, `AudioQueueStop`/`Dispose` échoués, la sûreté du matériel et la relation happens-before globale restent **NOT_PROVEN**.

Livrables : `audits/r39_owner_lifetime_exit_ticket_review.py` (**16 constats OPEN, dont 4 critiques** ; 32 ancrages C31/C36/C37/C39), `tests/test_r39_owner_lifetime_exit_ticket_review.py` (**20 tests source-only**) et 3 dossiers B07/B09/B10. La validation propriétaire doit, si elle réussit, vérifier **777 Python, 33 assertions natives C, 220 sources SHA-256 et 40 rapports SHA-256 R20–R39**, avec C39 `COMPILED_UNLINKED`.

**PENDING :** aucun témoin GEN-R39 Mac Intel n'est encore fourni. Les onze portes historiques du Bureau restent OPEN / zéro résolue. PR #1 reste DRAFT et non fusionnée.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
