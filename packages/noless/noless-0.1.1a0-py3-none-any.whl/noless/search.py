"""Dataset search and download functionality"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import os
import json


class DatasetSearcher:
    """Search for datasets across multiple sources"""
    
    def __init__(self):
        self.sources = {
            "huggingface": HuggingFaceSearcher(),
            "uci": UCISearcher()
        }
        self._kaggle_enabled = self._has_kaggle_credentials()
        if self._kaggle_enabled:
            self.sources["kaggle"] = KaggleSearcher()
    
    def search(self, query: str, source: str = "all", limit: int = 10) -> List[Dict]:
        """Search for datasets
        
        Args:
            query: Search query
            source: Source to search (all, huggingface, kaggle, uci)
            limit: Maximum number of results
            
        Returns:
            List of dataset information dictionaries
        """
        results = []
        
        if source == "all":
            for source_name, searcher in self.sources.items():
                try:
                    source_results = searcher.search(query, limit=limit // len(self.sources))
                    results.extend(source_results)
                except Exception as e:
                    print(f"Error searching {source_name}: {e}")
        else:
            if source == "kaggle" and not self._kaggle_enabled:
                raise RuntimeError("Kaggle API credentials not configured. Add kaggle.json to continue.")
            if source in self.sources:
                results = self.sources[source].search(query, limit=limit)
        
        return results[:limit]

    def _has_kaggle_credentials(self) -> bool:
        potential_paths = []
        kaggle_dir = os.environ.get("KAGGLE_CONFIG_DIR")
        if kaggle_dir:
            potential_paths.append(os.path.join(kaggle_dir, "kaggle.json"))
        potential_paths.append(os.path.join(os.path.expanduser("~"), ".kaggle", "kaggle.json"))
        return any(os.path.exists(path) for path in potential_paths)
    
    def download_dataset(self, dataset_id: str, output_dir: str) -> bool:
        """Download a dataset by ID
        
        Args:
            dataset_id: Dataset identifier (format: source:id)
            output_dir: Output directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if ":" in dataset_id:
                source, ds_id = dataset_id.split(":", 1)
                if source in self.sources:
                    return self.sources[source].download(ds_id, output_dir)
            return False
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return False


class HuggingFaceSearcher:
    """Search Hugging Face datasets"""
    
    BASE_URL = "https://huggingface.co/api/datasets"
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Hugging Face datasets"""
        try:
            url = f"{self.BASE_URL}?search={query}&limit={limit}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                datasets = response.json()
                results = []
                
                for ds in datasets[:limit]:
                    results.append({
                        "id": f"huggingface:{ds.get('id', '')}",
                        "name": ds.get("id", "Unknown"),
                        "source": "Hugging Face",
                        "type": "Dataset",
                        "size": ds.get("downloads", "N/A"),
                        "url": f"https://huggingface.co/datasets/{ds.get('id', '')}",
                        "description": ds.get("description", "")[:100]
                    })
                
                return results
        except Exception as e:
            print(f"Hugging Face search error: {e}")
        
        return []
    
    def download(self, dataset_id: str, output_dir: str) -> bool:
        """Download from Hugging Face"""
        try:
            from huggingface_hub import snapshot_download
            os.makedirs(output_dir, exist_ok=True)
            snapshot_download(repo_id=dataset_id, repo_type="dataset", 
                            local_dir=os.path.join(output_dir, dataset_id.replace("/", "_")))
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False


class KaggleSearcher:
    """Search Kaggle datasets"""
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Kaggle datasets"""
        try:
            # Use Kaggle API if available
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            datasets = api.dataset_list(search=query, page_size=limit)
            results = []
            
            for ds in datasets[:limit]:
                results.append({
                    "id": f"kaggle:{ds.ref}",
                    "name": ds.title,
                    "source": "Kaggle",
                    "type": "Dataset",
                    "size": ds.size if hasattr(ds, 'size') else "N/A",
                    "url": f"https://www.kaggle.com/datasets/{ds.ref}",
                    "description": ds.subtitle[:100] if hasattr(ds, 'subtitle') else ""
                })
            
            return results
        except ImportError:
            print("Kaggle API not configured. Install kaggle and setup API key.")
        except Exception as e:
            print(f"Kaggle search error: {e}")
        
        return []
    
    def download(self, dataset_id: str, output_dir: str) -> bool:
        """Download from Kaggle"""
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            os.makedirs(output_dir, exist_ok=True)
            api.dataset_download_files(dataset_id, path=output_dir, unzip=True)
            return True
        except Exception as e:
            print(f"Download error: {e}")
            return False


class UCISearcher:
    """Search UCI Machine Learning Repository"""
    
    BASE_URL = "https://archive.ics.uci.edu/ml"
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search UCI ML Repository"""
        try:
            # UCI doesn't have a public API, so we'll provide popular datasets
            # This is a simplified version - in production, you'd scrape or use an API
            popular_datasets = [
                {
                    "id": "uci:iris",
                    "name": "Iris",
                    "source": "UCI ML",
                    "type": "Classification",
                    "size": "Small",
                    "url": "https://archive.ics.uci.edu/ml/datasets/iris",
                    "description": "Classic iris flower dataset"
                },
                {
                    "id": "uci:wine",
                    "name": "Wine Quality",
                    "source": "UCI ML",
                    "type": "Classification",
                    "size": "Medium",
                    "url": "https://archive.ics.uci.edu/ml/datasets/wine+quality",
                    "description": "Wine quality dataset"
                },
                {
                    "id": "uci:adult",
                    "name": "Adult Income",
                    "source": "UCI ML",
                    "type": "Classification",
                    "size": "Medium",
                    "url": "https://archive.ics.uci.edu/ml/datasets/adult",
                    "description": "Census income dataset"
                }
            ]
            
            # Simple keyword matching
            query_lower = query.lower()
            results = [ds for ds in popular_datasets 
                      if query_lower in ds["name"].lower() or query_lower in ds["description"].lower()]
            
            return results[:limit] if results else popular_datasets[:limit]
        except Exception as e:
            print(f"UCI search error: {e}")
        
        return []
    
    def download(self, dataset_id: str, output_dir: str) -> bool:
        """Download from UCI (placeholder)"""
        print(f"UCI download for {dataset_id} - Manual download may be required")
        return False
