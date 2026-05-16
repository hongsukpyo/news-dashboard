"""
뉴스 수집 메인 스크립트 (LLM 없음 - 짧은 설명만 사용)

파이프라인:
1. 카테고리별 네이버 + RSS 수집
2. 중복 제거 + 최신순 정렬 + 상위 N개 선별
3. data/news.json 저장
"""
import json
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

from sources_naver import fetch_naver_news
from sources_rss import fetch_rss_feeds

KST = timezone(timedelta(hours=9))

# ============================================================
# 카테고리별 검색어 / RSS 피드
# ============================================================
CATEGORIES = {
    "AI/테크": {
        # 빅테크 동향 + AI 거버넌스 + LLM + 생성형 AI
        "naver_queries": [
            "OpenAI",
            "Anthropic",
            "구글 AI",
            "AI 거버넌스",
            "AI 규제",
            "LLM 모델",
            "생성형 AI",
        ],
        "rss_feeds": [
            "https://techcrunch.com/category/artificial-intelligence/feed/",
            "https://www.theverge.com/rss/index.xml",
            "https://www.technologyreview.com/feed/",
        ],
    },
    "경제": {
        # 미국 증시 + 한국 증시 + 부동산(서울)
        "naver_queries": [
            "미국 증시",
            "나스닥",
            "S&P 500",
            "코스피",
            "코스닥",
            "서울 아파트",
            "부동산 시장",
        ],
        "rss_feeds": [
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
        ],
    },
    "시사": {
        # 선거 + 국제 분쟁
        "naver_queries": [
            "대선",
            "총선",
            "우크라이나",
            "중동 분쟁",
            "이스라엘",
        ],
        "rss_feeds": [
            "http://feeds.bbci.co.uk/news/world/rss.xml",
            "https://www.reutersagency.com/feed/?best-topics=world&post_type=best",
        ],
    },
}

# 카테고리당 최대 기사 수 (수집 후 최신순 상위 N개)
MAX_PER_CATEGORY = 20


def dedupe(articles):
    """제목 기반 중복 제거"""
    seen = set()
    result = []
    for a in articles:
        key = a["title"].strip().lower()
        if key in seen or not key:
            continue
        seen.add(key)
        result.append(a)
    return result


def collect_category(category, config, naver_id, naver_secret):
    articles = []

    # 네이버 뉴스
    if naver_id and naver_secret:
        for query in config["naver_queries"]:
            try:
                items = fetch_naver_news(query, naver_id, naver_secret, display=10)
                for it in items:
                    it["category"] = category
                    it["query"] = query
                articles.extend(items)
                print(f"  네이버[{query}]: {len(items)}건")
            except Exception as e:
                print(f"  네이버[{query}] 실패: {e}")

    # RSS
    for feed_url in config["rss_feeds"]:
        try:
            items = fetch_rss_feeds(feed_url, limit=10)
            for it in items:
                it["category"] = category
            articles.extend(items)
            print(f"  RSS[{feed_url[:55]}...]: {len(items)}건")
        except Exception as e:
            print(f"  RSS[{feed_url[:55]}...] 실패: {e}")

    # 중복 제거 + 최신순
    articles = dedupe(articles)
    articles.sort(key=lambda x: x.get("pub_date", ""), reverse=True)
    return articles[:MAX_PER_CATEGORY]


def main():
    naver_id = os.environ.get("NAVER_CLIENT_ID")
    naver_secret = os.environ.get("NAVER_CLIENT_SECRET")

    if not naver_id or not naver_secret:
        print("⚠️  NAVER_CLIENT_ID/SECRET 없음 → RSS만 수집")

    output = {
        "generated_at": datetime.now(KST).isoformat(),
        "categories": {},
    }

    for category, config in CATEGORIES.items():
        print(f"\n=== {category} ===")
        articles = collect_category(category, config, naver_id, naver_secret)
        output["categories"][category] = articles
        print(f"  ✓ 최종 {len(articles)}건")

    data_path = Path(__file__).parent.parent / "data" / "news.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in output["categories"].values())
    print(f"\n✅ 완료: 총 {total}건 → {data_path}")


if __name__ == "__main__":
    main()
