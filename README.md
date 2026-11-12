# FREQMED — Physical Acoustic & Electromagnetic Frequency Generators

**Mission (owner-directed, 12 November 2026): build a system capable of generating real physical acoustic and electromagnetic frequencies through suitable hardware.**

FREQMED is **not** primarily a CSV reader, a document-research platform, or a simulator. The Bureau described in [RoadMap.md](RoadMap.md) owns the scientific research agenda, specifications, safety reviews and certifications. Engineering develops both generator subsystems.

## Generator architecture

- **GEN-CORE** — typed frequency commands, state machine, stop mechanisms, immutable safety gates.
- **GEN-ACOUSTIC** — native physical acoustic-output backend for an identified output device (Mac Intel first); no inference of physical sound pressure from digital amplitude.
- **GEN-EM** — driver interface for specifically identified, qualified external EM-generating equipment; no universal RF transmitter or arbitrary use of built-in wireless radios.
- **Guardian** — equipment constraints, safe shutdown and independent approvals.
- **UI** — preserve user-approved Windows 11 Fluent × macOS visual direction and 10 languages (en, fr, de, ar, es, pt, hr, it, zh, ko).

The previous V4/V5 previews and R29–R32 CSV/ledger/analysis prototypes are **historical secondary components**. They are neither the generators nor evidence of physical output.

## Non-negotiable controls

- `NEVER_SIMULATION=ENFORCED`: no simulated physical experiment, fabricated signal measurement, fake device or hidden simulation mode.
- `ZERO_COST_FOSS=ENFORCED`: FOSS project code and no paid mandatory software. macOS system APIs are proprietary platform dependencies and must be disclosed.
- `REAL_OUTPUT=NOT_AUTHORIZED`: no acoustic or electromagnetic output test before qualified hardware, relevant safety controls and approval.
- `BIOLOGICAL_EXPOSURE=NOT_AUTHORIZED`: no cell, animal or human exposure; no treatment, diagnostic or clinical claim.
- `PRODUCTION=NOT_AUTHORIZED`: software tests are not scientific or regulatory certification.
- Manufacturer partnerships are **not mandatory**; device identity, limits and safety evidence still matter.

## Governance as of 12 November 2026

P0.00 retains its historical **CERTIFIED_GOVERNANCE_ONLY** status. P0.01 is **IN_PROGRESS_REBASE_REVIEW** for the radical mission change; subsequent milestones remain pending/locked, with explicit sequential Bureau/Guardian certification required.

Read the authoritative [RoadMap.md](RoadMap.md) for the 28-stage generator development and safety plan. The early standalone generator source kit is a **candidate**, not an authorized hardware-output application.

Repository: `eddarsglobal/freqmed` (canonical local location: `~/Documents/App_py/freqmed`).
