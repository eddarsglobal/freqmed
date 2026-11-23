# GEN-R64 — PCM integrity and native-state consistency

**Source-only preview for RoadMap/Bureau review.** Parent branch: candidate/gen-r63-digital-pcm-20261123 (commit 8914f47a72672c08cf9c0cd42da41c07a9f64264).

The two C files are identical to the local complete R64 kit; they are NOT a stand-alone build. The complete Python/FFI integration, fixed state transitions, 10-language UI, 642 automated tests and Mac runner are pending synchronization from the owner's Mac.

R64 verifies bounded finite digital PCM data, mono/stereo, normalized digital peak <=0.01, and zero first/last frames. Digital values are NOT measured acoustic output or safety limits. No output API, AudioQueue, RF, SPL, medical use, or physical emission.

Main remains unchanged. `P0.01=IN_PROGRESS_REBASE_REVIEW`, `P0.02=PENDING`, `REAL_OUTPUT=NOT_AUTHORIZED`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`, `PRODUCTION=NOT_AUTHORIZED`. Bureau functional review labels are not signatures. **DO NOT MERGE** this draft candidate.
