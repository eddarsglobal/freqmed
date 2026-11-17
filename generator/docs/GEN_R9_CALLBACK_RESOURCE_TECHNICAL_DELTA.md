# GEN-R9 — Acoustic callback ownership and queue resource lifecycle

## Engineering change (source-only)

1. AudioQueue output callback does not request stop or drain; it only performs buffered PCM bookkeeping and updates atomic failure/completion flags.
2. The control loop requests `AudioQueueStop(..., false)` only after successful queue start and final frame enqueue. A single atomic compare/exchange still prevents duplicate drain.
3. Listener registration is tracked explicitly. Cleanup first sets `stop_requested`; on a started queue it requests immediate stop only upon fault; it removes `kAudioQueueProperty_IsRunning` listener before invoking synchronous `AudioQueueDispose(..., true)`.
4. Both listener removal and synchronous disposal errors return a failure code. No new CLI output action is permitted.
5. The executable retains `output_hard_denied.c`, no acoustic backend linked, and no EM command path.

## Evidence limitations

R9 adds **20 code-contract and native executable-denial checks**, not a simulation of physical effects or instruments. Source inspection does not prove callback scheduling, real audio latency, freedom from race conditions on a Mac under load, or a verified hardware cutoff. GEN-R9 requires compilation and regression verification on the owner Mac Intel. No sound or EM field has been generated.

Apple references:
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener(_:_:_:_:)

`NEVER_SIMULATION=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`
