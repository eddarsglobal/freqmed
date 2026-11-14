# GEN-R10 — Acoustic Failure Recovery & Shutdown Integrity (source candidate)

## Correctifs
1. Rejet avant écriture d'un tampon CoreAudio nul, mémoire nulle, de capacité inférieure à 16 bits, ou de taille non alignée avec les échantillons PCM.
2. Un échec d'`AudioQueueEnqueueBuffer` n'est jamais interprété comme la mise en file réussie de la dernière trame; verrou `failed`.
3. Le listener `kAudioQueueProperty_IsRunning` ne confirme l'arrêt normal qu'après début et demande de vidange, sans défaut ni arrêt forcé.
4. Watchdog sur **horloge réelle monotone du système** `CLOCK_MONOTONIC`, surveillant aussi les erreurs d'horloge, retournement de l'horloge, borne avant/après attente. Garde secondaire par nombre d'itérations inchangé.
5. R9 non régressé : callback sans appel d'arrêt; seule la boucle de contrôle demande la vidange; suppression du listener avant `AudioQueueDispose(..., true)`; erreurs de nettoyage remontées.
6. Aucun mécanisme de tentative de réactivation après défaut ou timeout.

## Limites
Le backend de sortie est compilé séparément et ne figure dans **aucun exécutable utilisable**. Ces gardes sont vérifiés par lecture du code et tests du binaire sans émission, **pas** par simulation physique, dispositif virtuel, fréquence produite ni observation de callbacks d'une sortie active. La borne logicielle ne qualifie pas la latence d'un arrêt matériel ou d'un interverrouillage. Aucun instrument EM qualifié.

## API Apple
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener(_:_:_:_:)

`NEVER_SIMULATION=ENFORCED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
