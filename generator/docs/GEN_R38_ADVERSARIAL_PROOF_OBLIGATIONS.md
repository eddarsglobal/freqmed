# FREQMED GEN-R38 — Adversarial Owner Alias & Exit-Path Proof Obligations

**Aucune simulation de callback ou d'interleaving C11 ; mutations textuelles uniquement.**

| Chemin / menace | Ancrage source inspecté | Obligation non déchargée |
|---|---|---|
| `owner_ctx` alloué, non publié | `calloc`, deux `free(owner_ctx)` | Exhaustivité de toutes les copies et de tous les échecs |
| `ctx` remis à NewOutput | `AudioQueueNewOutput(...,ctx,...)` | Aucun callback tardif après libération |
| `ctx` remis au listener | `queue_running_listener,ctx` | Durée de vie listener indépendante des compteurs |
| Entrée output avant gate | `ptr→ctx→ctx->queue_admission` | La validité avant le premier accès atomique |
| Entrée listener avant gate | `data→ctx→ctx->queue_admission` | Idem, indépendamment des propriétés OS |
| Décrément output et leave | Un `fetch_sub`, un `gate_leave` | Appariement effectif sur tous les ordonnancements |
| Sortie listener partagée | `goto listener_exit` | Couverture de tout appel réel, y compris échec OS |
| Bail local C37 | `FM37Lease phase` | Initialisation à zéro et absence de partage interthreads |
| Fin C37 | `ACTIVE→FINISHED→leave` | Appariement once-only, sortie sur tout parcours réel |
| `fm36_leave` échoue | compteur R36 / retour négatif | Ne pas masquer l'échec derrière `FINISHED` |
| Propriétaire R36 atomique | `_Atomic(void *) owner` | Tous les alias de `owner` gardés vivants |
| Compteur R36 global | `atomic_uint admitted` | Identité propre à chaque callback et HB C11 |
| `ctx->queue` non atomique | Enqueue / clear | Preuve de non-concurrence à l'échelle du moteur |
| Stop OS échoué | `r31_immediate_stop_status != noErr` | État réel de la file et coupure physique |
| Dispose OS échoué | `AudioQueueDispose != noErr` | Quiescence OS et libération sûre |
| Modules C36/C37 | Objets `clang -c` non liés | Intégration interdite tant que preuves manquent |
| Intégrité / traçabilité | Manifestes SHA-256, rapports R16–R37 | Ne pas assimiler à une démonstration d'absence de race |
| Matériel et exposition | Aucune sortie dans le binaire | Aucune qualification physique ou médicale |

## Discipline de validation

- Les contrôles sont effectués sur les fichiers C31/C36/C37 **inchangés**. Aucun correctif C autonome ne peut lever les obligations du Bureau.
- Les résultats `PASS` de l'auditeur signifient seulement que les obligations ouvertes restent correctement détectées et documentées.
- Le scanner lexical ne voit pas les alias produits par du code externe, des APIs système ou des transformations de compilateur ; il ne démontre pas l'absence de race.
- Tout échec d'audit, rapport manquant, différence d'empreinte ou comportement OS non prouvé doit conduire à **fail-closed**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
