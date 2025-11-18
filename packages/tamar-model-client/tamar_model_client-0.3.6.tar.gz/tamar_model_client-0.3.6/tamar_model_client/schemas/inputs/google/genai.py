from google.genai import types
from pydantic import BaseModel
from typing import Optional, Union


class GoogleGenAiInput(BaseModel):
    model: str
    contents: Union[types.ContentListUnion, types.ContentListUnionDict]
    config: Optional[types.GenerateContentConfigOrDict] = None

    model_config = {
        "arbitrary_types_allowed": True
    }
