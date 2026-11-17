# FREQMED GEN-R43 — Independent Post-Closure Admission, Ticket Authentication & Lifetime Capacity Review

**Dernier témoin propriétaire réellement acquis : GEN-R42 Mac Intel logiciel PASS (17 novembre 2026), 837/837 tests Python, 33/33 assertions natives C, 244/244 fichiers source SHA-256 et 46/46 rapports SHA-256.** Aucun de ces résultats logiciels ne certifie C11 global, Apple CoreAudio ou une coupure physique.

## Changement concret : autorisation avant publication

Le nouveau candidat C11 isolé `candidates/r43_publication_authority.c` et son en-tête `.h` ne sont **jamais liés, chargés ni exécutés**. Tous les candidats C31/C36/C37/C39/C40/C41/C42 et le moteur original restent inchangés.

R42 associait dans un mot atomique `CLOSED` et le compteur de réservation. Cependant, le ticket pouvait devenir visible après un `CLOSED` concurrent. R43 ajoute une **seconde étape CAS d'autorisation**, sur **ce même mot atomique** `fm43_gate`. Celui-ci contient désormais trois champs : bit `CLOSED` (31), nombre total de réservations (0–7), nombre d'autorisations accordées (8–15). La fonction `fm43_reserve` consomme un permis à vie lorsque la porte est ouverte. Après `fm36_try_enter`, `fm43_authorize` exige encore la porte ouverte et un nombre d'autorisations inférieur aux réservations, puis augmente le compteur d'autorisations par CAS. Un CAS d'autorisation qui se situe **après `CLOSED` dans l'ordre de modification atomique** ne peut gagner.

**Limite critique :** le CAS d'autorisation est distinct de l'écriture `*owner_out=owner` / `*ticket_out=slot`. Une fermeture peut survenir **entre ces deux actes** ; le retour externe peut donc encore se produire après fermeture. R43 ne prouve PAS « aucun callback après fermeture », ne fournit ni barrière de quiescence OS ni suppression de tous les callbacks déjà admis.

## Représentation du ticket et conservation du propriétaire

C43 expose un `FM43Ticket*` opaque. Pour `fm43_complete(ticket, expected_userdata)`, l'identité du pointeur doit correspondre à un slot privé et le jeton `os_userdata` capturé doit égaler `expected_userdata` **après une lecture de phase acquire**, avant la transition CAS `ACTIVE→FINISHED` et `fm36_leave`.

Il s'agit d'un **appariement de deux pointeurs, pas d'une authentification de l'appelant**. Un détenteur d'un couple valide peut le recopier, le divulguer ou tenter une fin anticipée. Un ticket valide qui n'appelle jamais `complete` n'est pas récupéré. Le CAS reste **AT-MOST-ONCE**, pas **EXACTLY-ONCE**.

Les **quatre slots C11 sont statiques, permanents et jamais réutilisés**. Les échecs consomment définitivement les permis. Cette capacité ne convient pas aux callbacks CoreAudio réels et non bornés. Les alias externes d'`owner` restent sous contrat de conservation jusqu'à la fin du processus, et `fm36_leave` compensateur peut échouer.

## Périmètre de preuve GEN-R43

- `audits/r43_publication_authority_review.py` : **21 obligations OPEN, 6 CRITICAL**, 42 ancrages source SHA-pinnés, six contrats documentaires, recalcul de la chaîne R16–R42 et maintien de **11 portes du Bureau OPEN / 0 résolue**.
- `tests/test_r43_publication_authority_review.py` : **20 tests source-only**, trois mutations adversariales textuelles. Aucune exécution d'un callback C43, aucun interleaving simulé, aucune activité acoustique/EM.
- `RUN_GEN_R43_MAC_INTEL.command` : `clang -c` en objet isolé non lié, `nm`, garde du CLI `output_hard_denied.c`, rapports historiques et **48 preuves R20–R43 JSON/MD SHA-256** seulement après succès total.
- **Objectifs Mac Intel GEN-R43 PENDING : 857 tests Python, 33 assertions C natives, 252 sources SHA-256, 48 rapports SHA-256.** Ces comptes sont des cibles, pas un résultat natif déjà attesté.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`. PR #1 reste DRAFT, non fusionnée.
