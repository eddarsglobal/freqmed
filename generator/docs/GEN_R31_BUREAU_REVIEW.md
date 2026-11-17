# FREQMED GEN-R31 — Revue indépendante du Bureau B07/B09/B10

**Verdict : `SHUTDOWN_STOP_ATTEMPT_REORDERED_SOURCE_ONLY_OS_SAFETY_UNPROVEN`.**

## Décision conservatrice

**B10 / sécurité physique :** SH31_01 + SH31_02 demeurent **CRITICAL OPEN_NOT_PROVEN**. GEN-R31 supprime **dans la source** le contournement particulier de l'appel d'arrêt précédant le retour occupé. Toutefois, une tentative `AudioQueueStop` qui échoue peut laisser la file active ; le programme ne possède ni preuve de non-émission ni stratégie matérielle indépendante. **Interdiction d'activer ce candidat**, même si tous les tests Python/C réussissent.

**B07 / contrat OS :** SH31_05 + SH31_06 restent ouverts : retrait du listener, échec `AudioQueueDispose`, callbacks tardifs et validité de userdata avant admission. La libération de mémoire reste interdite sans preuve OS et C11.

**B09 / modèle C11 :** SH31_03 + SH31_04 + SH31_07 restent ouverts : accès à `ctx->queue` sans lease côté contrôleur, réentrance `AudioQueueEnqueueBuffer` sous verrou PCM, attribution exclusive des ressources, appariement enter/leave et preuve happens-before.

**B10 / ressources :** SH31_08 : borne des ressources OS conservées en quarantaine, état de fermeture, non-émission et arrêt sûr du processus. La quarantaine n'est pas une mesure physique.

| Gouvernance | Statut |
|---|---|
| Nouveau C31 | Objet C **isolé, non lié et jamais exécuté** |
| Code C original / candidats R26, R29, portail R28 | **Inchangés** |
| Nouveau dossier R31 | **8 OPEN, dont 2 CRITICAL** |
| Constats R30 | **12 OPEN, dont 2 CRITICAL** |
| Constats R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| Obligations R23 / R24 | 15 / 7 OPEN |
| Portes originales Bureau | **11 OPEN, 0 résolue** |
| Essais physiques / CoreAudio actif | **AUCUN** |
| Signatures indépendantes | **AUCUNE** |
| Mac Intel GEN-R31 | **PENDING** |
| PR #1 | **DRAFT, non fusionnée** |

**Objectifs non encore attestés** : 617 tests Python, 33 assertions natives C, 169 fichiers source SHA-256 et 24 rapports de revue privés SHA-256. Ne pas transformer un succès logiciel en preuve de race freedom, de quiescence ou de coupure physique.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
