# FREQMED GEN-R35 — Apple CoreAudio OS Contract Evidence Matrix

**Revues des pages publiques Apple : 16 novembre 2026.** Ne pas transformer une page publique vivante en certificat immuable d'un chemin d'erreur. Aucun callback, instrument, ou test CoreAudio n'a été exécuté.

| API / contrat | Évidence publique consultée | Évidence que la documentation ne fournit pas dans ce périmètre |
|---|---|---|
| `AudioQueueStop(..., true)` | Demande arrêt immédiat synchrone | Coupure physique après statut non nul |
| `AudioQueueStop(..., false)` | Fonctionnement asynchrone et callbacks jusqu'à arrêt effectif | Exclusion de callback OS tardif sur appel échoué |
| `AudioQueueStop` / matériel | Arrête le matériel associé s'il n'est pas utilisé par d'autres services | Silence matériel de tous appareils et autres services |
| `AudioQueueDispose(..., true)` | Disposition synchrone, ressources/buffers libérés | Postcondition équivalente après échec |
| `AudioQueueDispose` / callback | La queue n'invoque plus de callbacks après disposition | Preuve C11 de durée de vie sur toute entrée déjà commencée |
| `AudioQueuePropertyListenerProc` | `inUserData` provient de l'enregistrement | Validité de la mémoire après tous échecs de suppression |
| `AudioQueueRemovePropertyListener` | Sélection par queue, propriété, fonction et `userdata` identiques | Quiescence de tous les callbacks déjà entrés sur `OSStatus != noErr` |
| Callback pré-`try_enter` | Aucune garantie complète démontrée dans les pages ci-dessus | Obligation propriétaire de vie du `ctx` avant déréférence du gate |
| C11 `happens-before` | Non déduit des seules pages API Apple | Preuve interthreads de la synchronisation C11 et des références partagées |

Sources directes :
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29
- https://developer.apple.com/documentation/audiotoolbox/audioqueuepropertylistenerproc
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

**Classes du dossier** : `DOCUMENTED_REQUEST_SUCCESS_PATH` ; `DOCUMENTED_CONDITIONAL` ; `DOCUMENTED_POST_DISPOSAL_ONLY` ; `DOCUMENTED_ARGUMENT_CONTRACT` ; `DOCUMENTED_API_PARAMETERS` ; `NOT_ESTABLISHED_BY_PAGES`.

### Exigences de preuve encore manquantes

`PA35_01` et `PA35_02` : lifetime OS pré-admission. `PA35_03` : dispose échouée. `PA35_04` : stop échoué/coupure physique. Les huit autres constats, ainsi que les 14 R34 et 11 portes du Bureau, restent ouverts.

**Aucune qualification médicale ni biologique.** Les constats source sont ancrés par empreintes SHA-256, mais les textes publics Apple ne sont pas capturés sous une licence d'archive ni épinglés de manière immuable. Les éléments non documentés sont notés comme **non prouvés**, non comme impossibles.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
