# FREQMED GEN-R42 — Bureau indépendant B07/B09/B10

**Verdict documentaire maximal : `CLOSED_COUNT_ATOMIC_RESERVATION_REVIEWED_OWNER_OS_AND_CAPACITY_PROOFS_OPEN`.** Ni certification C11 globale, ni certification Apple CoreAudio, ni certification instrumentale.

### B07 — OS, callbacks et chemins d'échec

**IX42_01 CRITICAL :** C31 transmet encore le propriétaire `ctx` directement à la file de sortie et au listener. C42 n'est pas intégré, n'est pas un wrapper ABI de callback Apple. **IX42_06 CRITICAL :** les situations d'échec de `AudioQueueStop` ou `Dispose` et la coupure physique ne sont pas démontrées. Une fermeture de porte C11 locale ne prouve aucune quiescence OS ni arrêt d'un signal physique.

### B09 — forgery, atomicité et capacité

**IX42_02, 03, 04 et 05 CRITICAL.** Le propriétaire et ses alias externes peuvent encore être libérés hors du contrat. Le pointeur opaque élimine l'indice entier public de R41, mais n'authentifie pas l'adresse : duplication, fuite ou usage prématuré d'un pointeur valide restent possibles. Le mot atomique CLOSED/count donne un ordre de modification partagé pour les **nouvelles réservations** et la fermeture ; cependant, les réservations déjà acceptées peuvent publier après une fermeture survenue après leur dernier contrôle. **Il n'existe aucune preuve d'arrêt atomique de tous les callbacks réels.**

Les quatre slots à durée de vie du processus sont saturables et non réutilisables. Une saturation crée un refus permanent, **pas une solution de capacité de production**. Les annulations qui compensent l'admission par `fm36_leave` peuvent elles-mêmes échouer. Le ticket CAS terminal empêche la double sortie d'un même slot valide, **pas l'oubli de la sortie**. L'authenticité de tout pointeur, le happens-before global du contexte C31, l'achèvement OS et la durée de vie des alias restent ouverts.

### B10 — sûreté physique

Les tests `clang`, `nm`, empreintes SHA-256, mutations textuelles et audits source ne peuvent attester la coupure physique. **Aucun instrument ou générateur n'est activé**, aucun essai humain ou biologique, aucune signature indépendante délivrée.

| Groupe | Constatations encore ouvertes |
|---|---|
| GEN-R42 | **20 OPEN, 6 CRITICAL** |
| GEN-R41 | 19 OPEN, 5 CRITICAL |
| GEN-R40 | 18 OPEN, 5 CRITICAL |
| GEN-R39 | 16 OPEN, 4 CRITICAL |
| GEN-R38 | 18 OPEN, 5 CRITICAL |
| GEN-R37 | 14 OPEN, 4 CRITICAL |
| GEN-R36 / R35 / R34 | 12 / 12 / 14 |
| R33 / R32 / R31 / R30 | 12 / 10 / 8 / 12 |
| R29 / R28 / R27 | 7 / 5 / 9 |
| R23 / R24 | 15 / 7 |
| Bureau historique | **11 OPEN, 0 résolue** |
| Intégration C42 aux callbacks | NON |
| Ticket réellement authentifié | NON |
| Ferme les entrées OS après fermeture | NON PROUVÉ |
| Liberté des races C11 globale | NOT_PROVEN |
| Arrêt / coupure physique | NOT_PROVEN |

Les registres historiques se recoupent ; ne pas additionner leurs totaux comme s'il s'agissait de vulnérabilités indépendantes.

**Cibles propriétaire Mac Intel PENDING : 837 Python, 33 C natives, 244 sources SHA-256, 46 rapports SHA-256.** PR #1 DRAFT, non fusionnée. Aucun droit de production ou d'émission autorisé.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
