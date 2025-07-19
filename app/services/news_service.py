import os
import requests
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from openai import OpenAI
from app.models.news_model import News

# 환경변수
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class NewsService:
    def __init__(self, session: Session):
        self.session = session
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)

    def fetch_news_from_naver(self, query: str = "재난") -> List[News]:
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
        return self.session.exec(
            select(News).order_by(News.pub_date.desc())
        ).all()

    def get_news_by_id(self, news_id: int) -> News:
        news = self.session.get(News, news_id)
        if not news:
            raise ValueError("News not found")
        return news

    def fetch_full_text(self, news_url: str) -> str:
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            res = requests.get(news_url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, "html.parser")
            for selector in [
                "div#dic_area",
                "div.newsct_article",
                "div.article_body"
            ]:
                article = soup.select_one(selector)
                if article and article.text.strip():
                    return article.get_text(separator="\n").strip()
            return "본문을 가져올 수 없습니다."
        except Exception as e:
            return f"[크롤링 오류] {e}"

    def fetch_description_from_api(self, title: str) -> str:
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

    def generate_summary_by_news_id(self, news_id: int) -> str:
        news = self.get_news_by_id(news_id)
        full_text = self.fetch_full_text(news.naver_url)

        # ❗ description 대체된 기사 or 크롤링 실패인 경우
        if "가져올 수 없습니다" in full_text or "[자세한 기사 보기]" in full_text:
            return "이미 요약된 글입니다."

        summary = self.summarize_text(full_text)
        if not summary:
            raise ValueError("요약 생성 실패")

        return summary

    def summarize_text(self, text: str) -> Optional[str]:
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "뉴스 본문을 3줄 이내로 간결하게 요약해줘."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] 요약 실패: {e}")
            return None

    def _strip_html(self, text: str) -> str:
        return BeautifulSoup(text, "html.parser").get_text()

    def _parse_pubdate(self, pubdate_str: str) -> datetime:
        return datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
