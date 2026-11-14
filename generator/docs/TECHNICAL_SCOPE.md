# GEN-R2 technical boundary

CoreAudio default-output **metadata** only; no `AudioQueueStart` reachable or linked into the executable. Actual AudioQueue output implementation is source-only (`src/acoustic_macos.c`). The EM backend never opens any transport. R1 Mac Intel 13/13 PASS is based on user-provided terminal log; R2 Mac Intel not yet witnessed. Output devices are not certified transducers; no physical emission proven.
