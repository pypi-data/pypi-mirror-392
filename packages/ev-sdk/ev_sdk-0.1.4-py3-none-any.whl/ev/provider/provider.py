from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, cast

from daft.ai.provider import PROVIDERS, Provider
from typing_extensions import Unpack

if TYPE_CHECKING:
    from daft.ai.openai.typing import OpenAIProviderOptions
    from daft.ai.protocols import (
        PrompterDescriptor,
        TextEmbedderDescriptor,
    )

    from ev.provider.typing import DaftProviderOptions


def not_implemented_err(provider: Provider, method: str) -> NotImplementedError:
    return NotImplementedError(f"{method} is not currently implemented for the '{provider.name}' provider")


def load_daft_provider(name: str | None = None, **options: Unpack[DaftProviderOptions]) -> Provider:
    try:
        # Check if openai is available before instantiating the provider
        import importlib.util

        if importlib.util.find_spec("openai") is None:
            raise ImportError("openai package not found")

        return DaftProvider(name, **options)
    except ImportError as e:
        # The daft provider requires the openai package, fail fast.
        raise ImportError("The Daft provider requires the 'openai' package. Install it with: pip install openai") from e


#
# PATCHING DAFT'S PROVIDERS LOOKUP TABLE
#

PROVIDERS["daft"] = load_daft_provider  # type: ignore


class DaftProvider(Provider):
    _name: str
    _options: OpenAIProviderOptions
    DEFAULT_TEXT_EMBEDDER = "qwen3-embedding-8b"
    DEFAULT_PROMPTER_MODEL = "gpt-5-mini"

    def __init__(self, name: str | None = None, **options: Unpack[DaftProviderOptions]) -> None:
        self._name = name or "daft"
        self._options = cast("OpenAIProviderOptions", dict(options))

        # Configure the api_key, raising an error if it does not exist
        api_key = options.get("api_key")
        if api_key is None:
            api_key = os.environ.get("DAFT_PROVIDER_API_KEY")
        if api_key is None:
            raise ValueError(
                "The api_key option must be set by either passing it as an option or setting"
                "the DAFT_PROVIDER_API_KEY environment variable"
            )
        self._options["api_key"] = api_key

        # Configure base_url with a fallback to the inference endpoint.
        base_url = options.get("base_url")
        if base_url is None:
            base_url = os.environ.get("DAFT_PROVIDER_BASE_URL", "https://inference.daft.ai/v1")
        self._options["base_url"] = base_url

    @property
    def name(self) -> str:
        return self._name

    def get_text_embedder(
        self, model: str | None = None, dimensions: int | None = None, **options: Any
    ) -> TextEmbedderDescriptor:
        from ev.provider.protocols.text_embedder import DaftTextEmbedderDescriptor

        return DaftTextEmbedderDescriptor(
            provider_name=self._name,
            provider_options=self._options,
            model_name=(model or self.DEFAULT_TEXT_EMBEDDER),
            dimensions=dimensions,
            model_options=options,
        )

    def get_prompter(self, model: str | None = None, **options: Any) -> PrompterDescriptor:
        from ev.provider.protocols.prompter import DaftPrompterDescriptor

        # Extract return_format from options if provided
        return_format = options.pop("return_format", None)
        system_message = options.pop("system_message", None)
        use_chat_completions = options.pop("use_chat_completions", False)

        # Extract udf options from options if provided
        udf_options = options.pop("udf_options", None)

        return DaftPrompterDescriptor(
            provider_name=self._name,
            provider_options=self._options,
            model_name=(model or self.DEFAULT_PROMPTER_MODEL),
            model_options=options,
            system_message=system_message,
            return_format=return_format,
            udf_options=udf_options,
            use_chat_completions=use_chat_completions,
        )
