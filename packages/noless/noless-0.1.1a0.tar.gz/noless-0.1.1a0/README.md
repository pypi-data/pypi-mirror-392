Noless CLI
---

# NoLess: Multi-Agent AI Model Builder

```
                        ╔══════════════════════════════════════════════════════════════════════╗
                        ║                                                                      ║
                        ║  ███╗   ██╗ ██████╗     ██╗     ███████╗███████╗███████╗             ║
                        ║  ████╗  ██║██╔═══██╗    ██║     ██╔════╝██╔════╝██╔════╝             ║
                        ║  ██╔██╗ ██║██║   ██║    ██║     █████╗  ███████╗███████╗             ║
                        ║  ██║╚██╗██║██║   ██║    ██║     ██╔══╝  ╚════██║╚════██║             ║
                        ║  ██║ ╚████║╚██████╔╝    ███████╗███████╗███████║███████║             ║
                        ║  ╚═╝  ╚═══╝ ╚═════╝     ╚══════╝╚══════╝╚══════╝╚══════╝             ║
                        ║                                                                      ║
                        ║  Multi-Agent AI Model Builder | LLM-Powered Intelligence              ║
                        ║  Build AI Models Without Limits | Six Specialized Agents              ║
                        ║  Real-Time Code Generation | Intelligent Dataset Discovery             ║
                        ║                                                                      ║
                        ╚══════════════════════════════════════════════════════════════════════╝
```

NoLess is an advanced CLI-driven AI engineering system that uses a coordinated **multi-agent architecture** to automatically build machine learning projects from end to end. It searches datasets, designs architectures, generates production-ready code, manages training, and optimizes performance — all autonomously.

This approach eliminates boilerplate work and dramatically accelerates machine learning development.

---

## Key Features

### Multi-Agent Architecture

NoLess uses six specialized AI agents that collaborate to generate complete ML solutions:

| Agent                  | Function                                        |
| ---------------------- | ----------------------------------------------- |
| **Orchestrator Agent** | Controls workflow and execution                 |
| **Dataset Agent**      | Searches OpenML, Hugging Face, Kaggle, UCI      |
| **Model Agent**        | Designs optimized architectures                 |
| **Code Agent**         | Generates clean, production-ready code          |
| **Training Agent**     | Builds and manages the training pipeline        |
| **Optimization Agent** | Performs hyperparameter tuning and improvements |

### Dataset Search

* OpenML (20,000+ datasets)
* HuggingFace Datasets Hub
* UCI Repository
* Kaggle Repository
* Task-aware filtering and dataset ranking

### Real-Time Code Generation

Automatically generates:

* Model architectures
* Training scripts
* Preprocessing pipelines
* Evaluation metrics
* Configuration files
* Documentation

All files follow industry best practices and production-level standards.

### Interactive CLI

* Step-by-step workflow
* Intelligent recommendations
* Rich outputs and enhanced usability
* ASCII banner and clean interface

### Framework Support

* PyTorch
* TensorFlow / Keras
* scikit-learn

---

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install noless
```

### Option 2: Install from Source

```bash
git clone https://github.com/DWE-CLOUD/NoLess.git
cd NoLess
pip install -r requirements.txt
pip install -e .
```

### Verify Installation

```bash
noless --help
```

---

## Quick Start

### Interactive Mode

```bash
python -m noless.cli interactive
```

### Direct Creation

```bash
python -m noless.cli create \
  --task image-classification \
  --framework pytorch \
  --agents
```

---

## Usage Examples

### Multi-Agent Project Creation

```bash
python -m noless.cli create \
  --task image-classification \
  --framework pytorch \
  --output ./my_classifier \
  --agents
```

### Dataset Search

```bash
python -m noless.cli search \
  --query "diabetes classification" \
  --source openml \
  --limit 10
```

### Dataset Download

```bash
python -m noless.cli download openml:37 --output ./data
```

---

## Autopilot Mode (Ollama-LMM Powered)

NoLess can use local LLMs (via Ollama) to automatically plan, design, and build entire projects.

```bash
python -m noless.cli autopilot \
  --description "detect defects in solar panel images" \
  --output ./solar_inspector
```

Specify a model:

```bash
python -m noless.cli autopilot --llm-model deepseek-r1:7b
```

Autopilot performs requirement analysis, dataset extraction, dataset selection, downloading, multi-agent generation, and documentation creation.

---

## Generated Project Structure

```
my_model/
├── train.py
├── model.py
├── config.yaml
├── utils.py
├── requirements.txt
└── README.md
```

All modules are cleanly structured, modular, and fully customizable.

---

## Supported Tasks

| Task                    | Description                 | Frameworks          |
| ----------------------- | --------------------------- | ------------------- |
| Image Classification    | Vision-based categorization | PyTorch, TensorFlow |
| Text Classification     | NLP classification tasks    | PyTorch, TensorFlow |
| Object Detection        | Bounding box detection      | PyTorch             |
| Sentiment Analysis      | Polarity scoring            | PyTorch, TensorFlow |
| Regression              | Numerical prediction        | All                 |
| Clustering              | Unsupervised grouping       | scikit-learn        |
| Time-Series Forecasting | Sequential prediction       | PyTorch, TensorFlow |
| General NLP Tasks       | Sequence and token tasks    | PyTorch, TensorFlow |

---

## Multi-Agent Architecture

### How It Works

1. The Orchestrator interprets the request
2. The Dataset Agent performs multi-source dataset search
3. The Model Agent creates an appropriate architecture
4. The Code Agent generates the necessary modules
5. The Training Agent constructs training workflows
6. The Optimization Agent tunes configurations and parameters

### Communication

* Asynchronous message passing
* Shared context memory
* Priority scheduling
* Real-time updates

---

## CLI Reference

```bash
noless search -q "query"
noless create -t TASK -f FRAMEWORK [--agents]
noless interactive
noless autopilot
noless download DATASET_ID
noless agents
noless templates
```

---

## Configuration Example

```yaml
task: image-classification
framework: pytorch

model:
  architecture: resnet50
  pretrained: true
  num_classes: 10

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
```

---

## Roadmap

* Distributed training
* Automated model deployment
* Experiment tracking and model registry
* Additional dataset sources
* Web-based UI
* Custom agent plugins
* AutoML-style pipeline search

---

## License

MIT License. Refer to the `LICENSE` file.

---

## Acknowledgments

* OpenML
* Hugging Face
* PyTorch and TensorFlow teams
* Rich library
* Click CLI framework

---


Just tell me.