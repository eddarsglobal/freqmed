# FREQMED GEN-R30 — Bureau indépendant : admission, sortie et quiescence

**Verdict maximal autorisé : `ADVERSARIAL_COREAUDIO_LIFETIME_GAPS_CONFIRMED_UNCERTIFIED`.** N'affirmer ni absence de races ni validité OS de callbacks après une validation lexicale. Aucun des constats n'est reproduit par une exécution CoreAudio.

| Collège | Obligation prioritaire R30 |
|---|---|
| **B10 / sécurité physique** | Q30_02 + Q30_12 **CRITICAL** : après `AudioQueueStart`, le retour anticipé `closed_and_empty==false` court-circuite `AudioQueueStop` et `AudioQueueDispose`. Interdiction d'intégrer ce candidat tant qu'une fermeture fail-closed prouvée et indépendante n'existe pas |
| **B07 / contrat OS** | Q30_01, 06, 08, 09, 10 : cycle de vie `userdata`, callbacks tardifs, retrait listener, échecs `AudioQueueDispose`, échec partiel `AudioQueueNewOutput` |
| **B09 / concurrence C11** | Q30_03, 04, 05, 07, 11 : propriété des accès contrôleur, PCM, `ctx->queue=NULL`, enqueues sous verrou, appariement des leases et contrat temps réel |

### Portes toujours OPEN

La nouvelle revue n'autorise pas à résoudre les **7 constats R29**, **5 contraintes de conception R28**, **9 risques R27**, **15 obligations R23**, **7 risques R24** ou **11 portes originales du Bureau**. Aucune signature externe n'est ajoutée. Le rapport R30 doit conserver l'état `OPEN_NOT_PROVEN` pour les 12 constats et `CRITICAL=2`.

### Audit de portée

- C original et candidats C R26/R29, C11 R28 : **inchangés**.
- Nouveau binaire de production, appel AudioQueue actif, sortie physique, mesure instrumentale : **AUCUN**.
- R30 : **audit C11/OS et documentation seulement**, le candidat C R29 demeure isolé.
- En cas de `FAIL` dans la suite Mac Intel : `MAC_INTEL=BLOCK` et aucun rapport de certification.
- Après PASS logiciel : seulement `GEN_R30_MAC_INTEL_SOFTWARE=PASS` ; `BUREAU_CERTIFICATION=PENDING`, `REAL_OUTPUT=NOT_AUTHORIZED`.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
