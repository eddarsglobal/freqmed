# GEN-R8 — Cycle de vie AudioQueue : corrections et limites

## Défaut antérieur

Dans R5–R7, `last_frame_enqueued` était observé par la boucle principale ; après mise en file du dernier échantillon, l’exécutable source utilisait `AudioQueueStop(ctx.queue,true)` et interrompait potentiellement les tampons encore en lecture. Le simple fait d'enfiler le dernier tampon n'est pas une confirmation d'audition/lecture du signal.

## Correctif candidat

- `queue_started`, `graceful_drain_requested` et `queue_stopped` sont des atomiques, distincts de `last_frame_enqueued`.
- Après la dernière mise en file, une seule demande `AudioQueueStop(...,false)` est lancée pour vidanger normalement ; elle ne se déclenche jamais avant le démarrage.
- Pour un signal court entièrement mis en file avant démarrage, une demande de vidange est faite après la réussite d'`AudioQueueStart`.
- `AudioQueueAddPropertyListener(kAudioQueueProperty_IsRunning)` observe le passage à l'arrêt ; un état OFF logiciel n'est pas déduit du nombre d'échantillons écrits.
- En cas de dérive de route, d'erreur CoreAudio ou de dépassement watchdog : arrêt immédiat logiciel et disposition de la file.
- Le binaire contrôlable reste construit uniquement avec `output_hard_denied.c`, sans backend `acoustic_macos.c` lié, ni ouverture de matériel EM.

## API Apple documentées

- `AudioQueueStop(queue, false)` laisse les tampons en file terminer ; `true` interrompt immédiatement : https://developer.apple.com/documentation/audiotoolbox/audioqueuestop(_:_:)
- `kAudioQueueProperty_IsRunning` reflète l'état courant de la file et émet une notification sur les transitions : https://developer.apple.com/documentation/audiotoolbox/kaudioqueueproperty_isrunning
- `AudioQueueAddPropertyListener` installe la notification : https://developer.apple.com/documentation/audiotoolbox/audioqueueaddpropertylistener(_:_:_:_:)

## Limitations

Ce code n'a pas été exécuté avec une sortie audio physique. L'API OS peut signaler une file arrêtée sans garantir un niveau de pression sonore, une puissance physique ou l'exactitude d'une fréquence acoustique. Le matériel de diffusion, l'interface, la coupure indépendante et le protocole d'essai restent absents.

Aucune simulation ou mesure scientifique n'a été exécutée ni inventée.
