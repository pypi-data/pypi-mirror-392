#!/usr/bin/env python3
"""
Central Config Example - Demonstrates KayGraph's Config system.

This example shows how to:
1. Create centralized configuration for graphs
2. Use config in nodes for prompts and LLM parameters
3. Override config at node level
4. Switch between config profiles (dev/prod/test)
5. Merge configurations dynamically
"""

import logging
from kaygraph import Graph, Config
from nodes import QueryNode, ThinkNode, SearchNode, AnswerNode, CustomNode
from config_profiles import get_config, merge_configs, DEV_CONFIG, PROD_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_basic_config():
    """Example 1: Basic config usage with graph."""
    print("\n" + "=" * 60)
    print("Example 1: Basic Config Usage")
    print("=" * 60)

    # Create config
    config = Config(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        system_prompt="You are a helpful AI assistant.",
        think_prompt="Analyze this query: {query}",
        answer_prompt="Answer: {query}\nContext: {context}",
        verbose=True
    )

    # Build graph with config
    query_node = QueryNode()
    think_node = ThinkNode()
    search_node = SearchNode()
    answer_node = AnswerNode()

    # Connect nodes
    query_node >> think_node
    think_node - "search" >> search_node >> answer_node
    think_node - "answer" >> answer_node

    # Pass config to graph - automatically propagates to all nodes
    graph = Graph(query_node, config=config)

    # Run
    shared = {"query": "What is machine learning?"}
    graph.run(shared)

    print(f"\nQuery: {shared['query']}")
    print(f"Analysis: {shared['analysis']['reasoning'][:80]}...")
    print(f"Answer: {shared['answer'][:80]}...")
    print(f"\n✅ All nodes used the same config automatically!")


def example_2_node_override():
    """Example 2: Node-level config override."""
    print("\n" + "=" * 60)
    print("Example 2: Node-Level Config Override")
    print("=" * 60)

    # Graph-level config (default for all nodes)
    graph_config = Config(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        verbose=True
    )

    # Most nodes use graph config
    query_node = QueryNode()
    think_node = ThinkNode()

    # But this node has custom config
    custom_config = Config(
        temperature=0.3,  # More deterministic
        custom_setting="special_mode",
        verbose=True
    )
    custom_node = CustomNode(config=custom_config)

    query_node >> think_node >> custom_node

    graph = Graph(query_node, config=graph_config)

    # Run
    shared = {"query": "Test query"}
    graph.run(shared)

    print(f"\n✅ QueryNode and ThinkNode used graph config (temp=0.7)")
    print(f"✅ CustomNode used its own config (temp=0.3)")


def example_3_config_profiles():
    """Example 3: Using config profiles (dev/prod)."""
    print("\n" + "=" * 60)
    print("Example 3: Config Profiles (Dev vs Prod)")
    print("=" * 60)

    # Build graph once
    def build_graph():
        query_node = QueryNode()
        think_node = ThinkNode()
        search_node = SearchNode()
        answer_node = AnswerNode()

        query_node >> think_node
        think_node - "search" >> search_node >> answer_node
        think_node - "answer" >> answer_node

        return query_node

    shared = {"query": "What is KayGraph?"}

    # Run with DEV config
    print("\n--- DEV Environment ---")
    dev_graph = Graph(build_graph(), config=DEV_CONFIG)
    dev_shared = shared.copy()
    dev_graph.run(dev_shared)
    print(f"Model: {DEV_CONFIG.get('model')}")
    print(f"Answer: {dev_shared['answer'][:60]}...")

    # Run with PROD config (different prompts and model)
    print("\n--- PROD Environment ---")
    prod_graph = Graph(build_graph(), config=PROD_CONFIG)
    prod_shared = shared.copy()
    prod_graph.run(prod_shared)
    print(f"Model: {PROD_CONFIG.get('model')}")
    print(f"Answer: {prod_shared['answer'][:60]}...")

    print(f"\n✅ Same graph, different configs - easy env switching!")


def example_4_config_merging():
    """Example 4: Merging configurations dynamically."""
    print("\n" + "=" * 60)
    print("Example 4: Dynamic Config Merging")
    print("=" * 60)

    # Start with dev config
    base_config = get_config("dev")

    # Add custom overrides
    custom_overrides = Config(
        model="gpt-4",  # Upgrade model
        custom_feature="enabled",
        max_tokens=2000  # Increase limit
    )

    # Merge configs (custom overrides take precedence)
    merged = merge_configs(base_config, custom_overrides)

    print(f"\nBase model: {base_config.get('model')}")
    print(f"Custom model: {custom_overrides.get('model')}")
    print(f"Merged model: {merged.get('model')}")
    print(f"Merged max_tokens: {merged.get('max_tokens')}")
    print(f"Merged custom_feature: {merged.get('custom_feature')}")
    print(f"Merged max_retries (from base): {merged.get('max_retries')}")

    # Use merged config
    query_node = QueryNode()
    think_node = ThinkNode()
    query_node >> think_node

    graph = Graph(query_node, config=merged)
    shared = {"query": "Test"}
    graph.run(shared)

    print(f"\n✅ Merged config combines best of both worlds!")


def example_5_config_templates():
    """Example 5: Using config for prompt templates."""
    print("\n" + "=" * 60)
    print("Example 5: Prompt Templates via Config")
    print("=" * 60)

    # Config with detailed prompt templates
    config = Config(
        # Simple template
        think_prompt="Quick analysis: {query}",

        # Complex template with multiple placeholders
        answer_prompt="""Question: {query}

Analysis:
{context}

Please provide a comprehensive answer.""",

        # Model settings
        model="gpt-4o-mini",
        temperature=0.7,
        verbose=True
    )

    # Nodes automatically use these templates
    query_node = QueryNode()
    think_node = ThinkNode()
    search_node = SearchNode()
    answer_node = AnswerNode()

    query_node >> think_node
    think_node - "search" >> search_node >> answer_node
    think_node - "answer" >> answer_node

    graph = Graph(query_node, config=config)
    shared = {"query": "Explain KayGraph config system"}
    graph.run(shared)

    print(f"\n✅ Prompts generated from templates!")
    print(f"Answer: {shared['answer'][:80]}...")


def example_6_backward_compatibility():
    """Example 6: Backward compatibility - nodes work without config."""
    print("\n" + "=" * 60)
    print("Example 6: Backward Compatibility")
    print("=" * 60)

    # Old way - no config (still works!)
    query_node = QueryNode()
    think_node = ThinkNode()
    search_node = SearchNode()
    answer_node = AnswerNode()

    query_node >> think_node
    think_node - "search" >> search_node >> answer_node
    think_node - "answer" >> answer_node

    # Graph without config
    graph = Graph(query_node)  # No config parameter

    shared = {"query": "Test backward compatibility"}
    graph.run(shared)

    print(f"\n✅ Nodes work fine without config!")
    print(f"Answer: {shared['answer'][:60]}...")
    print(f"\n📝 Nodes use empty Config() by default with built-in defaults")


def example_7_config_inspection():
    """Example 7: Inspecting and exporting config."""
    print("\n" + "=" * 60)
    print("Example 7: Config Inspection")
    print("=" * 60)

    config = Config(
        model="gpt-4o-mini",
        temperature=0.7,
        max_tokens=500,
        custom_key="custom_value"
    )

    # Get specific values
    print(f"\nModel: {config.get('model')}")
    print(f"Temperature: {config.get('temperature')}")
    print(f"Unknown key with default: {config.get('unknown', 'default_value')}")

    # Export as dict
    config_dict = config.to_dict()
    print(f"\nFull config dict: {config_dict}")

    # Check if config is empty
    empty_config = Config()
    print(f"\nEmpty config bool: {bool(empty_config)}")  # False
    print(f"Non-empty config bool: {bool(config)}")      # True

    # String representation
    print(f"\nConfig repr: {repr(config)}")

    print(f"\n✅ Config inspection complete!")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("KayGraph Central Config Examples")
    print("=" * 60)

    examples = [
        example_1_basic_config,
        example_2_node_override,
        example_3_config_profiles,
        example_4_config_merging,
        example_5_config_templates,
        example_6_backward_compatibility,
        example_7_config_inspection,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            logger.error(f"Example failed: {e}", exc_info=True)

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
