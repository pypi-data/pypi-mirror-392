from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from daft import DataType
from daft.ai.openai.protocols.text_embedder import OpenAITextEmbedder
from daft.ai.protocols import TextEmbedder, TextEmbedderDescriptor
from daft.ai.typing import EmbeddingDimensions, UDFOptions
from daft.dependencies import np
from openai import AsyncOpenAI, OpenAIError, RateLimitError
from openai._types import omit
from openai.types.create_embedding_response import Usage as CreateEmbeddingUsage

from ev.provider.protocols.metrics import DAFT_INFERENCE_METRICS as _DAFT_INFERENCE_METRICS
from ev.provider.typing import DaftModelInfo

if TYPE_CHECKING:
    from daft.ai.openai.typing import OpenAIProviderOptions
    from daft.ai.typing import Embedding, Options
    from openai.types.create_embedding_response import CreateEmbeddingResponse


MODELS: Final[dict[str, DaftModelInfo]] = {
    "qwen3-embedding-8b": DaftModelInfo(
        dimensions=EmbeddingDimensions(
            size=4096,
            dtype=DataType.float32(),
        ),
    ),
    "qwen3-0p6b-deploy": DaftModelInfo(
        dimensions=EmbeddingDimensions(
            size=1024,
            dtype=DataType.float32(),
        ),
    ),
}


@dataclass
class DaftTextEmbedderDescriptor(TextEmbedderDescriptor):
    provider_name: str
    provider_options: OpenAIProviderOptions
    model_name: str
    dimensions: int | None
    model_options: Options

    def __post_init__(self) -> None:
        if self.provider_options.get("base_url") is None:
            if self.model_name not in MODELS:
                supported_models = ", ".join(MODELS.keys())
                raise ValueError(
                    f"Unsupported OpenAI embedding model '{self.model_name}', expected one of: {supported_models}"
                )
            model = MODELS[self.model_name]
            if self.dimensions is not None and not model.supports_overriding_dimensions:
                raise ValueError(f"OpenAI embedding model '{self.model_name}' does not support specifying dimensions")

    def get_provider(self) -> str:
        return self.provider_name

    def get_model(self) -> str:
        return self.model_name

    def get_options(self) -> Options:
        return self.model_options

    def get_dimensions(self) -> EmbeddingDimensions:
        if self.dimensions is not None:
            return EmbeddingDimensions(size=self.dimensions, dtype=DataType.float32())
        model_dimensions = MODELS[self.model_name].dimensions
        if model_dimensions is None:
            raise ValueError(f"Model '{self.model_name}' must define dimensions.")
        return model_dimensions

    def get_udf_options(self) -> UDFOptions:
        return UDFOptions(concurrency=1, num_gpus=None)

    def is_async(self) -> bool:
        return True

    def instantiate(self) -> TextEmbedder:
        return DaftTextEmbedder(
            client=AsyncOpenAI(**self.provider_options),
            model=self.model_name,
            dimensions=self.dimensions,
        )


# The Daft Provider uses an OpenAI-compatible endpoint.
# For now, we simply alias the DaftTextEmbedder because we
# do not yet have any Daft Provider specific logic. We will
# update this to proxy to the underlying implementation at
# some later time, and perhaps in the near future we can
# migrate the implementation to Rust.
class DaftTextEmbedder(OpenAITextEmbedder):
    async def _embed_text_batch(self, input_batch: list[str]) -> list[Embedding]:
        """Embeds text as a batch call, falling back to _embed_text on rate limit exceptions."""
        try:
            response = await self._client.embeddings.create(
                input=input_batch,
                model=self._model,
                encoding_format="float",
                dimensions=self._dimensions if self._dimensions is not None else omit,
            )

            usage = response.usage
            if usage is not None and isinstance(usage, CreateEmbeddingUsage):
                _DAFT_INFERENCE_METRICS.record(
                    model=self._model,
                    protocol="embed_text",
                    input_tokens=usage.prompt_tokens,
                    total_tokens=usage.total_tokens,
                )

            return [np.array(embedding.embedding) for embedding in response.data]
        except RateLimitError:
            # fall back to individual calls when rate limited
            # consider sleeping or other backoff mechanisms
            return await asyncio.gather(*(self._embed_text(text) for text in input_batch))
        except OpenAIError as ex:
            raise ValueError("The `embed_text` method encountered an OpenAI error.") from ex

    async def _embed_text(self, input_text: str) -> Embedding:
        """Embeds a single text input and possibly returns a zero vector."""
        try:
            response: CreateEmbeddingResponse = await self._client.embeddings.create(
                input=input_text,
                model=self._model,
                encoding_format="float",
                dimensions=self._dimensions if self._dimensions is not None else omit,
            )

            usage = response.usage
            if usage is not None and isinstance(usage, CreateEmbeddingUsage):
                _DAFT_INFERENCE_METRICS.record(
                    model=self._model,
                    protocol="embed_text",
                    input_tokens=usage.prompt_tokens,
                    total_tokens=usage.total_tokens,
                )

            return np.array(response.data[0].embedding)
        except Exception as ex:
            if self._zero_on_failure:
                if self._dimensions is not None:
                    size = self._dimensions
                else:
                    model_dimensions = MODELS[self._model].dimensions
                    if model_dimensions is None:
                        raise ValueError(f"Model '{self._model}' must define dimensions.")
                    size = model_dimensions.size
                return np.zeros(size, dtype=np.float32)
            else:
                raise ex
