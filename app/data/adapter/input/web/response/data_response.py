from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class DataResponse(BaseModel):
    """정보 응답 모델"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    keywords: List[str]
    published_at: Optional[str] = None