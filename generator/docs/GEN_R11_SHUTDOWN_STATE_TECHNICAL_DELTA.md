# GEN-R11 — Acoustic Shutdown State Integrity (source-only, no output)

## Engineering delta after GEN-R10
- `FMInternalAcousticFault` records a bounded in-memory classification for invalid PCM buffers, enqueue failure, graceful-stop failure, property listener failure, monotonic clock failure, route drift and shutdown fault.
- `fm_latch_first_fault` uses a C11 atomic compare-and-exchange to retain the **first** reason. It also sets the existing `failed` flag; a later error cannot erase it.
- `shutdown_in_progress` is initialized to zero, then closed using a one-shot `atomic_exchange` before the stop gate, listener removal and synchronous queue disposal.
- The output callback, controller's graceful-drain request and property listener check the shutdown barrier. The listener cannot report a normal stop after a latched fault.
- The final return checks the first-fault latch. There is no automatic restart and no new `arm`, `play`, `emit` or `transmit` CLI command.
- The R9 listener-removal order and `AudioQueueDispose(queue,true)` remain in place. R10 monotonic OS watchdog and invalid-buffer rejection are retained.

## Evidence limits / known risks
All new evidence is from source-level C11 atomic contracts and an actual **no-output** native executable. A clean source review or `AudioQueueDispose(true)` does not establish absence of every callback race, a bounded *hardware* cutoff, acoustic output, independent measurements, or performance under real output load.
`acoustic_macos.c` is compiled to an isolated object but **never linked** into the runnable R11 executable. No physical sound, RF, EM field, synthetic instrument or numerical/physical simulation is performed.

## Documented macOS APIs
- https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose(_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener(_:_:_:_:)
- https://developer.apple.com/documentation/audiotoolbox/audioqueuestop(_:_:)

`NEVER_SIMULATION=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
