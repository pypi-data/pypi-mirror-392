"""Enhanced Interactive CLI with Multi-Agent System"""

import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
import questionary
from questionary import Style

from noless.art import ASCII_BANNER, AGENT_ICONS
from noless.agents import MultiAgentSystem
from noless.search import DatasetSearcher
from noless.openml_search import OpenMLSearcher
from noless.generator import ModelGenerator
from noless.templates import TemplateManager

console = Console()

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:#673ab7 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#2196f3 bold'),
    ('pointer', 'fg:#673ab7 bold'),
    ('highlighted', 'fg:#673ab7 bold'),
    ('selected', 'fg:#2196f3'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])


def print_banner():
    """Print ASCII banner"""
    console.print(ASCII_BANNER, style="bold cyan")


@click.group()
@click.version_option(version="0.1.0")
def main():
    """NoLess - Multi-Agent AI Model Builder
    
    Build AI models with intelligent agents working together!
    """
    pass


@main.command()
@click.option("--query", "-q", help="Search query for datasets")
@click.option("--source", "-s", 
              type=click.Choice(["all", "huggingface", "kaggle", "uci", "openml"]), 
              default="all",
              help="Dataset source to search")
@click.option("--limit", "-l", default=10, help="Maximum number of results")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
def search(query, source, limit, interactive):
    """Search for datasets across multiple sources"""
    print_banner()
    
    if interactive or not query:
        query = questionary.text(
            "What type of dataset are you looking for?",
            style=custom_style
        ).ask()
        
        if not query:
            console.print("[yellow]Search cancelled[/yellow]")
            return
        
        source = questionary.select(
            "Which source would you like to search?",
            choices=["all", "openml", "huggingface", "kaggle", "uci"],
            style=custom_style
        ).ask()
        
        limit = int(questionary.text(
            "How many results?",
            default="10",
            style=custom_style
        ).ask())
    
    console.print(Panel.fit(
        f"[bold cyan]🔍 Searching for: {query}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Initialize multi-agent system
    mas = MultiAgentSystem()
    
    # Execute search with agents
    task = {
        "action": "search",
        "query": query,
        "source": source,
        "limit": limit,
        "needs_dataset": True
    }
    
    results = asyncio.run(mas.dataset_agent.process(task))
    datasets = results.get("datasets", [])
    
    if not datasets:
        console.print("[yellow]No datasets found.[/yellow]")
        return
    
    # Display results
    table = Table(title=f"📊 Found {len(datasets)} Datasets", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=4)
    table.add_column("Name", style="green")
    table.add_column("Source", style="yellow")
    table.add_column("Type", style="blue")
    table.add_column("Size", style="magenta")
    
    for idx, result in enumerate(datasets[:limit], 1):
        table.add_row(
            str(idx),
            result.get("name", "N/A"),
            result.get("source", "N/A"),
            result.get("type", "N/A"),
            str(result.get("size", "N/A"))
        )
    
    console.print(table)
    
    # Interactive follow-up
    if interactive:
        if questionary.confirm("Would you like to download a dataset?", style=custom_style).ask():
            dataset_idx = questionary.text(
                "Enter dataset number:",
                style=custom_style
            ).ask()
            
            try:
                idx = int(dataset_idx) - 1
                if 0 <= idx < len(datasets):
                    selected = datasets[idx]
                    console.print(f"\n[green]Selected: {selected['name']}[/green]")
                    
                    output_dir = questionary.text(
                        "Output directory:",
                        default="./datasets",
                        style=custom_style
                    ).ask()
                    
                    console.print(f"[cyan]Downloading to {output_dir}...[/cyan]")
                    # Download logic here
            except ValueError:
                console.print("[red]Invalid selection[/red]")


@main.command()
@click.option("--interactive", "-i", is_flag=True, default=True, help="Interactive mode")
@click.option("--task", "-t", help="Type of ML task")
@click.option("--framework", "-f", help="ML framework")
@click.option("--dataset", "-d", help="Dataset name or path")
@click.option("--output", "-o", default="./model_project", help="Output directory")
def create(interactive, task, framework, dataset, output):
    """Create a new AI model project with multi-agent assistance"""
    print_banner()
    
    console.print(Panel.fit(
        "[bold green]🤖 Multi-Agent Model Builder[/bold green]\n"
        "Our intelligent agents will help you build your model!",
        border_style="green"
    ))
    
    # Interactive mode
    if interactive:
        console.print("\n[bold cyan]Let's build your AI model together![/bold cyan]\n")
        
        # Task selection
        if not task:
            task = questionary.select(
                "What type of model do you want to build?",
                choices=[
                    "image-classification",
                    "text-classification",
                    "object-detection",
                    "sentiment-analysis",
                    "regression",
                    "clustering",
                    "time-series",
                    "nlp"
                ],
                style=custom_style
            ).ask()
        
        # Framework selection
        if not framework:
            framework = questionary.select(
                "Which framework would you like to use?",
                choices=["pytorch", "tensorflow", "sklearn"],
                style=custom_style
            ).ask()
        
        # Dataset
        if not dataset:
            has_dataset = questionary.confirm(
                "Do you have a dataset ready?",
                style=custom_style
            ).ask()
            
            if has_dataset:
                dataset = questionary.text(
                    "Enter dataset path:",
                    style=custom_style
                ).ask()
            else:
                should_search = questionary.confirm(
                    "Would you like to search for datasets?",
                    style=custom_style,
                    default=True
                ).ask()
                
                if should_search:
                    console.print("[cyan]Starting dataset search...[/cyan]")
                    # Trigger search
        
        # Output directory
        custom_output = questionary.confirm(
            f"Save project to '{output}'?",
            style=custom_style,
            default=True
        ).ask()
        
        if not custom_output:
            output = questionary.text(
                "Enter output directory:",
                default="./model_project",
                style=custom_style
            ).ask()
    
    # Initialize multi-agent system
    console.print("\n")
    mas = MultiAgentSystem()
    
    # Create task for agents
    agent_task = {
        "action": "create_project",
        "task": task,
        "framework": framework,
        "dataset": dataset,
        "output": output,
        "requirements": {
            "task": task,
            "framework": framework,
            "interactive": True
        },
        "specifications": {
            "task": task,
            "framework": framework,
            "output_dir": output
        }
    }
    
    # Execute with agents
    results = asyncio.run(mas.execute_task(agent_task))
    
    # Generate the actual project
    console.print("\n[bold cyan]📝 Generating project files...[/bold cyan]\n")
    
    generator = ModelGenerator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task_id = progress.add_task("[cyan]Creating project structure...", total=100)
        
        project = generator.create_project(
            task=task,
            framework=framework,
            dataset=dataset,
            output_dir=output
        )
        
        progress.update(task_id, completed=100)
    
    # Display results
    console.print("\n")
    console.print(Panel.fit(
        f"[bold green]✅ Project Created Successfully![/bold green]\n\n"
        f"📁 Location: [cyan]{output}[/cyan]\n"
        f"📝 Files generated: [cyan]{len(project['files'])}[/cyan]\n\n"
        f"[bold]Generated Files:[/bold]\n"
        f"  • train.py - Training script\n"
        f"  • model.py - Model architecture\n"
        f"  • config.yaml - Configuration\n"
        f"  • utils.py - Utility functions\n"
        f"  • requirements.txt - Dependencies",
        border_style="green"
    ))
    
    console.print("\n[bold cyan]🚀 Next Steps:[/bold cyan]")
    console.print(f"1. cd {output}")
    console.print("2. pip install -r requirements.txt")
    console.print("3. python train.py")
    
    if interactive:
        start_training = questionary.confirm(
            "\nWould you like to start training now?",
            style=custom_style,
            default=False
        ).ask()
        
        if start_training:
            console.print("\n[bold green]🎓 Starting training with AI agents...[/bold green]\n")
            training_task = {"epochs": 5}
            asyncio.run(mas.training_agent.process(training_task))


@main.command()
def interactive():
    """Start interactive mode - guided model building"""
    print_banner()
    
    console.print(Panel.fit(
        "[bold magenta]🎯 Interactive Model Builder[/bold magenta]\n"
        "Let's build your AI model step by step!",
        border_style="magenta"
    ))
    
    # Welcome
    console.print("\n[bold]Welcome to NoLess Interactive Mode![/bold]\n")
    console.print("I'll guide you through building your AI model with intelligent agents.\n")
    
    # Main menu
    action = questionary.select(
        "What would you like to do?",
        choices=[
            "🔍 Search for datasets",
            "🤖 Build a new model",
            "📋 Browse templates",
            "💻 Generate training script",
            "🎓 Train existing model",
            "⚡ Optimize model",
            "❌ Exit"
        ],
        style=custom_style
    ).ask()
    
    if "Search" in action:
        # Trigger search in interactive mode
        from click.testing import CliRunner
        runner = CliRunner()
        runner.invoke(search, ['--interactive'])
    
    elif "Build" in action:
        # Trigger create in interactive mode
        from click.testing import CliRunner
        runner = CliRunner()
        runner.invoke(create, ['--interactive'])
    
    elif "Browse" in action:
        # Show templates
        from click.testing import CliRunner
        runner = CliRunner()
        runner.invoke(templates, [])
    
    elif "Generate" in action:
        model_type = questionary.text(
            "Model type (e.g., cnn, rnn, transformer):",
            style=custom_style
        ).ask()
        
        task_type = questionary.select(
            "Task type:",
            choices=["classification", "regression", "detection", "generation"],
            style=custom_style
        ).ask()
        
        console.print(f"\n[green]Generating {model_type} for {task_type}...[/green]")
    
    elif "Train" in action:
        console.print("\n[bold green]🎓 Training Agent Activated[/bold green]\n")
        mas = MultiAgentSystem()
        asyncio.run(mas.training_agent.process({"epochs": 10}))
    
    elif "Optimize" in action:
        console.print("\n[bold yellow]⚡ Optimization Agent Activated[/bold yellow]\n")
        mas = MultiAgentSystem()
        result = asyncio.run(mas.optimization_agent.process({}))
        
        console.print("\n[bold]Optimization Suggestions:[/bold]")
        for key, value in result.items():
            console.print(f"  • {key}: [cyan]{value}[/cyan]")


@main.command()
@click.option("--task", "-t", help="Filter templates by task")
def templates(task):
    """List available model templates"""
    print_banner()
    
    console.print(Panel.fit(
        "[bold magenta]📋 Available Model Templates[/bold magenta]",
        border_style="magenta"
    ))
    
    manager = TemplateManager()
    templates_list = manager.list_templates(task_filter=task)
    
    table = Table(show_header=True, header_style="bold magenta", title="Model Templates")
    table.add_column("Template", style="cyan", width=30)
    table.add_column("Task", style="green", width=20)
    table.add_column("Framework", style="yellow", width=12)
    table.add_column("Description", style="white")
    
    for tmpl in templates_list:
        table.add_row(
            tmpl["name"],
            tmpl["task"],
            tmpl["framework"],
            tmpl["description"]
        )
    
    console.print("\n")
    console.print(table)
    console.print("\n")


@main.command()
def agents():
    """Show multi-agent system status"""
    print_banner()
    
    console.print(Panel.fit(
        "[bold cyan]🤖 Multi-Agent System[/bold cyan]",
        border_style="cyan"
    ))
    
    # Show agent information
    table = Table(title="Available Agents", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan")
    table.add_column("Icon", style="yellow", justify="center")
    table.add_column("Capability", style="green")
    table.add_column("Status", style="blue")
    
    agents_info = [
        ("Orchestrator", AGENT_ICONS["orchestrator"], "Coordinates all agents", "🟢 Active"),
        ("Dataset Agent", AGENT_ICONS["dataset_agent"], "Searches & prepares datasets", "🟢 Active"),
        ("Model Agent", AGENT_ICONS["model_agent"], "Designs architectures", "🟢 Active"),
        ("Code Agent", AGENT_ICONS["code_agent"], "Generates code in real-time", "🟢 Active"),
        ("Training Agent", AGENT_ICONS["training_agent"], "Manages training process", "🟢 Active"),
        ("Optimization Agent", AGENT_ICONS["optimization_agent"], "Optimizes performance", "🟢 Active"),
    ]
    
    for name, icon, capability, status in agents_info:
        table.add_row(name, icon, capability, status)
    
    console.print("\n")
    console.print(table)
    console.print("\n")
    
    console.print("[bold]How it works:[/bold]")
    console.print("1. 🎯 Orchestrator analyzes your request")
    console.print("2. 📊 Dataset Agent finds the best datasets")
    console.print("3. 🤖 Model Agent designs the architecture")
    console.print("4. 💻 Code Agent writes the code")
    console.print("5. 🎓 Training Agent handles training")
    console.print("6. ⚡ Optimization Agent improves performance\n")


@main.command()
@click.argument("dataset_id")
@click.option("--output", "-o", default="./datasets", help="Output directory")
def download(dataset_id, output):
    """Download a dataset by ID"""
    print_banner()
    
    console.print(Panel.fit(
        f"[bold cyan]📥 Downloading: {dataset_id}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Determine source
    if dataset_id.startswith("openml:"):
        openml_id = int(dataset_id.split(":")[1])
        searcher = OpenMLSearcher()
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading from OpenML...", total=100)
            result = searcher.download_dataset(openml_id, output)
            progress.update(task, completed=100)
        
        if result:
            console.print(f"\n[green]✅ Dataset downloaded to: {output}[/green]")
        else:
            console.print("[red]❌ Failed to download dataset[/red]")
    else:
        # Use regular searcher
        searcher = DatasetSearcher()
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading...", total=100)
            result = searcher.download_dataset(dataset_id, output)
            progress.update(task, completed=100)
        
        if result:
            console.print(f"\n[green]✅ Dataset downloaded to: {output}[/green]")
        else:
            console.print("[red]❌ Failed to download dataset[/red]")


if __name__ == "__main__":
    main()
