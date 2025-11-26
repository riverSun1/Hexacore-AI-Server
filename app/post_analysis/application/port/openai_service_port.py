from abc import ABC, abstractmethod
from typing import Dict, Optional


class OpenAIServicePort(ABC):
    """OpenAI 서비스 포트 (인터페이스)"""

    @abstractmethod
    async def analyze_stock_post(
        self,
        text: str,
        prompt_template: Optional[str] = None
    ) -> Dict[str, any]:
        """
        주식 게시글을 분석하여 title, content, keywords를 추출합니다

        Args:
            text: 분석할 텍스트
            prompt_template: 사용할 프롬프트 템플릿 (None이면 기본 프롬프트)

        Returns:
            {
                "title": str,
                "content": str,
                "keywords": List[str]
            }
        """
        pass