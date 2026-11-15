# FREQMED — Bureau GEN-R28 : Admission C11, file CoreAudio et fermeture

**Verdict maximal : `BOUNDED_C11_ADMISSION_DESIGN_UNCERTIFIED`.** L'unité C11 compilable constitue un brouillon de contrat, non une preuve d'absence de race, d'absence de callback tardif ou de coupure physique.

**B07 — OS et cycle de vie.** Prouver le contrat de retrait des listeners et l'admission des callbacks après `AudioQueueDispose`, y compris les erreurs. `ctx->queue` peut devenir invalide même quand `owner_ctx` reste alloué. Interdire tout `free` d'un userdata publié avant justification indépendante.

**B09 — Mémoire et temps réel.** Vérifier le protocole lease/closed de toutes les entrées callback, listener et contrôleur. Chaque sortie d'une lease acceptée doit être comptabilisée exactement une fois. Aucune lecture/écriture non atomique de `queue` ne doit se produire sans preuve happens-before. Ne pas confondre une CAS C11 avec une preuve OS. Étudier les risques de réentrance `AudioQueueEnqueueBuffer` sous `pcm_writer_gate` (AD02) et leur borne de temps.

**B10 — Sûreté du processus.** Une quarantaine permanente peut conserver tas et ressources OS : définir et vérifier les limites de mémoire, les erreurs de disposition et le protocole d'arrêt. Ne donner aucune permission d'émission ou d'essai matériel.

| Statut | GEN-R28 |
|---|---|
| Source originale C modifiée | **0** |
| Candidat R26 modifié | **0** |
| Nouvelle unité C11 | **1**, isolée, non liée |
| Nouveaux contrôles de conception | **5 OPEN_NOT_PROVEN** |
| Constats adversariaux R27 | **9 OPEN** |
| Obligations R23 | **15 OPEN** |
| Constats R24 | **7 OPEN** |
| Portes Bureau | **11 OPEN / 0 résolue** |
| C11 race freedom / quiescence | **NOT_PROVEN** |
| Disposition OS en échec | **NOT_TESTED** |
| CoreAudio actif / émission | **INTERDITS** |
| Signature indépendante | **NONE** |

**Cible logicielle Mac Intel avant signature : 557 Python, 33 C, 150 SHA-256, 18 rapports vérifiés.** Aucun chiffre cible ne vaut témoignage d'exécution. R28 ne corrige pas encore le backend ; la prochaine étape d'intégration isolée nécessitera une revue source/OS plus approfondie, sans émission.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
