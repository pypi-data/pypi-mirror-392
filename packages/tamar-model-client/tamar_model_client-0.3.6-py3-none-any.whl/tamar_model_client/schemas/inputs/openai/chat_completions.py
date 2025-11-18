import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types import ChatModel, Metadata, ReasoningEffort
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionAudioParam, completion_create_params, \
    ChatCompletionPredictionContentParam, ChatCompletionStreamOptionsParam, ChatCompletionToolChoiceOptionParam, \
    ChatCompletionToolParam
from pydantic import BaseModel
from typing import List, Optional, Union, Iterable, Dict, Literal


class OpenAIChatCompletionsInput(BaseModel):
    messages: Iterable[ChatCompletionMessageParam]
    model: Union[str, ChatModel]
    audio: Optional[ChatCompletionAudioParam] | NotGiven = NOT_GIVEN
    frequency_penalty: Optional[float] | NotGiven = NOT_GIVEN
    function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN
    functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN
    logit_bias: Optional[Dict[str, int]] | NotGiven = NOT_GIVEN
    logprobs: Optional[bool] | NotGiven = NOT_GIVEN
    max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN
    max_tokens: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    modalities: Optional[List[Literal["text", "audio"]]] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    parallel_tool_calls: bool | NotGiven = NOT_GIVEN
    prediction: Optional[ChatCompletionPredictionContentParam] | NotGiven = NOT_GIVEN
    presence_penalty: Optional[float] | NotGiven = NOT_GIVEN
    prompt_cache_key: str | NotGiven = NOT_GIVEN
    reasoning_effort: Optional[ReasoningEffort] | NotGiven = NOT_GIVEN
    response_format: completion_create_params.ResponseFormat | NotGiven = NOT_GIVEN
    safety_identifier: str | NotGiven = NOT_GIVEN
    seed: Optional[int] | NotGiven = NOT_GIVEN
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | NotGiven = NOT_GIVEN
    stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    stream_options: Optional[ChatCompletionStreamOptionsParam] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    tool_choice: ChatCompletionToolChoiceOptionParam | NotGiven = NOT_GIVEN
    tools: Iterable[ChatCompletionToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    verbosity: Optional[Literal["low", "medium", "high"]] | NotGiven = NOT_GIVEN
    web_search_options: completion_create_params.WebSearchOptions | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }
