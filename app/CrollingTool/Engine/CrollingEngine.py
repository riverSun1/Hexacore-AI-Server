import re
from attr import attr
import requests
from bs4 import BeautifulSoup

class CrollingEngine():

    def __init__(self,url: str):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}


    def GetPageToList(self):
        links = []
        for i in range(1, 6):
            url = f"https://www.paxnet.co.kr/tbbs/list?tbbsType=L&id=N11023&page={i}"
            res = requests.get(url, headers=self.headers)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "lxml")

            soup = BeautifulSoup(res.text, "lxml")

            articles = soup.find_all("p", attrs={"class": "tit"})

            for article in articles:
                atag = article.find("a", attrs={"class": "best-title"})
                if atag:
                    command = atag.get("href")

                    match = re.search(r"orgBbsWrtView\((\d+),\s*'([^']+)'\)", command)
                    if match:
                        seq = match.group(1)
                        board_id = match.group(2)
                        view_url = f"https://www.paxnet.co.kr/tbbs/view?id={board_id}&seq={seq}&page={i}"
                        links.append(view_url)

            for link in links:
                print("🎯 스크랩 중:", link)
                res = requests.get(link, headers=self.headers)
                soup = BeautifulSoup(res.text, "lxml")

                # 제목
                title_tag = soup.find("h1")
                title = title_tag.get_text(strip=True) if title_tag else "제목 없음"
                print(title)
                # 본문
                content_div = soup.find("div", attrs={"class": "board-view-cont"})
                if content_div:  # None 체크 필수
                   p_tags = content_div.find_all("p")  # 자식 p 태그 전부 가져오기
                   print(p_tags)
                   if p_tags:
                       for p in p_tags:
                           print(p)
                           text = p.get_text(strip=True)
                           print(text)
                   else:
                       # p 태그가 없으면 div 안의 텍스트 전체 출력
                       text = content_div.get_text(strip=True)
                       print(text)
                else:
                    print("본문 없음")
    # 내일 코드 합질것
    # 팀장님 한테 크롤링 5페이지로 타엽 이유 너무 오래걸림
    # 현재 퐉스넷 게시판 제목과 내용을 가져옴. 더필요한 컬럼 확실하게 정리 필요.
    # 어떤값으로 던저주면 되는지. #어제배운 분석 사용안했는데 괜찮은지.
