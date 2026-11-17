# FREQMED GEN-R30 — OS/C11 proof-obligation matrix (never certified)

**Type:** source-anchored review requirements, not actual CoreAudio experiments. All rows are OPEN_NOT_PROVEN. No synthetic interleavings or scientific simulations.

| ID | Risk | Mechanism to prove | Independent evidence required |
|---|---|---|---|
| Q30_01 | userdata before admission | OS pointer lifetime precedes any gate atomic load | Apple API/callback lifetime contract, with signed proof |
| Q30_02 | **CRITICAL** live queue early exit | closed-but-busy branch returns after Start without Stop/Dispose | bounded fail-closed cleanup redesign, formal path review |
| Q30_03 | stop without lease | controller invokes Stop while callbacks may use queue | explicit synchronized ownership model |
| Q30_04 | prefill coverage | controller allocate/prefill/use queue without callback lease | complete queue/buffer access matrix |
| Q30_05 | enqueue under PCM gate | reentrant callbacks and lock duration | documented scheduling contract and bounded verified path |
| Q30_06 | late OS callbacks | closed-and-empty does not prevent entry to userdata | OS cancellation/quiescence evidence |
| Q30_07 | non-atomic queue clear | controller nulls queue after dispose | C11 HB plus OS disposal postconditions |
| Q30_08 | listener remove failure | disposal follows a failed removal | OSStatus-specific ownership and callback termination |
| Q30_09 | dispose failure | retained queue ref may be stale, live or ambiguous | OSStatus failure ownership and safe shutdown evidence |
| Q30_10 | queue creation failure | partially created queue may have captured userdata | API failure lifecycle proof |
| Q30_11 | atomic admission protocol | try_enter/leave pairing and lock-free progress | C11 release sequence proof + platform atomic guarantees |
| Q30_12 | **CRITICAL** quarantine vs cutoff | software refusal is not a physical stop | safe hardware/OS shutdown design, no activation in this phase |

### Evidence class distinctions

1. **SOURCE_OBSERVATION:** a visible ordering or branch in SHA-pinned C.
2. **COMPILATION_CHECK:** only proves C syntax/types/target codegen under test build.
3. **RUNTIME_OS_PROOF:** absent; no CoreAudio callback was started.
4. **PHYSICAL_MEASUREMENT:** absent; no qualified acoustic or EM instrument and no authorized emission.
5. **FORMAL_C11_PROOF:** absent; atomic operations are not themselves a proof of race freedom.

A source-only audit can return `PASS` for accurately documenting these deficiencies while all twelve safety proofs remain open. Even a successful Mac Intel test run must **not** change these proof statuses.

References: https://developer.apple.com/documentation/audiotoolbox/audioqueuedispose%28_%3A_%3A%29 ; https://developer.apple.com/documentation/audiotoolbox/audioqueuestop%28_%3A_%3A%29 ; https://developer.apple.com/documentation/audiotoolbox/audioqueueremovepropertylistener%28_%3A_%3A_%3A_%3A%29

`NEVER_SIMULATION=ENFORCED`; `ZERO_COST_FOSS=ENFORCED`; `REAL_OUTPUT=NOT_AUTHORIZED`; `PRODUCTION=NOT_AUTHORIZED`.
