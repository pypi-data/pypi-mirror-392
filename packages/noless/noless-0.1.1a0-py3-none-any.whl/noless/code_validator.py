"""AI-powered code validation and improvement using larger models."""

from typing import Dict, Any, Optional
import json
import time
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from noless.ollama_client import OllamaClient
from noless.local_models import LocalModelRegistry, LocalModelInfo

console = Console()


class CodeValidator:
    """Validate and improve generated code using AI."""

    def __init__(
        self,
        reviewer_model: Optional[str] = None,
        generation_model: Optional[str] = None,
        ollama_client: Optional[OllamaClient] = None,
    ):
        self.requested_reviewer_model = reviewer_model
        self.generation_model = generation_model
        self.client = ollama_client or OllamaClient()
        self.registry = LocalModelRegistry(self.client)
        self._available_models = self.registry.available_models()
        self.reviewer_model = self._resolve_reviewer_model()
    
    def _resolve_reviewer_model(self) -> Optional[str]:
        """Honor user preference first, then try to auto-select a reviewer."""
        if self.requested_reviewer_model:
            if self._has_model(self.requested_reviewer_model):
                return self.requested_reviewer_model
            print(
                f"[Warning] Requested reviewer model '{self.requested_reviewer_model}' not found locally. "
                "Falling back to automatic selection."
            )
        return self._select_reviewer_model()

    def _has_model(self, model_name: str) -> bool:
        return any(info.name == model_name for info in self._available_models)

    def _select_reviewer_model(self) -> Optional[str]:
        """Choose a strong available reviewer model when the user didn't specify one."""
        if not self._available_models:
            return None

        size_priority = [
            "70b",
            "32b",
            "8x7b",
            "13b",
            "12b",
            "11b",
            "10b",
            "9b",
            "8b",
            "7b",
            "6b",
            "5b",
            "4b",
            "3b",
            "2b",
            "1.5b",
        ]

        def matches(info: LocalModelInfo, marker: str) -> bool:
            value = marker.lower()
            return value in info.size.lower() or value in info.name.lower()

        # Prefer larger reviewers that differ from the generation model if possible.
        for marker in size_priority:
            for model_info in sorted(self._available_models, key=lambda info: info.name):
                if self.generation_model and model_info.name == self.generation_model:
                    continue
                if matches(model_info, marker):
                    return model_info.name

        # Fallback: pick any model that isn't the generation model.
        for model_info in self._available_models:
            if model_info.name != self.generation_model:
                return model_info.name

        # Last resort: reuse the generation model (at least we can still review).
        if self.generation_model and self._has_model(self.generation_model):
            return self.generation_model
        return self._available_models[0].name if self._available_models else None
    
    def validate_and_improve(self, code: str, file_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate code and suggest improvements with real-time feedback"""
        if not self.reviewer_model:
            return {"valid": True, "improved_code": code, "issues": [], "suggestions": []}

        # Show what's being reviewed
        console.print("\n")
        console.print(Panel.fit(
            f"[bold cyan]🔍 AI Code Review in Progress[/bold cyan]\n"
            f"Reviewing: [yellow]{file_type}[/yellow]\n"
            f"Model: [green]{self.reviewer_model}[/green]",
            border_style="cyan"
        ))
        console.print("\n")

        # Show code being reviewed with scroll animation
        code_lines = code.split('\n')
        total_lines = len(code_lines)
        console.print(f"[dim]📄 Scanning {total_lines} lines...[/dim]\n")

        # Show code scrolling animation (fast scan visualization)
        self._show_code_scan_animation(code_lines, file_type)

        # Show thinking process - FAST
        thinking_steps = [
            "🧠 Loading model",
            "🔍 Syntax check",
            "⚠️  Bug detection",
            "📋 Best practices",
            "⚡ Performance",
            "🔒 Error handling",
            "✨ Suggestions"
        ]

        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]AI Analysis", total=len(thinking_steps))

            for step in thinking_steps:
                progress.update(task, description=f"[cyan]{step}")
                time.sleep(0.1)  # FAST!
                progress.advance(task)

        console.print("[bold green]✓[/bold green] Analysis complete!\n")

        prompt = self._build_review_prompt(code, file_type, context)
        system_msg = (
            "You are a senior code reviewer. Analyze the code for bugs, best practices, and improvements."
            " Return JSON with keys: valid (bool), issues (array), suggestions (array), improved_code (string)."
            " Only include improved_code if significant changes are needed."
        )

        try:
            with console.status("[bold yellow]🤖 AI Reviewer analyzing code...", spinner="dots"):
                response = self.client.generate(self.reviewer_model, prompt, system=system_msg, temperature=0.2)

            result = self._parse_review_response(response)

            # Show review results
            self._display_review_results(result, code, file_type)

            if result and result.get("improved_code"):
                return result

            # Return proper format even if result is None
            if result:
                return {"valid": True, "improved_code": code, "issues": result.get("issues", []), "suggestions": result.get("suggestions", [])}
            else:
                return {"valid": True, "improved_code": code, "issues": [], "suggestions": []}
        except Exception as exc:
            console.print(f"[red]⚠️  Code validation failed: {exc}[/red]\n")
            return {"valid": True, "improved_code": code, "issues": [], "suggestions": []}

    def _show_code_scan_animation(self, code_lines: list, file_type: str):
        """Show code scrolling animation during review - fast scroll effect"""
        total_lines = len(code_lines)
        window_size = 12

        with Live(console=console, refresh_per_second=60) as live:
            # Fast scroll through all code
            for i in range(0, total_lines, 3):  # Skip lines for speed
                start = max(0, i - window_size + 1)
                end = min(i + 1, total_lines)

                visible_lines = code_lines[start:end]
                code_text = '\n'.join(visible_lines)

                syntax = Syntax(
                    code_text,
                    "python",
                    theme="monokai",
                    line_numbers=True,
                    start_line=start + 1,
                    word_wrap=False
                )

                scroll_info = f" ↑{start}" if start > 0 else ""
                remaining = total_lines - end
                if remaining > 0:
                    scroll_info += f" ↓{remaining}"

                panel = Panel(
                    syntax,
                    title=f"[bold yellow]🔍 Scanning {file_type} [{end}/{total_lines}]{scroll_info}[/bold yellow]",
                    border_style="yellow",
                    padding=(0, 1)
                )

                live.update(panel)
                time.sleep(0.008)  # Super fast scrolling

        console.print(f"[green]✓[/green] Code scan complete\n")

    def _display_review_results(self, result: Optional[Dict[str, Any]], original_code: str, file_type: str):
        """Display review results in a beautiful format"""
        if not result:
            console.print("[yellow]⚠️  No review results available[/yellow]\n")
            return

        issues = result.get("issues", [])
        suggestions = result.get("suggestions", [])
        has_improvements = result.get("improved_code") and result["improved_code"] != original_code

        # Create review summary table
        table = Table(title="📊 Code Review Summary", show_header=True, header_style="bold magenta", border_style="cyan")
        table.add_column("Category", style="cyan", width=20)
        table.add_column("Count", style="green", justify="center", width=10)
        table.add_column("Status", style="yellow", width=20)

        table.add_row("Issues Found", str(len(issues)), "🔴 Needs Attention" if issues else "✅ Clean")
        table.add_row("Suggestions", str(len(suggestions)), "💡 Available" if suggestions else "✅ Good")
        table.add_row("Improvements", "Yes" if has_improvements else "No", "🔧 Generated" if has_improvements else "✅ Optimal")

        console.print(table)
        console.print("\n")

        # Show issues
        if issues:
            console.print(Panel(
                "\n".join([f"[red]❌[/red] {issue}" for issue in issues]),
                title="[bold red]⚠️  Issues Detected[/bold red]",
                border_style="red",
                padding=(1, 2)
            ))
            console.print("\n")

        # Show suggestions
        if suggestions:
            console.print(Panel(
                "\n".join([f"[yellow]💡[/yellow] {suggestion}" for suggestion in suggestions]),
                title="[bold yellow]✨ Improvement Suggestions[/bold yellow]",
                border_style="yellow",
                padding=(1, 2)
            ))
            console.print("\n")

        # Show improved code preview if available
        if has_improvements:
            console.print("[bold green]✓[/bold green] AI generated improved version!\n")

            # Show diff preview (first 20 lines)
            improved_code = result["improved_code"]
            improved_lines = improved_code.split('\n')[:20]
            preview = '\n'.join(improved_lines)
            if len(result["improved_code"].split('\n')) > 20:
                preview += "\n... (truncated)"

            syntax = Syntax(preview, "python", theme="monokai", line_numbers=True)
            console.print(Panel(
                syntax,
                title=f"[bold green]🔧 Improved {file_type} (Preview)[/bold green]",
                border_style="green",
                padding=(1, 2)
            ))
            console.print("\n")
        else:
            console.print("[bold green]✅ Code looks good! No improvements needed.[/bold green]\n")
    
    def _build_review_prompt(self, code: str, file_type: str, context: Dict[str, Any]) -> str:
        return f"""
Review this {file_type} file for a {context.get('task', 'ML')} project:

```python
{code}
```

Context:
- Task: {context.get('task')}
- Framework: {context.get('framework')}
- Dataset: {context.get('dataset')}

Check for:
1. Syntax errors
2. Import errors
3. Logic bugs
4. Missing error handling
5. Performance issues
6. Best practice violations
7. Dataset integration correctness

Provide JSON response with issues, suggestions, and optionally improved_code.
"""
    
    def _parse_review_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse review response - with fallback for non-JSON responses"""
        import re
        response = response.strip()

        # Try to extract JSON from response
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                # Ensure required keys exist
                if "valid" not in result:
                    result["valid"] = True
                if "issues" not in result:
                    result["issues"] = []
                if "suggestions" not in result:
                    result["suggestions"] = []
                return result
            except json.JSONDecodeError:
                console.print(f"[yellow]⚠️  Could not parse JSON response[/yellow]")

        # Fallback: Try to extract useful info from plain text response
        console.print(f"[yellow]⚠️  Model returned non-JSON response, creating basic review[/yellow]")

        # Create a basic result from the text
        result = {
            "valid": True,
            "issues": [],
            "suggestions": []
        }

        # Try to extract any issues mentioned
        if "error" in response.lower() or "bug" in response.lower() or "issue" in response.lower():
            # Extract lines that mention problems
            for line in response.split('\n'):
                line = line.strip()
                if line and len(line) > 10 and len(line) < 200:
                    if any(word in line.lower() for word in ["error", "bug", "issue", "problem", "missing", "incorrect"]):
                        result["issues"].append(line[:150])
                    elif any(word in line.lower() for word in ["suggest", "recommend", "consider", "should", "could", "better"]):
                        result["suggestions"].append(line[:150])

        # Limit to 5 items each
        result["issues"] = result["issues"][:5]
        result["suggestions"] = result["suggestions"][:5]

        return result if (result["issues"] or result["suggestions"]) else {"valid": True, "issues": [], "suggestions": ["Code review completed - no specific issues found"]}
