# FREQMED GEN-R37 — Independent Static-Anchor Integration Feasibility & C11 Ownership Proof Review

**Baseline réelle : GEN-R36 FIX1 Mac Intel PASS, 717/717 tests Python, 33/33 assertions natives C, 200/200 fichiers source SHA-256, 34/34 rapports SHA-256.** Ces preuves logicielles n'autorisent ni émission physique, ni qualification C11/CoreAudio.

## Proposition intégrable plus tard, mais pas intégrée aujourd'hui

Le nouveau candidat **`candidates/r37_callback_lease_adapter.c`** est une unité C11 indépendante. Elle utilise les cinq fonctions **externes** du module R36, sans appeler CoreAudio ni exposer de callback OS réel. Le module R36 et le C31 sont **inchangés**. Le C37 est seulement compilé en objet isolé `-c` ; aucun lien, chargement ou dispatch n'est autorisé.

Le défaut initial était précis : dans le C31, l'OS remet `ctx` directement aux deux callbacks. Le callback doit accéder à `ctx->queue_admission` pour obtenir une admission atomique : si `ctx` est périmé, ce premier accès est déjà trop tard.

Le C37 ajoute donc un *contrat d'adaptation* :
- `fm37_prepare_token(owner,&userdata)` revendique l'ancre statique R36 et la publie **avant** une hypothétique remise à l'OS. Dès la revendication, **aucun alias du contexte ne doit le libérer**, même si `mark_exposed` échoue.
- `fm37_output_enter` et `fm37_property_enter` acquièrent `fm36_try_enter` **avant** de donner accès au propriétaire. Ces fonctions ne correspondent **pas** aux signatures CoreAudio ; les wrappers OS restent à concevoir et qualifier.
- `FM37Lease` doit être une structure **fraîche, initialisée à zéro et propre à un callback**, jamais partagée entre threads. Elle tient `os_userdata`, `owner`, et `phase`.
- `fm37_lease_owner` ne donne accès au propriétaire que si `phase==ACTIVE`, mais ne prouve aucune relation de *happens-before* pour les autres champs C.
- `fm37_finish` effectue un changement local irréversible `ACTIVE→FINISHED`, efface les pointeurs locaux puis appelle `fm36_leave`. Cela empêche une deuxième sortie **séquentielle pour le même bail local**, pas un appel `finish` manquant, un bail partagé de façon incorrecte ni la désynchronisation d'un compteur global.
- `fm37_seal_token` refuse de nouvelles admissions via R36. Un OSStatus d'arrêt ou de disposition échoué **ne devient pas** une preuve de quiescence, de coupure physique ou de libération sûre.

## Décisions d'intégration et préconditions bloquantes

| Risque | Choix du candidat | Preuve encore nécessaire |
|---|---|---|
| `userdata` périmé avant gate | Ancre statique process-lifetime R36 | Wrappers OS exacts et durée de vie de la mémoire propriétaire |
| Callback et listener séparés | Deux fonctions d'entrée explicites | Vrais callbacks CoreAudio non exécutés |
| Double sortie séquentielle | Bail local `FINISHED` avant `fm36_leave` | Contrôle de toutes les sorties de callbacks et absence de partage |
| Fin de bail oubliée | Aucun mécanisme asynchrone ne la répare | Vérification exhaustive des sorties et erreurs |
| Alias `owner` libérés ailleurs | Conservation contractuelle jusqu'à fin du processus | Audit de tous les alias et sites de libération |
| Arrêt/disposition OS échoués | Quarantaine logicielle et refus d'admission | Contrat OS et coupure physique indépendants |
| Propriétés non atomiques de `ctx` | Aucune correction dans C37 | Preuve C11 *happens-before* intégrale |
| Liaison accidentelle à l'exécutable | `clang -c`, audit `nm` et allowlist | Témoin Mac Intel et contrôle du packaging |

**GEN-R37 ne peut être présenté comme un correctif du chemin de production.** Les callbacks C31 restent inchangés ; aucune fonction d'émission n'a été ajoutée, aucun traitement de PCM ni exposition physique.

## Livrables

`audits/r37_adapter_ownership_proof_review.py` relève **14 constats ouverts dont 4 critiques**, avec deux ancrages source SHA-256 par constat, six contrats C11 documentaires, recomputation des preuves R16–R36, et vérification du linker. `tests/test_r37_adapter_ownership_proof_review.py` ajoute **20 tests source-only**, dont cinq mutations défensives du code texte.

`RUN_GEN_R37_MAC_INTEL.command` doit établir **36 rapports SHA-256 R20–R37**, avec les candidats C31/C36/C37 compilés mais **non liés** et le CLI `output_hard_denied.c` seul pour les sorties.

**Cibles Mac Intel R37 non encore attestées : 737 tests Python, 33 assertions natives C, 207 fichiers source SHA-256 et 36 rapports SHA-256.** Toutes les obligations R36 et historiques demeurent ouvertes ; 11 portes du Bureau OPEN/0 résolue.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
