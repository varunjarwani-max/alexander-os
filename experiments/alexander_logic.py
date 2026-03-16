"""
alexander_logic.py
------------------
Alexander OS — Core SLM Kernel (Prototype)

This module simulates the central "kernel" logic of Alexander OS:
  1. Receives a student's natural-language prompt.
  2. Detects the subject domain (STEM vs. Humanities).
  3. Hot-swaps the active Small Language Model to match the domain.
  4. Constructs a Socratic response that directs the student back
     to their physical textbook rather than delivering a direct answer.

On the production iPad, model loading is handled via Apple MLX and
the Apple Neural Engine. This Python prototype simulates that behavior
for development and testing on non-Apple hardware.

Author : Varun Jarwani
Project: Alexander OS
"""

from __future__ import annotations

import re
import time
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("alexander_os.kernel")


# ---------------------------------------------------------------------------
# Domain Enum
# ---------------------------------------------------------------------------
class Domain(Enum):
    """Represents the two broad academic domains Alexander OS supports."""
    STEM       = auto()   # → Qwen 2.5 Math 1.5B
    HUMANITIES = auto()   # → Llama 3.2 1B


# ---------------------------------------------------------------------------
# Model Registry
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ModelSpec:
    """Immutable specification for a Small Language Model."""
    name        : str
    parameters  : str          # e.g. "1B", "1.5B"
    quantization: str          # e.g. "4-bit MLX"
    domain      : Domain
    mlx_path    : str          # HuggingFace repo or local MLX path
    ram_mb      : int          # approximate RAM footprint after quantization


MODEL_REGISTRY: dict[Domain, ModelSpec] = {
    Domain.STEM: ModelSpec(
        name         = "Qwen 2.5 Math",
        parameters   = "1.5B",
        quantization = "4-bit MLX",
        domain       = Domain.STEM,
        mlx_path     = "mlx-community/Qwen2.5-Math-1.5B-Instruct-4bit",
        ram_mb       = 950,
    ),
    Domain.HUMANITIES: ModelSpec(
        name         = "Llama 3.2",
        parameters   = "1B",
        quantization = "4-bit MLX",
        domain       = Domain.HUMANITIES,
        mlx_path     = "mlx-community/Llama-3.2-1B-Instruct-4bit",
        ram_mb       = 700,
    ),
}


# ---------------------------------------------------------------------------
# Subject Detection
# ---------------------------------------------------------------------------

# STEM keyword set — triggers Qwen 2.5 Math
_STEM_KEYWORDS: frozenset[str] = frozenset({
    # Mathematics
    "algebra", "calculus", "derivative", "integral", "equation", "matrix",
    "vector", "probability", "statistics", "trigonometry", "logarithm",
    "polynomial", "quadratic", "theorem", "proof", "geometry", "coordinate",
    # Physics
    "velocity", "acceleration", "force", "momentum", "energy", "torque",
    "inertia", "gravity", "friction", "optics", "electromagnetism", "circuit",
    "wavelength", "frequency", "quantum", "entropy", "thermodynamics",
    # Chemistry
    "molecule", "atom", "reaction", "bond", "orbital", "mole", "titration",
    "oxidation", "reduction", "periodic", "element", "compound", "isotope",
    # General STEM signals
    "calculate", "solve", "formula", "proof", "derive", "compute",
})

# Humanities keyword set — triggers Llama 3.2
_HUMANITIES_KEYWORDS: frozenset[str] = frozenset({
    "history", "war", "civilization", "empire", "revolution", "literature",
    "poem", "novel", "character", "theme", "metaphor", "philosophy", "ethics",
    "democracy", "government", "constitution", "economy", "culture", "religion",
    "geography", "society", "language", "grammar", "essay", "rhetoric",
    "shakespeare", "socrates", "plato", "aristotle", "enlightenment",
    "renaissance", "colonialism", "freedom", "justice", "rights",
})


