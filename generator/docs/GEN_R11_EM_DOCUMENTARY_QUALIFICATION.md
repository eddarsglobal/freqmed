# GEN-R11 — EM Device Documentary Qualification Gate (NOT A DEVICE QUALIFICATION)

## Factual starting point
GEN-R7 real Mac Intel IOKit evidence: 10 USB devices, 23 USB interfaces, 4 serial callout nodes, 0 USBTMC interfaces. These observations identify **no qualified EM generator**. A serial service or USB class is not proof of a particular instrument or its safety.

## New code: documents only, no instrument I/O
`src/em_qualification_gate.h` and `.c` define a bounded evidence structure with manufacturer/model fields and SHA-256 format fields for the vendor protocol, independent cutoff documentation and metrology plan. A structural screen returns only **MISSING** or **PRESENT_UNVERIFIED**; it cannot establish authenticity, authorship, measurements, legal conformity, or physical device identity.
`fm_em_hardware_qualified_in_r11(...)` **always returns 0**. The EM evidence source is compiled as an isolated native object and never linked into the runnable executable, and `em_backend.c` still unconditionally refuses output.

## Evidence required for a later decision (B05, B06, B09, B10)
Document the exact real instrument's manufacturer/model and serial interface actually available, manufacturer-published protocol and its legal reuse conditions, device identity and non-sensitive pinning, operational limits from real specifications, independent physical cutoff and its test procedure, applicable RF/EMC compliance, independent calibrated metrology equipment, and an explicitly authorized non-biological bench. No generic SCPI/RF commands are inferred or sent. Do not substitute formal-looking hashes for authenticity or Bureau approval.

Verdict R11: `EM_HARDWARE_QUALIFIED=NO`, `EM_OUTPUT=BLOCKED_NO_QUALIFIED_EM_DEVICE`, `EM_PROTOCOL_COMMANDS=NONE`, `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`.
