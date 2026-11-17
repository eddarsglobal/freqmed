# FREQMED GEN-R34 — Pre-admission, Callback Lifetime & OS Proof Witness Matrix

**Le présent document est un inventaire de preuves manquantes, non une simulation ou un certificat.** Le moteur C d'émission ne doit pas être lié.

| Phase | Témoin source qui existe | Témoin OS/C11 absent | Décision prudente |
|---|---|---|---|
| BEFORE_PUBLISH | `calloc`, initialisation, deux `free(owner_ctx)` avant publication | Couverture exhaustive de tous les alias et chemins d'échec | Uniquement ces sorties locales clairement observées |
| NEWOUTPUT_PUBLICATION | `AudioQueueNewOutput(...,ctx,...)` | Contrat de durée de vie userdata après constructeur échoué | Garder contexte sur erreur |
| CALLBACK_ENTER_PRE_ADMISSION | `ptr/data` convertis, accès à `ctx->queue_admission` | Preuve que l'OS ne peut plus invoquer un nouveau callback avec userdata après libération | Ne pas libérer après publication |
| ADMITTED_CALLBACK | `try_enter`, puis compteur actif | Appariement de toutes les sorties, preuve HB interthreads | Aucun acquittement C11 |
| REJECTED_CALLBACK | `try_enter` refuse après fermeture | Durée de vie de `ctx` nécessaire pour lire le gate | Le rejet ne rend pas un free sûr |
| SHUTDOWN_CLOSE | `fm_r28_gate_close`, `closed_and_empty` | Contrat d'arrêt des entrées OS | Une file C11 vide n'est pas une file OS quiescente |
| STOP_ERROR | `AudioQueueStop(...,true)!=noErr`, quarantaine | État du matériel, buffers, callbacks et file OS après échec | Aucune émission autorisée |
| LISTENER_REMOVE_ERROR | flag `listener_remove_failed` | Fin de listener déjà déclenché ou retardé | Garder `userdata` |
| DISPOSE_ERROR | défaut `FM_FAULT_DISPOSAL` | Validité de `AudioQueueRef`, ressources et garantie sur callbacks | Ne pas libérer ou réessayer automatiquement |
| DISPOSE_SUCCESS | `dispose_confirmed`, `ctx->queue=NULL` | Distinction postcondition OS de succès vs already-entered callbacks et preuve C11 | Ne pas déduire un `free` automatique |
| PROCESS_QUARANTINE | refus de session et heap conservé | Preuve de coupure physique et d'absence de callbacks tardifs | Ne pas produire ni déclarer safe-to-exit |

## Interprétation exacte des textes Apple

- `AudioQueueDispose(..., true)` décrit une disposition synchrone. Apple indique qu'après la disposition la file ne produit plus de callbacks. Ce comportement documenté sur succès n'implique aucune postcondition garantissant la fin de callback sur un statut d'échec.
- `AudioQueueStop(..., true)` arrête la file synchronement ; l'audio hardware associé peut rester sollicité par d'autres services audio.
- `AudioQueueRemovePropertyListener` retire le listener correspondant à ses arguments, mais un code d'échec ne garantit aucun résultat de suppression.

Sources officielles :
https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

**Niveaux de preuve distincts :** code source SHA-256 observé, objet C compilé non lié, contrat OS vérifié, preuve C11 formelle, mesure physique instrumentale, validation indépendante et signature Bureau. Seuls les deux premiers niveaux ont des témoins logiciels dans cette phase.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
