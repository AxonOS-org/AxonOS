# AxonOS

## Cognitive Operating System for Brain-Computer Interfaces

AxonOS is a pre-clinical technical infrastructure project for the brain-computer interface boundary.

It defines the missing operating layer between neural hardware, real-time signal processing, consent enforcement, typed neural intent events, and AI-enabled applications.

AxonOS is strictly an **OS for the Brain**.

It is not merely an AI-agent framework, chatbot runtime, generic Python SDK, or speculative token project.

---

<!-- AXONOS_CONCEPT_VIDEO_START -->

## AxonOS Concept Video

[![AxonOS Concept Preview](public/media/AxonOS%20Concept%20Preview.gif)](public/media/AxonOS%20Concept.mp4)

Watch the full concept video:

[AxonOS Concept.mp4](public/media/AxonOS%20Concept.mp4)

This is a simulated concept demonstration using EEG-style telemetry and gameplay input. It is not a clinical, medical-device, or regulatory claim.

<!-- AXONOS_CONCEPT_VIDEO_END -->

---

## Repository Role

This repository is the public top-level AxonOS entry point.

It contains:

- public media assets;
- legacy Python prototype material;
- early project bootstrap files;
- links to the canonical AxonOS technical stack.

The canonical technical standard lives here:

**https://github.com/AxonOS-org/axonos-standard**

This repository should be read as the public project gateway, not as the complete safety-critical implementation.

---

## Core Thesis

Raw neural data should not become the default application API.

A BCI operating layer must define:

- what neural-derived data crosses the boundary;
- which application is allowed to receive it;
- which consent state authorized it;
- how long the event remains valid;
- whether the event is typed and schema-valid;
- whether raw signal access is prohibited;
- whether the event has provenance and auditability.

The AxonOS principle:

> Applications should receive typed, consent-bound intent events, not unrestricted raw neural streams.

---

## System Layer Model

```text
neural hardware
    ↓
acquisition boundary
    ↓
real-time kernel substrate
    ↓
consent and neural-permission enforcement
    ↓
deterministic intent processing
    ↓
typed neural intent events
    ↓
application SDK
    ↓
assistive, research, or intelligent applications
```

---

## Public AxonOS Stack

| Repository | Role | Status |
|---|---|---|
| [`axonos-standard`](https://github.com/AxonOS-org/axonos-standard) | Canonical technical standard and architecture manual | Canonical |
| [`axonos-rfcs`](https://github.com/AxonOS-org/axonos-rfcs) | Engineering RFCs and design records | Normative when finalized |
| [`axonos-kernel`](https://github.com/AxonOS-org/axonos-kernel) | Real-time kernel substrate | Research-grade |
| [`axonos-sdk`](https://github.com/AxonOS-org/axonos-sdk) | Application-facing SDK and typed intent boundary | Active |
| [`axonos-consent`](https://github.com/AxonOS-org/axonos-consent) | Consent FSM and neural permission reference crate | Pre-clinical reference |
| [`axon-bci-gateway`](https://github.com/AxonOS-org/axon-bci-gateway) | Acquisition-boundary / OpenBCI HIL gateway | Non-safety acquisition boundary |
| [`axonos-swarm`](https://github.com/AxonOS-org/axonos-swarm) | Distributed timing and coordination research | Experimental |

---

## Evidence Posture

AxonOS separates claims by evidence level.

| Level | Meaning |
|---|---|
| L0 | Design intent or architecture statement |
| L1 | Static proof, model checking, type-level guarantee, deterministic unit proof |
| L2 | Software test, fuzzing, simulation, property test, or CI result |
| L3 | Hardware-in-the-loop or measured physical validation |
| L4 | Independent third-party audit or laboratory validation |

Current public repositories primarily contain L0, L1, and L2 evidence.

AxonOS does not currently claim L3 or L4 clinical validation.

---

## Non-Claims

AxonOS does not currently claim:

- FDA clearance;
- CE mark;
- clinical efficacy;
- certified medical-device status;
- production implantation readiness;
- complete IEC 62304 compliance;
- complete ISO 14971 compliance;
- complete ISO 13485 quality-system compliance;
- independent clinical validation;
- medical-device approval in any jurisdiction.

These are possible future milestones, not current claims.

---

## Recommended Reading Order

1. [`axonos-standard`](https://github.com/AxonOS-org/axonos-standard)
2. [`TECHNICAL_DUE_DILIGENCE_POSITION.txt`](https://github.com/AxonOS-org/axonos-standard/tree/main/docs/regulatory)
3. [`COMPATIBILITY.md`](https://github.com/AxonOS-org/axonos-standard/tree/main/docs/governance)
4. [`CLAIMS.md`](https://github.com/AxonOS-org/axonos-standard/tree/main/docs/regulatory)
5. [`axonos-consent`](https://github.com/AxonOS-org/axonos-consent)
6. [`axonos-sdk`](https://github.com/AxonOS-org/axonos-sdk)
7. [`axonos-kernel`](https://github.com/AxonOS-org/axonos-kernel)
8. [`axon-bci-gateway`](https://github.com/AxonOS-org/axon-bci-gateway)

---

## Contact

Website: https://axonos.org  
GitHub: https://github.com/AxonOS-org  
General contact: connect@axonos.org  
Security: security@axonos.org  

---

## License

MIT, unless a repository-specific license states otherwise.
