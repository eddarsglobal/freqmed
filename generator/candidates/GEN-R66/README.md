# GEN-R66 — C11 sequence audit, digital command only

**Source preview for RoadMap/Bureau review**. This draft branch is stacked on the GEN-R65 candidate commit `e497ccaccd35bb9b316f0061670b641a70ca3a65`.

## Engineering scope
- Add the **read-only native audit** `acoustic_sequence_audit_r66.c/.h` to check every ephemeral R65 float32 PCM command chunk independently of the R65 chunk generator: contiguous frames; exact samples/channel count; bounded and finite numeric values; matching stereo channels; true first/last zero frames; zero unused tail; consistent reported digital peaks; completed stream; sticky fail-closed.
- Fix R65 digital envelope zero edges for **sub-frame ramps**, as discovered by a regression case for 1 ms at 8 kHz.
- The **complete local GEN-R66 kit** also contains the Python ctypes/route-lease integration, 10-language R65 button result with native R66 status, 42 new tests, 734 total automated tests, docs, SHA256 manifest and Mac Intel runner.

## Proof and limits
The **complete ZIP** was tested on Linux after fresh extraction: `734/734` tests PASS, 0 skipped in 21 isolated modules; SHA256 `85/85` PASS; C/FFI selftest PASS; JavaScript/Bash syntax PASS. This GitHub PR initially contains **source preview C files only**. The complete kit must be synchronized from the owner's Mac via `SYNC_R66_GITHUB_MAC_INTEL.command` before it can be described as remotely buildable or review-complete. Mac Intel GEN-R66 CoreAudio/Safari verification is **PENDING**. No playback or output driver. Numeric tests do not constitute acoustic measurements.

## Bureau/RoadMap
R66 is an exceptional preparatory **source-only P1.01/P1.02 candidate** under RoadMap clause E. `P0.01=IN_PROGRESS_REBASE_REVIEW`; `P0.02=PENDING`; `P1.01/P1.02=PENDING`; `REAL_OUTPUT=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`; `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`; `NEVER_SIMULATION=ENFORCED`. B07/B08/B09/B10 scopes are not independent signatures; B04 metrology NOT_EVALUATED. No merge to main, no self-certification.
