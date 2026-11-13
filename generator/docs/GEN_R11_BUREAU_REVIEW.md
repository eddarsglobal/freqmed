# GEN-R11 — Bureau Engineering Review Request (NON CERTIFIED)

- **B09 — Architecture / security:** review atomic first-fault latching, memory ordering and races, shutdown barrier, listener and callback lifetime, CoreAudio error paths, and linkage audit. Source-unit tests are not dynamic proof of concurrency safety.
- **B07 — DSP:** review distinction between sample enqueue, CoreAudio running state, stopping and real output, and verify no automatic restart after failures.
- **B04 — Acoustics/metrology:** no sound-pressure data, transducer, calibrated acoustic sensor or independently observed cutoff. No physical output authorized.
- **B05 / B06 — EM / instrumentation:** inspect documentary screening code, the absence of a real qualified generator and the absence of any IO/driver for EM output. Evidence hash is not a certificate.
- **B10 — Safety / ethics:** written non-biological bench authorization, independent hardware interlock, medical/regulatory scope and exposure controls remain unresolved.
- **RoadMapGuardian:** P0.01 is IN_PROGRESS. These are preparatory source candidates and **not** certified P1/P2 work. PR #1 stays DRAFT, `main` unmodified; no gate or emission unlock.

Owner Mac Intel GEN-R10 witness: **195/195 Python and 33/33 native C assertions PASS**, output hard-denied. GEN-R11 native Mac Intel evidence remains **PENDING**, target 215 software tests + 33 prior native C assertions.

`NEVER_SIMULATION=ENFORCED` · `REAL_OUTPUT=NOT_AUTHORIZED` · `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED` · `PRODUCTION=NOT_AUTHORIZED`.
