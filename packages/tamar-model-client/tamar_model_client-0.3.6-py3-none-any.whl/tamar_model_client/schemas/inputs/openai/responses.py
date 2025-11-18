import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body
from openai.types import Metadata, ResponsesModel, Reasoning
from openai.types.responses import ResponseInputParam, ResponseIncludable, ResponseTextConfigParam, \
    response_create_params, ToolParam
from openai.types.responses.response_prompt_param import ResponsePromptParam
from pydantic import BaseModel
from typing import List, Optional, Union, Iterable, Literal


class OpenAIResponsesInput(BaseModel):
    background: Optional[bool] | NotGiven = NOT_GIVEN
    include: Optional[List[ResponseIncludable]] | NotGiven = NOT_GIVEN
    input: Union[str, ResponseInputParam] | NotGiven = NOT_GIVEN
    instructions: Optional[str] | NotGiven = NOT_GIVEN
    max_output_tokens: Optional[int] | NotGiven = NOT_GIVEN
    max_tool_calls: Optional[int] | NotGiven = NOT_GIVEN
    metadata: Optional[Metadata] | NotGiven = NOT_GIVEN
    model: ResponsesModel | NotGiven = NOT_GIVEN
    parallel_tool_calls: Optional[bool] | NotGiven = NOT_GIVEN
    previous_response_id: Optional[str] | NotGiven = NOT_GIVEN
    prompt: Optional[ResponsePromptParam] | NotGiven = NOT_GIVEN
    prompt_cache_key: str | NotGiven = NOT_GIVEN
    reasoning: Optional[Reasoning] | NotGiven = NOT_GIVEN
    safety_identifier: str | NotGiven = NOT_GIVEN
    service_tier: Optional[Literal["auto", "default", "flex", "scale", "priority"]] | NotGiven = NOT_GIVEN
    store: Optional[bool] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    stream_options: Optional[response_create_params.StreamOptions] | NotGiven = NOT_GIVEN
    temperature: Optional[float] | NotGiven = NOT_GIVEN
    text: ResponseTextConfigParam | NotGiven = NOT_GIVEN
    tool_choice: response_create_params.ToolChoice | NotGiven = NOT_GIVEN
    tools: Iterable[ToolParam] | NotGiven = NOT_GIVEN
    top_logprobs: Optional[int] | NotGiven = NOT_GIVEN
    top_p: Optional[float] | NotGiven = NOT_GIVEN
    truncation: Optional[Literal["auto", "disabled"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    verbosity: Optional[Literal["low", "medium", "high"]] | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }
