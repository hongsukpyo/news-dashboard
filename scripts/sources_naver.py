"""네이버 뉴스 검색 API 클라이언트"""
import re
import urllib.parse
import urllib.request
import json
from datetime import datetime
from email.utils import parsedate_to_datetime


def _clean_html(text: str) -> str:
    """네이버가 반환하는 <b> 태그, HTML 엔티티 제거"""
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&")
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'")
    return text.strip()


def fetch_naver_news(query: str, client_id: str, client_secret: str, display: int = 10):
    """
    네이버 뉴스 검색 API 호출
    docs: https://developers.naver.com/docs/serviceapi/search/news/news.md
    """
    encoded = urllib.parse.quote(query)
    url = f"https://openapi.naver.com/v1/search/news.json?query={encoded}&display={display}&sort=date"

    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", client_id)
    req.add_header("X-Naver-Client-Secret", client_secret)

    with urllib.request.urlopen(req, timeout=10) as res:
        data = json.loads(res.read().decode("utf-8"))

    articles = []
    for item in data.get("items", []):
        try:
            pub = parsedate_to_datetime(item["pubDate"]).isoformat()
        except Exception:
            pub = ""
        articles.append({
            "title": _clean_html(item["title"]),
            "summary": _clean_html(item["description"]),
            "link": item["originallink"] or item["link"],
            "source": "네이버뉴스",
            "pub_date": pub,
        })
    return articles
