import asyncio
import json
from typing import Dict
from openai import OpenAI

from app.post_analysis.application.port.openai_service_port import OpenAIServicePort
from app.crawling.Engine.prompts import DEFAULT_PROMPT


class OpenAIServiceImpl(OpenAIServicePort):
    """OpenAI 서비스 구현체"""

    def __init__(self, api_key: str = None):
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()

    async def analyze_stock_post(
        self,
        text: str,
        prompt_template: str = None
    ) -> Dict[str, any]:
        """
        주식 게시글을 분석하여 title, content, keywords를 추출합니다

        Args:
            text: 분석할 텍스트
            prompt_template: 사용할 프롬프트 템플릿 (None이면 DEFAULT_PROMPT 사용)
                            템플릿에 {text} 플레이스홀더 필요
        """
        template = prompt_template or DEFAULT_PROMPT
        prompt = template.format(text=text[:3000])

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0
            ).choices[0].message.content
        )

        try:
            # JSON 파싱
            result = json.loads(response)
            return {
                "title": result.get("title", "제목 없음"),
                "content": result.get("content", "내용 없음"),
                "keywords": result.get("keywords", [])
            }
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본값 반환
            return {
                "title": "분석 실패",
                "content": "게시글 분석 중 오류가 발생했습니다.",
                "keywords": []
            }