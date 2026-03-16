# Alexander OS

> **Offline-first, distraction-free educational AI for K-12 iPads.**  
> All inference runs locally on the Apple Neural Engine. No internet. No surveillance. No distractions.

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: iPadOS](https://img.shields.io/badge/Platform-iPadOS%2017%2B-blue.svg)]()
[![Framework: MLX](https://img.shields.io/badge/Framework-Apple%20MLX-black.svg)]()
[![Status: Pre-Alpha](https://img.shields.io/badge/Status-Pre--Alpha-orange.svg)]()

---

## The Problem

School districts across the United States spend billions deploying 1:1 iPad programs. The intent is learning. The outcome is TikTok. The device meant to replace textbooks has instead replaced attention spans.

Existing solutions — content filters, MDM lockdowns, screen time limits — treat the symptom. They do not treat the cause. A student who cannot access TikTok will find the next distraction. The deeper problem is that the device is inherently networked, and networks are inherently adversarial to focus.

**The only real solution is to sever the network entirely.**

---

## The Solution: Alexander OS

Alexander OS is an offline-first educational operating environment that runs on existing school iPads. It does three things no existing edtech product does simultaneously:

1. **Severs the internet at the OS level** during study sessions — not via filtering, but via true network isolation. The device cannot phone home, stream, or be surveilled.
2. **Runs Small Language Models entirely on-device** using the Apple Neural Engine and the MLX framework. No API calls. No cloud. No latency. No data leaving the device.
3. **Acts as a Socratic tutor, not a search engine.** Instead of giving students answers, it directs them back to the exact page in their physical textbook — rebuilding reading habits and deep focus.

---

## Key Features

### 🔒 Network Isolation
The internet is severed at the session level. Alexander OS operates in a true offline mode — no background syncs, no telemetry, no API calls. Student queries never leave the device. This is not a content filter; it is architectural separation.

### 🧠 Dynamic SLM Hot-Swapping
Running two language models simultaneously on a base iPad (4–6GB RAM) causes thermal throttling and memory crashes. Alexander OS solves this with a lightweight subject-detection kernel that hot-swaps between two quantized models:

| Model | Parameters | Use Case |
|-------|-----------|----------|
| `Llama 3.2` | 1B (4-bit quantized) | Humanities, History, Literature, General |
| `Qwen 2.5 Math` | 1.5B (4-bit quantized) | Mathematics, Physics, Chemistry, STEM |

Only one model is loaded into the Neural Engine's memory pool at any time. Switching takes under 2 seconds on Apple Silicon.

### 📖 Socratic Tutoring Engine
Alexander OS is explicitly prohibited from giving direct answers. Its system prompt enforces a pedagogical constraint: every response must reference the student's physical textbook by chapter and page, ask a guiding question, and build toward understanding rather than completion. It is designed to make the student think, not to think for the student.

### 🛡️ Zero Student Data Exposure
Because all inference is local, there is no user data to expose. No query logs are transmitted. No student profiles are built. No third-party APIs process student input. Compliance with FERPA, COPPA, and state-level student privacy laws is structural — not contractual.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| On-device inference | [Apple MLX](https://github.com/ml-explore/mlx) |
| Hardware acceleration | Apple Neural Engine (ANE) |
| STEM model | Qwen 2.5 Math 1.5B (4-bit via MLX) |
| Humanities model | Llama 3.2 1B (4-bit via MLX) |
| Development environment | macOS, Python 3.11+ |
| UI prototype | SwiftUI (iPadOS 17+) |
| Quantization | `mlx_lm.convert` with `--q-bits 4` |
| Fine-tuning | MLX LoRA fine-tuning pipeline |

---

## Repository Structure

```
alexander-os/
│
├── README.md                   ← You are here
│
├── ui-prototype/               ← SwiftUI mockups and screen designs
│   ├── screens/                ← Individual screen layouts
│   └── assets/                 ← Icons, color palette, typography
│
├── experiments/                ← Core logic prototypes (Python)
│   ├── alexander_logic.py      ← SLM kernel: subject detection + hot-swap
│   ├── rag_pipeline.py         ← Retrieval from school-uploaded PDFs
│   └── socratic_prompt.py      ← Prompt engineering for Socratic mode
│
└── docs/                       ← Technical documentation
    ├── architecture.md         ← Edge-AI system design
    ├── hardware_specs.md       ← Development hardware requirements
    └── privacy_model.md        ← Student data protection framework
```

---

## Development Status

This repository represents the pre-alpha research and architecture phase.  

- [x] Core SLM hot-swap kernel (Python prototype)  
- [x] Subject detection logic  
- [x] Socratic prompt architecture  
- [x] System architecture documentation  
- [x] Hardware specification documentation  
- [ ] MLX model quantization pipeline  
- [ ] SwiftUI prototype (in progress)  
- [ ] On-device RAG from school PDFs  
- [ ] MDM/school deployment configuration  

---

## Why This Matters

> *"The most dangerous thing you can do to a child's mind is give them infinite content and infinite answers and call it education."*

The global edtech industry is optimised for engagement. Alexander OS is optimised for the opposite: focused, deep, offline learning. It is the first educational AI tool designed to make itself less necessary over time — by redirecting students to books, not to screens.

---

## Founder

**Varun Jarwani** — Ahmedabad, India  
18-year-old engineer and founder. Built the core logic prototype while preparing for India's Joint Entrance Examination (JEE).  

---

## License

MIT License. See [LICENSE](LICENSE) for details.
