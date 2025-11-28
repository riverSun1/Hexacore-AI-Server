import re
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from sched import scheduler
from typing import List, Optional, Dict, Any
import asyncio
import requests
from bs4 import BeautifulSoup


from app.crawling.Engine.prompts import STRICT_JSON_PROMPT, CRAWLING_JSON_PROMPT

from app.data.domain.data import Data
from app.post_analysis.infrastructure.service.openai_service_impl import OpenAIServiceImpl



@dataclass
class Article:
    title: str
    content: str
    published_at: str
    url: str = ""
    analysis: Optional[Dict[str, Any]] = None


class CrawlingEngine:

    def __init__(self, url: str = ""):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        self.OAS = OpenAIServiceImpl()

    def extract_links_from_list_page(self, html: str, page: int) -> List[str]:
        """목록 페이지 HTML에서 게시글 링크를 추출합니다."""
        links = []
        soup = BeautifulSoup(html, "lxml")
        articles = soup.find_all("p", attrs={"class": "tit"})

        for article in articles:
            atag = article.find("a", attrs={"class": "best-title"})
            if atag:
                command = atag.get("href")
                match = re.search(r"orgBbsWrtView\((\d+),\s*'([^']+)'\)", command)
                if match:
                    seq = match.group(1)
                    board_id = match.group(2)
                    view_url = f"https://www.paxnet.co.kr/tbbs/view?id={board_id}&seq={seq}&page={page}"
                    links.append(view_url)

        return links

    def parse_article(self, html: str) -> tuple[str, str, str]:
        """게시글 HTML에서 제목과 본문을 파싱합니다."""
        soup = BeautifulSoup(html, "lxml")

        # 제목
        title_tag = soup.find("h1")
        title = title_tag.get_text(strip=True) if title_tag else "제목 없음"

        # 본문
        content_div = soup.find("div", attrs={"class": "board-view-cont"})
        if content_div:
            content = content_div.get_text(strip=True)
        else:
            content = ""

        # published_at 파싱 (에러 핸들링)
        published_at = ""
        try:
            time_span = soup.select_one("span.time")
            if time_span and time_span.get("data-date-format"):
                published_at = time_span["data-date-format"]
        except (AttributeError, KeyError, TypeError):
            published_at = ""

        return title, content, published_at

    def crawl_pages(self, page_count: int = 5) -> List[Article]:
        """여러 페이지를 크롤링하여 게시글 목록을 반환합니다."""
        all_links = []

        for i in range(1, page_count + 1):
            url = f"https://www.paxnet.co.kr/tbbs/list?tbbsType=L&id=N11023&page={i}"
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            links = self.extract_links_from_list_page(res.text, i)
            all_links.extend(links)

        articles = []
        for link in all_links:
            print(f"🎯 스크랩 중: {link}")
            res = requests.get(link, headers=self.headers)
            title, content ,published_at= self.parse_article(res.text)

            # OpenAI 분석

            print(f"제목: {title}")
            print(f"본문: {content[:200]}...")
            print(f"작성시간: {published_at}")

            articles.append(Article(title=title, content=content, url=link,published_at=published_at))

        return articles

    # aync test
    async def article_analysis(self, page_count: int = 5):
        articles = self.crawl_pages(page_count=page_count)
        return_articles = []

        for article in articles:
            # 엄격한 JSON 형식 프롬프트로 게시글 분석 (prompts.py에서 다른 프롬프트 선택 가능)
            analysis = await self.OAS.analyze_stock_post(article.content, prompt_template=CRAWLING_JSON_PROMPT)
            return_articles.append(Data(
                title=analysis.get("title"),
                content=analysis.get("content"),
                keywords=analysis.get("keywords"),
                published_at=article.published_at
            ))

        return return_articles


