"""Project statistics tracking - counts projects built, success rates, etc."""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class ProjectStats:
    """Track project statistics persistently."""

    def __init__(self):
        self.stats_dir = Path.home() / ".noless"
        self.stats_file = self.stats_dir / "project_stats.json"
        self._ensure_stats_dir()
        self._load_stats()

    def _ensure_stats_dir(self) -> None:
        """Ensure stats directory exists."""
        self.stats_dir.mkdir(parents=True, exist_ok=True)

    def _load_stats(self) -> None:
        """Load stats from file or create default."""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            except (json.JSONDecodeError, Exception):
                self.stats = self._default_stats()
        else:
            self.stats = self._default_stats()
            self._save_stats()

    def _default_stats(self) -> Dict[str, Any]:
        """Return default stats structure."""
        return {
            "total_projects_built": 0,
            "projects_by_task": {},
            "projects_by_framework": {},
            "total_refinements": 0,
            "datasets_searched": 0,
            "models_used": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "project_history": []
        }

    def _save_stats(self) -> None:
        """Save stats to file."""
        self.stats["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            console.print(f"[dim]Warning: Could not save stats: {e}[/dim]")

    def record_project_build(
        self,
        task: str,
        framework: str,
        output_dir: str,
        llm_model: Optional[str] = None,
        dataset: Optional[str] = None,
        success: bool = True
    ) -> int:
        """Record a new project build and return the total count."""
        self.stats["total_projects_built"] += 1

        # Track by task
        if task not in self.stats["projects_by_task"]:
            self.stats["projects_by_task"][task] = 0
        self.stats["projects_by_task"][task] += 1

        # Track by framework
        if framework not in self.stats["projects_by_framework"]:
            self.stats["projects_by_framework"][framework] = 0
        self.stats["projects_by_framework"][framework] += 1

        # Track models used
        if llm_model:
            if llm_model not in self.stats["models_used"]:
                self.stats["models_used"][llm_model] = 0
            self.stats["models_used"][llm_model] += 1

        # Add to history (keep last 50)
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "framework": framework,
            "output_dir": output_dir,
            "llm_model": llm_model,
            "dataset": dataset,
            "success": success
        }
        self.stats["project_history"].append(history_entry)
        if len(self.stats["project_history"]) > 50:
            self.stats["project_history"] = self.stats["project_history"][-50:]

        self._save_stats()
        return self.stats["total_projects_built"]

    def record_refinement(self, count: int = 1) -> None:
        """Record refinement actions."""
        self.stats["total_refinements"] += count
        self._save_stats()

    def record_dataset_search(self, count: int = 1) -> None:
        """Record dataset searches."""
        self.stats["datasets_searched"] += count
        self._save_stats()

    def get_total_projects(self) -> int:
        """Get total number of projects built."""
        return self.stats["total_projects_built"]

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get a summary of all stats."""
        return {
            "total_projects": self.stats["total_projects_built"],
            "total_refinements": self.stats["total_refinements"],
            "datasets_searched": self.stats["datasets_searched"],
            "favorite_task": max(self.stats["projects_by_task"].items(), key=lambda x: x[1])[0] if self.stats["projects_by_task"] else "N/A",
            "favorite_framework": max(self.stats["projects_by_framework"].items(), key=lambda x: x[1])[0] if self.stats["projects_by_framework"] else "N/A",
            "favorite_model": max(self.stats["models_used"].items(), key=lambda x: x[1])[0] if self.stats["models_used"] else "N/A",
            "created_at": self.stats["created_at"],
            "last_updated": self.stats["last_updated"]
        }

    def show_stats_panel(self) -> None:
        """Display stats in a beautiful panel."""
        total = self.stats["total_projects_built"]

        # Create main stats table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Label", style="cyan")
        table.add_column("Value", style="bold green")

        table.add_row("🏗️  Total Projects Built", str(total))
        table.add_row("🔄 Total Refinements", str(self.stats["total_refinements"]))
        table.add_row("🔍 Datasets Searched", str(self.stats["datasets_searched"]))

        if self.stats["projects_by_task"]:
            fav_task = max(self.stats["projects_by_task"].items(), key=lambda x: x[1])
            table.add_row("⭐ Most Used Task", f"{fav_task[0]} ({fav_task[1]}x)")

        if self.stats["projects_by_framework"]:
            fav_fw = max(self.stats["projects_by_framework"].items(), key=lambda x: x[1])
            table.add_row("🛠️  Most Used Framework", f"{fav_fw[0]} ({fav_fw[1]}x)")

        if self.stats["models_used"]:
            fav_model = max(self.stats["models_used"].items(), key=lambda x: x[1])
            table.add_row("🤖 Most Used LLM", f"{fav_model[0]} ({fav_model[1]}x)")

        # Milestone message
        milestone_msg = ""
        if total >= 100:
            milestone_msg = "🏆 LEGENDARY BUILDER!"
        elif total >= 50:
            milestone_msg = "🌟 Expert Builder!"
        elif total >= 25:
            milestone_msg = "⭐ Advanced Builder!"
        elif total >= 10:
            milestone_msg = "🎯 Active Builder!"
        elif total >= 5:
            milestone_msg = "🚀 Getting Started!"
        elif total >= 1:
            milestone_msg = "👋 Welcome to NoLess!"

        console.print(Panel.fit(
            table,
            title=f"[bold magenta]📊 NoLess Statistics {milestone_msg}[/bold magenta]",
            border_style="magenta",
            padding=(1, 2)
        ))

    def show_build_counter(self) -> None:
        """Show a simple build counter."""
        total = self.stats["total_projects_built"]

        # Choose emoji based on count
        if total >= 50:
            emoji = "🏆"
        elif total >= 25:
            emoji = "⭐"
        elif total >= 10:
            emoji = "🎯"
        else:
            emoji = "📊"

        console.print(f"\n[bold cyan]{emoji} Projects Built: [green]{total}[/green][/bold cyan]")

    def show_recent_projects(self, limit: int = 5) -> None:
        """Show recent project history."""
        if not self.stats["project_history"]:
            console.print("[dim]No project history yet.[/dim]")
            return

        table = Table(title="📜 Recent Projects", show_header=True, header_style="bold magenta")
        table.add_column("#", style="cyan", width=4)
        table.add_column("Date", style="yellow", width=12)
        table.add_column("Task", style="green", width=20)
        table.add_column("Framework", style="blue", width=12)
        table.add_column("LLM", style="magenta", width=15)

        recent = list(reversed(self.stats["project_history"][-limit:]))
        for idx, entry in enumerate(recent, 1):
            timestamp = entry.get("timestamp", "")
            date_str = timestamp.split("T")[0] if "T" in timestamp else timestamp[:10]
            table.add_row(
                str(idx),
                date_str,
                entry.get("task", "N/A"),
                entry.get("framework", "N/A"),
                entry.get("llm_model", "N/A")[:15] if entry.get("llm_model") else "N/A"
            )

        console.print(table)

    def reset_stats(self) -> None:
        """Reset all stats (use with caution)."""
        self.stats = self._default_stats()
        self._save_stats()
        console.print("[yellow]Stats have been reset.[/yellow]")

    def import_existing_projects(self, search_path: str = ".") -> int:
        """Scan for existing NoLess projects and import them into stats."""
        import os
        import yaml
        from pathlib import Path

        search_dir = Path(search_path)
        if not search_dir.exists():
            console.print(f"[red]Path not found: {search_path}[/red]")
            return 0

        imported_count = 0
        console.print(f"\n[cyan]Scanning for NoLess projects in {search_dir.absolute()}...[/cyan]\n")

        # Look for directories that start with "noless" or contain config.yaml with ML task info
        for item in search_dir.iterdir():
            if not item.is_dir():
                continue

            # Check if it looks like a NoLess project
            is_noless_project = False
            project_info = {
                "task": "unknown",
                "framework": "unknown",
                "output_dir": str(item.absolute()),
                "llm_model": None,
                "dataset": None
            }

            # Check for config.yaml which contains task and framework info
            config_path = item / "config.yaml"
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = yaml.safe_load(f) or {}

                    # Extract task and framework from config
                    if "task" in config:
                        project_info["task"] = config["task"]
                        is_noless_project = True
                    if "framework" in config:
                        project_info["framework"] = config["framework"]
                        is_noless_project = True
                except Exception:
                    pass

            # Also check if folder name starts with "noless"
            if item.name.lower().startswith("noless"):
                is_noless_project = True

            # Check for essential NoLess project files
            essential_files = ["model.py", "train.py", "requirements.txt"]
            has_essentials = all((item / f).exists() for f in essential_files)

            if has_essentials:
                is_noless_project = True

                # Try to detect task from model.py content
                model_py = item / "model.py"
                if model_py.exists():
                    try:
                        content = model_py.read_text()
                        if "nn.Conv2d" in content or "Conv2D" in content:
                            if project_info["task"] == "unknown":
                                project_info["task"] = "image-classification"
                        if "nn.Embedding" in content or "LSTM" in content:
                            if project_info["task"] == "unknown":
                                project_info["task"] = "text-classification"
                        if "torch" in content:
                            project_info["framework"] = "pytorch"
                        elif "tensorflow" in content or "keras" in content:
                            project_info["framework"] = "tensorflow"
                        elif "sklearn" in content:
                            project_info["framework"] = "sklearn"
                    except Exception:
                        pass

            if is_noless_project:
                # Don't import duplicates
                already_imported = any(
                    entry.get("output_dir") == project_info["output_dir"]
                    for entry in self.stats["project_history"]
                )

                if not already_imported:
                    # Get modification time as timestamp
                    try:
                        mod_time = item.stat().st_mtime
                        from datetime import datetime
                        timestamp = datetime.fromtimestamp(mod_time).isoformat()
                    except Exception:
                        timestamp = datetime.now().isoformat()

                    # Record this project
                    self.stats["total_projects_built"] += 1

                    # Track by task
                    task = project_info["task"]
                    if task not in self.stats["projects_by_task"]:
                        self.stats["projects_by_task"][task] = 0
                    self.stats["projects_by_task"][task] += 1

                    # Track by framework
                    framework = project_info["framework"]
                    if framework not in self.stats["projects_by_framework"]:
                        self.stats["projects_by_framework"][framework] = 0
                    self.stats["projects_by_framework"][framework] += 1

                    # Add to history
                    history_entry = {
                        "timestamp": timestamp,
                        "task": task,
                        "framework": framework,
                        "output_dir": project_info["output_dir"],
                        "llm_model": project_info["llm_model"],
                        "dataset": project_info["dataset"],
                        "success": True,
                        "imported": True  # Mark as imported
                    }
                    self.stats["project_history"].append(history_entry)

                    console.print(f"  [green]+[/green] Imported: {item.name} ({task}/{framework})")
                    imported_count += 1

        # Keep only last 50 in history
        if len(self.stats["project_history"]) > 50:
            self.stats["project_history"] = self.stats["project_history"][-50:]

        self._save_stats()

        if imported_count > 0:
            console.print(f"\n[bold green]Imported {imported_count} existing projects![/bold green]")
        else:
            console.print(f"\n[yellow]No new projects found to import.[/yellow]")

        return imported_count


# Global instance for easy access
_stats_instance = None


def get_project_stats() -> ProjectStats:
    """Get the global ProjectStats instance."""
    global _stats_instance
    if _stats_instance is None:
        _stats_instance = ProjectStats()
    return _stats_instance


def record_build(task: str, framework: str, output_dir: str, llm_model: str = None, dataset: str = None) -> int:
    """Convenience function to record a project build."""
    stats = get_project_stats()
    return stats.record_project_build(task, framework, output_dir, llm_model, dataset)


def show_build_count() -> None:
    """Convenience function to show build count."""
    stats = get_project_stats()
    stats.show_build_counter()
