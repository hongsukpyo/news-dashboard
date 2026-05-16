# 📰 뉴스 대시보드

GitHub Actions로 자동 수집 + GitHub Pages로 무료 배포하는 개인 뉴스 대시보드.
**비용 0원, LLM 호출 없이 빠르게 동작합니다.**

## 수집하는 뉴스

| 카테고리 | 네이버 검색어 | RSS 피드 |
|---|---|---|
| **AI/테크** | OpenAI, Anthropic, 구글 AI, AI 거버넌스, AI 규제, LLM 모델, 생성형 AI | TechCrunch AI, The Verge, MIT Tech Review |
| **경제** | 미국 증시, 나스닥, S&P 500, 코스피, 코스닥, 서울 아파트, 부동산 시장 | Bloomberg Markets, Reuters Business |
| **시사** | 대선, 총선, 우크라이나, 중동 분쟁, 이스라엘 | BBC World, Reuters World |

각 카테고리당 최대 20건, 중복 제거 + 최신순 정렬.

## 기능

- ✅ 카테고리별 탭 + 통합 검색
- ✅ 검색어 태그 클릭 → 같은 키워드 모아보기
- ✅ 자동 업데이트 (매일 08:00 / 20:00 KST)
- ✅ 수동 트리거 (Actions 탭 "Run workflow")
- ✅ 다크모드 자동 대응

## 🚀 배포 가이드 (10분)

### 1. 코드 푸시

```bash
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/<아이디>/<저장소>.git
git push -u origin main
```

### 2. 네이버 뉴스 API 키 발급 (5분)

1. https://developers.naver.com/apps/#/register
2. 애플리케이션 등록
   - 사용 API: **검색** → **뉴스** 체크
   - 환경: **WEB 설정** → 서비스 URL은 `https://example.com` 같이 아무 값
3. 발급된 **Client ID** / **Client Secret** 복사

### 3. GitHub Secrets에 등록

저장소 → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

### 4. GitHub Pages 활성화

저장소 → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: **main** / **/ (root)** → Save

→ `https://<아이디>.github.io/<저장소>/`

### 5. 최초 실행

**Actions** 탭 → **Update News Dashboard** → **Run workflow** 클릭

⏱ 약 1~2분 후 데이터 자동 커밋 → 대시보드 표시

## 🛠 커스터마이징

### 검색어/카테고리 변경

`scripts/fetch_news.py`의 `CATEGORIES` dict 수정:

```python
CATEGORIES = {
    "AI/테크": {
        "naver_queries": ["새 키워드 추가"],
        "rss_feeds": ["https://새 RSS URL"],
    },
}
```

### 업데이트 시간 변경

`.github/workflows/update-news.yml`의 `cron` (UTC 기준):
```yaml
- cron: '0 23 * * *'   # KST 08:00
- cron: '0 11 * * *'   # KST 20:00
```

### 카테고리당 기사 수 변경

`scripts/fetch_news.py`의 `MAX_PER_CATEGORY = 20`

## 💰 비용

| 항목 | 비용 |
|---|---|
| GitHub Pages | 무료 |
| GitHub Actions | 무료 (회당 1~2분, 월 60분 미만) |
| 네이버 뉴스 API | 무료 (일 25,000회) |

## 📁 구조

```
news-dashboard/
├── .github/workflows/update-news.yml
├── scripts/
│   ├── fetch_news.py          # 메인
│   ├── sources_naver.py       # 네이버 API
│   └── sources_rss.py         # RSS
├── data/news.json             # Actions가 자동 갱신
├── index.html / style.css / app.js
├── requirements.txt
└── README.md
```
# news-dashboard
