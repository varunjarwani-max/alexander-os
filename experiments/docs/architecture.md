# Architecture: Alexander OS Edge-AI System

**Document type:** Technical Architecture  
**Project:** Alexander OS  
**Author:** Varun Jarwani  
**Status:** Pre-Alpha Design

---

## Overview

Alexander OS is an edge-AI educational system. "Edge" means all computation happens on the student's iPad — no server, no cloud, no internet. This document explains the architectural decisions that make this possible, with particular focus on the memory management strategy that allows two language models to coexist on hardware with strict RAM constraints.

---

## 1. Why Edge-AI for Education?

Most AI tutoring products (Khan Academy Khanmigo, Chegg, Photomath) are cloud-dependent. They send the student's query to a remote server, process it, and return a response. This architecture has three fundamental problems in a K-12 context:

**1.1 Privacy**  
Every student query — potentially containing personal struggles, misunderstandings, and learning patterns — is transmitted to and stored on a third-party server. This creates FERPA/COPPA compliance complexity and genuine privacy risk.

**1.2 Network Dependency**  
A cloud AI cannot function without internet. This makes it useless in low-connectivity classrooms, during exams, or in any scenario where network access is deliberately restricted. More importantly, it means the device must remain connected — and a connected device is a distracted device.

**1.3 The Core Contradiction**  
A tool that requires internet access cannot simultaneously sever internet access. You cannot build a distraction-free environment on top of a network dependency.

**Alexander OS resolves all three by moving the model to the device.**

---

## 2. The Apple Neural Engine (ANE) as Inference Backend

Modern iPads (iPad 10th Gen and later) contain a dedicated Neural Engine — a matrix multiplication co-processor optimised for machine learning inference. Key specifications:

| Device | Neural Engine | Unified Memory |
|--------|--------------|----------------|
| iPad 10th Gen | 16-core ANE | 4 GB |
| iPad Air M2 | 16-core ANE | 8 GB |
| iPad Pro M4 | 38-core ANE | 16 GB |

The ANE can execute quantized transformer inference at speeds comparable to small GPU clusters, while consuming a fraction of the power. Apple's MLX framework is purpose-built to target the ANE through Metal Performance Shaders.

---

## 3. The Model Hot-Swap Architecture

### 3.1 The RAM Problem

The two models used in Alexander OS have the following memory footprints after 4-bit quantization:

| Model | Parameters | 4-bit RAM Usage |
|-------|-----------|----------------|
| Llama 3.2 | 1B | ~700 MB |
| Qwen 2.5 Math | 1.5B | ~950 MB |
| **Combined** | — | **~1,650 MB** |

A base iPad 10 has 4GB of total unified memory shared between the OS, the application layer, and the Neural Engine. iPadOS and the application framework consume approximately 1.5–2 GB at baseline, leaving 2–2.5 GB available for model inference.

Loading both models simultaneously (~1,650 MB) plus OS overhead pushes the device into memory pressure territory, triggering:
- Thermal throttling (reduced ANE clock speeds)
- Memory swapping (dramatically increased latency)
- Application termination by the OS memory manager (WatchdogTermination)

**Running both models at once is not viable on base hardware.**

### 3.2 The Hot-Swap Solution

Alexander OS implements a **domain-aware model scheduler**. The flow is:

```
Student Prompt
      │
      ▼
┌─────────────────────┐
│  Subject Detector   │  Keyword + context analysis
│  (Kernel Layer)     │  → classifies as STEM or HUMANITIES
└────────┬────────────┘
         │
    ┌────┴────┐
    │         │
  STEM     HUMANITIES
    │         │
    ▼         ▼
Qwen 2.5   Llama 3.2
Math 1.5B    1B
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────────┐
│  Socratic Response  │
│  Builder            │
└─────────────────────┘
         │
         ▼
   Student Screen
```

When a domain switch is required:

1. The current model is fully unloaded from the Neural Engine memory pool (`mx.metal.clear_cache()`)
2. The target model is loaded via `mlx_lm.load()`
3. The ANE initialises the new model's weight matrices
4. Inference proceeds

The full swap cycle takes approximately **1.5–2 seconds** on an M-series Neural Engine. For a student asking a question, this latency is imperceptible — it is absorbed into the "Athena is thinking…" indicator.

### 3.3 Why Not Use a Single Larger Model?

The alternative is a single general-purpose model large enough to handle both STEM and Humanities — for example, Llama 3.2 3B or Phi-3.5 Mini 3.8B.

This approach fails on base iPads for two reasons:

- A 3B model at 4-bit quantization requires ~1.9 GB. Combined with OS overhead, this approaches the memory ceiling of a 4GB device.
- More critically, general models perform significantly worse on mathematical reasoning than domain-specialist models. Qwen 2.5 Math is specifically trained on mathematical reasoning chains and outperforms equivalently-sized general models on AMC, MATH, and GSM8K benchmarks by substantial margins.

**Two small specialists, hot-swapped, outperform one larger generalist — at lower RAM cost.**

---

## 4. The Socratic Tutoring Constraint

The AI is explicitly prohibited from giving direct answers. This is not a technical limitation — it is an architectural decision enforced at the system prompt level.

Every inference call is wrapped with a system prompt containing three hard constraints:

```
CONSTRAINT 1: You must never provide the direct answer to a student's question.
CONSTRAINT 2: Every response must reference a specific chapter and page in the student's textbook.
CONSTRAINT 3: Every response must end with a question that requires the student to think.
```

This transforms the model from a search engine (which destroys learning) into a Socratic tutor (which accelerates it). The student is directed back to their physical textbook — rebuilding the reading habits that screen-based learning has eroded.

---

## 5. The RAG Pipeline (On-Device)

Schools upload their curriculum PDFs once via an MDM-managed setup flow. Alexander OS processes these documents locally:

1. **Chunking:** PDFs are segmented into chapter-aware chunks. Chapter boundaries are detected via heading patterns and page structure analysis.
2. **Embedding:** Chunks are embedded using a lightweight sentence embedding model running on the ANE.
3. **Storage:** Embeddings are stored in a local vector index (no cloud database).
4. **Retrieval:** At inference time, the student's query is embedded and matched against the index. The top-k chunks are injected into the model's context window as grounding material.

All of this runs offline. The school's textbooks never leave the device.

---

## 6. Privacy Architecture

| Data Type | Handling |
|-----------|----------|
| Student queries | Processed locally, never transmitted |
| Model responses | Generated locally, never logged externally |
| Textbook content | Stored locally, never uploaded |
| Usage patterns | Zero telemetry in offline mode |
| Student identity | No account system in core product |

This is not a privacy policy. It is a privacy architecture — the system is physically incapable of transmitting data when running in offline mode because the network adapter is disabled.

---

## 7. Deployment Model

Alexander OS is designed for MDM (Mobile Device Management) deployment by school IT departments via Apple School Manager. The school controls:

- Which textbooks are loaded
- Which subjects are enabled
- Session duration limits
- Focus mode scheduling (e.g., enabled during school hours only)

No student data is accessible to the school through Alexander OS. The system is designed to be a tool, not a surveillance instrument.
