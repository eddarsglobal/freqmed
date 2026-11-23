# FREQMED GEN-R63 — Source candidate, no physical output

This branch stages the GEN-R63 digital PCM module for review. It is source-only: the full R59-R62 dependencies, application, Mac runner and regression tests must be brought into this branch before any integration.

Parent of complete conversation kit: GEN-R62-FIX2 v0.7.4. Developer Linux regression: 582/582 PASS. Apple CoreAudio on Mac Intel and Safari are not yet attested for GEN-R63. The C module has no CoreAudio playback or output entrypoint. It computes transient, bounded digital samples only.

RoadMap: P0.01 IN_PROGRESS_REBASE_REVIEW; P0.02 PENDING; REAL_OUTPUT NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE NOT_AUTHORIZED; PRODUCTION NOT_AUTHORIZED; NEVER_SIMULATION ENFORCED. Digital command frames are not experimental acoustic measurements or sound emissions.

Do not merge to main. This branch is not an independently buildable generator. It needs the complete local candidate source kit before qualification.
