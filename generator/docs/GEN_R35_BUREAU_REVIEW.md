# FREQMED GEN-R35 — Bureau B07/B09/B10 Pre-Admission & OS Contract Review

**Verdict maximal de revue : `PUBLIC_OS_CONTRACTS_CLASSIFIED_PRE_ADMISSION_LIFETIME_NOT_PROVEN`.**

## B07 — durée de vie OS `userdata`

**PA35_01 et PA35_02 CRITICAL / OPEN_NOT_PROVEN.** Avant le premier appel `fm_r28_gate_try_enter`, les callbacks de sortie et de listener manipulent un `ctx` fourni par CoreAudio et accèdent à `ctx->queue_admission`. La validité du pointeur doit être garantie **avant** la première admission ; un compteur C11 à zéro ne suffit pas. Aucun use-after-free n'a été provoqué ni constaté.

**PA35_03 CRITICAL / OPEN_NOT_PROVEN.** Une disposition synchronisée avec statut de succès est documentée par Apple, mais aucune garantie de cette même postcondition ne peut être inférée après `OSStatus != noErr`. Les rapports doivent distinguer le contrat OS réussi de la preuve de C11 *happens-before* encore manquante.

## B10 — arrêt physique

**PA35_04 CRITICAL / OPEN_NOT_PROVEN.** Un échec `AudioQueueStop(queue,true)` n'atteste pas la coupure acoustique. La quarantaine et la rétention de la mémoire ne remplacent pas une mesure instrumentale ni un dispositif de sécurité indépendant ; aucune émission n'est autorisée.

## B09 — compteurs, C11 et file

Les huit autres obligations R35 restent HIGH/OPEN : compteurs post-admission, fermeture du gate non équivalente à annulation OS, erreurs de constructeur et de listener, ordre de `ctx->queue`, preuves séparées des dispositions et bornes de conservation des ressources.

| Dossier | Portes ouvertes |
|---|---|
| GEN-R35 | **12, dont 4 CRITICAL** |
| GEN-R34 | **14, dont 4 CRITICAL** |
| GEN-R33 | 12, dont 3 CRITICAL |
| GEN-R32 | 10, dont 2 CRITICAL |
| GEN-R31 | 8, dont 2 CRITICAL |
| GEN-R30 | 12, dont 2 CRITICAL |
| R29 / R28 / R27 | 7 / 5 / 9 |
| R23 / R24 | 15 / 7 |
| Bureau historique | **11 OPEN / 0 résolue** |

Le portail du Bureau ne peut pas être ouvert par une documentation Apple, une régression lexicale ou une compilation sans liaison. L'audit R35 ne produit **aucune signature indépendante**.

**Validation Mac Intel à obtenir, sans anticiper les résultats : 697 tests Python, 33 assertions C natives, 193 fichiers SHA-256 et 32 rapports SHA-256.**

`GEN_R35_MAC_INTEL=PENDING`; `USERDATA_PRE_ADMISSION_LIFETIME=NOT_PROVEN`; `COREAUDIO_CALLBACK_QUIESCENCE=NOT_PROVEN`; `C11_RACE_FREEDOM=NOT_PROVEN`; `PHYSICAL_CUTOFF=NOT_PROVEN`; `BUREAU_CERTIFICATION=PENDING`.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`. PR #1 **DRAFT, non fusionnée**.
