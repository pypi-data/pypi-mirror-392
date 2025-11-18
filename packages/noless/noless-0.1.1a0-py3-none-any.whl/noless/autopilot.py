"""Autopilot workflow that leverages local Ollama models for planning."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from rich.panel import Panel
from rich.console import Console

from noless.ollama_client import OllamaClient

console = Console()


@dataclass
class AutopilotPlan:
    task: str
    framework: str
    dataset_query: str
    architecture: Optional[str] = None
    hyperparameters: Dict[str, str] = field(default_factory=dict)
    notes: str = ""


class AutopilotPlanner:
    """Drive requirement gathering + planning using a local LLM."""

    SYSTEM_PROMPT = (
        "You are NoLess Autopilot."
        " Ask for clarifications when needed and always answer with valid JSON."
        " Keep recommendations grounded for practical ML pipelines."
    )

    def __init__(self, model_name: str, client: Optional[OllamaClient] = None):
        self.model_name = model_name
        self.client = client or OllamaClient()

    # ------------------------------------------------------------------
    def follow_up_questions(self, description: str, max_questions: int = 3) -> List[str]:
        prompt = (
            "A user wants to build an ML project with the following description:\n"
            f"{description}\n"
            f"Return JSON with a `questions` array containing at most {max_questions}"
            " short clarification questions. Answer with JSON only."
        )
        response = self.client.generate(self.model_name, prompt, system=self.SYSTEM_PROMPT)
        try:
            payload = json.loads(response)
            return [q.strip() for q in payload.get("questions", []) if q.strip()]
        except json.JSONDecodeError:
            return []

    def draft_plan(self, description: str, answers: Dict[str, str]) -> AutopilotPlan:
        prompt = (
            "User project description: \n"
            f"{description}\n"
            "Clarifications: \n"
        )
        for question, answer in answers.items():
            prompt += f"- {question}: {answer}\n"
        prompt += (
            "\nReturn JSON with keys task, framework, dataset_query, architecture, hyperparameters (object), and notes."
            " sentiment-analysis, regression, clustering, nlp, time-series."
        )

        response = self.client.generate(self.model_name, prompt, system=self.SYSTEM_PROMPT)
        try:
            payload = json.loads(response)
        except json.JSONDecodeError:
            payload = {}

        return AutopilotPlan(
            task=payload.get("task", "image-classification"),
            framework=payload.get("framework", "pytorch"),
            dataset_query=payload.get("dataset_query", description),
            architecture=payload.get("architecture"),
            hyperparameters=payload.get("hyperparameters", {}),
            notes=payload.get("notes", "Generated with limited context."),
        )

    def suggest_dataset_hints(self, description: str, task: str, answers: Dict[str, str]) -> Dict[str, Any]:
        prompt = (
            "You are assisting the NoLess Autopilot with dataset discovery.\n"
            f"Task: {task}\n"
            f"User description: {description}\n"
            f"Clarifications: {json.dumps(answers)}\n"
            "Return JSON with keys 'keywords' (array of short search terms),"
            " 'queries' (array of longer phrases) and 'reason' (string)."
            " Limit keywords to 3 items, lowercase, no punctuation."
        )
        response = self.client.generate(self.model_name, prompt, system=self.SYSTEM_PROMPT)
        try:
            payload = json.loads(response)
        except json.JSONDecodeError:
            payload = {}

        return {
            "keywords": payload.get("keywords", []),
            "queries": payload.get("queries", []),
            "reason": payload.get("reason", ""),
        }

    def render_plan(self, plan: AutopilotPlan) -> Panel:
        body = (
            f"[bold]Task:[/bold] {plan.task}\n"
            f"[bold]Framework:[/bold] {plan.framework}\n"
            f"[bold]Dataset Search:[/bold] {plan.dataset_query}\n"
        )
        if plan.architecture:
            body += f"[bold]Architecture:[/bold] {plan.architecture}\n"
        if plan.hyperparameters:
            hp = ", ".join(f"{k}={v}" for k, v in plan.hyperparameters.items())
            body += f"[bold]Hyperparameters:[/bold] {hp}\n"
        if plan.notes:
            body += f"\n[dim]{plan.notes}[/dim]"
        return Panel(body, title="🧠 Autopilot Plan", border_style="cyan")
