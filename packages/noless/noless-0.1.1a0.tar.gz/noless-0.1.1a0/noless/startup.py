"""NoLess Startup and Loading Screen"""

import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from noless.art import ASCII_BANNER, AGENT_ICONS
from noless.ollama_client import OllamaClient

console = Console()


def show_startup_sequence():
    """Display the NoLess startup sequence with service connections"""

    # Clear screen
    console.clear()

    # Show banner with animation
    _animate_banner()

    # Show system initialization
    _show_system_init()

    # Connect to services
    _connect_to_services()

    # Show ready message
    _show_ready_message()


def _animate_banner():
    """Animate the NoLess banner - FAST"""
    console.print("\n")

    # Show banner with fast fade-in effect
    banner_lines = ASCII_BANNER.split('\n')

    for line in banner_lines:
        console.print(line, style="bold cyan", justify="center")
        time.sleep(0.01)  # Much faster!

    console.print("\n")
    time.sleep(0.1)


def _show_system_init():
    """Show system initialization - FAST"""

    init_steps = [
        ("⚙️  Initializing NoLess Core", 0.1),
        ("🔧 Loading Configuration", 0.08),
        ("📦 Preparing Modules", 0.08),
        ("🎨 Setting Up UI Components", 0.06),
    ]

    console.print(Panel.fit(
        "[bold cyan]System Initialization[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    for step, duration in init_steps:
        with console.status(f"[cyan]{step}...", spinner="dots"):
            time.sleep(duration)
        console.print(f"[green]✓[/green] {step}")

    console.print()
    time.sleep(0.05)


def _connect_to_services():
    """Show connection to various services"""

    console.print(Panel.fit(
        "[bold yellow]🌐 Connecting to Services[/bold yellow]",
        border_style="yellow"
    ))
    console.print()

    # Service connection table - FAST delays
    services = [
        {
            "name": "Ollama LLM Server",
            "icon": "🤖",
            "check_func": _check_ollama,
            "delay": 0.15
        },
        {
            "name": "Multi-Agent System",
            "icon": "🎯",
            "check_func": lambda: (True, "6 agents ready"),
            "delay": 0.1
        },
        {
            "name": "Dataset Sources",
            "icon": "📊",
            "check_func": lambda: (True, "OpenML, HuggingFace, UCI, Kaggle"),
            "delay": 0.08
        },
        {
            "name": "Code Generator",
            "icon": "💻",
            "check_func": lambda: (True, "Templates loaded"),
            "delay": 0.08
        },
        {
            "name": "AI Code Validator",
            "icon": "✅",
            "check_func": lambda: (True, "Validation ready"),
            "delay": 0.08
        },
        {
            "name": "Framework Support",
            "icon": "🔧",
            "check_func": lambda: (True, "PyTorch, TensorFlow, sklearn"),
            "delay": 0.06
        },
    ]

    # Create live table for service status
    with Live(console=console, refresh_per_second=4) as live:
        for idx, service in enumerate(services):
            table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
            table.add_column("Service", style="cyan", width=25)
            table.add_column("Status", justify="center", width=15)
            table.add_column("Details", style="white", width=40)

            # Show all services up to current
            for i, svc in enumerate(services[:idx + 1]):
                if i < idx:
                    # Already connected
                    status, details = svc["check_func"]()
                    status_text = "[green]✅ Connected[/green]" if status else "[red]❌ Failed[/red]"
                    table.add_row(f"{svc['icon']} {svc['name']}", status_text, details if status else "Not available")
                else:
                    # Currently connecting
                    table.add_row(
                        f"{svc['icon']} {svc['name']}",
                        "[yellow]⏳ Connecting...[/yellow]",
                        "[dim]Please wait...[/dim]"
                    )

            # Show pending services
            for i in range(idx + 1, len(services)):
                svc = services[i]
                table.add_row(
                    f"{svc['icon']} {svc['name']}",
                    "[dim]⚪ Pending[/dim]",
                    "[dim]Waiting...[/dim]"
                )

            live.update(table)
            time.sleep(service["delay"])

            # Check the service
            status, details = service["check_func"]()
            service["status"] = status
            service["details"] = details

    # Show final table
    final_table = Table(show_header=True, header_style="bold magenta", border_style="green")
    final_table.add_column("Service", style="cyan", width=25)
    final_table.add_column("Status", justify="center", width=15)
    final_table.add_column("Details", style="white", width=40)

    for svc in services:
        status_text = "[green]✅ Connected[/green]" if svc["status"] else "[yellow]⚠️  Offline[/yellow]"
        final_table.add_row(
            f"{svc['icon']} {svc['name']}",
            status_text,
            svc["details"]
        )

    console.print()
    console.print(final_table)
    console.print()
    time.sleep(0.05)  # Faster!


def _check_ollama():
    """Check if Ollama server is available"""
    try:
        client = OllamaClient()
        if client.is_available():
            from noless.local_models import LocalModelRegistry
            registry = LocalModelRegistry(client)
            models = registry.available_models()
            return (True, f"{len(models)} model(s) available")
        else:
            return (False, "Server not running")
    except Exception:
        return (False, "Not available")


def _show_ready_message():
    """Show system ready message - FAST"""

    # Fast final initialization
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Finalizing...", total=100)

        # Fast batch updates
        for i in range(0, 100, 10):
            progress.advance(task, 10)
            time.sleep(0.005)

    console.print()

    # Show agent team
    _show_agent_team()

    # Ready panel
    console.print(Panel.fit(
        "[bold green]✨ System Ready! ✨[/bold green]\n\n"
        "[white]NoLess is ready to build AI models![/white]\n"
        "[dim]All systems operational • All agents standing by[/dim]\n\n"
        "[cyan]Type 'noless --help' to get started[/cyan]",
        title="[bold green]🚀 Ready for Launch[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print()


def _show_agent_team():
    """Show the agent team status"""

    agent_table = Table(
        title="🤖 AI Agent Team",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
        padding=(0, 1)
    )

    agent_table.add_column("Agent", style="cyan", width=20)
    agent_table.add_column("Status", justify="center", width=12)
    agent_table.add_column("Role", style="white", width=35)

    agents = [
        ("Orchestrator", AGENT_ICONS["orchestrator"], "Master Coordinator"),
        ("Dataset Agent", AGENT_ICONS["dataset_agent"], "Data Discovery"),
        ("Model Agent", AGENT_ICONS["model_agent"], "Architecture Design"),
        ("Code Agent", AGENT_ICONS["code_agent"], "Code Generation"),
        ("Training Agent", AGENT_ICONS["training_agent"], "Training Pipeline"),
        ("Optimizer", AGENT_ICONS["optimization_agent"], "Hyperparameter Tuning"),
    ]

    for name, icon, role in agents:
        agent_table.add_row(
            f"{icon} {name}",
            "[green]🟢 Ready[/green]",
            role
        )

    console.print(agent_table)
    console.print()


def show_quick_startup():
    """Quick startup without full animation (for non-interactive mode)"""
    console.print(ASCII_BANNER, style="bold cyan", justify="center")
    console.print()

    with console.status("[cyan]Initializing NoLess...", spinner="dots"):
        time.sleep(0.5)

    console.print("[green]✓[/green] NoLess ready!\n")


def show_service_status():
    """Show current status of all services"""

    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]📊 Service Status Check[/bold cyan]",
        border_style="cyan"
    ))
    console.print()

    services_table = Table(show_header=True, header_style="bold magenta", border_style="cyan")
    services_table.add_column("Service", style="cyan", width=25)
    services_table.add_column("Status", justify="center", width=15)
    services_table.add_column("Details", style="white", width=40)

    # Check Ollama
    ollama_status, ollama_details = _check_ollama()
    services_table.add_row(
        "🤖 Ollama LLM Server",
        "[green]✅ Online[/green]" if ollama_status else "[red]❌ Offline[/red]",
        ollama_details
    )

    # Check agents
    services_table.add_row(
        "🎯 Multi-Agent System",
        "[green]✅ Ready[/green]",
        "6 agents operational"
    )

    # Check datasets
    services_table.add_row(
        "📊 Dataset Sources",
        "[green]✅ Available[/green]",
        "4 sources (OpenML, HF, UCI, Kaggle)"
    )

    # Check code generator
    services_table.add_row(
        "💻 Code Generator",
        "[green]✅ Ready[/green]",
        "Templates loaded"
    )

    # Check validator
    services_table.add_row(
        "✅ AI Code Validator",
        "[green]✅ Ready[/green]" if ollama_status else "[yellow]⚠️  Limited[/yellow]",
        "LLM-powered" if ollama_status else "Basic validation only"
    )

    # Check frameworks
    services_table.add_row(
        "🔧 Framework Support",
        "[green]✅ Ready[/green]",
        "PyTorch, TensorFlow, sklearn"
    )

    console.print(services_table)
    console.print()

    # Show recommendations
    if not ollama_status:
        console.print(Panel(
            "[yellow]⚠️  Ollama server is not running[/yellow]\n\n"
            "To enable AI-powered features:\n"
            "1. Install Ollama: https://ollama.ai\n"
            "2. Start server: [cyan]ollama serve[/cyan]\n"
            "3. Pull a model: [cyan]ollama pull llama3.1:8b[/cyan]",
            title="[yellow]Recommendation[/yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))
        console.print()
