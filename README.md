# AxonOS

**AxonOS is an open operating layer for brain-computer interfaces.**

It is the missing systems layer between neural hardware, deterministic runtime infrastructure, and intelligent applications.

AxonOS is not an AI-agent framework.  
AxonOS is not a generic Python SDK.  
AxonOS is not a machine-learning inference pipeline.

AxonOS is an **OS for the Brain**: a technical stack for deterministic neural signal handling, typed intent events, consent-aware runtime enforcement, neural permissions, and real-time BCI infrastructure.

---

## What this repository is

This repository is the **public entry point** for the AxonOS project.

It maps the AxonOS technical stack, explains the project boundary, points to the canonical repositories, and gives reviewers a clean route into the implementation.

The actual engineering work lives in dedicated repositories.

---

## Technical stack

| Layer | Repository | Role |
|---|---|---|
| Standard | `axonos-standard` | Canonical AxonOS standard, validation taxonomy, and normative artifacts |
| Kernel | `axonos-kernel` | `no_std` Rust kernel substrate, scheduling, IPC, bounded runtime primitives |
| SDK | `axonos-sdk` | Developer-facing typed APIs and application boundary |
| Consent | `axonos-consent` | Runtime consent state machine and observation-gate enforcement |
| RFCs | `axonos-rfcs` | Engineering design records and protocol evolution |
| Gateway | `axon-bci-gateway` | Acquisition boundary and OpenBCI integration surface |
| Swarm | `axonos-swarm` | Distributed timing and mesh coordination research layer |

---

## Core idea

Current BCI stacks tend to jump directly from neural hardware to application code.

AxonOS inserts a deterministic operating layer between them.

```text
Neural hardware
    ↓
Signal gateway
    ↓
AxonOS runtime boundary
    ↓
Typed intent events
    ↓
Applications
```

This boundary is where AxonOS defines:

- deterministic scheduling;
- bounded IPC;
- zero-copy signal movement;
- neural permissions;
- consent-aware observation gating;
- typed intent events;
- provenance and evidence discipline.

---

## Evidence discipline

AxonOS uses the canonical AxonOS validation taxonomy:

| Level | Meaning |
|---|---|
| L1 | Source-level, simulation, tests, CI, and formal/bounded verification artifacts |
| L2 | Hardware measurement traces, board-level validation, timing captures, and reproducible measurement logs |
| L3 | External validation, lab validation, clinical validation, certification evidence, or regulatory artifacts |

A repository MUST NOT claim a higher evidence level than its artifacts support.

This flagship repository does not claim L3 validation.

---

## Non-claims

AxonOS is pre-clinical and pre-regulatory.

This repository does not claim:

- medical-device approval;
- clinical deployment readiness;
- regulatory approval;
- patient-ready safety;
- external certification;
- completed L3 validation.

AxonOS is a technical infrastructure project. Any clinical, regulatory, or medical-device claim requires separate evidence artifacts.

---

## Recommended reading order

1. `axonos-standard` — canonical standard and validation discipline.
2. `axonos-kernel` — runtime substrate.
3. `axonos-consent` — consent-state enforcement.
4. `axonos-sdk` — developer-facing APIs.
5. `axonos-rfcs` — engineering decisions.
6. `axon-bci-gateway` — acquisition integration.
7. `axonos-swarm` — distributed timing research.

---

## Project posture

AxonOS is founder-led, open-source, and pre-seed.

The project is designed for serious technical review, not hype.

> AxonOS is not building another AI app.  
> AxonOS is building the deterministic operating layer for future neural interfaces.

---

## Media

Concept media is stored under:

```text
public/media/
```

If present, `AxonOS Concept Preview.gif` and `AxonOS Concept.mp4` are retained as visual project assets.

---

## License

This repository is licensed under the MIT License.

Individual AxonOS repositories may use their own explicit license terms.

---

## Contact

General: connect@axonos.org  
Security: security@axonos.org  
Website: https://axonos.org