def detect_domain(prompt: str) -> Domain:
    """
    Classify a student prompt as STEM or HUMANITIES.

    Strategy:
    - Tokenize the lowercased prompt into words.
    - Count keyword hits for each domain set.
    - Return the domain with the higher hit count.
    - Default to HUMANITIES on a tie (Llama is cheaper on RAM).

    Parameters
    ----------
    prompt : str
        Raw student input text.

    Returns
    -------
    Domain
        The detected academic domain.
    """
    tokens = set(re.findall(r"\b[a-z]+\b", prompt.lower()))

    stem_hits       = len(tokens & _STEM_KEYWORDS)
    humanities_hits = len(tokens & _HUMANITIES_KEYWORDS)

    log.debug(
        "Domain detection — STEM hits: %d | Humanities hits: %d",
        stem_hits,
        humanities_hits,
    )

    if stem_hits > humanities_hits:
        return Domain.STEM
    return Domain.HUMANITIES


# ---------------------------------------------------------------------------
# Model Manager (Hot-Swap Kernel)
# ---------------------------------------------------------------------------

class ModelManager:
    """
    Manages loading and unloading of SLMs to stay within iPad RAM limits.

    On the production device this wraps `mlx_lm.load()` and
    `mlx_lm.generate()`. In this prototype it simulates those calls
    with logging and timing to demonstrate the hot-swap logic.
    """

    def __init__(self) -> None:
        self._active_model: Optional[ModelSpec] = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _unload_current(self) -> None:
        if self._active_model is None:
            return
        log.info(
            "⬇  Unloading  %-16s (%s params, ~%d MB freed)",
            self._active_model.name,
            self._active_model.parameters,
            self._active_model.ram_mb,
        )
        # Production: del model; del tokenizer; mx.metal.clear_cache()
        self._active_model = None

    def _load_model(self, spec: ModelSpec) -> None:
        log.info(
            "⬆  Loading    %-16s (%s params, %s, ~%d MB)",
            spec.name,
            spec.parameters,
            spec.quantization,
            spec.ram_mb,
        )
        # Production:
        #   from mlx_lm import load
        #   self._model, self._tokenizer = load(spec.mlx_path)
        time.sleep(0.05)   # simulate ~1–2 s load time on Neural Engine
        self._active_model = spec
        log.info("✓  %s ready on Apple Neural Engine.", spec.name)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ensure_model(self, domain: Domain) -> ModelSpec:
        """
        Guarantee the correct model is loaded for the given domain.
        Unloads the current model first if a swap is required.

        Parameters
        ----------
        domain : Domain
            The target academic domain.

        Returns
        -------
        ModelSpec
            The now-active model specification.
        """
        target = MODEL_REGISTRY[domain]

        if self._active_model is target:
            log.info("↺  %s already active. No swap needed.", target.name)
            return target

        self._unload_current()
        self._load_model(target)
        return target

    @property
    def active(self) -> Optional[ModelSpec]:
        return self._active_model


# ---------------------------------------------------------------------------
# Socratic Response Builder
# ---------------------------------------------------------------------------

# Textbook reference table — maps broad topics to (chapter, page, description)
# In production this is replaced by the RAG pipeline over school-uploaded PDFs.
_TEXTBOOK_REFS: dict[str, tuple[str, int, str]] = {
    "inertia"        : ("7", 214, "Moment of Inertia of Rigid Bodies"),
    "derivative"     : ("3", 88,  "Definition of the Derivative"),
    "integral"       : ("5", 142, "The Definite Integral"),
    "force"          : ("4", 102, "Newton's Second Law"),
    "thermodynamics" : ("18", 490, "The Laws of Thermodynamics"),
    "oxidation"      : ("11", 312, "Oxidation-Reduction Reactions"),
    "democracy"      : ("2", 44,  "Origins of Democratic Thought"),
    "renaissance"    : ("14", 388, "The Italian Renaissance"),
    "metaphor"       : ("6", 167, "Figurative Language in Literature"),
}

