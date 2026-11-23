# GEN-R65 — Segmented digital PCM preparation (source preview)

Stacked on full GEN-R64 candidate commit `d9911daba62fa75aa9f05a1ef295a32a373fd7bf`. This branch is **source preview only** until the Mac runner pushes the complete R65 source kit and tests.

New C11 module computes bounded numeric PCM command frames in ephemeral **256-frame** chunks, checks exact session consistency and scrubs cursor data. This source does not transmit waveform buffers, use AudioQueue, produce sound, perform acoustic measurements or simulate physical devices.

Linux validation of the **complete conversation ZIP**, not yet this partial GitHub tree: `692/692` automated tests passed (642 inherited + 50 R65). Fresh extraction and 81/81 SHA256 manifest passed. Mac Intel CoreAudio/UID and Safari R65 execution: PENDING.

P0.01 IN_PROGRESS_REBASE_REVIEW, P0.02 PENDING, P1.01/P1.02 PENDING. REAL_OUTPUT NOT_AUTHORIZED; PRODUCTION NOT_AUTHORIZED; BIOLOGICAL_EXPOSURE NOT_AUTHORIZED. B07/B08/B09/B10 technical review functions; B04 physical metrology NOT_EVALUATED. No independent certification is claimed; **DO NOT MERGE**.
