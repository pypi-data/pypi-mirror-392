"""Model and training script generation"""

import os
import yaml
import json
from typing import Dict, Optional, Any
from jinja2 import Template
from noless.ollama_client import OllamaClient
from noless.code_validator import CodeValidator
from noless.ui import show_file_being_created, show_live_code_generation
from rich.console import Console

console = Console()


class ModelGenerator:
    """Generate model projects and training scripts"""
    
    def __init__(self, llm_model: Optional[str] = None, ollama_client: Optional[OllamaClient] = None, 
                 enable_validation: bool = True, reviewer_model: Optional[str] = None, 
                 interactive: bool = False):
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.llm_model = llm_model
        self.ollama_client = ollama_client
        if llm_model and not ollama_client:
            self.ollama_client = OllamaClient()
        self.reviewer_model = reviewer_model or llm_model
        self.interactive = interactive
        self.validator = None
        if enable_validation and (reviewer_model or llm_model):
            validator = CodeValidator(
                reviewer_model=reviewer_model,
                generation_model=self.llm_model,
                ollama_client=self.ollama_client,
            )
            if validator.reviewer_model:
                self.reviewer_model = validator.reviewer_model
                self.validator = validator
    
    def create_project(self, task: str, framework: str, dataset: Optional[str],
                      output_dir: str, architecture: Optional[str] = None,
                      dataset_metadata: Optional[Dict[str, Any]] = None,
                      requirements_context: Optional[Dict[str, Any]] = None) -> Dict:
        """Create a complete model project
        
        Args:
            task: ML task type
            framework: ML framework (pytorch, tensorflow, sklearn)
            dataset: Dataset name or path
            output_dir: Output directory for the project
            architecture: Model architecture
            dataset_metadata: Dataset info from autopilot (columns, shape, etc.)
            requirements_context: User clarifications and task description
            
        Returns:
            Project information dictionary
        """
        os.makedirs(output_dir, exist_ok=True)
        
        context = {
            "task": task,
            "framework": framework,
            "dataset": dataset,
            "architecture": architecture,
            "dataset_metadata": dataset_metadata or {},
            "requirements": requirements_context or {},
        }
        
        # Generate config
        print(f"\n📝 Generating config.yaml...")
        config = self._generate_config(task, framework, dataset, architecture)
        config_path = os.path.join(output_dir, "config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        print(f"✅ Created {config_path}")
        
        # Generate model definition (LLM-powered if available)
        console.print(f"\n[bold cyan]📝 Generating model.py...[/bold cyan]")
        model_script = self._generate_model_with_llm(context) if self.llm_model else self._generate_model_definition(task, framework, architecture)

        # Show live code generation - ALL lines with scrolling window
        if model_script:
            code_lines = model_script.split('\n')
            if len(code_lines) > 10:  # Only show animation for larger files
                show_live_code_generation("model.py", code_lines, delay=0.008)  # Fast scrolling through ALL lines

        if self.validator:
            validation = self.validator.validate_and_improve(model_script, "model.py", context)
            if validation and validation.get("improved_code") and validation["improved_code"] != model_script:
                console.print(f"[green]✅ Model code improved by AI reviewer[/green]")
                model_script = validation["improved_code"]
            if validation and validation.get("issues"):
                console.print(f"[yellow]⚠️  Found {len(validation['issues'])} issues (fixed in improved version)[/yellow]")

        model_path = os.path.join(output_dir, "model.py")
        show_file_being_created(model_path, model_script, show_preview=True)
        with open(model_path, "w") as f:
            f.write(model_script)
        
        # Generate training script (LLM-powered if available)
        console.print(f"\n[bold cyan]📝 Generating train.py...[/bold cyan]")
        train_script = self._generate_train_with_llm(context) if self.llm_model else self._generate_training_script_content(task, framework, architecture)

        # Show live code generation for train.py - ALL lines with scrolling
        if train_script:
            code_lines = train_script.split('\n')
            if len(code_lines) > 10:
                show_live_code_generation("train.py", code_lines, delay=0.008)  # Fast scrolling

        if self.validator:
            validation = self.validator.validate_and_improve(train_script, "train.py", context)
            if validation and validation.get("improved_code") and validation["improved_code"] != train_script:
                console.print(f"[green]✅ Training code improved by AI reviewer[/green]")
                train_script = validation["improved_code"]
            if validation and validation.get("issues"):
                console.print(f"[yellow]⚠️  Found {len(validation['issues'])} issues (fixed in improved version)[/yellow]")

        train_path = os.path.join(output_dir, "train.py")
        with open(train_path, "w") as f:
            f.write(train_script)
        print(f"✅ Created {train_path}")
        
        # Generate test suite (LLM-powered if available)
        print(f"\n📝 Generating test_model.py...")
        test_script = self._generate_tests_with_llm(context) if self.llm_model else self._generate_basic_tests(task, framework)
        test_path = os.path.join(output_dir, "test_model.py")
        with open(test_path, "w") as f:
            f.write(test_script)
        print(f"✅ Created {test_path}")
        
        # Generate requirements (include pytest)
        requirements = self._generate_requirements(framework)
        if "pytest" not in requirements:
            requirements += "pytest>=7.4.0\npytest-cov>=4.1.0\n"
        req_path = os.path.join(output_dir, "requirements.txt")
        with open(req_path, "w") as f:
            f.write(requirements)
        
        # Generate README
        readme = self._generate_readme(task, framework, dataset)
        readme_path = os.path.join(output_dir, "README.md")
        with open(readme_path, "w") as f:
            f.write(readme)
        
        return {
            "output_dir": output_dir,
            "files": [config_path, train_path, model_path, test_path, req_path, readme_path]
        }
    
    def generate_training_script(self, model_type: str, task: str, 
                                 framework: str, output_path: str) -> str:
        """Generate a standalone training script"""
        script_content = self._generate_training_script_content(task, framework, model_type)
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w") as f:
            f.write(script_content)
        
        return output_path
    
    def _generate_config(self, task: str, framework: str, 
                        dataset: Optional[str], architecture: Optional[str]) -> Dict:
        """Generate configuration dictionary"""
        config = {
            "task": task,
            "framework": framework,
            "dataset": dataset or "your_dataset_path",
            "model": {
                "architecture": architecture or self._default_architecture(task, framework),
                "pretrained": True
            },
            "training": {
                "batch_size": 32,
                "epochs": 10,
                "learning_rate": 0.001,
                "optimizer": "adam",
                "loss_function": self._default_loss(task)
            },
            "data": {
                "train_split": 0.8,
                "val_split": 0.1,
                "test_split": 0.1,
                "shuffle": True
            }
        }
        return config
    
    def _generate_training_script_content(self, task: str, framework: str, 
                                          architecture: Optional[str]) -> str:
        """Generate training script content"""
        if framework == "pytorch":
            return self._pytorch_training_script(task, architecture)
        elif framework == "tensorflow":
            return self._tensorflow_training_script(task, architecture)
        elif framework == "sklearn":
            return self._sklearn_training_script(task)
        return ""
    
    def _pytorch_training_script(self, task: str, architecture: Optional[str]) -> str:
        """Generate PyTorch training script"""
        script = '''"""Training script for PyTorch model"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import yaml
from model import Model
from tqdm import tqdm


class CustomDataset(Dataset):
    """Custom dataset class - implement based on your data"""
    
    def __init__(self, data_path, transform=None):
        self.data_path = data_path
        self.transform = transform
        # TODO: Load your data here
        
    def __len__(self):
        # TODO: Return dataset size
        return 1000
    
    def __getitem__(self, idx):
        # TODO: Return data sample and label
        return torch.randn(3, 224, 224), torch.tensor(0)


def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for batch_idx, (data, target) in enumerate(tqdm(dataloader, desc="Training")):
        data, target = data.to(device), target.to(device)
        
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        _, predicted = output.max(1)
        total += target.size(0)
        correct += predicted.eq(target).sum().item()
    
    avg_loss = total_loss / len(dataloader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def validate(model, dataloader, criterion, device):
    """Validate the model"""
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    
    with torch.no_grad():
        for data, target in tqdm(dataloader, desc="Validation"):
            data, target = data.to(device), target.to(device)
            output = model(data)
            loss = criterion(output, target)
            
            total_loss += loss.item()
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
    
    avg_loss = total_loss / len(dataloader)
    accuracy = 100. * correct / total
    return avg_loss, accuracy


def main():
    """Main training function"""
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Create datasets and dataloaders
    train_dataset = CustomDataset(config["dataset"])
    train_loader = DataLoader(
        train_dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=config["data"]["shuffle"],
        num_workers=4
    )
    
    val_dataset = CustomDataset(config["dataset"])  # TODO: Use validation split
    val_loader = DataLoader(
        val_dataset,
        batch_size=config["training"]["batch_size"],
        shuffle=False,
        num_workers=4
    )
    
    # Create model
    model = Model(num_classes=10).to(device)  # TODO: Set num_classes
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=config["training"]["learning_rate"]
    )
    
    # Training loop
    best_val_acc = 0
    for epoch in range(config["training"]["epochs"]):
        print(f"\\nEpoch {epoch+1}/{config['training']['epochs']}")
        
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc = validate(model, val_loader, criterion, device)
        
        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), "best_model.pth")
            print(f"Saved best model with accuracy: {best_val_acc:.2f}%")
    
    print(f"\\nTraining complete! Best validation accuracy: {best_val_acc:.2f}%")


if __name__ == "__main__":
    main()
'''
        return script
    
    def _tensorflow_training_script(self, task: str, architecture: Optional[str]) -> str:
        """Generate TensorFlow training script"""
        script = '''"""Training script for TensorFlow model"""

import tensorflow as tf
from tensorflow import keras
import yaml
from model import create_model


def load_data(config):
    """Load and preprocess data"""
    # TODO: Implement data loading
    # Example for image data:
    train_ds = tf.keras.preprocessing.image_dataset_from_directory(
        config["dataset"],
        validation_split=config["data"]["val_split"],
        subset="training",
        seed=123,
        image_size=(224, 224),
        batch_size=config["training"]["batch_size"]
    )
    
    val_ds = tf.keras.preprocessing.image_dataset_from_directory(
        config["dataset"],
        validation_split=config["data"]["val_split"],
        subset="validation",
        seed=123,
        image_size=(224, 224),
        batch_size=config["training"]["batch_size"]
    )
    
    return train_ds, val_ds


def main():
    """Main training function"""
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Setup GPU
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"Using GPU: {gpus[0]}")
    else:
        print("Using CPU")
    
    # Load data
    train_ds, val_ds = load_data(config)
    
    # Create model
    model = create_model(num_classes=10)  # TODO: Set num_classes
    
    # Compile model
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config["training"]["learning_rate"]),
        loss=keras.losses.SparseCategoricalCrossentropy(),
        metrics=['accuracy']
    )
    
    # Callbacks
    callbacks = [
        keras.callbacks.ModelCheckpoint(
            'best_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        )
    ]
    
    # Train model
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config["training"]["epochs"],
        callbacks=callbacks
    )
    
    # Evaluate
    test_loss, test_acc = model.evaluate(val_ds)
    print(f"\\nFinal validation accuracy: {test_acc*100:.2f}%")
    
    # Save model
    model.save('final_model.h5')
    print("Model saved!")


if __name__ == "__main__":
    main()
'''
        return script
    
    def _sklearn_training_script(self, task: str) -> str:
        """Generate scikit-learn training script"""
        script = '''"""Training script for scikit-learn model"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import yaml
import joblib
from model import create_model


def load_data(config):
    """Load and preprocess data"""
    # TODO: Implement data loading
    # Example:
    data = pd.read_csv(config["dataset"])
    X = data.drop('target', axis=1).values
    y = data['target'].values
    return X, y


def main():
    """Main training function"""
    # Load configuration
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Load data
    X, y = load_data(config)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y,
        test_size=(1 - config["data"]["train_split"]),
        random_state=42
    )
    
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.5,
        random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)
    
    # Create and train model
    model = create_model()
    
    print("Training model...")
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train_scaled)
    val_pred = model.predict(X_val_scaled)
    test_pred = model.predict(X_test_scaled)
    
    print(f"\\nTraining Accuracy: {accuracy_score(y_train, train_pred):.4f}")
    print(f"Validation Accuracy: {accuracy_score(y_val, val_pred):.4f}")
    print(f"Test Accuracy: {accuracy_score(y_test, test_pred):.4f}")
    
    print("\\nClassification Report:")
    print(classification_report(y_test, test_pred))
    
    # Save model and scaler
    joblib.dump(model, 'model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("\\nModel and scaler saved!")


if __name__ == "__main__":
    main()
'''
        return script
    
    def _generate_model_definition(self, task: str, framework: str, 
                                   architecture: Optional[str]) -> str:
        """Generate model definition"""
        if framework == "pytorch":
            return self._pytorch_model(task, architecture)
        elif framework == "tensorflow":
            return self._tensorflow_model(task, architecture)
        elif framework == "sklearn":
            return self._sklearn_model(task)
        return ""
    
    def _pytorch_model(self, task: str, architecture: Optional[str]) -> str:
        """Generate PyTorch model"""
        if "image" in task or "object-detection" in task:
            return '''"""PyTorch model definition"""

import torch
import torch.nn as nn
import torchvision.models as models


class Model(nn.Module):
    """Custom model for image classification"""
    
    def __init__(self, num_classes=10, pretrained=True):
        super(Model, self).__init__()
        
        # Load pretrained model (e.g., ResNet)
        self.backbone = models.resnet50(pretrained=pretrained)
        
        # Replace final layer
        num_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(num_features, num_classes)
    
    def forward(self, x):
        return self.backbone(x)
'''
        else:
            return '''"""PyTorch model definition"""

import torch
import torch.nn as nn


class Model(nn.Module):
    """Custom neural network model"""
    
    def __init__(self, input_size=784, hidden_size=256, num_classes=10):
        super(Model, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size // 2, num_classes)
        )
    
    def forward(self, x):
        return self.network(x)
'''
    
    def _tensorflow_model(self, task: str, architecture: Optional[str]) -> str:
        """Generate TensorFlow model"""
        return '''"""TensorFlow model definition"""

import tensorflow as tf
from tensorflow import keras


def create_model(num_classes=10, input_shape=(224, 224, 3)):
    """Create a CNN model"""
    
    base_model = keras.applications.ResNet50(
        include_top=False,
        weights='imagenet',
        input_shape=input_shape
    )
    
    base_model.trainable = False  # Freeze base model
    
    model = keras.Sequential([
        base_model,
        keras.layers.GlobalAveragePooling2D(),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dropout(0.5),
        keras.layers.Dense(num_classes, activation='softmax')
    ])
    
    return model
'''
    
    def _sklearn_model(self, task: str) -> str:
        """Generate scikit-learn model"""
        return '''"""Scikit-learn model definition"""

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression


def create_model(model_type='random_forest'):
    """Create a scikit-learn model"""
    
    if model_type == 'random_forest':
        return RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
    elif model_type == 'svm':
        return SVC(
            kernel='rbf',
            C=1.0,
            random_state=42
        )
    elif model_type == 'logistic':
        return LogisticRegression(
            max_iter=1000,
            random_state=42
        )
    else:
        return RandomForestClassifier(random_state=42)
'''
    
    def _generate_requirements(self, framework: str) -> str:
        """Generate requirements.txt"""
        base_reqs = "numpy>=1.24.0\npandas>=2.0.0\npyyaml>=6.0\ntqdm>=4.65.0\n"
        
        if framework == "pytorch":
            return base_reqs + "torch>=2.0.0\ntorchvision>=0.15.0\n"
        elif framework == "tensorflow":
            return base_reqs + "tensorflow>=2.13.0\n"
        elif framework == "sklearn":
            return base_reqs + "scikit-learn>=1.3.0\njoblib>=1.3.0\n"
        return base_reqs
    
    def _generate_readme(self, task: str, framework: str, dataset: Optional[str]) -> str:
        """Generate README.md"""
        return f'''# Model Training Project

## Task: {task}
## Framework: {framework}
## Dataset: {dataset or "Custom dataset"}

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the model in `config.yaml`

3. Prepare your dataset at the path specified in config

## Training

Run the training script:
```bash
python train.py
```

## Files

- `train.py`: Main training script
- `model.py`: Model architecture definition
- `config.yaml`: Configuration file
- `requirements.txt`: Python dependencies

## Customization

1. Modify `config.yaml` to adjust hyperparameters
2. Edit `model.py` to change model architecture
3. Update `train.py` for custom training logic

## Results

Training results and checkpoints will be saved in the project directory.
'''
    
    def _default_architecture(self, task: str, framework: str) -> str:
        """Get default architecture for task"""
        if "image" in task:
            return "resnet50"
        elif "text" in task or "nlp" in task:
            return "bert-base"
        else:
            return "mlp"
    
    def _default_loss(self, task: str) -> str:
        """Get default loss function for task"""
        if "classification" in task:
            return "cross_entropy"
        elif "regression" in task:
            return "mse"
        else:
            return "cross_entropy"
    
    # ========== LLM-Powered Generation ==========
    
    def _generate_model_with_llm(self, context: Dict[str, Any]) -> str:
        """Generate complete model.py using LLM"""
        if not self.ollama_client or not self.llm_model:
            print("[Info] LLM not configured, using template.")
            return self._generate_model_definition(context["task"], context["framework"], context.get("architecture"))
        
        # Use interactive feedback loop if enabled
        if self.interactive:
            from noless.feedback_loop import FeedbackLoop
            loop = FeedbackLoop(self.ollama_client, self.llm_model, self.reviewer_model)
            code = loop.start_interactive_generation(context, "model")
            if code:  # User accepted the code
                return code
            # If empty, user cancelled - use fallback
            print("[Info] Using template fallback.")
            return self._generate_model_definition(context["task"], context["framework"], context.get("architecture"))
        
        print(f"[LLM] Generating model.py with {self.llm_model}...")
        prompt = self._build_enhanced_model_prompt(context)
        system_msg = (
            "You are an expert Python/ML engineer. Generate ONLY executable Python code."
            " CRITICAL RULES:"
            " 1. NO thinking process, NO reasoning, NO explanations"
            " 2. NO markdown code fences (no ```python)"
            " 3. NO comments like '# Let me think' or '# First I will'"
            " 4. Start IMMEDIATELY with import statements"
            " 5. Return PURE Python code that can be saved directly to .py file"
            " 6. Include ALL imports, complete class implementations, proper error handling"
            " 7. NO placeholders or TODOs - complete working code only"
        )
        try:
            response = self.ollama_client.generate(
                self.llm_model, 
                prompt, 
                system=system_msg, 
                temperature=0.2,
                options={"num_predict": 4096}  # Ensure enough tokens for complete code
            )
            code = self._extract_code_block(response)
            if code and "class" in code and "def" in code and len(code) > 500:
                print(f"[LLM] ✅ Model code generated ({len(code)} chars, {len(code.split(chr(10)))} lines)")
                return code
            print(f"[Warning] LLM returned incomplete code ({len(code) if code else 0} chars), using fallback.")
        except Exception as exc:
            print(f"[Warning] LLM model generation failed ({exc}), using fallback.")
        return self._generate_model_definition(context["task"], context["framework"], context.get("architecture"))
    
    def _generate_train_with_llm(self, context: Dict[str, Any]) -> str:
        """Generate complete train.py using LLM"""
        if not self.ollama_client or not self.llm_model:
            print("[Info] LLM not configured, using template.")
            return self._generate_training_script_content(context["task"], context["framework"], context.get("architecture"))
        
        # Use interactive feedback loop if enabled
        if self.interactive:
            from noless.feedback_loop import FeedbackLoop
            loop = FeedbackLoop(self.ollama_client, self.llm_model, self.reviewer_model)
            code = loop.start_interactive_generation(context, "train")
            if code:
                return code
            print("[Info] Using template fallback.")
            return self._generate_training_script_content(context["task"], context["framework"], context.get("architecture"))
        
        print(f"[LLM] Generating train.py with {self.llm_model}...")
        prompt = self._build_enhanced_train_prompt(context)
        system_msg = (
            "You are an expert Python/ML engineer. Generate ONLY executable Python code."
            " CRITICAL RULES:"
            " 1. NO thinking process, NO reasoning, NO explanations"
            " 2. NO markdown code fences (no ```python)"
            " 3. NO comments like '# Let me think' or '# First I will'"
            " 4. Start IMMEDIATELY with import statements"
            " 5. Return PURE Python code that can be saved directly to .py file"
            " 6. Include ALL imports, data loading, training loop, validation, checkpointing"
            " 7. NO placeholders or TODOs - complete working code only"
        )
        try:
            response = self.ollama_client.generate(
                self.llm_model, 
                prompt, 
                system=system_msg, 
                temperature=0.2,
                options={"num_predict": 4096}
            )
            code = self._extract_code_block(response)
            if code and "def" in code and ("train" in code.lower() or "main" in code) and len(code) > 800:
                print(f"[LLM] ✅ Training script generated ({len(code)} chars, {len(code.split(chr(10)))} lines)")
                return code
            print(f"[Warning] LLM returned incomplete code ({len(code) if code else 0} chars), using fallback.")
        except Exception as exc:
            print(f"[Warning] LLM train generation failed ({exc}), using fallback.")
        return self._generate_training_script_content(context["task"], context["framework"], context.get("architecture"))
    
    def _generate_tests_with_llm(self, context: Dict[str, Any]) -> str:
        """Generate test_model.py with comprehensive tests using LLM"""
        if not self.ollama_client or not self.llm_model:
            print("[Info] LLM not configured, using template.")
            return self._generate_basic_tests(context["task"], context["framework"])
        
        print(f"[LLM] Generating test_model.py with {self.llm_model}...")
        prompt = self._build_test_prompt(context)
        system_msg = (
            "You are an expert Python test engineer. Generate a complete test_model.py using pytest."
            " Include unit tests for model forward pass, data loading, training step, and shape validation."
            " Return ONLY valid Python code with no markdown fences or explanations."
        )
        try:
            response = self.ollama_client.generate(self.llm_model, prompt, system=system_msg, temperature=0.2)
            code = self._extract_code_block(response)
            if code and ("def test_" in code or "class Test" in code):
                print("[LLM] ✅ Test suite generated successfully")
                return code
            print("[Warning] LLM returned incomplete code, using fallback.")
        except Exception as exc:
            print(f"[Warning] LLM test generation failed ({exc}), using fallback.")
        return self._generate_basic_tests(context["task"], context["framework"])
    
    def _build_model_prompt(self, context: Dict[str, Any]) -> str:
        task = context["task"]
        framework = context["framework"]
        arch = context.get("architecture", "resnet50")
        dataset_meta = context.get("dataset_metadata", {})
        
        prompt = f"""
Create a complete model.py file for:
- Task: {task}
- Framework: {framework}
- Architecture: {arch}
- Dataset metadata: {json.dumps(dataset_meta, indent=2)}

Requirements:
1. Import all necessary libraries
2. Define a Model class with proper __init__ and forward methods
3. Use pretrained weights where applicable
4. Infer num_classes from dataset metadata if available
5. Add docstrings and type hints
6. Include any custom layers or preprocessing needed

Generate the complete Python file now.
"""
        return prompt.strip()
    
    def _build_enhanced_model_prompt(self, context: Dict[str, Any]) -> str:
        """Enhanced prompt that generates more complete code"""
        task = context["task"]
        framework = context["framework"]
        arch = context.get("architecture", "resnet50")
        dataset_meta = context.get("dataset_metadata", {})
        requirements = context.get("requirements", {})
        
        # Extract useful info from metadata
        num_classes = dataset_meta.get("num_classes") or dataset_meta.get("target_classes", 10)
        num_features = dataset_meta.get("num_features") or dataset_meta.get("input_dim")
        
        prompt = f"""Generate a COMPLETE, PRODUCTION-READY model.py file.

TASK SPECIFICATION:
- ML Task: {task}
- Framework: {framework}
- Architecture: {arch}
- Number of classes: {num_classes}
- Input features: {num_features if num_features else "auto-detect from data"}

DATASET CONTEXT:
{json.dumps(dataset_meta, indent=2)}

USER REQUIREMENTS:
{json.dumps(requirements, indent=2)}

MANDATORY COMPONENTS (implement ALL):

1. IMPORTS - Include ALL necessary imports:
   - Framework imports ({framework})
   - Neural network layers and functions
   - Pretrained model imports if using {arch}
   - Type hints from typing module
   
2. MODEL CLASS - Complete implementation:
   - Class name: Model (or specific like ResNetClassifier)
   - __init__ method with all layer definitions
   - forward method with complete computation graph
   - Support for {arch} architecture
   - Proper initialization of layers
   - Handle num_classes={num_classes}
   
3. HELPER FUNCTIONS:
   - create_model() factory function
   - load_pretrained() if applicable
   - Model loading/saving utilities
   
4. ARCHITECTURE-SPECIFIC CODE:
   - Implement {arch} correctly
   - Use pretrained weights where available
   - Add custom layers for {task}
   - Proper activation functions
   - Dropout/BatchNorm where appropriate
   
5. PRODUCTION FEATURES:
   - Docstrings for all classes/methods
   - Type hints
   - Device handling (CPU/GPU)
   - Input shape validation
   - Error handling

CRITICAL: Generate the COMPLETE file from top to bottom. No placeholders, no TODO comments, no "# rest of implementation". Every function must have a body. Every class must be complete.

START OF model.py:
"""
        return prompt.strip()
    
    def _build_train_prompt(self, context: Dict[str, Any]) -> str:
        task = context["task"]
        framework = context["framework"]
        dataset = context.get("dataset", "dataset.csv")
        dataset_meta = context.get("dataset_metadata", {})
        requirements = context.get("requirements", {})
        
        prompt = f"""
Create a complete train.py file for:
- Task: {task}
- Framework: {framework}
- Dataset path: {dataset}
- Dataset metadata: {json.dumps(dataset_meta, indent=2)}
- User requirements: {json.dumps(requirements, indent=2)}

Requirements:
1. Load data from the provided dataset path (CSV, images, etc.)
2. Implement proper train/val/test splits
3. Create DataLoader with appropriate batch size and transforms
4. Implement training loop with loss, optimizer, and metrics
5. Add validation loop and early stopping
6. Save best model checkpoint
7. Log training progress with tqdm
8. Handle both CPU and GPU
9. Load config from config.yaml
10. Include a main() function

Generate the complete Python file now.
"""
        return prompt.strip()
    
    def _build_enhanced_train_prompt(self, context: Dict[str, Any]) -> str:
        """Enhanced prompt for complete training script"""
        task = context["task"]
        framework = context["framework"]
        dataset = context.get("dataset", "dataset.csv")
        dataset_meta = context.get("dataset_metadata", {})
        requirements = context.get("requirements", {})
        
        # Determine dataset type
        if dataset and dataset.endswith('.csv'):
            data_format = "CSV file"
            load_method = "pandas"
        elif 'image' in task.lower():
            data_format = "Image dataset"
            load_method = "ImageFolder or custom loader"
        else:
            data_format = "Dataset file"
            load_method = "appropriate loader"
        
        prompt = f"""Generate a COMPLETE, PRODUCTION-READY train.py file.

TASK SPECIFICATION:
- ML Task: {task}
- Framework: {framework}
- Dataset path: {dataset}
- Data format: {data_format}

DATASET METADATA:
{json.dumps(dataset_meta, indent=2)}

USER REQUIREMENTS:
{json.dumps(requirements, indent=2)}

MANDATORY COMPONENTS (implement ALL):

1. IMPORTS - Include ALL necessary imports:
   - {framework} and related libraries
   - torch.utils.data or tf.data
   - yaml for config loading
   - argparse for CLI
   - tqdm for progress bars
   - numpy, pandas if needed
   - pathlib for file handling
   - Model class from model.py
   
2. DATA LOADING - Complete implementation:
   - load_data() function that reads from {dataset}
   - Proper handling of {data_format}
   - Train/validation/test split (e.g., 70/15/15)
   - Dataset class if needed
   - Data transforms/augmentation for training
   - DataLoader with proper batch_size, shuffle, num_workers
   
3. TRAINING LOOP - Full implementation:
   - train_epoch() function
   - Iterate over batches
   - Forward pass
   - Loss calculation
   - Backward pass and optimization
   - Progress bar with loss display
   - Handle device (CPU/GPU)
   
4. VALIDATION LOOP - Complete implementation:
   - validate() function
   - No gradient computation
   - Calculate metrics (accuracy, F1, etc.)
   - Return validation loss and metrics
   
5. MAIN TRAINING FUNCTION:
   - Load config from config.yaml
   - Set device (cuda/cpu)
   - Load data
   - Initialize model from model.py
   - Setup optimizer (Adam, SGD, etc.)
   - Setup loss function
   - Training loop over epochs
   - Call train_epoch() and validate()
   - Track best model
   - Save checkpoints
   - Early stopping logic
   
6. CHECKPOINTING:
   - Save best model based on validation metric
   - Save to 'best_model.pt' or 'best_model.h5'
   - Include model state, optimizer state, epoch
   
7. CLI AND MAIN:
   - argparse for --config, --epochs, --batch-size, --lr
   - main() function
   - if __name__ == '__main__' block
   
8. PRODUCTION FEATURES:
   - Error handling
   - Logging
   - Device detection
   - Seed setting for reproducibility
   - Config validation

CRITICAL: Generate the COMPLETE file. Every function must have implementation. No TODOs. No placeholders. No "# implementation here" comments. Write the actual working code.

START OF train.py:
"""
        return prompt.strip()
    
    def _build_test_prompt(self, context: Dict[str, Any]) -> str:
        task = context["task"]
        framework = context["framework"]
        
        prompt = f"""
Create a complete test_model.py file using pytest for:
- Task: {task}
- Framework: {framework}

Requirements:
1. Import pytest, model, and necessary libraries
2. Create fixtures for model, sample data, and config
3. Test model initialization
4. Test forward pass with sample inputs
5. Test output shapes
6. Test model save/load
7. Test data loading functions
8. Test training step (single batch)
9. Add integration test for full training loop (1 epoch)
10. Include edge case tests

Generate the complete Python file now.
"""
        return prompt.strip()
    
    def _extract_code_block(self, response: str) -> str:
        """Extract Python code from LLM response, removing markdown fences and thinking"""
        import re
        response = response.strip()

        # Try to extract from ```python ... ``` blocks
        match = re.search(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
        if match:
            code = match.group(1).strip()
            # If code was truncated mid-sentence, try to fix common issues
            if code and not code.endswith(('\n', ')', ']', '}', '"', "'")):
                # Try to find last complete line
                lines = code.split('\n')
                if len(lines) > 1:
                    # Remove potentially incomplete last line
                    code = '\n'.join(lines[:-1])
            return self._clean_thinking_from_code(code)

        # If no fences, assume entire response is code
        if any(response.startswith(prefix) for prefix in ["import ", "from ", '"""', "'''", "class ", "def ", "#"]):
            return self._clean_thinking_from_code(response)

        # Last resort: try to find Python code in the response
        code_indicators = ["import ", "def ", "class "]
        for indicator in code_indicators:
            if indicator in response:
                # Extract from first code indicator to end
                start_idx = response.find(indicator)
                return self._clean_thinking_from_code(response[start_idx:])

        return self._clean_thinking_from_code(response)

    def _clean_thinking_from_code(self, code: str) -> str:
        """Remove thinking/reasoning comments from generated code"""
        lines = code.split('\n')
        cleaned_lines = []

        # Patterns that indicate thinking/reasoning (not legitimate code comments)
        thinking_patterns = [
            r'^#\s*(let me|first i|now i|i will|i need|thinking|let\'s|we need|i\'ll)',
            r'^#\s*(okay|alright|so|well|hmm|ah|here)',
            r'^#\s*(step \d|next|finally|then)',
            r'^#\s*\.\.\.',
        ]

        import re
        for line in lines:
            line_lower = line.strip().lower()

            # Skip empty thinking comments
            if line.strip() == '#':
                continue

            # Check if line matches thinking patterns
            is_thinking = False
            for pattern in thinking_patterns:
                if re.match(pattern, line_lower):
                    is_thinking = True
                    break

            if not is_thinking:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)
    
    def _generate_basic_tests(self, task: str, framework: str) -> str:
        """Fallback test generation"""
        return f'''"""Basic tests for model"""

import pytest
import torch
from model import Model


def test_model_init():
    """Test model initialization"""
    model = Model(num_classes=10)
    assert model is not None


def test_forward_pass():
    """Test forward pass"""
    model = Model(num_classes=10)
    x = torch.randn(2, 3, 224, 224)
    output = model(x)
    assert output.shape == (2, 10)


def test_model_device():
    """Test model moves to device"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Model(num_classes=10).to(device)
    assert next(model.parameters()).device.type == device.type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
