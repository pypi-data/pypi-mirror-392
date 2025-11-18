"""Smart query understanding using small LLMs for better dataset search."""

import json
import re
from typing import Dict, Any, List, Optional
from rich.console import Console
from noless.ollama_client import OllamaClient
from noless.local_models import LocalModelRegistry

console = Console()


def _robust_json_parse(text: str) -> Optional[Dict[str, Any]]:
    """Robustly parse JSON from LLM response, handling common issues."""
    text = text.strip()

    # Method 1: Try to parse the entire response
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Method 2: Find JSON block between ```json and ```
    json_block_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Method 3: Find the outermost { } pair with proper brace matching
    start_idx = text.find('{')
    if start_idx != -1:
        brace_count = 0
        end_idx = -1
        in_string = False
        escape_next = False

        for i in range(start_idx, len(text)):
            char = text[i]

            if escape_next:
                escape_next = False
                continue

            if char == '\\':
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_idx = i
                        break

        if end_idx != -1:
            json_str = text[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Try to fix common issues
                json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass

    # Method 4: Try to find just the first simple object
    match = re.search(r'\{[^{}]*\}', text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


class QueryUnderstanding:
    """Use small LLMs to understand user queries and extract better search keywords."""

    def __init__(self, ollama_client: Optional[OllamaClient] = None):
        self.client = ollama_client or OllamaClient()
        self.small_model = self._find_small_model()

    def _find_small_model(self) -> Optional[str]:
        """Find a small, fast model for query understanding."""
        if not self.client.is_available():
            return None

        try:
            registry = LocalModelRegistry(self.client)
            models = registry.available_models()

            # Priority list for small models (fastest/smallest first)
            small_model_priority = [
                "smollm",
                "gemma:2b",
                "qwen2:0.5b",
                "qwen2:1.5b",
                "phi3:mini",
                "phi3",
                "tinyllama",
                "llama3.2:1b",
                "llama3.2:3b",
                "gemma3:4b",
                "gemma:7b",
            ]

            # Check for available small models
            for target in small_model_priority:
                for model in models:
                    model_name = model.name.lower()
                    if target in model_name or model_name.startswith(target):
                        console.print(f"[dim]Using {model.name} for query understanding[/dim]")
                        return model.name

            # Fallback to any small model (< 8B)
            for model in models:
                size = model.size.lower()
                if any(s in size for s in ["2b", "3b", "4b", "1.5b", "0.5b", "1b"]):
                    console.print(f"[dim]Using {model.name} for query understanding[/dim]")
                    return model.name

            # If no small model, use the first available
            if models:
                console.print(f"[dim]Using {models[0].name} for query understanding[/dim]")
                return models[0].name

        except Exception as e:
            console.print(f"[dim]Could not find small model: {e}[/dim]")

        return None

    def understand_query(self, user_query: str) -> Dict[str, Any]:
        """Understand user query and extract semantic information."""
        if not self.small_model:
            return self._fallback_understanding(user_query)

        prompt = f"""Analyze this user's machine learning project request:

"{user_query}"

Extract:
1. Main ML task (classification, regression, etc.)
2. Data domain (images, text, tabular, audio, etc.)
3. Specific subject (cats, sentiment, housing prices, etc.)
4. Dataset keywords (specific terms to search for)
5. Dataset synonyms (alternative search terms)

Return ONLY a JSON object:
{{
    "task": "main ML task",
    "domain": "data type",
    "subject": "specific subject matter",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "synonyms": ["synonym1", "synonym2"],
    "search_queries": ["full search query 1", "full search query 2"]
}}

Examples:
- "classify dog breeds" -> {{"task": "classification", "domain": "images", "subject": "dog breeds", "keywords": ["dog", "breeds", "canine"], "synonyms": ["puppy", "pets"], "search_queries": ["dog breed image classification", "canine breeds dataset"]}}
- "predict house prices" -> {{"task": "regression", "domain": "tabular", "subject": "housing", "keywords": ["house", "prices", "real estate"], "synonyms": ["property", "homes"], "search_queries": ["house prices prediction", "real estate regression"]}}

Return ONLY valid JSON, no explanation."""

        try:
            response = self.client.generate(
                self.small_model,
                prompt,
                system="You are a query understanding expert. Extract semantic information from user requests. Return only valid JSON.",
                temperature=0.1
            )

            # Parse JSON response using robust parser
            result = _robust_json_parse(response)
            if result:
                # Validate and clean result
                return self._validate_understanding(result, user_query)
            else:
                console.print(f"[dim]Could not parse LLM response, using fallback[/dim]")
        except Exception as e:
            console.print(f"[dim]Query understanding failed: {e}[/dim]")

        return self._fallback_understanding(user_query)

    def _validate_understanding(self, result: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Validate and clean the understanding result."""
        # Ensure required keys exist
        if "keywords" not in result:
            result["keywords"] = self._extract_basic_keywords(original_query)

        if "synonyms" not in result:
            result["synonyms"] = []

        if "search_queries" not in result:
            result["search_queries"] = [original_query]

        # Clean keywords - remove stopwords and short words
        stopwords = {"the", "and", "that", "this", "with", "from", "your", "what", "have",
                     "want", "need", "build", "create", "make", "model", "dataset", "data",
                     "classify", "predict", "train", "learn", "machine", "learning", "ai"}

        cleaned_keywords = []
        for kw in result["keywords"]:
            if isinstance(kw, str):
                kw = kw.lower().strip()
                if kw not in stopwords and len(kw) >= 3:
                    cleaned_keywords.append(kw)

        result["keywords"] = cleaned_keywords[:6]  # Limit to 6 keywords

        # Ensure search queries are strings
        result["search_queries"] = [str(q) for q in result.get("search_queries", [])[:3]]

        return result

    def _fallback_understanding(self, query: str) -> Dict[str, Any]:
        """Fallback to basic keyword extraction if LLM not available."""
        keywords = self._extract_basic_keywords(query)

        return {
            "task": "classification",
            "domain": "unknown",
            "subject": " ".join(keywords[:2]) if keywords else "general",
            "keywords": keywords,
            "synonyms": [],
            "search_queries": [query]
        }

    def _extract_basic_keywords(self, text: str) -> List[str]:
        """Basic keyword extraction without LLM."""
        stopwords = {"the", "and", "that", "this", "with", "from", "your", "what", "have",
                     "want", "need", "object", "model", "build", "dataset", "data", "which",
                     "able", "tell", "classifier", "classification", "project", "using",
                     "create", "make", "train", "learning", "machine", "predict", "predict"}

        tokens = re.findall(r"[A-Za-z0-9]+", text.lower())
        keywords = []
        for token in tokens:
            if token not in stopwords and not token.isdigit() and len(token) >= 3:
                if token not in keywords:
                    keywords.append(token)
                if len(keywords) >= 6:
                    break

        return keywords or ["classification"]

    def get_optimized_search_terms(self, user_query: str) -> Dict[str, Any]:
        """Get optimized search terms for dataset discovery."""
        console.print("[dim]🧠 Understanding your query...[/dim]")

        understanding = self.understand_query(user_query)

        # Combine keywords and synonyms for broader search
        all_terms = list(set(understanding["keywords"] + understanding.get("synonyms", [])))

        # Generate additional search variations
        search_variations = understanding.get("search_queries", [])

        # Add domain-specific terms
        if understanding.get("domain") == "images":
            all_terms.extend(["image", "visual", "picture"])
        elif understanding.get("domain") == "text":
            all_terms.extend(["text", "nlp", "corpus"])
        elif understanding.get("domain") == "tabular":
            all_terms.extend(["csv", "tabular", "structured"])

        # Remove duplicates
        all_terms = list(set(all_terms))

        result = {
            "primary_keywords": understanding["keywords"],
            "all_search_terms": all_terms[:10],
            "search_queries": search_variations,
            "task": understanding.get("task", "classification"),
            "domain": understanding.get("domain", "unknown"),
            "subject": understanding.get("subject", "general")
        }

        console.print(f"[green]✓[/green] [dim]Extracted keywords: {', '.join(result['primary_keywords'])}[/dim]")

        return result

    def suggest_dataset_names(self, query_understanding: Dict[str, Any]) -> List[str]:
        """Suggest potential dataset names based on understanding."""
        suggestions = []

        subject = query_understanding.get("subject", "")
        task = query_understanding.get("task", "classification")
        keywords = query_understanding.get("primary_keywords", [])

        # Common dataset patterns
        if subject:
            suggestions.append(f"{subject}")
            suggestions.append(f"{subject}_{task}")

        for kw in keywords[:3]:
            suggestions.append(kw)

        # Add common dataset suffixes
        if task == "classification":
            suggestions.extend([f"{keywords[0]}_classification" if keywords else "classification"])
        elif task == "regression":
            suggestions.extend([f"{keywords[0]}_regression" if keywords else "regression"])

        return list(set(suggestions))[:8]


def get_smart_keywords(user_query: str, ollama_client: Optional[OllamaClient] = None) -> Dict[str, Any]:
    """Convenience function to get smart keywords from user query."""
    qu = QueryUnderstanding(ollama_client)
    return qu.get_optimized_search_terms(user_query)
