import click
from enum import Enum
import llm
from llm.default_plugins.openai_models import Chat, AsyncChat
from pathlib import Path
from pydantic import Field, field_validator
from typing import Optional, Union
import json
import time
import httpx


def get_electronhub_models():
    models = fetch_cached_json(
        url="https://api.electronhub.ai/v1/models",
        path=llm.user_dir() / "electronhub_models.json",
        cache_timeout=3600,
    )["data"]
    return models


def get_supports_images(model_definition):
    # ElectronHub models may have different structure, check for vision/multimodal support
    try:
        # Check if model has vision capabilities
        if "vision" in model_definition.get("id", "").lower():
            return True
        # Check capabilities if available
        capabilities = model_definition.get("capabilities", {})
        return capabilities.get("vision", False) or capabilities.get("multimodal", False)
    except (KeyError, AttributeError):
        return False


def has_parameter(model_definition, parameter):
    try:
        # Check if model supports specific parameters
        capabilities = model_definition.get("capabilities", {})
        if parameter == "structured_outputs":
            return capabilities.get("structured_outputs", False)
        elif parameter == "tools":
            return capabilities.get("function_calling", False) or capabilities.get("tools", False)
        return False
    except (KeyError, AttributeError):
        return False


class ReasoningEffortEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class _mixin:
    class Options(Chat.Options):
        provider: Optional[Union[dict, str]] = Field(
            description=("JSON object to control provider routing"),
            default=None,
        )
        reasoning_effort: Optional[ReasoningEffortEnum] = Field(
            description='One of "high", "medium", or "low" to control reasoning effort',
            default=None,
        )
        reasoning_max_tokens: Optional[int] = Field(
            description="Specific token limit to control reasoning effort",
            default=None,
        )
        reasoning_enabled: Optional[bool] = Field(
            description="Set to true to enable reasoning with default parameters",
            default=None,
        )

        @field_validator("provider")
        def validate_provider(cls, provider):
            if provider is None:
                return None

            if isinstance(provider, str):
                try:
                    return json.loads(provider)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON in provider string")
            return provider

    def build_kwargs(self, prompt, stream):
        kwargs = super().build_kwargs(prompt, stream)
        kwargs.pop("provider", None)
        kwargs.pop("reasoning_effort", None)
        kwargs.pop("reasoning_max_tokens", None)
        kwargs.pop("reasoning_enabled", None)
        extra_body = {}
        if prompt.options.provider:
            extra_body["provider"] = prompt.options.provider
        reasoning = {}
        if prompt.options.reasoning_effort:
            reasoning["effort"] = prompt.options.reasoning_effort
        if prompt.options.reasoning_max_tokens:
            reasoning["max_tokens"] = prompt.options.reasoning_max_tokens
        if prompt.options.reasoning_enabled is not None:
            reasoning["enabled"] = prompt.options.reasoning_enabled
        if reasoning:
            extra_body["reasoning"] = reasoning
        if extra_body:
            kwargs["extra_body"] = extra_body
        return kwargs


class ElectronHubChat(_mixin, Chat):
    needs_key = "electronhub"
    key_env_var = "ELECTRONHUB_API_KEY"

    def __str__(self):
        return "ElectronHub: {}".format(self.model_id)


class ElectronHubAsyncChat(_mixin, AsyncChat):
    needs_key = "electronhub"
    key_env_var = "ELECTRONHUB_API_KEY"

    def __str__(self):
        return "ElectronHub: {}".format(self.model_id)


@llm.hookimpl
def register_models(register):
    # Only do this if the electronhub key is set
    key = llm.get_key("", "electronhub", "ELECTRONHUB_API_KEY")
    if not key:
        return
    for model_definition in get_electronhub_models():
        supports_images = get_supports_images(model_definition)
        kwargs = dict(
            model_id="electronhub/{}".format(model_definition["id"]),
            model_name=model_definition["id"],
            vision=supports_images,
            supports_schema=has_parameter(model_definition, "structured_outputs"),
            supports_tools=has_parameter(model_definition, "tools"),
            api_base="https://api.electronhub.ai/v1",
        )
        register(
            ElectronHubChat(**kwargs),
            ElectronHubAsyncChat(**kwargs),
        )


class DownloadError(Exception):
    pass


