# FREQMED — Bureau GEN-R29 : audit d'intégration de l'admission C11

**Verdict admissible : `ISOLATED_INTEGRATION_REVIEWED_C11_OS_PROOF_OPEN`.** Un prototype C isolé est ajouté, mais aucune qualification C11, CoreAudio, acoustique, EM ou médicale n'est conclue.

**B07 — durée de vie OS** : refuser la certification tant que l'OS ne garantit pas la validité de userdata dès l'entrée et tant que les callbacks/listeners tardifs et les échecs de disposition n'ont pas été qualifiés. La propriété du pointeur `ctx->queue` est distincte de la propriété de `owner_ctx`.

**B09 — concurrence et temps réel** : démontrer une relation happens-before pour chaque lecture/écriture partagée, le succès et l'échec de la CAS, chaque bail accepté et chaque sortie de callback. Documenter l'absence de blocage et la latence réelle de `AudioQueueEnqueueBuffer` sous verrou PCM. Le succès de tests lexicaux n'est pas une preuve.

**B10 — ressources et sécurité physique** : la branche qui refuse une disposition pendant un bail laisse potentiellement les ressources CoreAudio vivantes. Vérifier l'impact d'une sortie physique hypothétique, sans jamais l'activer ; conserver le binaire de refus matériel et l'interdiction d'exposition biologique.

| Contrôle | GEN-R29 |
|---|---|
| Nouvelle source C isolée | `candidates/acoustic_macos_r29.c` |
| Backend C historique modifié | **0** |
| Candidat R26 / contrat R28 modifiés | **0 / 0** |
| Nouveau C exécuté ou lié | **NON** |
| Nouveaux constats source | **7 OPEN_NOT_PROVEN** |
| Risques R27 | 9 OPEN |
| Contrôles R28 | 5 OPEN |
| Obligations R23 / R24 | 15 / 7 OPEN |
| Portes du Bureau | **11 OPEN, 0 résolue** |
| Callback CoreAudio exécuté | **NON** |
| Échec OS `AudioQueueDispose` qualifié | **NON** |
| Certificats indépendants | **AUCUN** |

**Cibles Mac Intel non encore attestées : 577 Python, 33 assertions C, 156 sources SHA-256, 20 rapports SHA-256.** Conserver la PR #1 DRAFT, sans fusion.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
