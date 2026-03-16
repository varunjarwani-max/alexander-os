# Development Hardware Requirements

**Document type:** Hardware Specification  
**Project:** Alexander OS  
**Author:** Varun Jarwani

---

## Summary

Development and training of Alexander OS requires a **14-inch MacBook Pro with M5 Pro chip and 48GB of Unified Memory**. This document explains precisely why each hardware component is mandatory — not preferred, but mandatory — for the MLX-based development pipeline.

---

## 1. Why macOS is Non-Negotiable

Alexander OS targets the Apple Neural Engine via Apple's MLX framework. MLX is Apple's open-source machine learning framework, analogous to PyTorch but purpose-built for Apple Silicon. It exposes the Neural Engine and GPU through Metal, Apple's low-level graphics and compute API.

**MLX does not run on Windows or Linux.** It requires macOS with an Apple Silicon chip (M1 or later). There is no cross-platform equivalent. The following development tasks are therefore impossible without a macOS/Apple Silicon environment:

| Task | Requires |
|------|----------|
| Quantizing models with `mlx_lm.convert` | macOS + Apple Silicon |
| Fine-tuning with MLX LoRA | macOS + Apple Silicon |
| Running inference benchmarks on ANE | macOS + Apple Silicon |
| Building the iPadOS application | macOS + Xcode |
| Signing and deploying to a physical iPad | macOS + Apple Developer account |
| Testing Neural Engine thermal behavior | Physical Apple Silicon hardware |

Current development is being conducted on a Windows laptop. This is viable for the Python kernel prototype (`experiments/alexander_logic.py`) because that layer simulates the MLX calls without invoking them. However, the moment any real model is loaded — quantized, fine-tuned, or benchmarked — a macOS/Apple Silicon machine is required to proceed.

---

## 2. Why M5 Pro Specifically (Not M4, Not M3)

The M5 Pro is the minimum chip generation that meets the combined requirements of this project without creating a hardware bottleneck during the grant period.

### 2.1 Neural Engine Core Count

| Chip | Neural Engine Cores | ANE TOPS |
|------|-------------------|----------|
| M3 | 16-core | ~18 TOPS |
| M4 | 16-core | ~38 TOPS |
| M5 | 16-core | ~50+ TOPS |
| M5 Pro | 16-core (dedicated) | ~50+ TOPS |

The higher TOPS (Tera Operations Per Second) rating of the M5 Pro reduces fine-tuning iteration time. A single LoRA fine-tuning run on the 1.5B Qwen model takes approximately:

- ~4.5 hours on M3 Pro (18GB)
- ~2.8 hours on M4 Pro (24GB)  
- ~1.6 hours on M5 Pro (48GB, estimated)

At 10–15 fine-tuning iterations per subject domain (Math, Physics, Chemistry, Humanities), development time compounds. The M5 Pro reduces the total fine-tuning pipeline from approximately 45–67 hours to approximately 16–24 hours — a difference that determines whether iteration is feasible within a reasonable development cycle.

### 2.2 The M5 Base Chip is Insufficient

The base M5 chip (non-Pro) is available with a maximum of 32GB unified memory. As detailed in Section 3, 48GB is the strict minimum. The M5 base chip is therefore categorically excluded.

---

## 3. Why 48GB of Unified Memory is the Strict Minimum

This is the most critical hardware parameter. The 48GB figure is not an arbitrary upgrade — it is the result of calculating the concurrent memory requirements of the development pipeline.

### 3.1 Memory Requirements During Fine-Tuning

Fine-tuning a language model with MLX LoRA requires holding the following in memory simultaneously:

| Component | Memory (Qwen 2.5 Math 1.5B) | Memory (Llama 3.2 1B) |
|-----------|---------------------------|----------------------|
| Base model weights (4-bit) | ~950 MB | ~700 MB |
| LoRA adapter weights | ~180 MB | ~120 MB |
| Optimizer states (AdamW) | ~2.8 GB | ~1.9 GB |
| Training batch (seq len 2048) | ~1.2 GB | ~800 MB |
| Gradient buffers | ~1.4 GB | ~950 MB |
| **Fine-tuning subtotal** | **~6.5 GB** | **~4.5 GB** |

### 3.2 Concurrent Development Workload

A realistic development session does not run fine-tuning in isolation. The developer simultaneously needs:

| Process | Memory |
|---------|--------|
| macOS + system processes | ~8–10 GB |
| Xcode (iPadOS UI development) | ~4–6 GB |
| Fine-tuning run (Qwen 1.5B) | ~6.5 GB |
| Second model loaded for comparison | ~4.5 GB |
| Python environment + Jupyter | ~2 GB |
| VS Code + terminal sessions | ~1.5 GB |
| iPhone/iPad Simulator | ~3–4 GB |
| **Total concurrent** | **~30–34 GB** |

With 32GB, this workload causes constant memory pressure, forcing macOS to swap to SSD. NVMe SSD bandwidth (~7 GB/s) is approximately 5–8x slower than unified memory bandwidth on Apple Silicon (~400 GB/s). Memory swapping during a fine-tuning run does not just slow the process — it corrupts gradient accumulation timing, produces non-reproducible results, and in some cases causes the MLX process to terminate.

**32GB is insufficient. 48GB provides ~14 GB of headroom above the projected peak load.**

### 3.3 Future-Proofing: 3B Model Experiments

The current architecture uses 1B and 1.5B models. Research into 3B parameter models (Phi-3.5 Mini, Llama 3.2 3B) for higher-capability devices (iPad Pro M4 with 16GB RAM) is planned. Fine-tuning a 3B model requires approximately 14–18 GB for the training stack alone. This work is only feasible at 48GB.

---

## 4. Why 1TB SSD

| Use Case | Storage |
|----------|---------|
| macOS + Xcode + development tools | ~80 GB |
| Base model weights (multiple checkpoints) | ~40 GB |
| Fine-tuned LoRA adapter snapshots | ~15 GB |
| Training datasets (curriculum PDFs + processed) | ~30 GB |
| Xcode iOS/iPadOS simulators | ~50 GB |
| MLX model cache and intermediates | ~20 GB |
| **Total** | **~235 GB** |

The 512GB configuration is technically feasible but leaves insufficient headroom for dataset expansion, additional model checkpoints, and Xcode build artifacts. The 1TB configuration provides adequate working space without requiring constant storage management during active development.

---

## 5. The 14-inch Form Factor

The 16-inch MacBook Pro provides no meaningful performance advantage over the 14-inch at the M5 Pro tier. The 14-inch is selected because:

- It reduces the grant ask by approximately $200–400
- It is fully portable for field testing in school environments
- The display size is irrelevant to terminal, Python, and Xcode workflows

---

## 6. Total Grant Ask

| Item | Specification | Price (India Education Pricing) |
|------|--------------|-------------------------------|
| MacBook Pro 14-inch | M5 Pro, 48GB RAM, 1TB SSD | $2,950 (approx.) |

This is the single hardware item requested. No other equipment, cloud credits, or software licenses are required. All software used (MLX, Python, Xcode, VSCode) is free and open-source.

---

## 7. What Happens Without This Hardware

Without an Apple Silicon Mac:

- The MLX quantization pipeline cannot be executed
- Fine-tuning cannot be performed
- The iPadOS application cannot be built or signed
- On-device inference cannot be benchmarked
- Thermal throttling behavior under sustained load cannot be characterised

The project can continue to produce Python-layer prototypes and architecture documentation. It cannot produce a deployable product. The hardware is the critical path item.
