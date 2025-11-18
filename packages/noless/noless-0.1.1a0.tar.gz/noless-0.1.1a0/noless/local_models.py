"""Metadata helpers for local Ollama models installed by the user."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from rich.table import Table

from noless.ollama_client import OllamaClient


@dataclass
class LocalModelInfo:
    """Human-friendly metadata about a local LLM."""

    name: str
    family: str
    size: str
    strengths: List[str]
    preferred_tasks: List[str]
    notes: str = ""


class LocalModelRegistry:
    """Lookup helper that maps known models to recommended use-cases."""

    _MODEL_KB: Dict[str, LocalModelInfo] = {
        "deepseek-coder:6.7b": LocalModelInfo(
            name="deepseek-coder:6.7b",
            family="DeepSeek",
            size="6.7B",
            strengths=["Code generation", "Planning", "Bug fixes"],
            preferred_tasks=["code", "pipeline"],
            notes="Fast coder tuned for Python-heavy projects.",
        ),
        "deepseek-r1:7b": LocalModelInfo(
            name="deepseek-r1:7b",
            family="DeepSeek",
            size="7B",
            strengths=["Reasoning", "Data analysis", "Follow-up questions"],
            preferred_tasks=["general", "analysis"],
            notes="Great balance of reasoning quality and speed.",
        ),
        "mistral:7b": LocalModelInfo(
            name="mistral:7b",
            family="Mistral",
            size="7B",
            strengths=["Summaries", "Short form generation"],
            preferred_tasks=["general"],
            notes="Compact, efficient general-purpose model.",
        ),
        "mixtral:8x7b": LocalModelInfo(
            name="mixtral:8x7b",
            family="Mistral",
            size="8x7B MoE",
            strengths=["Reasoning", "Coding", "Complex instructions"],
            preferred_tasks=["general", "code"],
            notes="Sparse MoE capable of deep plans if you have the VRAM.",
        ),
        "llama3.1:8b": LocalModelInfo(
            name="llama3.1:8b",
            family="Meta Llama 3.1",
            size="8B",
            strengths=["Dialogue", "Classification", "Light coding"],
            preferred_tasks=["general", "analysis"],
            notes="Small yet capable assistant for most autopilot sessions.",
        ),
        "llama3.1:70b": LocalModelInfo(
            name="llama3.1:70b",
            family="Meta Llama 3.1",
            size="70B",
            strengths=["High quality reasoning", "Long context", "Advanced coding"],
            preferred_tasks=["general", "code", "analysis"],
            notes="If you have the horsepower, this is an excellent default.",
        ),
        "llama3.2:3b": LocalModelInfo(
            name="llama3.2:3b",
            family="Meta Llama 3.2",
            size="3B",
            strengths=["Quick drafts", "Basic classification"],
            preferred_tasks=["general"],
            notes="Tiny assistant that runs on CPUs but with limited reasoning.",
        ),
    }

    def __init__(self, client: Optional[OllamaClient] = None):
        self.client = client or OllamaClient()

    def available_models(self) -> List[LocalModelInfo]:
        """Return metadata for every locally installed model that we know."""
        installed = self.client.list_models()
        models: List[LocalModelInfo] = []
        for name in installed:
            if name in self._MODEL_KB:
                models.append(self._MODEL_KB[name])
            else:
                models.append(
                    LocalModelInfo(
                        name=name,
                        family="Custom",
                        size="?",
                        strengths=["General purpose"],
                        preferred_tasks=["general"],
                        notes="Model detected via Ollama, using generic profile.",
                    )
                )
        return models

    def describe_table(self) -> Table:
        table = Table(title="🧠 Local Ollama Models", show_header=True, header_style="bold magenta")
        table.add_column("Model", style="cyan")
        table.add_column("Family", style="yellow")
        table.add_column("Size", style="green")
        table.add_column("Strengths", style="blue")
        table.add_column("Notes", style="white")
        for info in self.available_models():
            table.add_row(
                info.name,
                info.family,
                info.size,
                ", ".join(info.strengths),
                info.notes,
            )
        return table

    def recommend(self, goal: str = "general") -> Optional[str]:
        """Pick a model name that best matches the request."""
        candidates = self.available_models()
        if not candidates:
            return None

        def score(info: LocalModelInfo) -> int:
            base = 1
            if goal in info.preferred_tasks:
                base += 2
            if "code" in info.preferred_tasks and goal == "code":
                base += 1
            if "analysis" in info.preferred_tasks and goal == "analysis":
                base += 1
            return base

        ranked = sorted(candidates, key=score, reverse=True)
        return ranked[0].name if ranked else None
