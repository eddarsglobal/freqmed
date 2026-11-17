# FREQMED GEN-R41 — Ticket Capacity, Pointer Aliasing & Failure-Path Containment Review

**Dernière validation Mac Intel attestée : GEN-R40 logiciel PASS le 17 novembre 2026, 797/797 tests Python, 33/33 assertions natives C, 228/228 sources SHA-256 et 42/42 rapports SHA-256.** Ces témoins ne certifient ni C11/OS ni sécurité physique.

## Ce que GEN-R41 améliore effectivement

C40 conserve quatre `FM40Ticket*` vers des emplacements privés statiques, jamais recyclés. Le type opaque empêche une copie **par valeur correctement typée**, mais un pointeur de ticket peut être partagé. Un callback peut échouer, omettre de terminer et laisser un compteur d'admission non soldé. Quatre tickets ne peuvent servir un flux CoreAudio non borné.

GEN-R41 apporte **deux fichiers C11 nouveaux, indépendants et non liés**, `generator/candidates/r41_index_ticket.h` et `.c`, pour isoler la **gestion de capacité, la représentation d'un ticket et l'enregistrement terminal des erreurs**.

- **Référence par indice :** `FM41TicketRef {unsigned slot_id;}`, index de 1 à 4, 0 invalide. Les adresses internes des tickets ne sont pas remises au client. **IMPORTANT : l'indice est copiable et falsifiable, sans authentification ni propriété exclusive**. Un détenteur d'un indice valide peut tenter une terminaison anticipée ; il ne constitue donc pas une capacité de sécurité.
- **Capacité process-lifetime :** 4 slots C11 privés, phases `UNUSED / RESERVED / ACTIVE / FINISHED / REJECTED`, jamais recyclés. Tout slot revendiqué est définitivement consommé, y compris après une admission refusée. Un épuisement entraîne `FM41_FAULT_CAPACITY` et un refus. **Ce modèle est manifestement insuffisant pour la production CoreAudio**, où le nombre d'entrées n'est pas limité à quatre sur toute la vie du processus.
- **Admission :** `fm41_begin` valide ses sorties, initialise les résultats invalides, refuse les erreurs déjà observées, revendique un slot par CAS, contrôle le masque d'erreurs une seconde fois, appelle `fm36_try_enter` avant publication d'owner et finit par publier un indice. Cette vérification double **n'est pas atomiquement coordonnée** avec des défaillances apparaissant juste après le second contrôle ; ne pas la présenter comme un verrou global.
- **Confinement de l'erreur :** masque `atomic_uint fm41_fault_latch`, mis à jour par `atomic_fetch_or`, jamais réinitialisé. Il enregistre capacité épuisée, admission, owner nul, index invalide, doublon de sortie, échec `fm36_leave`, inscription ou scellement refusés. **Ce registre logiciel n'est pas un `AudioQueueStop` ni une barrière de quiescence OS.**
- **Sortie :** `fm41_complete` refuse les indices hors bornes **avant** l'accès au slot. Seul un CAS `ACTIVE→FINISHED` réussi peut appeler une fois `fm36_leave`. La même valeur `slot_id` peut cependant être copiée ou forgée, et rien ne garantit qu'un callback réel appelle la terminaison.
- **Owner :** `owner_out` reste un pointeur non géré, sans garantie de durée de vie de tous les alias. L'ancre R36 exige sa conservation même si l'inscription OS échoue. `fm41_register_owner_once` et `fm41_seal` n'autorisent ni libération ni émission.

## Risques toujours bloquants

Le C31 réel continue de transmettre **`userdata=ctx`** à la sortie CoreAudio et au listener. Les candidats C36/C37/C39/C40/C41 ne sont **pas intégrés**, ne possèdent aucune preuve de quiescence Apple, d'appariement `begin/complete` exhaustive ou de coupure physique. Le C41 ne résout pas le problème de capacité : il le transforme en **échec explicite, persistant et sans repli**.

Les nouveaux outils : `audits/r41_capacity_alias_failure_review.py` (**19 constats `OPEN_NOT_PROVEN`, 5 CRITICAL**, 38 témoins SHA-pinnés, six contrats), `tests/test_r41_capacity_alias_failure_review.py` (**20 tests source-only** dont mutations de chaînes), et trois dossiers de Bureau. Le lanceur `RUN_GEN_R41_MAC_INTEL.command` compile C41 en **objet isolé non lié**, reprend la chaîne authentique R16–R40, contrôle `nm` et l'exécutable hard-denied, puis 44 rapports SHA-256 seulement si tout réussit.

**Objectifs GEN-R41 Mac Intel non encore attestés : 817 tests Python, 33 assertions C natives, 236 fichiers sources SHA-256, 44 rapports SHA-256 R20–R41.** La PR #1 reste DRAFT non fusionnée, Bureau 11 OPEN/0 résolue.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
