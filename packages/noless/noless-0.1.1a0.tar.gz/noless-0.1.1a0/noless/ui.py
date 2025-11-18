"""Enhanced UI components for NoLess CLI"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.box import ROUNDED, DOUBLE, HEAVY, MINIMAL
from rich.tree import Tree
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.columns import Columns
from rich import box
import time
from datetime import datetime

console = Console()


def create_welcome_screen():
    """Create a beautiful welcome screen"""
    from noless.art import ASCII_BANNER
    
    console.clear()
    console.print(ASCII_BANNER, style="bold cyan", justify="center")
    console.print()
    
    welcome_text = Panel(
        "[bold white]Welcome to NoLess - Your AI Model Building Assistant![/bold white]\n\n"
        "🤖 [cyan]Multi-Agent System[/cyan] - 6 intelligent agents working together\n"
        "🔍 [yellow]Dataset Search[/yellow] - 20,000+ datasets from 4 sources\n"
        "💻 [green]Code Generation[/green] - Real-time production-ready code\n"
        "⚡ [magenta]Interactive Mode[/magenta] - Guided model building experience\n\n"
        "[dim]Let's build something amazing together![/dim]",
        title="✨ Features",
        border_style="cyan",
        box=DOUBLE,
        padding=(1, 2)
    )
    
    console.print(welcome_text, justify="center")
    console.print()


def create_progress_bar(description):
    """Create a beautiful progress bar"""
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        TaskProgressColumn(),
        console=console
    )


def show_success_message(title, message):
    """Show a success message"""
    console.print()
    console.print(Panel(
        f"[bold green]✅ {message}[/bold green]",
        title=f"[green]{title}[/green]",
        border_style="green",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def show_error_message(title, message):
    """Show an error message"""
    console.print()
    console.print(Panel(
        f"[bold red]❌ {message}[/bold red]",
        title=f"[red]{title}[/red]",
        border_style="red",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def show_info_message(title, message):
    """Show an info message"""
    console.print()
    console.print(Panel(
        f"[bold cyan]ℹ️  {message}[/bold cyan]",
        title=f"[cyan]{title}[/cyan]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def create_dataset_table(datasets):
    """Create a beautiful dataset results table"""
    table = Table(
        title="📊 Dataset Search Results",
        show_header=True,
        header_style="bold magenta",
        box=HEAVY,
        border_style="cyan",
        title_style="bold cyan"
    )
    
    table.add_column("ID", style="cyan", width=4, justify="center")
    table.add_column("Name", style="green", width=35)
    table.add_column("Source", style="yellow", width=12, justify="center")
    table.add_column("Type", style="blue", width=12, justify="center")
    table.add_column("Size", style="magenta", width=15, justify="right")
    
    for idx, dataset in enumerate(datasets, 1):
        table.add_row(
            str(idx),
            dataset.get("name", "N/A")[:35],
            dataset.get("source", "N/A"),
            dataset.get("type", "N/A"),
            str(dataset.get("size", "N/A"))
        )
    
    return table


def create_agent_status_table():
    """Create agent status display"""
    from noless.art import AGENT_ICONS
    
    table = Table(
        title="🤖 Multi-Agent System Status",
        show_header=True,
        header_style="bold magenta",
        box=HEAVY,
        border_style="cyan",
        title_style="bold cyan"
    )
    
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Icon", style="yellow", justify="center", width=6)
    table.add_column("Status", style="green", justify="center", width=12)
    table.add_column("Capability", style="blue", width=40)
    
    agents_info = [
        ("Orchestrator", AGENT_ICONS["orchestrator"], "🟢 Active", "Plans and coordinates all operations"),
        ("Dataset Agent", AGENT_ICONS["dataset_agent"], "🟢 Active", "Searches 4 dataset repositories"),
        ("Model Agent", AGENT_ICONS["model_agent"], "🟢 Active", "Designs optimal architectures"),
        ("Code Agent", AGENT_ICONS["code_agent"], "🟢 Active", "Generates production code"),
        ("Training Agent", AGENT_ICONS["training_agent"], "🟢 Active", "Manages training pipelines"),
        ("Optimization Agent", AGENT_ICONS["optimization_agent"], "🟢 Active", "Tunes hyperparameters"),
    ]
    
    for name, icon, status, capability in agents_info:
        table.add_row(name, icon, status, capability)
    
    return table


def show_agent_working(agent_name, task_description):
    """Show agent working animation"""
    from noless.art import AGENT_ICONS, WORKING_ANIMATION
    
    icon = AGENT_ICONS.get(agent_name.lower().replace(" ", "_"), "🤖")
    
    with console.status(f"[cyan]{icon} {agent_name}:[/cyan] {task_description}", spinner="dots") as status:
        time.sleep(1.5)


def create_template_table(templates):
    """Create beautiful template display"""
    table = Table(
        title="📋 Available Model Templates",
        show_header=True,
        header_style="bold magenta",
        box=HEAVY,
        border_style="cyan",
        title_style="bold cyan"
    )
    
    table.add_column("Template", style="cyan", width=30)
    table.add_column("Task", style="green", width=20)
    table.add_column("Framework", style="yellow", width=12, justify="center")
    table.add_column("Description", style="white", width=45)
    
    for tmpl in templates:
        table.add_row(
            tmpl["name"],
            tmpl["task"],
            tmpl["framework"],
            tmpl["description"]
        )
    
    return table


def show_project_summary(output_dir, files):
    """Show beautiful project creation summary"""
    console.print()
    
    # Main success panel
    summary = Panel(
        f"[bold white]Project Location:[/bold white] [cyan]{output_dir}[/cyan]\n"
        f"[bold white]Files Created:[/bold white] [green]{len(files)}[/green]\n\n"
        "[bold]Generated Files:[/bold]\n"
        "  📝 [cyan]train.py[/cyan] - Complete training pipeline\n"
        "  🏗️  [cyan]model.py[/cyan] - Model architecture definition\n"
        "  ⚙️  [cyan]config.yaml[/cyan] - Hyperparameters & configuration\n"
        "  🛠️  [cyan]utils.py[/cyan] - Helper utilities\n"
        "  📦 [cyan]requirements.txt[/cyan] - Python dependencies\n"
        "  📚 [cyan]README.md[/cyan] - Documentation\n\n"
        "[bold green]✨ Your project is ready![/bold green]",
        title="[bold green]🎉 Success![/bold green]",
        border_style="green",
        box=DOUBLE,
        padding=(1, 2)
    )
    
    console.print(summary)
    
    # Next steps
    steps = Panel(
        "[bold]1.[/bold] [cyan]Review configuration[/cyan]\n"
        f"   Edit {output_dir}/config.yaml to customize settings\n\n"
        "[bold]2.[/bold] [cyan]Install dependencies[/cyan]\n"
        f"   cd {output_dir} && pip install -r requirements.txt\n\n"
        "[bold]3.[/bold] [cyan]Start training[/cyan]\n"
        "   python train.py\n\n"
        "[dim]💡 Tip: The code is fully customizable - edit as needed![/dim]",
        title="[bold cyan]🚀 Next Steps[/bold cyan]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    )
    
    console.print(steps)
    console.print()


def show_separator():
    """Show a visual separator"""
    console.print("\n" + "─" * console.width + "\n")


def pause_with_message(message="Press Enter to continue..."):
    """Pause with a styled message"""
    console.print(f"\n[dim italic]{message}[/dim italic]")
    try:
        input()
    except EOFError:
        # In non-interactive/piped runs stdin may be closed; just continue silently
        pass
    except KeyboardInterrupt:
        console.print("[dim italic]Input interrupted – continuing...[/dim italic]")


def create_live_agent_dashboard(agents_data):
    """Create a live dashboard showing all agent activities in real-time"""
    layout = Layout()

    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )

    # Header
    header_text = Text("🤖 Multi-Agent System - Live Dashboard", style="bold cyan", justify="center")
    layout["header"].update(Panel(header_text, border_style="cyan"))

    # Body with agent status
    table = Table(box=HEAVY, border_style="cyan", expand=True)
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Status", justify="center", width=12)
    table.add_column("Current Task", style="white", width=50)
    table.add_column("Progress", justify="center", width=15)

    for agent in agents_data:
        status_color = {
            "idle": "dim",
            "thinking": "yellow",
            "working": "cyan",
            "completed": "green",
            "error": "red"
        }.get(agent.get("status", "idle"), "white")

        table.add_row(
            agent["name"],
            f"[{status_color}]{agent['status_icon']} {agent['status'].upper()}[/{status_color}]",
            agent.get("task", "Idle"),
            agent.get("progress", "—")
        )

    layout["body"].update(Panel(table, title="Agent Activities", border_style="cyan"))

    # Footer with timestamp
    footer_text = Text(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}", style="dim", justify="center")
    layout["footer"].update(Panel(footer_text, border_style="cyan"))

    return layout


def create_enhanced_progress_bar(description, total=100):
    """Create an enhanced progress bar with time tracking"""
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="cyan", finished_style="green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console
    )


def show_agent_communication(from_agent, to_agent, message):
    """Display agent-to-agent communication"""
    from noless.art import AGENT_ICONS

    from_icon = AGENT_ICONS.get(from_agent.lower().replace(" ", "_"), "🤖")
    to_icon = AGENT_ICONS.get(to_agent.lower().replace(" ", "_"), "🤖")

    comm_text = f"[cyan]{from_icon} {from_agent}[/cyan] → [yellow]{to_icon} {to_agent}[/yellow]\n[dim]{message}[/dim]"

    console.print(Panel(
        comm_text,
        title="[bold]📡 Agent Communication[/bold]",
        border_style="blue",
        box=ROUNDED,
        padding=(0, 2)
    ))


def show_thinking_process(agent_name, thoughts):
    """Show AI agent's thinking process"""
    from noless.art import AGENT_ICONS, THINKING_BANNER

    icon = AGENT_ICONS.get(agent_name.lower().replace(" ", "_"), "🤖")

    thinking_panel = Panel(
        f"[bold cyan]{icon} {agent_name}[/bold cyan]\n\n"
        f"[yellow]💭 Thinking Process:[/yellow]\n{thoughts}\n\n"
        "[dim]Using LLM-powered reasoning...[/dim]",
        title="[bold]🧠 AI Reasoning[/bold]",
        border_style="yellow",
        box=DOUBLE,
        padding=(1, 2)
    )

    console.print(thinking_panel)


def show_code_preview(code, language="python", title="Generated Code"):
    """Display syntax-highlighted code preview"""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True, word_wrap=True)

    console.print(Panel(
        syntax,
        title=f"[bold cyan]💻 {title}[/bold cyan]",
        border_style="cyan",
        box=HEAVY,
        padding=(1, 2)
    ))


def show_project_tree(project_path, files):
    """Show project structure as a tree"""
    tree = Tree(
        f"[bold cyan]📁 {project_path}[/bold cyan]",
        guide_style="cyan"
    )

    for file in files:
        if file.endswith(".py"):
            tree.add(f"[green]🐍 {file}[/green]")
        elif file.endswith(".yaml") or file.endswith(".yml"):
            tree.add(f"[yellow]⚙️  {file}[/yellow]")
        elif file.endswith(".txt"):
            tree.add(f"[blue]📝 {file}[/blue]")
        elif file.endswith(".md"):
            tree.add(f"[magenta]📚 {file}[/magenta]")
        else:
            tree.add(f"[white]📄 {file}[/white]")

    console.print(Panel(
        tree,
        title="[bold]📦 Project Structure[/bold]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    ))


def show_feature_highlights():
    """Display feature highlights from art.py"""
    from noless.art import FEATURES_ART
    console.print(FEATURES_ART, style="bold")


def show_quick_start_guide():
    """Display quick start guide"""
    from noless.art import QUICK_START
    console.print(QUICK_START, style="bold cyan")


def show_agent_showcase():
    """Display agent showcase"""
    from noless.art import AGENT_SHOWCASE
    console.print(AGENT_SHOWCASE, style="bold cyan")


def show_performance_metrics(metrics):
    """Display performance metrics in a nice format"""
    table = Table(
        title="📊 Performance Metrics",
        show_header=True,
        header_style="bold magenta",
        box=HEAVY,
        border_style="green"
    )

    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Value", style="green", justify="right", width=20)
    table.add_column("Status", justify="center", width=15)

    for metric_name, metric_value in metrics.items():
        # Determine status based on metric type
        if isinstance(metric_value, (int, float)):
            if metric_value > 0.8:
                status = "[green]✅ Excellent[/green]"
            elif metric_value > 0.6:
                status = "[yellow]⚠️  Good[/yellow]"
            else:
                status = "[red]❌ Needs Work[/red]"
        else:
            status = "[cyan]ℹ️  Info[/cyan]"

        table.add_row(metric_name, str(metric_value), status)

    console.print(table)


def show_agent_collaboration_diagram():
    """Display agent collaboration workflow"""
    from noless.art import AGENT_COLLABORATION
    console.print(Panel(
        AGENT_COLLABORATION,
        title="[bold cyan]🔄 Agent Workflow[/bold cyan]",
        border_style="cyan",
        box=DOUBLE
    ))


def create_multi_column_layout(items, columns=2):
    """Create a multi-column layout for displaying items"""
    panels = []
    for item in items:
        panel = Panel(
            item["content"],
            title=item.get("title", ""),
            border_style=item.get("style", "cyan"),
            box=ROUNDED
        )
        panels.append(panel)

    console.print(Columns(panels, equal=True, expand=True))


def show_warning_message(title, message):
    """Show a warning message"""
    console.print()
    console.print(Panel(
        f"[bold yellow]⚠️  {message}[/bold yellow]",
        title=f"[yellow]{title}[/yellow]",
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def show_tips_panel(tips):
    """Display helpful tips in a panel"""
    tips_text = "\n".join([f"💡 [cyan]{tip}[/cyan]" for tip in tips])

    console.print(Panel(
        tips_text,
        title="[bold yellow]✨ Pro Tips[/bold yellow]",
        border_style="yellow",
        box=ROUNDED,
        padding=(1, 2)
    ))


def create_comparison_table(comparison_data):
    """Create a comparison table for different options"""
    table = Table(
        title="⚖️  Comparison",
        show_header=True,
        header_style="bold cyan",
        box=HEAVY,
        border_style="cyan"
    )

    # Add columns
    table.add_column("Feature", style="yellow", width=25)
    for option in comparison_data["options"]:
        table.add_column(option, justify="center", width=20)

    # Add rows
    for feature, values in comparison_data["features"].items():
        table.add_row(feature, *values)

    return table


def show_step_progress(current_step, total_steps, step_name):
    """Show current step in a multi-step process"""
    from noless.art import PROGRESS_BLOCKS

    filled = int((current_step / total_steps) * 20)
    bar = PROGRESS_BLOCKS["full"] * filled + PROGRESS_BLOCKS["empty"] * (20 - filled)

    console.print(Panel(
        f"[bold]Step {current_step} of {total_steps}[/bold]\n\n"
        f"[cyan]{bar}[/cyan] {int((current_step/total_steps)*100)}%\n\n"
        f"[yellow]Current: {step_name}[/yellow]",
        title="[bold cyan]📍 Progress[/bold cyan]",
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    ))


def show_markdown_content(markdown_text):
    """Render markdown content beautifully"""
    md = Markdown(markdown_text)
    console.print(Panel(
        md,
        border_style="cyan",
        box=ROUNDED,
        padding=(1, 2)
    ))


def animate_success():
    """Show an animated success message"""
    from noless.art import SPARKLE_ANIMATION, SUCCESS_BANNER

    # Animate sparkles
    with console.status("[bold green]Finalizing...[/bold green]", spinner="dots"):
        time.sleep(1)

    console.print(SUCCESS_BANNER, style="bold green")
    console.print("[green]" + " ✨ " * 20 + "[/green]", justify="center")


def show_live_code_generation(file_name: str, code_lines: list, delay: float = 0.01, window_size: int = 15):
    """Show code being written with a scrolling window view - FAST!"""
    from rich.live import Live
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text

    total_lines = len(code_lines)
    console.print(f"\n[bold cyan]💻 Generating {file_name}...[/bold cyan]")

    with Live(console=console, refresh_per_second=30) as live:
        for i in range(1, total_lines + 1):
            # Calculate window to show (scrolling effect)
            start_line = max(0, i - window_size)
            end_line = i

            # Get visible lines with proper line numbers
            visible_lines = code_lines[start_line:end_line]
            code_text = '\n'.join(visible_lines)

            # Create syntax highlighted display with correct starting line number
            syntax = Syntax(
                code_text,
                "python",
                theme="monokai",
                line_numbers=True,
                start_line=start_line + 1,
                word_wrap=False
            )

            # Show scroll indicator if not at top
            scroll_info = f" ↑ {start_line} lines above" if start_line > 0 else ""

            panel = Panel(
                syntax,
                title=f"[bold green]✍️  {file_name} - Line {i}/{total_lines}{scroll_info}[/bold green]",
                border_style="green",
                padding=(0, 1)
            )

            live.update(panel)
            time.sleep(delay)

    console.print(f"[bold green]✅ {file_name} complete! ({total_lines} lines)[/bold green]\n")


def show_file_being_created(file_path: str, content: str, show_preview: bool = True):
    """Show a file being created with preview - FAST"""
    console.print(f"\n[cyan]📝 Creating:[/cyan] [yellow]{file_path}[/yellow]")

    lines = content.split('\n')
    total_lines = len(lines)
    total_chars = len(content)

    # Fast writing progress - skip individual updates for speed
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Writing {total_lines} lines...", total=100)

        # Fast simulation - batch updates
        for i in range(0, 100, 10):
            progress.advance(task, 10)
            time.sleep(0.01)  # Super fast

    console.print(f"[green]✓[/green] Saved: {total_chars:,} chars, {total_lines} lines\n")


def show_download_progress(item_name: str, total_size: int = 100, source: str = ""):
    """Show download progress with details"""
    console.print(f"\n[bold cyan]⬇️  Downloading: {item_name}[/bold cyan]")
    if source:
        console.print(f"[dim]Source: {source}[/dim]\n")

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Downloading...", total=total_size)

        # Simulate download with varying speeds
        chunk_sizes = [5, 10, 15, 8, 12, 20, 10, 15, 5]
        downloaded = 0

        while downloaded < total_size:
            chunk = chunk_sizes[downloaded % len(chunk_sizes)]
            chunk = min(chunk, total_size - downloaded)
            progress.advance(task, chunk)
            downloaded += chunk
            time.sleep(0.1)

    console.print(f"[bold green]✅ Download complete![/bold green] {item_name}\n")


def show_dataset_preparation(dataset_name: str, steps: list):
    """Show dataset preparation steps"""
    console.print(f"\n[bold cyan]📊 Preparing Dataset: {dataset_name}[/bold cyan]\n")

    for i, step in enumerate(steps, 1):
        with console.status(f"[yellow]{step['icon']} {step['description']}...", spinner="dots"):
            time.sleep(step.get('duration', 1.0))
        console.print(f"[green]✓[/green] {step['description']}")

    console.print(f"\n[bold green]✅ Dataset ready![/bold green]\n")


def show_agent_thinking_live(agent_name: str, thoughts: list):
    """Show AI agent thinking process in real-time"""
    from noless.art import AGENT_ICONS, BRAIN_ANIMATION

    icon = AGENT_ICONS.get(agent_name.lower().replace(" ", "_"), "🤖")

    console.print(f"\n[bold cyan]{icon} {agent_name} is thinking...[/bold cyan]\n")

    for thought in thoughts:
        console.print(f"[yellow]💭[/yellow] {thought}")
        time.sleep(0.6)

    console.print(f"\n[bold green]✓[/bold green] {agent_name} finished thinking!\n")


def show_model_architecture_design(model_name: str, layers: list):
    """Show model architecture being designed"""
    console.print(f"\n[bold cyan]🏗️  Designing Model Architecture: {model_name}[/bold cyan]\n")

    tree = Tree(
        f"[bold green]{model_name}[/bold green]",
        guide_style="cyan"
    )

    for i, layer in enumerate(layers):
        time.sleep(0.3)
        layer_node = tree.add(f"[cyan]Layer {i+1}:[/cyan] [yellow]{layer}[/yellow]")
        console.clear()
        console.print(f"\n[bold cyan]🏗️  Designing Model Architecture: {model_name}[/bold cyan]\n")
        console.print(tree)

    console.print(f"\n[bold green]✅ Architecture design complete![/bold green]\n")


def create_live_training_dashboard(epochs: int, metrics: dict):
    """Create a live training dashboard"""
    console.print("\n[bold cyan]🎓 Training Dashboard[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
    table.add_column("Epoch", style="cyan", width=10)
    table.add_column("Loss", style="red", width=15)
    table.add_column("Accuracy", style="green", width=15)
    table.add_column("Status", style="yellow", width=20)

    for epoch in range(1, epochs + 1):
        loss = metrics.get('loss', 1.0) / epoch
        acc = metrics.get('accuracy', 0.5) + (epoch * 0.05)
        status = "✓ Complete" if epoch == epochs else "→ Training..."

        table.add_row(
            f"Epoch {epoch}",
            f"{loss:.4f}",
            f"{acc:.2%}",
            status
        )

    console.print(table)
    console.print("\n")
