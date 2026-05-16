"""RSS 피드 파서 (feedparser 사용)"""
import feedparser
from urllib.parse import urlparse


def fetch_rss_feeds(feed_url: str, limit: int = 10):
    """RSS/Atom 피드를 파싱해 표준화된 dict 리스트 반환"""
    parsed = feedparser.parse(feed_url)
    domain = urlparse(feed_url).netloc

    articles = []
    for entry in parsed.entries[:limit]:
        # 발행시각 추출
        pub_date = ""
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            import time, datetime as dt
            pub_date = dt.datetime.fromtimestamp(
                time.mktime(entry.published_parsed)
            ).isoformat()

        summary = entry.get("summary", "")
        # HTML 태그 제거
        import re
        summary = re.sub(r"<[^>]+>", "", summary)[:200]

        articles.append({
            "title": entry.get("title", "").strip(),
            "summary": summary.strip(),
            "link": entry.get("link", ""),
            "source": domain,
            "pub_date": pub_date,
        })
    return articles
