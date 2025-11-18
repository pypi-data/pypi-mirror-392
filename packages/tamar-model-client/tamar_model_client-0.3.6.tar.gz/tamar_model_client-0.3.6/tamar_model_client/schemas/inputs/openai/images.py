import httpx
from openai import NotGiven, NOT_GIVEN
from openai._types import Headers, Query, Body, FileTypes
from openai.types import ImageModel
from pydantic import BaseModel, field_validator
from typing import List, Optional, Union, Literal

from tamar_model_client.schemas.inputs.base import TamarFileIdInput
from tamar_model_client.utils import convert_file_field


class OpenAIImagesInput(BaseModel):
    prompt: str
    background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN
    model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN
    moderation: Optional[Literal["low", "auto"]] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    output_compression: Optional[int] | NotGiven = NOT_GIVEN
    output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN
    partial_images: Optional[int] | NotGiven = NOT_GIVEN
    quality: Optional[Literal["standard", "hd", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN
    response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal[
        "auto", "1024x1024", "1536x1024", "1024x1536", "256x256", "512x512", "1792x1024", "1024x1792"]] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }


class OpenAIImagesEditInput(BaseModel):
    image: Union[FileTypes, List[FileTypes], TamarFileIdInput, List[TamarFileIdInput]]
    prompt: str
    background: Optional[Literal["transparent", "opaque", "auto"]] | NotGiven = NOT_GIVEN
    input_fidelity: Optional[Literal["high", "low"]] | NotGiven = NOT_GIVEN
    mask: FileTypes | TamarFileIdInput | NotGiven = NOT_GIVEN
    model: Union[str, ImageModel, None] | NotGiven = NOT_GIVEN
    n: Optional[int] | NotGiven = NOT_GIVEN
    output_compression: Optional[int] | NotGiven = NOT_GIVEN
    output_format: Optional[Literal["png", "jpeg", "webp"]] | NotGiven = NOT_GIVEN
    partial_images: Optional[int] | NotGiven = NOT_GIVEN
    quality: Optional[Literal["standard", "low", "medium", "high", "auto"]] | NotGiven = NOT_GIVEN
    response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN
    size: Optional[Literal["256x256", "512x512", "1024x1024", "1536x1024", "1024x1536", "auto"]] | NotGiven = NOT_GIVEN
    stream: Optional[Literal[False]] | Literal[True] | NotGiven = NOT_GIVEN
    user: str | NotGiven = NOT_GIVEN
    extra_headers: Headers | None = None
    extra_query: Query | None = None
    extra_body: Body | None = None
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN

    model_config = {
        "arbitrary_types_allowed": True
    }

    @field_validator("image", mode="before")
    @classmethod
    def validate_image(cls, v):
        return convert_file_field(v)

    @field_validator("mask", mode="before")
    @classmethod
    def validate_mask(cls, v):
        return convert_file_field(v)
