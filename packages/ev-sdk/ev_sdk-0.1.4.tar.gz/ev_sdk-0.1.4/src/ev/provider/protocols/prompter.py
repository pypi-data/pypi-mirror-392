from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, cast

from daft.ai.openai.protocols.prompter import OpenAIPrompter
from daft.ai.protocols import Prompter, PrompterDescriptor
from daft.ai.typing import UDFOptions
from daft.udf.metrics import increment_counter
from openai._types import omit
from openai.types.completion_usage import CompletionUsage
from openai.types.responses import ResponseUsage

from ev.provider.protocols.metrics import DAFT_INFERENCE_METRICS as _DAFT_INFERENCE_METRICS

if TYPE_CHECKING:
    from daft.ai.openai.typing import OpenAIProviderOptions
    from daft.ai.typing import Options
    from pydantic import BaseModel


@dataclass
class DaftPrompterDescriptor(PrompterDescriptor):
    provider_name: str
    provider_options: OpenAIProviderOptions
    model_name: str
    model_options: Options
    system_message: str | None = None
    return_format: BaseModel | None = None
    udf_options: UDFOptions | None = None
    use_chat_completions: bool = False

    def get_provider(self) -> str:
        return self.provider_name

    def get_model(self) -> str:
        return self.model_name

    def get_options(self) -> Options:
        return self.model_options

    def get_udf_options(self) -> UDFOptions:
        return self.udf_options or UDFOptions(concurrency=1, num_gpus=None)

    def instantiate(self) -> Prompter:
        return DaftPrompter(
            provider_options=self.provider_options,
            model=self.model_name,
            system_message=self.system_message,
            return_format=self.return_format,
            generation_config=self.model_options,
            use_chat_completions=self.use_chat_completions,
        )


# The Daft Provider uses an OpenAI-compatible endpoint.
# For now, we simply alias the DaftPrompter because we
# do not yet have any Daft Provider specific logic. We will
# update this to proxy to the underlying implementation at
# some later time, and perhaps in the near future we can
# migrate the implementation to Rust.
class DaftPrompter(OpenAIPrompter):
    async def _prompt_with_chat_completions(self, messages_list: list[dict[str, Any]]) -> Any:
        """Generate responses using the Chat Completions API."""
        messages_param = cast("Any", messages_list)
        response_format_param = cast("Any", self.return_format) if self.return_format is not None else omit
        response: Any
        if self.return_format is not None:
            # Use structured outputs with Pydantic model
            response = await self.llm.chat.completions.parse(
                model=self.model,
                messages=messages_param,
                response_format=response_format_param,
                **self.generation_config,
            )
            result = response.choices[0].message.parsed
        else:
            # Return plain text
            response = await self.llm.chat.completions.create(
                model=self.model,
                messages=messages_param,
                **self.generation_config,
            )
            result = response.choices[0].message.content

        usage = response.usage
        if usage is not None and isinstance(usage, CompletionUsage):
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            increment_counter(self.INPUT_TOKENS_COUNTER_NAME, input_tokens)
            increment_counter(self.OUTPUT_TOKENS_COUNTER_NAME, output_tokens)
            increment_counter(self.TOTAL_TOKENS_COUNTER_NAME, total_tokens)
            increment_counter(self.REQUESTS_COUNTER_NAME)

            _DAFT_INFERENCE_METRICS.record(
                model=self.model,
                protocol="prompt",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
        return result

    async def _prompt_with_responses(self, messages_list: list[dict[str, Any]]) -> Any:
        """Generate responses using the Responses API."""
        responses_input = cast("Any", messages_list)
        text_format_param = cast("Any", self.return_format) if self.return_format is not None else omit
        response: Any
        if self.return_format is not None:
            response = await self.llm.responses.parse(
                model=self.model,
                input=responses_input,
                text_format=text_format_param,
                **self.generation_config,
            )
            result = response.output_parsed
        else:
            response = await self.llm.responses.create(
                model=self.model,
                input=responses_input,
                **self.generation_config,
            )
            result = response.output_text

        usage = response.usage
        if usage is not None and isinstance(usage, ResponseUsage):
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            total_tokens = usage.total_tokens

            increment_counter(self.INPUT_TOKENS_COUNTER_NAME, input_tokens)
            increment_counter(self.OUTPUT_TOKENS_COUNTER_NAME, output_tokens)
            increment_counter(self.TOTAL_TOKENS_COUNTER_NAME, total_tokens)
            increment_counter(self.REQUESTS_COUNTER_NAME)

            _DAFT_INFERENCE_METRICS.record(
                model=self.model,
                protocol="prompt",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
            )
        return result
