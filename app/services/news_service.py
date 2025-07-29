import os
import requests
from datetime import datetime
from typing import List, Optional

from bs4 import BeautifulSoup
from sqlmodel import Session, select
from openai import OpenAI
from app.models.news_model import News

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
            description = self._strip_html(item["description"])
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
                description=description,
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
    
    def generate_hot_keywords_summary(self, limit: int = 3) -> str:
        recent_news = self.session.exec(
            select(News).order_by(News.pub_date.desc()).limit(limit)
        ).all()

        if not recent_news:
            raise ValueError("최근 뉴스가 없습니다.")

        titles = [f"- {news.title}" for news in recent_news]
        prompt = (
            "다음은 최신 뉴스 제목들입니다:\n\n"
            + "\n".join(titles)
            + "\n\n이 뉴스 제목들을 기반으로 지금 핫한 이슈나 키워드를 3줄 이내로 요약해줘."
        )

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "사용자가 제공한 뉴스 제목들에서 중요한 키워드나 이슈를 추출해 요약해줘.말투는 친절하게"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[ERROR] 키워드 요약 실패: {e}")
            return "키워드를 생성하지 못했습니다."

    def _strip_html(self, text: str) -> str:
        return BeautifulSoup(text, "html.parser").get_text()

    def _parse_pubdate(self, pubdate_str: str) -> datetime:
        return datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
