# FREQMED GEN-R33 — Ownership, quiescence and safe-abandonment proof matrix

**Documentary contract, NOT a runtime executable, NOT a scientific simulation and NOT a proof of physical stop.**

| State | C heap ownership | AudioQueueRef status | Callback admission | Provisional source policy |
|---|---|---|---|---|
| PRE_PUBLISH_INVALID_FRAMES | Local, freed in C | Not published | No OS callback registered | PREPUBLICATION_RELEASE_SOURCE_PATH |
| PRE_PUBLISH_INVALID_FADE | Local, freed in C | Not published | No OS callback registered | PREPUBLICATION_RELEASE_SOURCE_PATH |
| NEW_OUTPUT_ERROR | Uncertain published userdata | OS creation failure unknown | Late entry not excluded | RETAIN_HEAP_NO_RETRY |
| ROUTE_REJECT_DISPOSE_SUCCESS | Published/retained | Disposal claims success | Late entry not excluded by C11 alone | RETAIN_USERDATA_NO_RETRY |
| ROUTE_REJECT_DISPOSE_FAILURE | Published/retained | OS ref ambiguous | Unknown | RETAIN_HEAP_AND_QUEUE_HANDLE_NO_RETRY |
| STOP_FAILURE | Published/retained | Potentially active | Unknown | RETAIN_HEAP_QUEUE_NO_RETRY |
| STOP_SUCCESS_BUSY_LEASE | Published/retained | Stop may have succeeded | Accepted leases still active | RETAIN_HEAP_QUEUE_NO_DISPOSE |
| LISTENER_REMOVE_FAILURE | Published/retained | Unknown | Listener may still dispatch | RETAIN_USERDATA_NEEDS_OS_PROOF |
| FINAL_DISPOSE_FAILURE | Published/retained | Unknown / no guaranteed valid handle | Unknown | RETAIN_HEAP_QUEUE_NO_RETRY |
| FINAL_DISPOSE_SUCCESS | Published/retained | Reported disposed | Late callbacks require independent exclusion | RETAIN_HEAP_PENDING_CALLBACK_PROOF |

### Proof classes

- `CODE_PATH_EXISTS`: confirmed only by lexical source scan of SHA-pinned C31.
- `C_HEAP_RELEASE_CONFIRMED`: strictly limited to observed prepublication `free(owner_ctx)` call sites; **not** generalized to every possible failure.
- `OS_QUEUE_OWNERSHIP`: **UNPROVEN** after failed constructor, stop, listener remove or disposal.
- `OS_CALLBACK_QUIESCENCE`: **NOT_PROVEN** for all published userdata cases.
- `C11_RACE_FREEDOM`: **NOT_PROVEN**; close-and-empty cannot substitute for documented OS lifetime guarantees.
- `PHYSICAL_OUTPUT_CUTOFF`: **NOT_PROVEN**, especially after nonzero `OSStatus` from `AudioQueueStop`.
- `CERTIFICATION`: **PENDING** with all 11 historic Bureau gates OPEN.

### Explicit prohibitions

Never transform **retain/abandon ownership** into a claim of **safe-to-exit, safe-to-free, hardware stop** or **safe-to-retry**. Never use a code-only report as permission to link or execute a CoreAudio emitter. Actual output, medical exposure, scientific simulation and instrumentation remain outside scope.

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `ACOUSTIC_OUTPUT=LOCKED`; `EM_OUTPUT=LOCKED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
