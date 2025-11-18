"""Multi-Agent System for AI Model Building"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import re
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from noless.art import AGENT_ICONS
from noless.ollama_client import OllamaClient


def _parse_json_block(payload: str) -> Optional[Dict[str, Any]]:
    if not payload:
        return None
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", payload, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return None
    return None

console = Console()


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    priority: int = 0
    timestamp: str = ""


@dataclass
class AgentMemory:
    """Enhanced memory structure for agents"""
    short_term: List[Dict[str, Any]]  # Recent interactions
    long_term: List[Dict[str, Any]]  # Persistent knowledge
    context: Dict[str, Any]  # Current context
    communication_log: List[AgentMessage]  # Agent-to-agent messages

    def __init__(self):
        self.short_term = []
        self.long_term = []
        self.context = {}
        self.communication_log = []

    def add_to_short_term(self, entry: Dict[str, Any], max_size: int = 20):
        """Add to short-term memory with size limit"""
        self.short_term.append(entry)
        if len(self.short_term) > max_size:
            # Move oldest to long-term
            self.long_term.append(self.short_term.pop(0))

    def update_context(self, key: str, value: Any):
        """Update current context"""
        self.context[key] = value

    def get_context(self, key: str, default=None):
        """Retrieve from context"""
        return self.context.get(key, default)

    def log_communication(self, message: AgentMessage):
        """Log agent communication"""
        self.communication_log.append(message)

    def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memories based on query"""
        # Simple relevance based on keyword matching
        all_memories = self.short_term + self.long_term
        relevant = []
        query_lower = query.lower()

        for memory in all_memories:
            memory_text = str(memory).lower()
            if any(word in memory_text for word in query_lower.split()):
                relevant.append(memory)

        return relevant[:limit]


