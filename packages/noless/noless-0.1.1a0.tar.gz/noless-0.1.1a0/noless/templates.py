"""Template management for model templates"""

from typing import List, Dict, Optional


class TemplateManager:
    """Manage model templates"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> List[Dict]:
        """Load available templates"""
        return [
            {
                "name": "image-classification-pytorch",
                "task": "image-classification",
                "framework": "pytorch",
                "description": "CNN for image classification using PyTorch with ResNet backbone"
            },
            {
                "name": "image-classification-tf",
                "task": "image-classification",
                "framework": "tensorflow",
                "description": "CNN for image classification using TensorFlow with transfer learning"
            },
            {
                "name": "text-classification-pytorch",
                "task": "text-classification",
                "framework": "pytorch",
                "description": "Text classifier using BERT with PyTorch"
            },
            {
                "name": "text-classification-tf",
                "task": "text-classification",
                "framework": "tensorflow",
                "description": "Text classifier using BERT with TensorFlow"
            },
            {
                "name": "object-detection-pytorch",
                "task": "object-detection",
                "framework": "pytorch",
                "description": "Object detection using Faster R-CNN with PyTorch"
            },
            {
                "name": "sentiment-analysis",
                "task": "sentiment-analysis",
                "framework": "pytorch",
                "description": "Sentiment analysis model using transformers"
            },
            {
                "name": "regression-sklearn",
                "task": "regression",
                "framework": "sklearn",
                "description": "Linear regression model using scikit-learn"
            },
            {
                "name": "clustering-sklearn",
                "task": "clustering",
                "framework": "sklearn",
                "description": "K-means clustering using scikit-learn"
            },
            {
                "name": "time-series-pytorch",
                "task": "time-series",
                "framework": "pytorch",
                "description": "LSTM for time series forecasting"
            }
        ]
    
    def list_templates(self, task_filter: Optional[str] = None) -> List[Dict]:
        """List available templates
        
        Args:
            task_filter: Filter templates by task type
            
        Returns:
            List of template dictionaries
        """
        if task_filter:
            return [t for t in self.templates if t["task"] == task_filter]
        return self.templates
    
    def get_template(self, name: str) -> Optional[Dict]:
        """Get a specific template by name"""
        for template in self.templates:
            if template["name"] == name:
                return template
        return None
