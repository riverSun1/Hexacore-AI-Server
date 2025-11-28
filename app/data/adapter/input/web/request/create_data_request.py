from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CreateDataItemRequest(BaseModel):
    """단일 데이터 생성 요청"""

    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    keywords: List[str] = Field(default_factory=list, description="키워드 목록")
    published_at: Optional[str] = Field(None, description="발행일시 (ISO 형식 문자열)")


class CreateDataListRequest(BaseModel):
    """여러 데이터를 한 번에 생성하는 요청"""

    items: List[CreateDataItemRequest] = Field(..., description="데이터 목록")


class CrawlingAnalysisPayload(BaseModel):
    title: str = Field(..., description="분석된 투자 포인트 제목")
    content: str = Field(..., description="분석된 투자 포인트 내용")
    keywords: List[str] = Field(default_factory=list, description="연관 키워드")
    published_at: Optional[str] = Field(None, description="발행일시 (ISO 형식 문자열)")


class CrawlingArticleRequest(BaseModel):
    analysis: CrawlingAnalysisPayload = Field(
        ..., description="OpenAI 분석 결과 (필수)"
    )


class CrawlingIngestRequest(BaseModel):
    articles: List[CrawlingArticleRequest] = Field(..., description="분석된 게시글 목록")

