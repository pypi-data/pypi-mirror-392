"""Interactive refinement system for post-generation code improvements."""

import os
import json
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.syntax import Syntax
from noless.ollama_client import OllamaClient

console = Console()


def _robust_json_parse(text: str) -> Optional[Dict[str, Any]]:
    """Robustly parse JSON from LLM response, handling common issues."""
    text = text.strip()

    # Method 1: Try to parse the entire response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Method 2: Find JSON block between ```json and ```
    json_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Method 3: Find the outermost { } pair
    # Count braces to find matching pair
    start_idx = text.find('{')
    if start_idx != -1:
        brace_count = 0
        end_idx = -1
        in_string = False
        escape_next = False

        for i in range(start_idx, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break

        if end_idx != -1:
            json_str = text[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try to fix common issues
                # Remove trailing commas before } or ]
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                # Replace single quotes with double quotes (careful with apostrophes)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

    # Method 4: Simplest regex match (last resort)
    match = re.search(r'\{[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


class RefinementAgent:
    """Agent that handles user-requested code refinements after project creation."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None, llm_model: Optional[str] = None):
        self.client = ollama_client or OllamaClient()
        self.llm_model = llm_model
        self.refinement_history: List[Dict[str, Any]] = []

    def start_refinement_loop(self, output_dir: str, project_info: Dict[str, Any]) -> None:
        """Start interactive refinement loop after project creation."""
        if not self.llm_model or not self.client.is_available():
            console.print("[yellow]Refinement requires an LLM model. Skipping refinement loop.[/yellow]")
            return

        console.print("\n")
        console.print(Panel.fit(
            "[bold cyan]🔄 Interactive Refinement Mode[/bold cyan]\n\n"
            "Your project has been created! You can now request changes:\n"
            "• [green]add[/green] - Add new features or files\n"
            "• [yellow]modify[/yellow] - Change existing code\n"
            "• [red]fix[/red] - Fix bugs or issues\n"
            "• [blue]optimize[/blue] - Improve performance\n"
            "• [cyan]explain[/cyan] - Get explanations about the code\n\n"
            "[dim]Type 'done' or 'exit' to finish refinement[/dim]",
            border_style="cyan",
            padding=(1, 2)
        ))

        refinement_count = 0

        while True:
            console.print("\n")
            user_request = Prompt.ask(
                "[bold cyan]💭 What changes would you like?[/bold cyan]",
                default="done"
            ).strip()

            if user_request.lower() in ["done", "exit", "quit", "q", ""]:
                if refinement_count > 0:
                    console.print(f"\n[bold green]✅ Refinement complete! Made {refinement_count} changes.[/bold green]")
                else:
                    console.print("\n[green]✅ No changes requested. Project is ready![/green]")
                break

            # Analyze the request
            request_type = self._classify_request(user_request)
            console.print(f"[dim]Request type: {request_type}[/dim]")

            # Show which files might be affected
            affected_files = self._identify_affected_files(user_request, output_dir)
            if affected_files:
                console.print(f"[cyan]Files that may be modified:[/cyan] {', '.join(affected_files)}")

            # Confirm before making changes
            if not Confirm.ask("[yellow]Proceed with this change?[/yellow]", default=True):
                console.print("[dim]Change skipped.[/dim]")
                continue

            # Apply the refinement
            success = self._apply_refinement(user_request, request_type, output_dir, project_info)

            if success:
                refinement_count += 1
                self.refinement_history.append({
                    "request": user_request,
                    "type": request_type,
                    "files_modified": affected_files,
                    "success": True
                })
                console.print(f"[bold green]✅ Change #{refinement_count} applied successfully![/bold green]")
            else:
                console.print("[red]Failed to apply change. Try a different request.[/red]")

            # Show refinement summary
            if refinement_count > 0 and refinement_count % 3 == 0:
                self._show_refinement_summary()

    def _classify_request(self, request: str) -> str:
        """Classify the type of user request using LLM."""
        prompt = f"""Classify this code change request into ONE category:
Request: "{request}"

Categories:
- add: Adding new features, functions, classes, or files
- modify: Changing existing functionality
- fix: Fixing bugs or errors
- optimize: Performance improvements
- explain: Asking for explanations
- refactor: Code restructuring

Return ONLY the category name (lowercase), nothing else."""

        try:
            response = self.client.generate(
                self.llm_model,
                prompt,
                system="You are a code request classifier. Return only the category name.",
                temperature=0.1
            )
            category = response.strip().lower()
            if category in ["add", "modify", "fix", "optimize", "explain", "refactor"]:
                return category
            return "modify"  # Default
        except Exception:
            return "modify"

    def _identify_affected_files(self, request: str, output_dir: str) -> List[str]:
        """Identify which files might be affected by the request."""
        # Get list of project files
        project_files = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                if file.endswith(('.py', '.yaml', '.yml', '.md', '.txt')):
                    rel_path = os.path.relpath(os.path.join(root, file), output_dir)
                    project_files.append(rel_path)

        # Ask LLM which files are likely affected
        prompt = f"""Given these project files: {project_files}

User request: "{request}"

Which files are most likely to be affected? Return a JSON array of filenames.
Example: ["model.py", "train.py"]

If adding a new file, include the suggested new filename.
Return ONLY the JSON array, nothing else."""

        try:
            response = self.client.generate(
                self.llm_model,
                prompt,
                system="You are a code analysis expert. Return only a JSON array of filenames.",
                temperature=0.1
            )
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            pass

        # Default: assume model.py and train.py
        return ["model.py", "train.py"]

    def _apply_refinement(self, request: str, request_type: str, output_dir: str, project_info: Dict[str, Any]) -> bool:
        """Apply the requested refinement to the codebase."""
        console.print("\n")
        with console.status("[bold yellow]🤖 AI is analyzing and applying changes...", spinner="dots"):
            try:
                if request_type == "explain":
                    return self._handle_explanation(request, output_dir)
                elif request_type == "add":
                    return self._handle_addition(request, output_dir, project_info)
                else:
                    return self._handle_modification(request, output_dir, project_info)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                return False

    def _handle_explanation(self, request: str, output_dir: str) -> bool:
        """Provide explanations about the code."""
        # Read relevant files
        code_content = {}
        for file in ["model.py", "train.py"]:
            file_path = os.path.join(output_dir, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    code_content[file] = f.read()

        prompt = f"""Based on the following code:

{json.dumps(code_content, indent=2)}

User question: "{request}"

Provide a clear, concise explanation. Focus on:
1. What the code does
2. How it works
3. Why it's designed this way
4. Any important details

Keep the explanation under 500 words."""

        try:
            response = self.client.generate(
                self.llm_model,
                prompt,
                system="You are a helpful code instructor. Explain code clearly and concisely.",
                temperature=0.3
            )

            console.print(Panel(
                response,
                title="[bold cyan]📖 Code Explanation[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            ))
            return True
        except Exception as e:
            console.print(f"[red]Failed to generate explanation: {e}[/red]")
            return False

    def _handle_addition(self, request: str, output_dir: str, project_info: Dict[str, Any]) -> bool:
        """Handle requests to add new features or files."""
        # Read existing code for context
        existing_code = {}
        for file in ["model.py", "train.py", "config.yaml"]:
            file_path = os.path.join(output_dir, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_code[file] = f.read()

        prompt = f"""You are adding features to an ML project.

Existing project files:
{json.dumps(existing_code, indent=2)}

User request: "{request}"

Generate the necessary code changes. Return a JSON object with:
{{
    "changes": [
        {{
            "file": "filename.py",
            "action": "create" or "append" or "modify",
            "content": "the code to add or create"
        }}
    ],
    "explanation": "brief explanation of what was added"
}}

IMPORTANT:
- Return ONLY valid JSON
- For "modify", provide the complete new file content
- For "append", provide only the new code to add
- For "create", provide the complete new file"""

        try:
            response = self.client.generate(
                self.llm_model,
                prompt,
                system="You are an expert ML engineer. Generate clean, working Python code. Return ONLY valid JSON.",
                temperature=0.2
            )

            changes = _robust_json_parse(response)
            if not changes:
                console.print("[yellow]Could not parse LLM response. Trying simpler approach...[/yellow]")
                # Fallback: Just add a placeholder or skip
                return False

            # Apply each change
            for change in changes.get("changes", []):
                file_path = os.path.join(output_dir, change["file"])
                action = change["action"]
                content = change["content"]

                if action == "create":
                    with open(file_path, 'w') as f:
                        f.write(content)
                    console.print(f"[green]Created new file:[/green] {change['file']}")
                elif action == "append":
                    with open(file_path, 'a') as f:
                        f.write("\n\n" + content)
                    console.print(f"[yellow]Appended to:[/yellow] {change['file']}")
                elif action == "modify":
                    with open(file_path, 'w') as f:
                        f.write(content)
                    console.print(f"[blue]Modified:[/blue] {change['file']}")

            if changes.get("explanation"):
                console.print(f"[dim]{changes['explanation']}[/dim]")

            return True
        except Exception as e:
            console.print(f"[red]Failed to add features: {e}[/red]")
            return False

    def _handle_modification(self, request: str, output_dir: str, project_info: Dict[str, Any]) -> bool:
        """Handle requests to modify existing code."""
        # Read existing files
        existing_code = {}
        for file in ["model.py", "train.py", "config.yaml", "test_model.py"]:
            file_path = os.path.join(output_dir, file)
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_code[file] = f.read()

        prompt = f"""You are modifying an ML project based on user request.

Current code:
{json.dumps(existing_code, indent=2)}

User request: "{request}"

Generate the modified code. Return a JSON object:
{{
    "modifications": [
        {{
            "file": "filename.py",
            "new_content": "complete new file content"
        }}
    ],
    "summary": "brief summary of changes"
}}

IMPORTANT:
- Return ONLY valid JSON
- Provide complete file contents, not diffs
- Keep existing functionality unless explicitly asked to change it
- Maintain code quality and best practices"""

        try:
            response = self.client.generate(
                self.llm_model,
                prompt,
                system="You are an expert ML engineer. Generate clean, working Python code. Return ONLY valid JSON.",
                temperature=0.2
            )

            result = _robust_json_parse(response)
            if not result:
                console.print("[yellow]Could not parse LLM response. The model may be too small for this task.[/yellow]")
                return False

            # Apply modifications
            for mod in result.get("modifications", []):
                file_path = os.path.join(output_dir, mod["file"])
                with open(file_path, 'w') as f:
                    f.write(mod["new_content"])
                console.print(f"[blue]Modified:[/blue] {mod['file']}")

            if result.get("summary"):
                console.print(f"[dim]{result['summary']}[/dim]")

            # Show preview of first modified file
            if result.get("modifications"):
                first_mod = result["modifications"][0]
                preview_lines = first_mod["new_content"].split('\n')[:15]
                preview = '\n'.join(preview_lines)
                if len(first_mod["new_content"].split('\n')) > 15:
                    preview += "\n... (truncated)"

                syntax = Syntax(preview, "python", theme="monokai", line_numbers=True)
                console.print(Panel(
                    syntax,
                    title=f"[bold green]Preview: {first_mod['file']}[/bold green]",
                    border_style="green",
                    padding=(0, 1)
                ))

            return True
        except Exception as e:
            console.print(f"[red]Failed to modify code: {e}[/red]")
            return False

    def _show_refinement_summary(self) -> None:
        """Show summary of all refinements made."""
        if not self.refinement_history:
            return

        table = Table(title="📋 Refinement History", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Request", style="white", width=40)
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Status", style="green", width=10)

        for idx, entry in enumerate(self.refinement_history, 1):
            table.add_row(
                str(idx),
                entry["request"][:37] + "..." if len(entry["request"]) > 40 else entry["request"],
                entry["type"],
                "✅" if entry["success"] else "❌"
            )

        console.print("\n")
        console.print(table)
