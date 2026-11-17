# FREQMED GEN-R32 — Bureau B07/B09/B10, revue indépendante de la fermeture en échec

**Verdict maximal autorisé : `FAILED_STOP_CONTAINMENT_REVIEWED_PHYSICAL_SAFETY_UNPROVEN`.**

### B10 — sécurité de sortie et confinement

**FS32_01, FS32_02 CRITICAL, OPEN_NOT_PROVEN.** Une opération `AudioQueueStop(ctx->queue,true)` peut renvoyer un statut non nul ; le candidat R31 retourne après quarantaine logicielle, sans vérifier un arrêt physique. Aucun rapport ne peut annoncer `SAFE_SHUTDOWN`, `HARDWARE_STOP=PASS` ou `OUTPUT_CUTOFF=PROVEN` en l'absence d'une preuve instrumentale indépendante. L'arrêt du processus et la conservation des ressources ne démontrent pas la fin d'une émission.

### B07 — contrat de l'OS

**FS32_03, FS32_06, FS32_07 HIGH, OPEN_NOT_PROVEN.** La fermeture du portail atomique ne prouve pas l'absence d'une entrée OS tardive sur `userdata` ; `AudioQueueRemovePropertyListener` et `AudioQueueDispose` doivent être examinés en cas de défaillance et en présence de callbacks déjà dispatchés. Ne pas convertir la validité supposée du contexte en validité de `ctx->queue`.

### B09 — mémoire partagée, accès PCM et temps réel

**FS32_04, FS32_08, FS32_09 HIGH, OPEN_NOT_PROVEN.** Chaque accès contrôleur/callback à la référence queue requiert une analyse happens-before complète. Les leases acceptés, les ressources retenues et `AudioQueueEnqueueBuffer` sous verrou PCM ne sont pas couverts par une simple lecture `closed_and_empty`.

### Autres obligations B10

**FS32_05, FS32_10 HIGH, OPEN_NOT_PROVEN.** Réussite de `AudioQueueStop` ≠ mesure physique, et arrêt du processus ≠ politique démontrée de coupure de tous les équipements.

| Catégorie | État |
|---|---|
| Nouveaux risques R32 | **10 OPEN, dont 2 CRITICAL** |
| R31 | **8 OPEN, dont 2 CRITICAL** |
| R30 | **12 OPEN, dont 2 CRITICAL** |
| R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN / 0 résolue** |
| Preuve de coupure physique | **NOT_PROVEN** |
| Quiescence callbacks | **NOT_PROVEN** |
| Races C11 | **NOT_PROVEN** |
| Échec réel AudioQueueStop | **NOT_TESTED** |
| Signatures indépendantes | **NONE** |
| Code C modifié | **0** |
| PR | **DRAFT ; aucune fusion** |

**Attente Mac Intel :** 637 tests Python, 33 assertions C, 175 fichiers épinglés, 26 rapports SHA-256. Un succès valide le dossier de revue mais **ne décharge aucune preuve de sécurité**.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
