from typing import Optional

from app.post_analysis.domain.post_analysis import PostAnalysisResult
from app.post_analysis.application.port.openai_service_port import OpenAIServicePort


class AnalyzeStockPostUseCase:
    """주식 게시글 분석 유스케이스"""

    def __init__(self, openai_service: OpenAIServicePort):
        self.openai_service = openai_service

    async def execute(
        self,
        raw_text: str,
        prompt_template: Optional[str] = None
    ) -> PostAnalysisResult:
        """
        주식 게시글 텍스트를 분석하여 title, content, keywords를 추출합니다.

        Args:
            raw_text: 크롤링된 게시글 원본 텍스트
            prompt_template: 사용할 프롬프트 템플릿 (None이면 기본 프롬프트)

        Returns:
            PostAnalysisResult: 분석 결과 (title, content, keywords)
        """
        analysis = await self.openai_service.analyze_stock_post(
            raw_text,
            prompt_template=prompt_template
        )

        return PostAnalysisResult(
            title=analysis.get("title", ""),
            content=analysis.get("content", ""),
            keywords=analysis.get("keywords", [])
        )