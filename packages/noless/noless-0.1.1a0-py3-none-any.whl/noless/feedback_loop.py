"""Interactive AI-Human Feedback Loop for Model Development"""

import os
import sys
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.layout import Layout
from rich.text import Text
import questionary
from questionary import Style

from noless.ollama_client import OllamaClient
from noless.local_models import LocalModelRegistry


console = Console()

custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#f44336 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
    ('disabled', 'fg:#858585 italic')
])


class FeedbackLoop:
    """Interactive loop for AI-human collaboration on code generation"""
    
    def __init__(self, ollama_client: OllamaClient, generator_model: str, reviewer_model: Optional[str] = None):
        self.client = ollama_client
        self.generator_model = generator_model
        self.reviewer_model = reviewer_model or generator_model
        self.conversation_history: List[Dict[str, str]] = []
        self.current_code: str = ""
        self.iteration_count: int = 0
        self.max_iterations: int = 10
        
    def start_interactive_generation(self, context: Dict[str, Any], file_type: str) -> str:
        """
        Start interactive code generation with human-in-the-loop feedback
        
        Args:
            context: Generation context (task, framework, dataset, etc.)
            file_type: Type of file to generate (model, train, test)
            
        Returns:
            Final generated code
        """
        console.print(Panel.fit(
            f"[bold cyan]🤖 Interactive {file_type}.py Generation[/bold cyan]\n"
            f"[dim]Generator:[/dim] {self.generator_model}\n"
            f"[dim]Reviewer:[/dim] {self.reviewer_model}",
            border_style="cyan"
        ))
        
        # Initial generation
        console.print("\n[yellow]⚡ Generating initial code...[/yellow]")
        initial_prompt = self._build_prompt(context, file_type)
        self.current_code = self._generate_code(initial_prompt)
        self.iteration_count = 1
        
        while self.iteration_count <= self.max_iterations:
            console.print(f"\n[bold cyan]━━━ Iteration {self.iteration_count}/{self.max_iterations} ━━━[/bold cyan]")
            
            # Show current code
            self._display_code_preview(self.current_code, file_type)
            
            # Ask user what they want to do
            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "✅ Accept this code",
                    "💬 Give feedback for improvement",
                    "🔍 Request AI review",
                    "📝 Show full code",
                    "🔄 Regenerate from scratch",
                    "❌ Cancel and use template"
                ],
                style=custom_style
            ).ask()
            
            if not action:  # User cancelled
                action = "❌ Cancel and use template"
            
            if action.startswith("✅"):
                console.print("\n[green]✅ Code accepted![/green]")
                return self.current_code
                
            elif action.startswith("💬"):
                feedback = Prompt.ask("\n[cyan]What improvements would you like?[/cyan]")
                if feedback.strip():
                    console.print("\n[yellow]⚡ Applying your feedback...[/yellow]")
                    self.current_code = self._apply_feedback(feedback, context, file_type)
                    self.iteration_count += 1
                    
            elif action.startswith("🔍"):
                console.print("\n[yellow]🔍 AI is reviewing the code...[/yellow]")
                review = self._get_ai_review(self.current_code, context, file_type)
                self._display_review(review)
                
                if review.get("suggestions"):
                    if Confirm.ask("\n[cyan]Apply AI suggestions?[/cyan]", default=True):
                        console.print("\n[yellow]⚡ Applying AI suggestions...[/yellow]")
                        self.current_code = self._apply_ai_suggestions(review, context, file_type)
                        self.iteration_count += 1
                        
            elif action.startswith("📝"):
                self._display_full_code(self.current_code, file_type)
                
            elif action.startswith("🔄"):
                console.print("\n[yellow]⚡ Regenerating from scratch...[/yellow]")
                self.current_code = self._generate_code(initial_prompt)
                self.iteration_count += 1
                
            elif action.startswith("❌"):
                console.print("\n[yellow]⚠️  Using template fallback[/yellow]")
                return ""  # Signal to use template
                
        console.print(f"\n[yellow]⚠️  Reached max iterations ({self.max_iterations}). Using current code.[/yellow]")
        return self.current_code
    
    def _generate_code(self, prompt: str) -> str:
        """Generate code using LLM"""
        system_msg = (
            "You are an expert Python/ML engineer. Generate complete, production-ready code."
            " Return ONLY valid Python code with no markdown fences or explanations."
            " Include all imports, classes, functions, and proper error handling."
        )
        
        try:
            with console.status(f"[cyan]Thinking with {self.generator_model}...", spinner="dots"):
                response = self.client.generate(
                    self.generator_model,
                    prompt,
                    system=system_msg,
                    temperature=0.3
                )
            return self._extract_code(response)
        except Exception as e:
            console.print(f"[red]Error generating code: {e}[/red]")
            return ""
    
    def _apply_feedback(self, feedback: str, context: Dict[str, Any], file_type: str) -> str:
        """Apply user feedback to improve code"""
        prompt = f"""
Current {file_type}.py code:
```python
{self.current_code}
```

User feedback: {feedback}

Context:
- Task: {context.get('task')}
- Framework: {context.get('framework')}
- Architecture: {context.get('architecture')}

Please improve the code based on the user's feedback. Return the complete updated code.
"""
        return self._generate_code(prompt)
    
    def _get_ai_review(self, code: str, context: Dict[str, Any], file_type: str) -> Dict[str, Any]:
        """Get AI review of the code"""
        prompt = f"""
Review this {file_type}.py code:
```python
{code}
```

Context:
- Task: {context.get('task')}
- Framework: {context.get('framework')}
- Architecture: {context.get('architecture')}

Provide a structured review with:
1. What's good about the code
2. Potential issues or bugs
3. Performance concerns
4. Best practice violations
5. Specific suggestions for improvement

Format your response as JSON with keys: strengths, issues, suggestions
"""
        
        system_msg = "You are an expert code reviewer. Provide constructive, actionable feedback."
        
        try:
            with console.status(f"[cyan]Reviewing with {self.reviewer_model}...", spinner="dots"):
                response = self.client.generate(
                    self.reviewer_model,
                    prompt,
                    system=system_msg,
                    temperature=0.2
                )
            
            # Try to parse JSON response
            import json
            import re
            
            # Extract JSON from markdown fences or raw response
            json_match = re.search(r'```(?:json)?\n(.*?)```', response, re.DOTALL)
            if json_match:
                response = json_match.group(1)
            
            try:
                return json.loads(response)
            except:
                # Fallback: parse as text
                return {
                    "review": response,
                    "suggestions": ["See review text for details"]
                }
        except Exception as e:
            console.print(f"[red]Error during review: {e}[/red]")
            return {"error": str(e)}
    
    def _apply_ai_suggestions(self, review: Dict[str, Any], context: Dict[str, Any], file_type: str) -> str:
        """Apply AI suggestions to code"""
        suggestions_text = "\n".join(review.get("suggestions", []))
        prompt = f"""
Current code:
```python
{self.current_code}
```

AI Review Suggestions:
{suggestions_text}

Context:
- Task: {context.get('task')}
- Framework: {context.get('framework')}
- Architecture: {context.get('architecture')}

Apply the suggestions to improve the code. Return the complete updated code.
"""
        return self._generate_code(prompt)
    
    def _build_prompt(self, context: Dict[str, Any], file_type: str) -> str:
        """Build initial generation prompt"""
        task = context.get("task")
        framework = context.get("framework")
        arch = context.get("architecture", "resnet50")
        dataset_meta = context.get("dataset_metadata", {})
        requirements = context.get("requirements", {})
        
        if file_type == "model":
            return f"""
Create a complete, production-ready model.py file for:
- Task: {task}
- Framework: {framework}
- Architecture: {arch}
- Dataset metadata: {dataset_meta}

Requirements:
1. All necessary imports (torch, tensorflow, etc.)
2. Complete Model class with __init__ and forward methods
3. Use pretrained weights where applicable
4. Proper input/output shapes based on dataset
5. Docstrings and type hints
6. Custom layers if needed for the architecture
7. Model initialization with proper parameter settings
8. Support for both training and inference modes

Generate COMPLETE, READY-TO-RUN code. No TODOs or placeholders.
"""
        
        elif file_type == "train":
            dataset = context.get("dataset", "dataset.csv")
            return f"""
Create a complete, production-ready train.py file for:
- Task: {task}
- Framework: {framework}
- Dataset path: {dataset}
- Dataset metadata: {dataset_meta}
- Requirements: {requirements}

Requirements:
1. Complete data loading from {dataset}
2. Train/validation/test split
3. DataLoader with transforms and augmentation
4. Full training loop with proper loss, optimizer, scheduler
5. Validation loop with metrics (accuracy, F1, etc.)
6. Model checkpointing (save best model)
7. Early stopping
8. Progress bars with tqdm
9. Logging (tensorboard or wandb optional)
10. CPU/GPU support with device detection
11. Config loading from config.yaml
12. Argument parsing with argparse
13. Main function and if __name__ == '__main__'

Generate COMPLETE, READY-TO-RUN code. No TODOs or placeholders.
"""
        
        else:  # test
            return f"""
Create a complete test_model.py file using pytest for:
- Task: {task}
- Framework: {framework}

Requirements:
1. All pytest imports and fixtures
2. Test model initialization
3. Test forward pass with various input shapes
4. Test output shapes match expected
5. Test model save/load
6. Test data loading
7. Test training step (single batch)
8. Test full training (1 epoch)
9. Test edge cases and error handling
10. Fixtures for model, data, config

Generate COMPLETE, READY-TO-RUN code. No TODOs or placeholders.
"""
    
    def _extract_code(self, response: str) -> str:
        """Extract code from LLM response"""
        import re
        response = response.strip()
        
        # Remove markdown fences
        match = re.search(r'```(?:python)?\n(.*?)```', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # If no fences, check if it looks like code
        if any(response.startswith(prefix) for prefix in ["import ", "from ", "\"\"\"", "class ", "def "]):
            return response
        
        return response
    
    def _display_code_preview(self, code: str, file_type: str):
        """Display code preview (first 30 lines)"""
        lines = code.split('\n')
        preview_lines = lines[:30]
        preview = '\n'.join(preview_lines)
        
        if len(lines) > 30:
            preview += f"\n... ({len(lines) - 30} more lines)"
        
        console.print(Panel(
            Syntax(preview, "python", theme="monokai", line_numbers=True),
            title=f"[bold cyan]{file_type}.py Preview[/bold cyan]",
            border_style="cyan"
        ))
    
    def _display_full_code(self, code: str, file_type: str):
        """Display full code"""
        console.print(Panel(
            Syntax(code, "python", theme="monokai", line_numbers=True),
            title=f"[bold cyan]Complete {file_type}.py[/bold cyan]",
            border_style="cyan",
            expand=False
        ))
        Prompt.ask("\n[dim]Press Enter to continue[/dim]")
    
    def _display_review(self, review: Dict[str, Any]):
        """Display AI review"""
        if "error" in review:
            console.print(f"\n[red]Review error: {review['error']}[/red]")
            return
        
        if "review" in review:
            # Text-based review
            console.print(Panel(
                Markdown(review["review"]),
                title="[bold yellow]🔍 AI Review[/bold yellow]",
                border_style="yellow"
            ))
        else:
            # Structured review
            review_text = ""
            
            if "strengths" in review:
                strengths = review["strengths"]
                if isinstance(strengths, list):
                    review_text += "**✅ Strengths:**\n" + "\n".join(f"- {s}" for s in strengths) + "\n\n"
                else:
                    review_text += f"**✅ Strengths:**\n{strengths}\n\n"
            
            if "issues" in review:
                issues = review["issues"]
                if isinstance(issues, list):
                    review_text += "**⚠️ Issues:**\n" + "\n".join(f"- {i}" for i in issues) + "\n\n"
                else:
                    review_text += f"**⚠️ Issues:**\n{issues}\n\n"
            
            if "suggestions" in review:
                suggestions = review["suggestions"]
                if isinstance(suggestions, list):
                    review_text += "**💡 Suggestions:**\n" + "\n".join(f"- {s}" for s in suggestions)
                else:
                    review_text += f"**💡 Suggestions:**\n{suggestions}"
            
            console.print(Panel(
                Markdown(review_text) if review_text else Text(str(review)),
                title="[bold yellow]🔍 AI Review[/bold yellow]",
                border_style="yellow"
            ))


def select_reviewer_model(client: OllamaClient, generator_model: str, show_header: bool = True) -> str:
    """Let user select a reviewer model (preferably larger/different than generator)"""
    registry = LocalModelRegistry(client)
    available = registry.available_models()
    
    if not available:
        console.print("[yellow]No models available, using generator model[/yellow]")
        return generator_model
    
    if len(available) == 1:
        # Only one model available
        console.print(f"[yellow]Only one model available ({available[0].name}), using it for review[/yellow]")
        return available[0].name
    
    if show_header:
        console.print("\n[bold cyan]🔍 Select AI Reviewer Model[/bold cyan]")
        console.print("[dim]Choose a model to review and improve the generated code[/dim]")
        console.print("[dim]💡 Tip: Larger models catch more issues but are slower[/dim]\n")
    
    # Show model options with recommendations
    choices = []
    model_map = {}  # Map display label to actual model name
    
    console.print(f"[dim]Found {len(available)} available models[/dim]")
    
    for model_info in available:
        name = model_info.name
        size = model_info.size  # This is a string like "7B" or "8x7B MoE"
        
        # Create informative label
        label = f"{name} ({size})"
        
        # Add recommendations based on model characteristics
        if name != generator_model:
            if any(marker in name.lower() for marker in ["70b", "32b", "34b", "65b"]):
                label += " ⭐ [Recommended - Large & Thorough]"
            elif any(marker in name.lower() for marker in ["20b", "mixtral", "gpt-oss"]):
                label += " ⭐ [Recommended - Balanced]"
            elif any(marker in name.lower() for marker in ["13b", "14b", "15b"]):
                label += " [Good for review]"
            else:
                label += " [Different model]"
        elif name == generator_model:
            label += " [Same as generator - faster]"
        
        choices.append(label)
        model_map[label] = name
    
    # Add option to skip review
    skip_option = "⏭️  Skip AI review (use generator model for validation)"
    choices.append(skip_option)
    model_map[skip_option] = None
    
    # Sort choices: recommended first, then others, skip option last
    def sort_key(choice):
        if "⭐" in choice and "Large" in choice:
            return (0, choice)  # Large models first
        elif "⭐" in choice and "Balanced" in choice:
            return (1, choice)  # Balanced models second
        elif "Good for review" in choice:
            return (2, choice)  # Good models third
        elif "⏭️" in choice:
            return (999, choice)  # Skip option last
        elif "Same as generator" in choice:
            return (5, choice)  # Same model near end
        else:
            return (3, choice)  # Different models in middle
    
    choices.sort(key=sort_key)
    
    console.print(f"[dim]Presenting {len(choices)} options for selection...[/dim]\n")
    
    # Flush output to ensure messages appear
    import sys
    sys.stdout.flush()
    sys.stderr.flush()
    
    try:
        selected = questionary.select(
            "Which model should review the generated code?",
            choices=choices,
            style=custom_style,
            use_shortcuts=True,  # Allow number keys for quick selection
            use_arrow_keys=True  # Explicitly enable arrow keys
        ).ask()
        
        if not selected:
            # User cancelled, use generator model
            console.print("[yellow]No selection made, using generator model[/yellow]")
            return generator_model
        
        # Extract model name from mapping
        result = model_map.get(selected, generator_model)
        return result
    except (EOFError, KeyboardInterrupt):
        # Handle terminal interruption
        console.print("\n[yellow]Selection interrupted, using generator model[/yellow]")
        return generator_model
    except Exception as e:
        # Fallback for any other error
        console.print(f"\n[yellow]Selection error ({e}), using generator model[/yellow]")
        return generator_model
