"""Utility functions for NoLess"""

import os
import requests
from typing import Optional


def download_file(url: str, output_path: str, chunk_size: int = 8192) -> bool:
    """Download a file from URL
    
    Args:
        url: URL to download from
        output_path: Path to save the file
        chunk_size: Download chunk size
        
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False


def validate_config(config: dict) -> bool:
    """Validate configuration dictionary
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = ["task", "framework", "training"]
    
    for key in required_keys:
        if key not in config:
            print(f"Missing required config key: {key}")
            return False
    
    return True


def get_model_size(num_parameters: int) -> str:
    """Get human-readable model size
    
    Args:
        num_parameters: Number of model parameters
        
    Returns:
        Formatted string (e.g., "10.5M parameters")
    """
    if num_parameters < 1000:
        return f"{num_parameters} parameters"
    elif num_parameters < 1_000_000:
        return f"{num_parameters/1000:.1f}K parameters"
    elif num_parameters < 1_000_000_000:
        return f"{num_parameters/1_000_000:.1f}M parameters"
    else:
        return f"{num_parameters/1_000_000_000:.1f}B parameters"


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"
