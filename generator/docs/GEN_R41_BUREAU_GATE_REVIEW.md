# FREQMED GEN-R41 — Bureau indépendant B07/B09/B10

**Verdict documentaire : `INDEX_TICKET_FAULT_CONTAINMENT_REVIEWABLE_OS_OWNER_COMPLETION_NOT_PROVEN`**. Ce dossier n'émet ni signature de certification C11, ni attestation Apple, ni mesure physique.

### B07 — durée de vie des callbacks et erreurs OS

**IX41_01 et IX41_04 : CRITICAL / OPEN_NOT_PROVEN.** Le C31 réel remet toujours `ctx` directement à CoreAudio. Les chemins de sortie C41 ne sont pas des callbacks Apple. Un masque de défauts ne stoppe pas un émetteur, ne supprime pas un listener et ne prouve pas la quiescence après `AudioQueueStop` ou `Dispose` échoués.

### B09 — capacité, alias et erreur persistante

**IX41_02 et IX41_03 : CRITICAL / OPEN_NOT_PROVEN.** Le propriétaire `owner` demeure sous contrat de durée de vie **externe**, jamais contraint par le module. Une sortie par CAS n'est **au plus qu'une fois par slot** ; aucun appel de sortie n'est garanti par le code C41. Le ticket par indice est copiable et falsifiable, et peut être utilisé prématurément si le slot est ACTIVE : **aucun contrôle de provenance cryptographique ni de propriété de l'indice**. Les quatre slots consommables à vie bloquent un callback flux non borné ; toute admission rejetée réduit encore cette capacité. Le double contrôle du masque d'erreur ne prouve pas l'atomicité de la fermeture face aux entrées concurrentes.

Les erreurs de compensation `fm36_leave` sont enregistrées mais ne réparent ni compteurs ni OS. L'alias `owner_out`, les champs de `ctx` non atomiques et les états d'échec OS exigent des preuves indépendantes.

### B10 — arrêt physique

**IX41_05 : CRITICAL / OPEN_NOT_PROVEN.** Compilation C11, tests de mutation textuelle, `nm` et 44 SHA-256 démontrent des propriétés du logiciel testé, **pas** l'absence de sortie mesurée par des instruments, ni l'arrêt physique d'un appareil. Aucun essai humain ou biologique.

| Ensemble | Obligations |
|---|---|
| GEN-R41 | **19 OPEN, dont 5 CRITICAL** |
| GEN-R40 | 18 OPEN, 5 CRITICAL |
| GEN-R39 | 16 OPEN, 4 CRITICAL |
| GEN-R38 | 18 OPEN, 5 CRITICAL |
| GEN-R37 | 14 OPEN, 4 CRITICAL |
| GEN-R36 / R35 / R34 | 12 / 12 / 14 OPEN |
| GEN-R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 OPEN |
| GEN-R29 / R28 / R27 | 7 / 5 / 9 OPEN |
| R23 / R24 | 15 / 7 OPEN |
| Bureau historique | **11 OPEN, 0 résolue** |
| C41 connecté au C31 | NON |
| C11 race freedom globale | NOT_PROVEN |
| Exécution CoreAudio | NONE |
| Arrêt physique | NOT_PROVEN |

**Objectifs propriétaire Mac Intel PENDING : 817 Python, 33 assertions natives C, 236 sources SHA-256, 44 rapports SHA-256.** PR #1 DRAFT, non fusionnée. Aucun acte d'intégration ou d'émission autorisé.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
