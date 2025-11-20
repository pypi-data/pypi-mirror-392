"""Model Pricing - Token pricing for LLM cost calculation"""

# Copyright 2025-present aiiware.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from aii.data.providers.model_catalog import get_model_pricing as _get_catalog_pricing


# v0.9.3: Pricing now loaded dynamically from llm-models.catalog.2025-11-18.json
# This dict serves as a fallback for models not in catalog
MODEL_PRICING_FALLBACK = {
    # No fallback models currently needed - all active models in catalog
}


def get_pricing(model: str) -> dict:
    """
    Get pricing for a model, checking catalog first, then fallback.

    Args:
        model: Model ID (lowercase)

    Returns:
        Dict with 'input' and 'output' keys, or empty dict if not found
    """
    # Try catalog first
    pricing = _get_catalog_pricing(model)
    if pricing:
        return pricing

    # Try fallback
    return MODEL_PRICING_FALLBACK.get(model.lower(), {})


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate estimated cost in USD.

    Args:
        model: Model name, optionally with provider prefix (e.g., "openai:gpt-4o-mini")
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Estimated cost in USD

    Example:
        >>> calculate_cost("gpt-5.1", 1000, 500)  # $1.25/M input, $10/M output
        0.006...
    """
    # Strip provider prefix if present (e.g., "openai:gpt-4o-mini" -> "gpt-4o-mini")
    model_name = model.split(":")[-1] if ":" in model else model

    pricing = get_pricing(model_name.lower())
    if not pricing:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost
