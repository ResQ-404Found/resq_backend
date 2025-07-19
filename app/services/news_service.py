import os
import requests
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from app.models.news_model import News

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

class NewsService:
    def __init__(self, session: Session):
        self.session = session

    def fetch_news_from_naver(self, query: str = "재난") -> List[News]:
        """네이버 뉴스 검색 API를 통해 뉴스 가져오기 + 저장"""
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {
            "query": query,
            "display": 20,
            "start": 1,
            "sort": "date"
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"[ERROR] 네이버 뉴스 API 요청 실패: {response.status_code}")
            return []

        data = response.json()
        items = data.get("items", [])
        added_news = []

        for item in items:
            title = self._strip_html(item["title"])
            origin_url = item["originallink"]
            naver_url = item["link"]
            pub_date = self._parse_pubdate(item["pubDate"])

            # 중복 확인
            existing = self.session.exec(
                select(News).where(
                    News.title == title,
                    News.pub_date == pub_date
                )
            ).first()
            if existing:
                continue

            news = News(
                title=title,
                origin_url=origin_url,
                naver_url=naver_url,
                pub_date=pub_date
            )
            self.session.add(news)
            self.session.commit()
            self.session.refresh(news)
            added_news.append(news)

        return added_news

    def get_news_list(self) -> List[News]:
        """뉴스 목록 반환 (최신순)"""
        return self.session.exec(
            select(News).order_by(News.pub_date.desc())
        ).all()

    def get_news_by_id(self, news_id: int) -> News:
        news = self.session.get(News, news_id)
        if not news:
            raise ValueError("News not found")
        return news

    def fetch_full_text(self, news_url: str) -> str:
        """네이버 뉴스 실제 링크에서 본문 크롤링"""
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(news_url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")

            # 우선순위대로 셀렉터 시도
            possible_selectors = [
                "div#dic_area",            # 대부분 기사 본문
                "div.newsct_article",      # 일부 모바일 페이지
                "div.article_body",        # 구버전
            ]

            for selector in possible_selectors:
                article = soup.select_one(selector)
                if article and article.text.strip():
                    return article.get_text(separator="\n").strip()

            return "본문을 가져올 수 없습니다."

        except Exception as e:
            return f"[크롤링 오류] {e}"


    def _strip_html(self, text: str) -> str:
        """네이버 API에서 오는 title의 <b>태그 제거용"""
        return BeautifulSoup(text, "html.parser").get_text()

    def _parse_pubdate(self, pubdate_str: str) -> datetime:
        """네이버 pubDate 파싱"""
        return datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")

    def fetch_description_from_api(self, title: str) -> str:
        """title로 다시 API 검색하여 description 가져옴"""
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        params = {
            "query": title,
            "display": 10,
            "sort": "date"
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            data = response.json()
            for item in data.get("items", []):
                clean_title = self._strip_html(item["title"])
                if clean_title == title:
                    return self._strip_html(item.get("description", ""))
        except Exception as e:
            print(f"[WARN] fallback description 검색 실패: {e}")
        
        return None
