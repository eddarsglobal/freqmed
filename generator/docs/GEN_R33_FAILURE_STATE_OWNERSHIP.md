# FREQMED GEN-R33 — Independent CoreAudio Failure-State Ownership & Safe-Abandonment Contract Design

**Baseline propriétaire réellement exécutée : GEN-R32, 637/637 tests Python, 33/33 assertions natives C, 175/175 fichiers source SHA-256, 26/26 rapports SHA-256 PASS.** Il s'agit de preuves logicielles d'un binaire non émetteur et d'un audit source. Aucune certification CoreAudio ou matérielle.

## Objet, frontières et refus d'une pseudo-correction

GEN-R33 **ne modifie aucun fichier C**. Le candidat `candidates/acoustic_macos_r31.c` reste compilé en objet isolé, **jamais lié ni exécuté**. L'objectif est de séparer : (a) propriété de la mémoire `owner_ctx`, (b) propriété/validité du handle `ctx->queue` détenu par l'OS, (c) droit de CoreAudio d'entrer dans les callbacks avec `userdata`, (d) état réel d'une sortie acoustique. Ces quatre dimensions ne se déduisent pas les unes des autres.

Il faut éviter une fausse garantie : **`AudioQueueStop(...,true)` retournant une erreur ne prouve aucun arrêt**. `AudioQueueDispose` échoué ne prouve ni queue valide ni queue morte. `closed_and_empty` est un prédicat C11, non un contrat d'annulation des appels OS. Même un `dispose_confirmed` ne suffit pas, sans preuve complémentaire, à rendre sûr un `free(owner_ctx)` après publication.

## Les dix états source et leur interprétation conservatrice

| Classe documentaire | Source et propriété du contexte | État de file OS | Décision conservatrice dans la source |
|---|---|---|---|
| PRE_PUBLISH_INVALID_FRAMES | `owner_ctx` local, pas de publication | Aucune file publiée | Libération prépublication présente dans le C, preuve de totalité encore à qualifier |
| PRE_PUBLISH_INVALID_FADE | `owner_ctx` local, pas de publication | Aucune file publiée | Même libération prépublication, avec test de conservation |
| NEW_OUTPUT_ERROR | `userdata` potentiellement capturé | Construction partielle non caractérisée | Conserver le contexte ; quarantaine ; pas de nouvel essai |
| ROUTE_REJECT_DISPOSE_SUCCESS | Contexte publié au créateur | Disposition OS indiquée réussie | Conserver le userdata en attendant la preuve de quiescence |
| ROUTE_REJECT_DISPOSE_FAILURE | Contexte publié | Queue et buffers potentiellement ambigus | Conserver les références C, refuser nouvel essai |
| STOP_FAILURE | Contexte publié, file possiblement encore active | OSStatus non nul ; état non qualifié | Conserver contexte/queue, quarantaine ; **aucune preuve de coupure physique** |
| STOP_SUCCESS_BUSY_LEASE | Contexte publié ; admissions déjà acceptées | Stop OS peut avoir réussi, callbacks encore incertains | Conserver contexte et queue, ne pas disposer pendant l'incertitude |
| LISTENER_REMOVE_FAILURE | Contexte publié, listener non confirmé retiré | Callback tardif possible | Conserver userdata ; preuve OS requise même après disposition |
| FINAL_DISPOSE_FAILURE | Contexte publié | File OS potentiellement invalide ou active | Conserver sans conclure à la validité du handle |
| FINAL_DISPOSE_SUCCESS | Contexte publié ; dispose_confirmed | File réputée disposée après succès OS | Conserver userdata en attente de preuve de fin de tous les callbacks |

Ces états **sont des catégories documentaires**. Ils ne sont pas un automate exécuté, et leurs libellés n'autorisent **aucune** libération supplémentaire, reprise, activation, mesure scientifique ni simulation.

## Audits, preuves et veto

- `audits/r33_failure_state_ownership_contract.py` : dix classes source avec deux ancrages du C31 et SHA-256, **12 constats OPEN_NOT_PROVEN dont 3 CRITICAL**, recalcul indépendant de la chaîne R16–R32 et du rapport propriétaire R32.
- `tests/test_r33_failure_state_ownership_contract.py` : 20 tests Python source-only, dont mutations adversariales, conservation du backend original R19, et impossibilité d'inférer un droit de libération d'un résultat OS.
- `RUN_GEN_R33_MAC_INTEL.command` : audit non émetteur, preuve de compilation C31 isolée, contrôle `nm` et génération d'un dossier de **28 rapports privés R20–R33 vérifiés SHA-256** uniquement après la réussite intégrale.

**Cibles Mac Intel R33 non attestées : 657 tests Python ; 33 assertions natives C ; 181 fichiers SHA-256 ; 28 rapports SHA-256.** Aucune de ces cibles n'autorise un changement des 11 portes du Bureau.

Références officielles à qualifier juridiquement/techniquement avant tout usage physique :
- Apple AudioQueueStop : https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
- Apple AudioQueueDispose : https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
- Apple AudioQueueRemovePropertyListener : https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
