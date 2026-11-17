# FREQMED GEN-R40 — Independent Ticket Ownership, Copy Prevention & Completion Coverage Review

**Reference réellement attestée : GEN-R39 Mac Intel logiciel PASS (17 novembre 2026)** — 777/777 tests Python, 33/33 assertions natives C, 220/220 sources SHA-256 et 40/40 rapports SHA-256. Ces résultats logiciels n'établissent ni sûreté OS/C11 globale ni sécurité physique.

## Problème hérité

Le candidat C39 impose, comme contrat externe, que l'appelant ne copie, ne réinitialise ni ne libère prématurément son `FM39Lease`. Son type struct est public et pourrait être dupliqué par valeur dans un consommateur C. C39 garantit une terminaison **au plus une fois par objet valide**, pas que chaque callback réel termine. Son `owner` reste aussi un alias externe.

## GEN-R40 : amélioration limitée et tangible de l'interface C11

Deux nouveaux fichiers source **isolés** : `candidates/r40_opaque_ticket.h` et `candidates/r40_opaque_ticket.c`.

1. **Type opaque** — seul `typedef struct FM40Ticket FM40Ticket;` apparaît dans l'interface publique. La définition de `struct FM40Ticket` reste privée dans le .c. Un appelant C correctement typé ne peut donc créer une variable de ce type, prendre son `sizeof`, copier le struct par valeur ou en modifier directement les membres. Un **contrôle négatif réel du compilateur `clang -fsyntax-only`** doit rejeter `FM40Ticket forbidden_copy;`.
2. **Quatre emplacements statiques** — `FM40_MAX_TICKETS=4`, `fm40_slots` privés à durée de vie du processus, C11 `atomic_uint phase`. Aucune allocation ni libération. Chaque emplacement revendiqué ne sera **jamais réutilisé**, même après admission refusée. **Limitation délibérée : seulement quatre tentatives d'entrée par processus ; cette capacité finie est incompatible avec un flux CoreAudio non borné**, donc le candidat n'est pas une architecture de production.
3. **Admission** — `fm40_begin` réserve un slot par CAS `UNUSED→RESERVED`, appelle `fm36_try_enter` avant de rendre le propriétaire accessible, puis publie `ACTIVE` en `memory_order_release`. Les erreurs conduisent à `REJECTED`; une admission provisoire sans propriétaire déclenche un `fm36_leave` compensateur, dont l'échec n'est pas résolu.
4. **Terminaison** — `fm40_complete` compare le **pointeur du ticket à l'adresse d'un des slots privés avant de le déréférencer**, puis seul le gagnant du CAS `ACTIVE→FINISHED` appelle `fm36_leave`. La protection est **AT-MOST-ONCE par emplacement valide**, pas une preuve **EXACTLY-ONCE** ni une garantie de `complete` sur toutes les sorties du callback. Le ticket reste alloué à vie.
5. **Propriétaire** — `fm40_register_owner_once` s'appuie sur l'ancre R36. Après la revendication d'`owner`, **aucun alias externe ne doit libérer le contexte avant la fin du processus**. La fonction remet explicitement un `owner_out` : des copies de ce pointeur restent possibles et non contrôlées.
6. **Fermeture** — `fm40_seal` délègue à `fm36_seal`. Elle **n'est pas une preuve de quiescence CoreAudio**, de résultat `AudioQueueStop/Dispose`, ni de coupure physique.

**Limite centrale :** l'opacité C empêche la copie **par valeur correctement typée**, non le partage ou la copie d'un pointeur, les cast, `memcpy` et autres comportements invalides. C40 ne prouve ni la durée de vie de `owner`, ni l'appel de `complete` au moins une fois, ni la sûreté des données non atomiques de C31. La capacité de quatre slots est volontairement bloquante.

## Périmètre et preuves

Le vrai C31 transmet toujours `userdata=ctx` au callback de sortie et au listener ; **aucune intégration C40 dans un callback OS**. C31/C36/C37/C39 sont inchangés. Le C40 est un **objet source compilé seulement en `clang -c`, jamais lié ni chargé**, aucun vrai callback ni son ou champ EM.

- Auditeur `audits/r40_ticket_copy_completion_review.py` : **18 constats OPEN, 5 CRITICAL**, 36 témoins source SHA-pinnés et six contrats documentaires C11, recalcule les preuves R16–R39, refuse toute promotion des 11 portes historiques du Bureau.
- Tests `tests/test_r40_ticket_copy_completion_review.py` : **20 nouveaux tests Python source-only** ; quatre mutations textuelles adversariales. Contrôle négatif de copie C avec compilateur, pas simulation scientifique.
- Lanceur `RUN_GEN_R40_MAC_INTEL.command` : C40 compilé séparément et **non lié**, `nm`, CLI hard-denied, et dossier **42 rapports R20–R40 SHA-256** conditionné à la réussite des tests.
- **Cibles GEN-R40 Mac Intel PENDING : 797 Python, 33 assertions C natives, 228 sources SHA-256, 42 rapports SHA-256**. Dernier résultat Mac réellement acquis : GEN-R39 logiciel PASS.

`NEVER_SIMULATION=ENFORCED` ; `ZERO_COST_FOSS=ENFORCED` ; `ACOUSTIC_OUTPUT=LOCKED` ; `EM_OUTPUT=LOCKED` ; `REAL_OUTPUT=NOT_AUTHORIZED` ; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` ; `PRODUCTION=NOT_AUTHORIZED`.
