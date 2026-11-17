# FREQMED GEN-R38 — Owner Alias & Callback Exit Path Matrix

**Base effectivement attestée le 16 novembre 2026 : GEN-R37 Mac Intel logiciel PASS — 737/737 Python, 33/33 assertions C natives, 207/207 sources SHA-256, 36/36 rapports SHA-256.** Les preuves logicielles ne certifient pas les callbacks OS ni le matériel.

## Délimitation : source existante, pas de nouveau moteur

GEN-R38 ne modifie aucun fichier C ; aucun nouveau callback ou adaptateur n'est ajouté. Il inspecte les **sources originales épinglées C31/C36/C37** pour déterminer si leur contrat garantit toutes les relations d'alias propriétaire et les sorties de callback. **Réponse : NON, les obligations demeurent ouvertes.**

### 12 relations documentaires d'alias

| Alias / source | Origine observée | Portée et limite |
|---|---|---|
| `owner_ctx` C31 | `calloc` | Propriétaire heap du contrôleur |
| `ctx` C31 | `AcousticContext *ctx=owner_ctx` | Alias direct du propriétaire |
| `ctx` publié via `AudioQueueNewOutput` | `userdata=ctx` | Alias que CoreAudio peut rappeler |
| `ctx` publié via listener | `queue_running_listener,ctx` | Alias transmis au listener |
| `ptr` | `output_callback` | Alias OS converti avant admission |
| `data` | `queue_running_listener` | Alias OS converti avant admission |
| `ctx->queue` | contrôleur / PCM | Référence non atomique sans preuve C11 globale |
| `&fm36_anchor` C36 | statique durée de vie processus | Jeton non réutilisable, **non intégré** |
| `fm36_anchor.owner` | publication atomique | Pointeur conservé, alias externes non contrôlés |
| `lease->owner` C37 | accès après `fm36_try_enter` | Bail non atomique, propriété externe |
| `FM37Lease` output | `fm37_output_enter` | Interface proposée, **pas un callback OS** |
| `FM37Lease` listener | `fm37_property_enter` | Interface proposée, **pas un callback OS** |

### Périmètre d'inventaire des sorties

**C31 contrôleur :** deux instructions `free(owner_ctx)` **avant** `AudioQueueNewOutput`, zéro **après**, dans le candidat. Ce dénombrement textuel ne prouve pas l'absence d'alias indirect ou de `free` dans un composant non inspecté.

**C31 output :** admission R28 précédant compteur `active_output_callbacks`, puis sortie de compteur et `fm_r28_gate_leave` une fois dans la fonction. Le callback convertit `ptr` avant l'accès au gate. Le scanner vérifie qu'aucun `return` textuel se situe entre admission et sortie.

**C31 listener :** compteur `active_property_listeners` après gate ; `goto listener_exit` sur erreurs reconnues, puis un décrément et un `fm_r28_gate_leave`. Un parcours textuel ne constitue pas une preuve d'absence de race avec l'OS.

**C37 :** les fonctions d'entrée output/property renvoient `fm37_begin`. La sortie `fm37_finish` exige `ACTIVE`, invalide le bail, puis `fm36_leave(token)`. Le contrat exige **un bail initialisé à zéro, propre au callback et jamais partagé**, et une sortie exactement une fois sur toutes les branches d'exécution réelles. Aucun wrapper OS ne décharge cette preuve actuellement. Si `fm36_leave` échoue, le bail est déjà `FINISHED` : l'erreur doit rester une obligation explicite.

**C36 :** l'owner est publié de façon atomique, avec une ancre statique et un compteur `admitted`. Il n'existe aucune identité de bail par callback et l'ancre ne peut contrôler un propriétaire libéré par un autre alias.

## Livrables et prudence

`audits/r38_owner_alias_exit_audit.py` : 12 lignes d'alias, **18 constatations `OPEN_NOT_PROVEN`, dont 5 critiques**, chacune liée à deux ancrages source SHA-256. Comparaison exacte des rapports R16–R37 recalculés et refus de lever les portes de sécurité.

`tests/test_r38_owner_alias_exit_audit.py` : 20 nouveaux tests **source-only** ; mutations du code sous forme de chaînes de texte, **pas de simulation scientifique**.

`RUN_GEN_R38_MAC_INTEL.command` : validation de l'intégrité, audit R38 et dossier privé conditionnel de **38 rapports R20–R38 SHA-256**. C31/C36/C37 **compilés mais non liés**, exécutable contrôlé non émetteur.

**Cibles GEN-R38 Mac Intel à vérifier : 757 tests Python, 33 assertions C natives, 213 fichiers SHA-256 et 38 rapports SHA-256.** Aucune exécution Mac R38 n'est attestée avant son journal réel.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