def fetch_cached_json(url, path, cache_timeout):
    path = Path(path)

    # Create directories if not exist
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.is_file():
        # Get the file's modification time
        mod_time = path.stat().st_mtime
        # Check if it's more than the cache_timeout old
        if time.time() - mod_time < cache_timeout:
            # If not, load the file
            with open(path, "r") as file:
                return json.load(file)

    # Try to download the data
    try:
        response = httpx.get(
            url,
            headers={"Authorization": f"Bearer {llm.get_key('', 'electronhub', 'ELECTRONHUB_API_KEY')}"},
            follow_redirects=True
        )
        response.raise_for_status()  # This will raise an HTTPError if the request fails

        # If successful, write to the file
        with open(path, "w") as file:
            json.dump(response.json(), file)

        return response.json()
    except httpx.HTTPError:
        # If there's an existing file, load it
        if path.is_file():
            with open(path, "r") as file:
                return json.load(file)
        else:
            # If not, raise an error
            raise DownloadError(
                f"Failed to download data and no cache is available at {path}"
            )


@llm.hookimpl
def register_commands(cli):
    @cli.group()
    def electronhub():
        "Commands relating to the llm-electronhub plugin"

    @electronhub.command()
    @click.option("--chat-only", is_flag=True, help="List only chat-capable models")
    @click.option("json_", "--json", is_flag=True, help="Output as JSON")
    def models(chat_only, json_):
        "List of ElectronHub models"
        all_models = get_electronhub_models()

        if chat_only:
            # Filter for models that support chat completions
            all_models = [
                model for model in all_models
                if model.get("capabilities", {}).get("chat_completion", True)
            ]

        if json_:
            click.echo(json.dumps(all_models, indent=2))
        else:
            # Custom format
            for model in all_models:
                bits = []
                bits.append(f"- id: {model['id']}")
                if "name" in model:
                    bits.append(f"  name: {model['name']}")
                if "context_length" in model:
                    bits.append(f"  context_length: {model['context_length']:,}")
                elif "max_tokens" in model:
                    bits.append(f"  max_tokens: {model['max_tokens']:,}")

                capabilities = model.get("capabilities", {})
                if capabilities:
                    bits.append("  capabilities:")
                    for key, value in capabilities.items():
                        bits.append(f"    {key}: {value}")

                bits.append(f"  supports_schema: {has_parameter(model, 'structured_outputs')}")
                bits.append(f"  supports_tools: {has_parameter(model, 'tools')}")
                bits.append(f"  vision: {get_supports_images(model)}")

                pricing = model.get("pricing", {})
                if pricing:
                    formatted_pricing = format_pricing(pricing)
                    if formatted_pricing:
                        bits.append("  pricing: " + formatted_pricing)

                click.echo("\n".join(bits) + "\n")

    @electronhub.command()
    @click.option("--key", help="Key to inspect")
    def key(key):
        "View information for the current key"
        key = llm.get_key(key, "electronhub", "ELECTRONHUB_API_KEY")
        click.echo(f"ElectronHub API Key: {key[:20]}...{key[-4:]}")
        click.echo("\nFetching available models...")
        try:
            models = get_electronhub_models()
            click.echo(f"Total models available: {len(models)}")
            chat_models = [m for m in models if m.get("capabilities", {}).get("chat_completion", True)]
            click.echo(f"Chat-capable models: {len(chat_models)}")
        except Exception as e:
            click.echo(f"Error fetching models: {e}")


def format_price(key, price_value):
    """Format a price value with appropriate scaling and no trailing zeros."""
    # Handle both string and numeric inputs
    try:
        price = float(price_value)
    except (ValueError, TypeError):
        return None

    if price == 0:
        return None

    # Determine scale based on magnitude
    if price < 0.0001:
        scale = 1000000
        suffix = "/M"
    elif price < 0.001:
        scale = 1000
        suffix = "/K"
    elif price < 1:
        scale = 1000
        suffix = "/K"
    else:
        scale = 1
        suffix = ""

    # Scale the price
    scaled_price = price * scale

    # Format without trailing zeros
    # Convert to string and remove trailing .0
    price_str = (
        f"{scaled_price:.10f}".rstrip("0").rstrip(".")
        if "." in f"{scaled_price:.10f}"
        else f"{scaled_price:.0f}"
    )

    return f"{key} ${price_str}{suffix}"


def format_pricing(pricing_dict):
    formatted_parts = []
    for key, value in pricing_dict.items():
        formatted_price = format_price(key, value)
        if formatted_price:
            formatted_parts.append(formatted_price)
    return ", ".join(formatted_parts)
