"""
Configuration profiles for different environments and use cases.
"""

from kaygraph import Config


# Development config - fast and cheap
DEV_CONFIG = Config(
    # LLM settings
    model="gpt-4o-mini",
    temperature=0.5,
    max_tokens=500,

    # System prompts
    system_prompt="You are a helpful AI assistant in development mode.",

    # Prompt templates
    think_prompt="Analyze this query: {query}\nDetermine if search is needed.",
    search_prompt="Search for: {query}",
    answer_prompt="Answer: {query}\nContext: {context}",

    # Retry settings
    max_retries=2,
    retry_wait=1,

    # Feature flags
    enable_logging=True,
    enable_metrics=True,
    verbose=True
)


# Production config - high quality
PROD_CONFIG = Config(
    # LLM settings
    model="gpt-4",
    temperature=0.7,
    max_tokens=2000,

    # System prompts
    system_prompt="You are a professional AI assistant providing high-quality responses.",

    # Prompt templates
    think_prompt="""Carefully analyze this user query: {query}

Consider:
1. What information is needed?
2. Is web search required?
3. What's the best approach?

Provide your analysis.""",

    search_prompt="Find comprehensive information about: {query}",

    answer_prompt="""Generate a complete answer to: {query}

Available context:
{context}

Requirements:
- Be accurate and thorough
- Cite sources when available
- Provide actionable information""",

    # Retry settings
    max_retries=3,
    retry_wait=2,

    # Feature flags
    enable_logging=True,
    enable_metrics=True,
    verbose=False
)


# Testing config - mock responses
TEST_CONFIG = Config(
    # Mock LLM settings
    model="mock",
    temperature=0.0,
    max_tokens=100,

    # Simple prompts for testing
    system_prompt="Test mode",
    think_prompt="Think: {query}",
    search_prompt="Search: {query}",
    answer_prompt="Answer: {query}",

    # No retries in tests
    max_retries=1,
    retry_wait=0,

    # Testing flags
    enable_logging=False,
    enable_metrics=False,
    verbose=False,
    mock_mode=True
)


# Experimental config - trying new models
EXPERIMENTAL_CONFIG = Config(
    # New model to test
    model="o1-mini",
    temperature=1.0,
    max_tokens=4000,

    # Creative prompts
    system_prompt="You are an experimental AI exploring new approaches.",

    think_prompt="""Let's think creatively about: {query}

Explore multiple angles and innovative solutions.""",

    search_prompt="Discover novel information about: {query}",

    answer_prompt="""Provide an innovative answer to: {query}

Context: {context}

Be creative and thorough.""",

    # Standard settings
    max_retries=3,
    retry_wait=2,

    # Experimental flags
    enable_logging=True,
    enable_metrics=True,
    verbose=True,
    experimental=True
)


# Budget config - minimize costs
BUDGET_CONFIG = Config(
    # Cheapest model
    model="gpt-3.5-turbo",
    temperature=0.3,
    max_tokens=300,

    # Concise prompts
    system_prompt="You are a concise AI assistant.",
    think_prompt="Analyze: {query}",
    search_prompt="{query}",
    answer_prompt="Answer {query} briefly using {context}",

    # Minimal retries
    max_retries=1,
    retry_wait=0,

    # Feature flags
    enable_logging=False,
    enable_metrics=False,
    verbose=False
)


def get_config(environment: str = "dev") -> Config:
    """
    Get configuration for specified environment.

    Args:
        environment: One of "dev", "prod", "test", "experimental", "budget"

    Returns:
        Config object for the environment
    """
    configs = {
        "dev": DEV_CONFIG,
        "prod": PROD_CONFIG,
        "test": TEST_CONFIG,
        "experimental": EXPERIMENTAL_CONFIG,
        "budget": BUDGET_CONFIG
    }

    config = configs.get(environment.lower())
    if not config:
        raise ValueError(f"Unknown environment: {environment}. "
                        f"Use one of: {list(configs.keys())}")

    return config


def merge_configs(*configs: Config) -> Config:
    """
    Merge multiple configs (later configs override earlier ones).

    Args:
        *configs: Config objects to merge

    Returns:
        Merged Config
    """
    if not configs:
        return Config()

    result = configs[0]
    for config in configs[1:]:
        result = result.merge(config)

    return result


if __name__ == "__main__":
    """Test config profiles."""
    print("Config Profiles Demo")
    print("=" * 50)

    # Show all profiles
    environments = ["dev", "prod", "test", "experimental", "budget"]

    for env in environments:
        config = get_config(env)
        print(f"\n{env.upper()} Config:")
        print(f"  Model: {config.get('model')}")
        print(f"  Temperature: {config.get('temperature')}")
        print(f"  Max Tokens: {config.get('max_tokens')}")
        print(f"  Max Retries: {config.get('max_retries')}")
        print(f"  Verbose: {config.get('verbose')}")

    # Demo config merging
    print("\n" + "=" * 50)
    print("\nConfig Merging Demo:")
    print("-" * 50)

    # Start with dev config
    base = DEV_CONFIG

    # Override with custom settings
    custom = Config(
        model="gpt-4",  # Upgrade model
        temperature=0.9,  # Increase creativity
        custom_setting="value"  # Add new setting
    )

    # Merge
    merged = merge_configs(base, custom)

    print(f"Base model: {base.get('model')}")
    print(f"Custom model: {custom.get('model')}")
    print(f"Merged model: {merged.get('model')}")
    print(f"Merged temperature: {merged.get('temperature')}")
    print(f"Merged custom_setting: {merged.get('custom_setting')}")
    print(f"Merged max_retries (from base): {merged.get('max_retries')}")
