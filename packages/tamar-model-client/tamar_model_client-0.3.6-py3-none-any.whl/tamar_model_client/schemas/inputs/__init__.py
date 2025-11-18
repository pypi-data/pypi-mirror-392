# Re-export all classes for backward compatibility
from tamar_model_client.schemas.inputs.base import (
    UserContext,
    TamarFileIdInput,
    BaseRequest,
)
# OpenAI
from tamar_model_client.schemas.inputs.openai.responses import OpenAIResponsesInput
from tamar_model_client.schemas.inputs.openai.chat_completions import OpenAIChatCompletionsInput
from tamar_model_client.schemas.inputs.openai.images import OpenAIImagesInput, OpenAIImagesEditInput
# Google
from tamar_model_client.schemas.inputs.google.genai import GoogleGenAiInput
from tamar_model_client.schemas.inputs.google.genai_images import GoogleGenAIImagesInput
from tamar_model_client.schemas.inputs.google.genai_videos import GoogleGenAiVideosInput
from tamar_model_client.schemas.inputs.google.vertexai_images import GoogleVertexAIImagesInput
# Anthropic
from tamar_model_client.schemas.inputs.anthropic.messages import AnthropicMessagesInput
# Freepik
from tamar_model_client.schemas.inputs.freepik.image_upscaler import FreepikImageUpscalerInput
# BytePlus
from tamar_model_client.schemas.inputs.byteplus.omnihuman_video import BytePlusOmniHumanVideoInput
# Unified
from tamar_model_client.schemas.inputs.unified import (
    ModelRequestInput,
    ModelRequest,
    BatchModelRequestItem,
    BatchModelRequest,
)

__all__ = [
    # Base
    "UserContext",
    "TamarFileIdInput",
    "BaseRequest",
    # OpenAI
    "OpenAIResponsesInput",
    "OpenAIChatCompletionsInput",
    "OpenAIImagesInput",
    "OpenAIImagesEditInput",
    # Google
    "GoogleGenAiInput",
    "GoogleVertexAIImagesInput",
    "GoogleGenAIImagesInput",
    "GoogleGenAiVideosInput",
    # Anthropic
    "AnthropicMessagesInput",
    # Freepik
    "FreepikImageUpscalerInput",
    # BytePlus
    "BytePlusOmniHumanVideoInput",
    # Unified
    "ModelRequestInput",
    "ModelRequest",
    "BatchModelRequestItem",
    "BatchModelRequest",
]
