from typing import Optional

from pydantic import BaseModel


class AnalyzePostRequest(BaseModel):
    """주식 게시글 분석 요청 모델"""
    raw_text: str
    prompt_template: Optional[str] = None  # None이면 DEFAULT_PROMPT 사용

    class Config:
        json_schema_extra = {
            "example": {
                "raw_text": "삼성전자가 2분기 실적을 발표했습니다. 영업이익은 전년 대비 50% 증가한 12조원을 기록했으며...",
                "prompt_template": None
            }
        }