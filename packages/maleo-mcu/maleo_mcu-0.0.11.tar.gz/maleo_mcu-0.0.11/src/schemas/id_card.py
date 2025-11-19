from pydantic import BaseModel, Field
from typing import Annotated
from maleo.types.string import OptStr


class SimpleIdCard(BaseModel):
    id_card: Annotated[dict[str, OptStr], Field(..., description="Id Card")]
