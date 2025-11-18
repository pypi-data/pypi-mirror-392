"""OpenML Dataset Search Integration"""

import openml
from typing import List, Dict, Optional
import pandas as pd
import re


class OpenMLSearcher:
    """Search and download datasets from OpenML"""
    
    def __init__(self):
        openml.config.apikey = None  # Can be set by user
        openml.config.cache_directory = "./openml_cache"
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Search OpenML for datasets
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of dataset information dictionaries
        """
        try:
            # Search datasets
            datasets = openml.datasets.list_datasets(output_format='dataframe')
            
            if datasets.empty:
                return []
            
            def _tokenize(text: str) -> List[str]:
                tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
                return [tok for tok in tokens if len(tok) > 2]

            keywords = _tokenize(query or "")
            if not keywords and query and query.strip():
                keywords = [query.strip().lower()]
            search_series = []
            for column in ["name", "description", "format", "tag"]:
                if column in datasets.columns:
                    search_series.append(datasets[column].astype(str).str.lower())

            if not search_series:
                filtered = datasets.head(limit)
            else:
                mask = pd.Series(False, index=datasets.index)
                if not keywords:
                    keywords = [query.lower()] if query else []
                for keyword in keywords or [""]:
                    if not keyword:
                        continue
                    keyword_mask = pd.Series(False, index=datasets.index)
                    for series in search_series:
                        keyword_mask = keyword_mask | series.str.contains(keyword, na=False)
                    mask = mask | keyword_mask
                filtered = datasets[mask].head(limit) if mask.any() else datasets.head(limit)
            
            results = []
            for idx, row in filtered.iterrows():
                results.append({
                    "id": f"openml:{row['did']}",
                    "name": row['name'],
                    "source": "OpenML",
                    "type": row.get('format', 'Dataset'),
                    "size": f"{row.get('NumberOfInstances', 'N/A')} instances",
                    "features": row.get('NumberOfFeatures', 'N/A'),
                    "url": f"https://www.openml.org/d/{row['did']}",
                    "description": row.get('name', '')[:100]
                })
            
            return results
            
        except Exception as e:
            print(f"OpenML search error: {e}")
            return []
    
    def get_dataset_details(self, dataset_id: int) -> Optional[Dict]:
        """Get detailed information about a dataset"""
        try:
            dataset = openml.datasets.get_dataset(dataset_id)
            
            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format="dataframe",
                target=dataset.default_target_attribute
            )
            
            return {
                "id": dataset_id,
                "name": dataset.name,
                "description": dataset.description,
                "format": dataset.format,
                "num_instances": len(X),
                "num_features": len(attribute_names),
                "target": dataset.default_target_attribute,
                "features": attribute_names,
                "data_preview": X.head(),
                "target_preview": y.head() if y is not None else None
            }
        except Exception as e:
            print(f"Error getting dataset details: {e}")
            return None
    
    def download_dataset(self, dataset_id: int, output_dir: str = "./datasets") -> Optional[str]:
        """Download a dataset from OpenML
        
        Args:
            dataset_id: OpenML dataset ID
            output_dir: Directory to save the dataset
            
        Returns:
            Path to the downloaded CSV if successful, otherwise None
        """
        try:
            dataset = openml.datasets.get_dataset(dataset_id)
            
            X, y, categorical_indicator, attribute_names = dataset.get_data(
                dataset_format="dataframe",
                target=dataset.default_target_attribute
            )
            
            # Save to CSV
            import os
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"{dataset.name}_{dataset_id}.csv")
            
            if y is not None:
                df = pd.concat([X, y], axis=1)
            else:
                df = X
            
            df.to_csv(output_path, index=False)
            
            # Save metadata
            metadata = {
                "name": dataset.name,
                "description": dataset.description,
                "num_instances": len(X),
                "num_features": len(attribute_names),
                "features": attribute_names,
                "target": dataset.default_target_attribute
            }
            
            import json
            metadata_path = os.path.join(output_dir, f"{dataset.name}_{dataset_id}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            print(f"Dataset saved to: {output_path}")
            print(f"Metadata saved to: {metadata_path}")
            
            return output_path
            
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return None
    
    def get_popular_datasets(self, limit: int = 10) -> List[Dict]:
        """Get popular/featured datasets from OpenML"""
        try:
            datasets = openml.datasets.list_datasets(output_format='dataframe')
            
            if datasets.empty:
                return []
            
            # Sort by number of downloads or likes
            if 'NumberOfDownloads' in datasets.columns:
                popular = datasets.nlargest(limit, 'NumberOfDownloads')
            else:
                popular = datasets.head(limit)
            
            results = []
            for idx, row in popular.iterrows():
                results.append({
                    "id": f"openml:{row['did']}",
                    "name": row['name'],
                    "source": "OpenML",
                    "type": "Dataset",
                    "size": f"{row.get('NumberOfInstances', 'N/A')} instances",
                    "features": row.get('NumberOfFeatures', 'N/A'),
                    "url": f"https://www.openml.org/d/{row['did']}"
                })
            
            return results
            
        except Exception as e:
            print(f"Error getting popular datasets: {e}")
            return []
    
    def search_by_task(self, task_type: str, limit: int = 10) -> List[Dict]:
        """Search datasets suitable for a specific task type
        
        Args:
            task_type: Task type (classification, regression, clustering, etc.)
            limit: Maximum number of results
        """
        task_keywords = {
            "classification": ["classification", "class", "categorical"],
            "regression": ["regression", "numeric", "continuous"],
            "clustering": ["clustering", "unsupervised"],
            "time-series": ["time", "series", "temporal"],
            "image": ["image", "vision", "picture"],
            "text": ["text", "nlp", "language"]
        }
        
        keywords = task_keywords.get(task_type.lower(), [task_type])
        
        all_results = []
        for keyword in keywords:
            results = self.search(keyword, limit=limit // len(keywords) + 1)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in all_results:
            if result['id'] not in seen:
                seen.add(result['id'])
                unique_results.append(result)
        
        return unique_results[:limit]
