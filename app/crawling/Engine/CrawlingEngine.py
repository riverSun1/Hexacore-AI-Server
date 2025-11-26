import re
from dataclasses import dataclass
from typing import List, Optional
import asyncio
import requests
from bs4 import BeautifulSoup

from app.post_analysis.infrastructure.service.openai_service_impl import OpenAIServiceImpl


@dataclass
class Article:
    title: str
    content: str
    url: str


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

    def parse_article(self, html: str) -> tuple[str, str]:
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

        return title, content

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
            title, content = self.parse_article(res.text)

            # OpenAI 분석

            print(f"제목: {title}")
            print(f"본문: {content[:200]}...")


            articles.append(Article(title=title, content=content, url=link))

        return articles

    # aync test
    async def article_analysis(self)-> List[Article]:
        articles=self.crawl_pages()
        return_articles = []
        for article in articles:
            analysis = await self.OAS.analyze_stock_post(article.content)

            print(f"분석: {type(analysis)}")
            print(f"분석: {(analysis)}")

            return_articles.append(Article(title=article.title, content=article.content, analysis=analysis))
        return return_articles


    # 기존 메서드 (호환성 유지)
    def get_page_to_list(self):
        """기존 메서드 - crawl_pages로 대체됨"""
        return self.article_analysis()