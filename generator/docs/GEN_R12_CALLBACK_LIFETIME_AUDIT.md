# FREQMED GEN-R12 — Callback Lifetime & Shutdown Race Audit

## Candidat technique : CoreAudio source seulement

GEN-R11 FIX1 est attesté sur le Mac Intel du propriétaire : 215/215 tests Python PASS, 33/33 assertions C PASS, five isolated native objects compiled unlinked. Aucun output acoustique/EM.

R12 ajoute aux sources `acoustic_macos.c` :
1. Deux compteurs atomiques `active_output_callbacks` et `active_property_listeners` pour les entrées/sorties des callbacks; la sortie du listener passe par un point de sortie commun, y compris en cas de propriété inattendue ou d'échec de lecture.
2. Une barrière `pcm_writer_gate` (`atomic_flag`) : deux callbacks qui tenteraient de modifier simultanément la phase, le compteur de trames ou les buffers PCM sont traités comme un défaut `FM_FAULT_OVERLAPPING_PCM_CALLBACK`, sans attendre activement ni réessayer.
3. Un indicateur atomique `dispose_confirmed` défini seulement après `AudioQueueDispose(queue,true)` réussi; les échecs déclenchent `FM_FAULT_DISPOSAL`.
4. Après la libération synchrone demandée à CoreAudio, inspection des compteurs d'activité; un callback/listener encore actif enregistre une cause d'échec et interdit de renvoyer un succès.
5. La première cause d'échec R11, la barrière de fermeture, les gardes de buffers R10, le watchdog OS monotone, le stop R9 géré par la boucle de contrôle, les refus d'API publique et le contrôle des symboles du binaire sont conservés.

## Ce que cela ne prouve PAS

Le compteur n'est pas une preuve complète de synchronisation ou de durée de vie. Il repose sur les garanties de l'API CoreAudio pour la fin de vie de sa file. Un callback très tardif, une erreur de disposal, des problèmes d'ordonnancement ou de visibilité mémoire, et l'interaction de la pile locale avec des callbacks encore actifs restent des risques à auditer indépendamment **avant** toute connexion physique. Un code qui retourne une erreur sur une libération ratée ne garantit pas automatiquement l'absence d'accès mémoire après retour. Ni les tests statiques, ni un résultat `nm PASS` ne peuvent le démontrer.

Ces compteurs portent sur un contrat de source **non lié / non exécuté** dans le binaire livrable. Aucune simulation d'instrument, sortie son, transmission EM, mesure acoustique ou essai biologique.

Références officielles : 
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener(_:_:_:_:)

`NEVER_SIMULATION=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