_SOCRATIC_TEMPLATES: list[str] = [
    (
        "Rather than giving you the answer directly, let's build the intuition. "
        "Open Chapter {chapter}, Page {page} — '{section}'. "
        "Read the first two paragraphs carefully. "
        "What relationship do you notice between {keyword} and the variable it depends on most?"
    ),
    (
        "Good question. Before I explain, I want you to look at something. "
        "Turn to Chapter {chapter}, Page {page} in your textbook — '{section}'. "
        "There's a diagram there. What does it suggest happens when {keyword} increases?"
    ),
    (
        "Let's think through this together. "
        "In Chapter {chapter}, Page {page} — '{section}' — your textbook gives a worked example. "
        "What is the first step in that example, and why do you think the author chose that approach?"
    ),
]


def build_socratic_response(prompt: str, model: ModelSpec) -> str:
    """
    Construct a Socratic response that references the student's textbook.

    In production this calls mlx_lm.generate() with a strict system prompt
    that enforces the Socratic constraint. Here we simulate the output
    deterministically for demonstration.

    Parameters
    ----------
    prompt  : str        The student's question.
    model   : ModelSpec  The currently loaded model.

    Returns
    -------
    str
        A Socratic response string.
    """
    prompt_lower = prompt.lower()

    # Find the best textbook reference
    ref_key   = None
    ref_data  = None
    for keyword, ref in _TEXTBOOK_REFS.items():
        if keyword in prompt_lower:
            ref_key  = keyword
            ref_data = ref
            break

    if ref_data is None:
        # Generic Socratic fallback when no direct keyword match
        return (
            f"[{model.name} · {model.parameters}]  "
            "That's a great question to sit with. "
            "Before I guide you, look through the index of your textbook for the key term "
            "in your question. Find the primary chapter it references. "
            "Read the introduction to that section and come back with what you think "
            "the central idea is — then we'll refine it together."
        )

    chapter, page, section = ref_data

    # Rotate through templates based on prompt length (deterministic variety)
    template = _SOCRATIC_TEMPLATES[len(prompt) % len(_SOCRATIC_TEMPLATES)]

    response_body = template.format(
        chapter = chapter,
        page    = page,
        section = section,
        keyword = ref_key,
    )

    return f"[{model.name} · {model.parameters}]  {response_body}"


# ---------------------------------------------------------------------------
# Alexander Kernel — Public Interface
# ---------------------------------------------------------------------------

class AlexanderKernel:
    """
    Top-level kernel for Alexander OS.

    Orchestrates domain detection, model hot-swapping,
    and Socratic response generation.

    Usage
    -----
    >>> kernel = AlexanderKernel()
    >>> response = kernel.respond("How do I calculate moment of inertia?")
    >>> print(response)
    """

    def __init__(self) -> None:
        self._manager = ModelManager()
        log.info("Alexander OS kernel initialised.")

    def respond(self, prompt: str) -> str:
        """
        Process a student prompt end-to-end.

        1. Detect the academic domain.
        2. Hot-swap the SLM if necessary.
        3. Generate a Socratic response.

        Parameters
        ----------
        prompt : str  The student's raw question.

        Returns
        -------
        str
            The Socratic response from the active model.
        """
        log.info("─" * 60)
        log.info("Student: %s", prompt)

        domain = detect_domain(prompt)
        log.info("Detected domain: %s", domain.name)

        model = self._manager.ensure_model(domain)
        response = build_socratic_response(prompt, model)

        log.info("Athena: %s", response)
        log.info("─" * 60)
        return response


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    kernel = AlexanderKernel()

    test_prompts = [
        "I don't understand how to calculate the moment of inertia for a cylinder.",
        "Can you explain what caused the Renaissance in Italy?",
        "How do I find the derivative of x squared plus 3x?",
        "What is the significance of metaphor in Shakespeare's Hamlet?",
        "I'm confused about oxidation and reduction reactions.",
    ]

    print("\n" + "=" * 60)
    print("  ALEXANDER OS — KERNEL DEMO")
    print("=" * 60 + "\n")

    for prompt in test_prompts:
        response = kernel.respond(prompt)
        print(f"\nQ: {prompt}")
        print(f"A: {response}\n")