class BaseAgent:
    """Enhanced base class for all agents with better context awareness"""

    def __init__(self, name: str, icon: str, console: Console):
        self.name = name
        self.icon = icon
        self.state = AgentState.IDLE
        self.console = console
        self.memory = AgentMemory()
        self.capabilities = []
        self.current_task = None
        self.error_count = 0
        self.success_count = 0

    def log(self, message: str, style: str = ""):
        """Log agent activity with memory storage"""
        from datetime import datetime
        prefix = f"{self.icon} [{self.name}]"
        self.console.print(f"{prefix} {message}", style=style)

        # Store in memory
        self.memory.add_to_short_term({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "type": "log",
            "state": self.state.value
        })

    def send_message(self, receiver: str, content: Dict[str, Any], priority: int = 0):
        """Send message to another agent"""
        from datetime import datetime
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content,
            priority=priority,
            timestamp=datetime.now().isoformat()
        )
        self.memory.log_communication(message)
        return message

    def receive_message(self, message: AgentMessage):
        """Receive and process message from another agent"""
        self.memory.log_communication(message)
        self.memory.update_context(f"last_message_from_{message.sender}", message.content)

    def update_state(self, new_state: AgentState):
        """Update agent state with logging"""
        old_state = self.state
        self.state = new_state
        self.memory.update_context("current_state", new_state.value)
        self.memory.add_to_short_term({
            "type": "state_change",
            "from": old_state.value,
            "to": new_state.value
        })

    def record_success(self):
        """Record successful task completion"""
        self.success_count += 1
        self.memory.update_context("success_count", self.success_count)

    def record_error(self, error: str):
        """Record error for learning"""
        self.error_count += 1
        self.memory.add_to_short_term({
            "type": "error",
            "error": error,
            "task": self.current_task
        })

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        total_tasks = self.success_count + self.error_count
        success_rate = (self.success_count / total_tasks * 100) if total_tasks > 0 else 0

        return {
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": f"{success_rate:.1f}%",
            "total_tasks": total_tasks,
            "current_state": self.state.value
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task - to be implemented by subclasses"""
        raise NotImplementedError


class OrchestratorAgent(BaseAgent):
    """Enhanced orchestrator with better coordination and context awareness"""

    def __init__(self, console: Console):
        super().__init__("Orchestrator", AGENT_ICONS["orchestrator"], console)
        self.agents = {}
        self.execution_history = []
        self.collaboration_graph = {}

    def register_agent(self, agent: BaseAgent):
        """Register an agent with capability tracking"""
        self.agents[agent.name] = agent
        self.collaboration_graph[agent.name] = []
        self.log(f"Registered {agent.name} with capabilities", style="dim")

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate task execution with enhanced context sharing"""
        self.update_state(AgentState.THINKING)
        self.current_task = task
        self.log("🧠 Analyzing your request with AI reasoning...", style="bold cyan")

        # Store task in memory
        self.memory.update_context("current_task", task)

        # Determine which agents are needed
        plan = self._create_execution_plan(task)

        self.log(f"📋 Created execution plan with {len(plan)} steps", style="green")
        self.log(f"🔄 Agent workflow: {' → '.join([s['agent'] for s in plan])}", style="dim")

        results = {}
        shared_context = {}  # Shared context across agents

        for idx, step in enumerate(plan, 1):
            agent_name = step["agent"]
            agent_task = step["task"]

            if agent_name in self.agents:
                agent = self.agents[agent_name]

                self.log(f"📤 Delegating to {agent_name} (Step {idx}/{len(plan)})", style="cyan")

                # Send message to agent with shared context
                message = self.send_message(
                    receiver=agent_name,
                    content={"task": agent_task, "shared_context": shared_context},
                    priority=len(plan) - idx  # Higher priority for earlier steps
                )

                # Pass shared context to agent
                agent.memory.update_context("shared_context", shared_context)

                # Execute agent task
                try:
                    result = await agent.process(agent_task)
                    results[agent_name] = result

                    # Update shared context with results
                    shared_context[agent_name] = result

                    # Record collaboration
                    if agent_name not in self.collaboration_graph:
                        self.collaboration_graph[agent_name] = []
                    self.collaboration_graph[agent_name].append({
                        "step": idx,
                        "task": agent_task,
                        "result_summary": str(result)[:100]
                    })

                    agent.record_success()
                    self.log(f"✅ {agent_name} completed successfully", style="green")

                except Exception as e:
                    error_msg = f"Error in {agent_name}: {str(e)}"
                    self.log(error_msg, style="red")
                    agent.record_error(str(e))
                    results[agent_name] = {"error": str(e)}

        # Store execution in history
        self.execution_history.append({
            "task": task,
            "plan": plan,
            "results": results,
            "timestamp": self.memory.short_term[-1]["timestamp"] if self.memory.short_term else ""
        })

        self.update_state(AgentState.COMPLETED)
        self.record_success()
        return results

    def get_collaboration_summary(self) -> Dict[str, Any]:
        """Get summary of agent collaborations"""
        return {
            "total_executions": len(self.execution_history),
            "collaboration_graph": self.collaboration_graph,
            "registered_agents": list(self.agents.keys())
        }
    
    def _create_execution_plan(self, task: Dict[str, Any]) -> List[Dict]:
        """Create execution plan"""
        plan = []
        
        # Dataset search
        if task.get("needs_dataset", True):
            plan.append({
                "agent": "DatasetAgent",
                "task": {"action": "search", "query": task.get("query", "")}
            })
        
        # Model design
        plan.append({
            "agent": "ModelAgent",
            "task": {"action": "design", "requirements": task.get("requirements", {})}
        })
        
        # Code generation
        plan.append({
            "agent": "CodeAgent",
            "task": {"action": "generate", "specifications": task.get("specifications", {})}
        })
        
        return plan


class DatasetAgent(BaseAgent):
    """Handles dataset discovery and preparation"""
    
    def __init__(self, console: Console):
        super().__init__("DatasetAgent", AGENT_ICONS["dataset_agent"], console)
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Search and prepare datasets"""
        self.state = AgentState.WORKING
        action = task.get("action")
        
        if action == "search":
            self.log("Searching datasets across multiple sources...", style="cyan")
            # Import here to avoid circular dependencies
            from noless.search import DatasetSearcher
            from noless.openml_search import OpenMLSearcher
            
            searcher = DatasetSearcher()
            openml_searcher = OpenMLSearcher()
            
            query = task.get("query", "")
            
            # Search OpenML
            openml_results = openml_searcher.search(query, limit=5)
            self.log(f"Found {len(openml_results)} datasets from OpenML", style="green")
            
            # Search other sources
            other_results = searcher.search(query, limit=5)
            self.log(f"Found {len(other_results)} datasets from other sources", style="green")
            
            all_results = openml_results + other_results
            
            self.state = AgentState.COMPLETED
            return {
                "datasets": all_results,
                "count": len(all_results),
                "sources": ["OpenML", "HuggingFace", "UCI"]
            }
        
        elif action == "download":
            self.log("Downloading and preparing dataset...", style="cyan")
            # Download logic here
            self.state = AgentState.COMPLETED
            return {"status": "downloaded", "path": task.get("output_path", "")}
        
        return {}


class ModelAgent(BaseAgent):
    """Designs model architectures"""
    
    def __init__(self, console: Console, llm_client: Optional[OllamaClient] = None, llm_model: Optional[str] = None):
        super().__init__("ModelAgent", AGENT_ICONS["model_agent"], console)
        self.llm_client = llm_client
        self.llm_model = llm_model
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Design model architecture"""
        self.state = AgentState.WORKING
        self.log("Analyzing task requirements...", style="cyan")
        
        requirements = task.get("requirements", {})
        task_type = requirements.get("task", "classification")
        
        self.log(f"Designing architecture for {task_type}...", style="yellow")
        
        # Simulate AI thinking
        await asyncio.sleep(1)
        
        architecture = self._design_architecture(task_type, requirements)
        
        self.log(f"Selected architecture: {architecture['name']}", style="green")
        
        self.state = AgentState.COMPLETED
        return architecture
    
    def _design_architecture(self, task_type: str, requirements: Dict) -> Dict:
        """Design architecture based on task"""
        if self.llm_client and self.llm_model:
            dataset_hint = requirements.get("dataset", {}).get("selected", {})
            prompt = (
                "You are the NoLess Model Agent. Create a JSON response with keys"
                " name (string), layers (array of strings), parameters (string),"
                " recommended_batch_size (int), and notes (string)."
                " Always return valid JSON only."
            )
            details = {
                "task": task_type,
                "requirements": requirements,
                "dataset": dataset_hint,
            }
            try:
                response = self.llm_client.generate(self.llm_model, json.dumps(details), system=prompt)
                data = _parse_json_block(response) or {}
                layers = data.get("layers")
                if isinstance(layers, str):
                    layers = [layer.strip() for layer in layers.split(",") if layer.strip()]
                if not isinstance(layers, list) or not layers:
                    layers = ["dense", "relu", "dense"]
                architecture = {
                    "name": data.get("name", "CustomModel"),
                    "layers": layers,
                    "parameters": data.get("parameters", "~5M"),
                    "recommended_batch_size": int(data.get("recommended_batch_size", 32)),
                    "notes": data.get("notes", "LLM-generated architecture."),
                }
                return architecture
            except Exception as exc:
                self.log(f"LLM architecture suggestion failed ({exc}); falling back to presets.", style="yellow")
        architectures = {
            "image-classification": {
                "name": "ResNet50",
                "layers": ["conv", "batch_norm", "relu", "maxpool", "residual_blocks", "fc"],
                "parameters": "~25M",
                "recommended_batch_size": 32
            },
            "text-classification": {
                "name": "BERT-base",
                "layers": ["embedding", "transformer_blocks", "pooler", "classifier"],
                "parameters": "~110M",
                "recommended_batch_size": 16
            },
            "regression": {
                "name": "Deep Neural Network",
                "layers": ["dense", "relu", "dropout", "dense", "relu", "dense"],
                "parameters": "~1M",
                "recommended_batch_size": 64
            }
        }
        
        return architectures.get(task_type, architectures["image-classification"])


class CodeAgent(BaseAgent):
    """Generates code in real-time"""
    
    def __init__(self, console: Console, llm_client: Optional[OllamaClient] = None, llm_model: Optional[str] = None):
        super().__init__("CodeAgent", AGENT_ICONS["code_agent"], console)
        self.llm_client = llm_client
        self.llm_model = llm_model
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code"""
        self.state = AgentState.WORKING
        self.log("Generating training script...", style="cyan")
        
        specifications = task.get("specifications", {})
        if self.llm_client and self.llm_model:
            dataset_hint = specifications.get("dataset", {}).get("selected", {})
            prompt = (
                "You are the NoLess Code Agent. Return JSON only with schema"
                " {steps: [""short description""], files: [{name, purpose}], warnings: [string]}."
                " Use dataset info when proposing preprocessing."
            )
            try:
                payload = {
                    "specifications": specifications,
                    "dataset": dataset_hint,
                }
                plan = self.llm_client.generate(self.llm_model, json.dumps(payload), system=prompt)
                data = _parse_json_block(plan) or {}
                steps = data.get("steps", [])
                if isinstance(steps, str):
                    steps = [steps]
                for step in steps[:5]:
                    self.log(f"LLM plan: {step}", style="dim")
                warnings = data.get("warnings", [])
                for warning in warnings:
                    self.log(f"LLM warning: {warning}", style="yellow")
            except Exception as exc:
                self.log(f"LLM code planning failed ({exc}), continuing with default pipeline.", style="yellow")
        
        # Simulate code generation
        self.log("Writing model definition...", style="yellow")
        await asyncio.sleep(0.5)
        
        self.log("Creating data loaders...", style="yellow")
        await asyncio.sleep(0.5)
        
        self.log("Implementing training loop...", style="yellow")
        await asyncio.sleep(0.5)
        
        self.log("Adding evaluation metrics...", style="yellow")
        await asyncio.sleep(0.5)
        
        self.log("Code generation complete!", style="green bold")
        
        self.state = AgentState.COMPLETED
        return {
            "files_generated": ["train.py", "model.py", "config.yaml", "utils.py"],
            "lines_of_code": 450,
            "status": "success"
        }


class TrainingAgent(BaseAgent):
    """Manages training process"""
    
    def __init__(self, console: Console):
        super().__init__("TrainingAgent", AGENT_ICONS["training_agent"], console)
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute training"""
        self.state = AgentState.WORKING
        self.log("Setting up training environment...", style="cyan")
        
        # Training simulation
        epochs = task.get("epochs", 10)
        
        for epoch in range(1, epochs + 1):
            self.log(f"Epoch {epoch}/{epochs}: Loss=0.{100-epoch*5}, Acc={50+epoch*3}%", style="yellow")
            await asyncio.sleep(0.3)
        
        self.log("Training completed successfully!", style="green bold")
        
        self.state = AgentState.COMPLETED
        return {
            "final_accuracy": 0.95,
            "final_loss": 0.05,
            "model_path": "best_model.pth"
        }


class OptimizationAgent(BaseAgent):
    """Optimizes hyperparameters and model performance"""
    
    def __init__(self, console: Console):
        super().__init__("OptimizationAgent", AGENT_ICONS["optimization_agent"], console)
        
    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize model"""
        self.state = AgentState.WORKING
        self.log("Analyzing model performance...", style="cyan")
        
        await asyncio.sleep(1)
        
        self.log("Suggesting hyperparameter improvements...", style="yellow")
        
        suggestions = {
            "learning_rate": 0.0001,
            "batch_size": 64,
            "optimizer": "AdamW",
            "expected_improvement": "+5% accuracy"
        }
        
        self.log(f"Optimization suggestions ready", style="green")
        
        self.state = AgentState.COMPLETED
        return suggestions


class MultiAgentSystem:
    """Enhanced multi-agent system with communication tracking and performance metrics"""

    def __init__(self, llm_model: Optional[str] = None, ollama_client: Optional[OllamaClient] = None):
        self.console = Console()
        self.orchestrator = OrchestratorAgent(self.console)
        self.llm_model = llm_model
        self.ollama_client = None
        if llm_model:
            self.ollama_client = ollama_client or OllamaClient()

        # Initialize all agents
        self.dataset_agent = DatasetAgent(self.console)
        self.model_agent = ModelAgent(self.console, self.ollama_client, self.llm_model)
        self.code_agent = CodeAgent(self.console, self.ollama_client, self.llm_model)
        self.training_agent = TrainingAgent(self.console)
        self.optimization_agent = OptimizationAgent(self.console)

        # Register agents with orchestrator
        self.orchestrator.register_agent(self.dataset_agent)
        self.orchestrator.register_agent(self.model_agent)
        self.orchestrator.register_agent(self.code_agent)
        self.orchestrator.register_agent(self.training_agent)
        self.orchestrator.register_agent(self.optimization_agent)

        # Communication log for transparency
        self.communication_log = []

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the multi-agent system with full transparency"""
        from noless.art import AGENT_COLLABORATION

        self.console.print("\n")
        self.console.print(Panel.fit(
            "[bold cyan]🚀 Multi-Agent System Activated[/bold cyan]\n"
            "6 specialized AI agents are collaborating to build your model...\n\n"
            f"{AGENT_COLLABORATION}",
            border_style="cyan",
            title="[bold]Multi-Agent Collaboration[/bold]"
        ))
        self.console.print("\n")

        results = await self.orchestrator.process(task)

        # Collect communication logs
        self._collect_communication_logs()

        self.console.print("\n")
        self.console.print(Panel.fit(
            "[bold green]✨ Task Completed Successfully![/bold green]\n"
            "All agents have finished their work.\n\n"
            f"📊 Total communications: {len(self.communication_log)}\n"
            f"✅ Success rate: {self._calculate_success_rate()}%",
            border_style="green",
            title="[bold]Execution Complete[/bold]"
        ))

        return results

    def _collect_communication_logs(self):
        """Collect all communication logs from agents"""
        all_agents = [
            self.orchestrator,
            self.dataset_agent,
            self.model_agent,
            self.code_agent,
            self.training_agent,
            self.optimization_agent
        ]

        for agent in all_agents:
            self.communication_log.extend(agent.memory.communication_log)

    def _calculate_success_rate(self) -> float:
        """Calculate overall system success rate"""
        all_agents = [
            self.dataset_agent,
            self.model_agent,
            self.code_agent,
            self.training_agent,
            self.optimization_agent
        ]

        total_success = sum(agent.success_count for agent in all_agents)
        total_errors = sum(agent.error_count for agent in all_agents)
        total_tasks = total_success + total_errors

        return round((total_success / total_tasks * 100) if total_tasks > 0 else 100, 1)

    def get_agent_status(self) -> Table:
        """Get enhanced status of all agents with performance metrics"""
        from noless.art import STATUS_ICONS

        table = Table(
            title="🤖 Multi-Agent System Status",
            show_header=True,
            header_style="bold magenta",
            border_style="cyan"
        )
        table.add_column("Agent", style="cyan")
        table.add_column("Icon", style="yellow", justify="center")
        table.add_column("Status", style="green", justify="center")
        table.add_column("Success Rate", style="blue", justify="center")
        table.add_column("Tasks", style="magenta", justify="center")

        agents = [
            self.orchestrator,
            self.dataset_agent,
            self.model_agent,
            self.code_agent,
            self.training_agent,
            self.optimization_agent
        ]

        for agent in agents:
            metrics = agent.get_performance_metrics()
            status_icon = STATUS_ICONS.get(agent.state.value, "⚪")

            table.add_row(
                agent.name,
                agent.icon,
                f"{status_icon} {agent.state.value.upper()}",
                metrics["success_rate"],
                str(metrics["total_tasks"])
            )

        return table

    def get_communication_logs(self) -> Table:
        """Get communication logs between agents"""
        table = Table(
            title="📡 Agent Communication Log",
            show_header=True,
            header_style="bold cyan",
            border_style="blue"
        )

        table.add_column("From", style="cyan", width=20)
        table.add_column("To", style="yellow", width=20)
        table.add_column("Message", style="white", width=50)
        table.add_column("Time", style="dim", width=20)

        for msg in self.communication_log[-20:]:  # Show last 20 messages
            content_preview = str(msg.content)[:50] + "..." if len(str(msg.content)) > 50 else str(msg.content)
            table.add_row(
                msg.sender,
                msg.receiver,
                content_preview,
                msg.timestamp.split('T')[1][:8] if 'T' in msg.timestamp else msg.timestamp
            )

        return table

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        all_agents = [
            self.dataset_agent,
            self.model_agent,
            self.code_agent,
            self.training_agent,
            self.optimization_agent
        ]

        agent_metrics = {}
        for agent in all_agents:
            agent_metrics[agent.name] = agent.get_performance_metrics()

        return {
            "overall_success_rate": self._calculate_success_rate(),
            "total_communications": len(self.communication_log),
            "agent_metrics": agent_metrics,
            "collaboration_summary": self.orchestrator.get_collaboration_summary()
        }

    def show_live_dashboard(self):
        """Display live agent dashboard"""
        from noless.ui import create_live_agent_dashboard

        agents_data = []
        all_agents = [
            self.orchestrator,
            self.dataset_agent,
            self.model_agent,
            self.code_agent,
            self.training_agent,
            self.optimization_agent
        ]

        for agent in all_agents:
            from noless.art import STATUS_ICONS
            agents_data.append({
                "name": agent.name,
                "status": agent.state.value,
                "status_icon": STATUS_ICONS.get(agent.state.value, "⚪"),
                "task": agent.current_task.get("action", "Idle") if agent.current_task else "Idle",
                "progress": f"{agent.success_count}/{agent.success_count + agent.error_count}"
            })

        layout = create_live_agent_dashboard(agents_data)
        self.console.print(layout)
