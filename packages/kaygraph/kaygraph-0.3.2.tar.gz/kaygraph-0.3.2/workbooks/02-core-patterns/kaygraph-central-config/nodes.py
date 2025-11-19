"""
Config-aware nodes demonstrating centralized configuration.
"""

import logging
from typing import Dict, Any
from kaygraph import Node

# Mock LLM for demonstration (no external dependencies)
def mock_llm(prompt: str, model: str = "mock", temperature: float = 0.7,
             max_tokens: int = 100) -> str:
    """Mock LLM that returns predictable responses."""
    if "mock" in model.lower() or "test" in model.lower():
        return f"[Mock response for: {prompt[:50]}...]"
    return f"[{model}@{temperature}] Response to: {prompt[:50]}..."


class QueryNode(Node):
    """
    Process user query using config for validation settings.
    """

    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query from shared state."""
        return shared.get("query", "")

    def exec(self, prep_res: str) -> str:
        """Validate and process query using config settings."""
        # Get validation settings from config
        min_length = self.config.get("min_query_length", 1)
        max_length = self.config.get("max_query_length", 1000)

        if len(prep_res) < min_length:
            raise ValueError(f"Query too short (min: {min_length} chars)")

        if len(prep_res) > max_length:
            prep_res = prep_res[:max_length]
            self.logger.warning(f"Query truncated to {max_length} chars")

        return prep_res.strip()

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store validated query."""
        shared["query"] = exec_res
        return None


class ThinkNode(Node):
    """
    Analyze query using config for prompts and LLM parameters.
    """

    def prep(self, shared: Dict[str, Any]) -> str:
        """Get query for analysis."""
        return shared["query"]

    def exec(self, prep_res: str) -> Dict[str, Any]:
        """
        Analyze query using config-based prompts and LLM settings.
        """
        # Get prompt template from config
        prompt_template = self.config.get(
            "think_prompt",
            "Analyze this query: {query}"
        )
        prompt = prompt_template.format(query=prep_res)

        # Get system prompt from config
        system_prompt = self.config.get("system_prompt", "")
        if system_prompt:
            prompt = f"{system_prompt}\n\n{prompt}"

        # Get LLM parameters from config
        model = self.config.get("model", "gpt-4o-mini")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 500)

        # Log if verbose mode enabled
        if self.config.get("verbose", False):
            self.logger.info(f"Using model: {model}, temp: {temperature}")

        # Call LLM (using mock for this example)
        response = mock_llm(prompt, model=model, temperature=temperature,
                          max_tokens=max_tokens)

        # Simple analysis based on response
        needs_search = "search" in prep_res.lower() or "?" in prep_res

        return {
            "reasoning": response,
            "needs_search": needs_search,
            "confidence": 0.8 if needs_search else 0.9
        }

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Dict[str, Any]) -> str:
        """Store analysis and route to next node."""
        shared["analysis"] = exec_res

        if exec_res["needs_search"]:
            return "search"
        else:
            return "answer"


class SearchNode(Node):
    """
    Mock search node using config for search parameters.
    """

    def prep(self, shared: Dict[str, Any]) -> str:
        """Get search query."""
        return shared.get("search_query", shared["query"])

    def exec(self, prep_res: str) -> Dict[str, Any]:
        """
        Execute search using config-based parameters.
        """
        # Get search config
        max_results = self.config.get("max_search_results", 5)
        search_depth = self.config.get("search_depth", "normal")

        # Mock search results
        results = {
            "query": prep_res,
            "results": [
                {"title": f"Result {i}", "url": f"https://example.com/{i}"}
                for i in range(1, max_results + 1)
            ],
            "depth": search_depth
        }

        if self.config.get("verbose", False):
            self.logger.info(f"Found {len(results['results'])} results")

        return results

    def post(self, shared: Dict[str, Any], prep_res: str,
             exec_res: Dict[str, Any]) -> str:
        """Store search results."""
        shared["search_results"] = exec_res
        return None


class AnswerNode(Node):
    """
    Generate final answer using config for prompts and parameters.
    """

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather context for answer generation."""
        return {
            "query": shared["query"],
            "analysis": shared.get("analysis", {}),
            "search_results": shared.get("search_results", {})
        }

    def exec(self, prep_res: Dict[str, Any]) -> str:
        """
        Generate answer using config-based prompts.
        """
        # Get prompt template from config
        prompt_template = self.config.get(
            "answer_prompt",
            "Answer: {query}\nContext: {context}"
        )

        # Build context
        context_parts = []
        if prep_res.get("analysis"):
            context_parts.append(f"Analysis: {prep_res['analysis'].get('reasoning', '')}")

        if prep_res.get("search_results"):
            results = prep_res['search_results'].get('results', [])
            context_parts.append(f"Found {len(results)} search results")

        context = "\n".join(context_parts) if context_parts else "No additional context"

        # Format prompt
        prompt = prompt_template.format(
            query=prep_res["query"],
            context=context
        )

        # Get LLM parameters from config
        model = self.config.get("model", "gpt-4o-mini")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 1000)

        # Generate answer
        answer = mock_llm(prompt, model=model, temperature=temperature,
                         max_tokens=max_tokens)

        return answer

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any],
             exec_res: str) -> str:
        """Store final answer."""
        shared["answer"] = exec_res

        # Log metrics if enabled
        if self.config.get("enable_metrics", False):
            self.logger.info(f"Answer generated: {len(exec_res)} chars")

        return None


class CustomNode(Node):
    """
    Example node with custom config override.
    This node uses different settings than the graph-level config.
    """

    def prep(self, shared: Dict[str, Any]) -> str:
        """Get data."""
        return shared.get("query", "")

    def exec(self, prep_res: str) -> str:
        """
        Process using node-specific config.
        """
        # This node might have custom config different from graph
        custom_setting = self.config.get("custom_setting", "default")
        temperature = self.config.get("temperature", 0.5)

        self.logger.info(f"Custom node using: {custom_setting}, temp: {temperature}")

        return f"Processed with custom config: {prep_res}"

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store result."""
        shared["custom_result"] = exec_res
        return None


if __name__ == "__main__":
    """Test individual nodes with config."""
    from kaygraph import Config

    print("Testing Config-Aware Nodes")
    print("=" * 50)

    # Create test config
    config = Config(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        think_prompt="Analyze: {query}",
        answer_prompt="Answer {query} with context: {context}",
        verbose=True,
        enable_metrics=True
    )

    # Test QueryNode
    print("\n1. Testing QueryNode...")
    query_node = QueryNode(config=config)
    shared = {"query": "What is KayGraph?"}
    query_node.run(shared)
    print(f"   Validated query: {shared['query']}")

    # Test ThinkNode
    print("\n2. Testing ThinkNode...")
    think_node = ThinkNode(config=config)
    think_node.run(shared)
    print(f"   Analysis: {shared['analysis']}")

    # Test AnswerNode
    print("\n3. Testing AnswerNode...")
    answer_node = AnswerNode(config=config)
    answer_node.run(shared)
    print(f"   Answer: {shared['answer'][:100]}...")

    # Test CustomNode with override
    print("\n4. Testing CustomNode with override...")
    custom_config = Config(
        temperature=0.3,  # Override temp
        custom_setting="special_mode"
    )
    custom_node = CustomNode(config=custom_config)
    custom_node.run(shared)
    print(f"   Custom result: {shared['custom_result']}")

    print("\n" + "=" * 50)
    print("All nodes tested successfully!")
