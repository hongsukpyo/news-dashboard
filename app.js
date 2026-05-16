let allData = null;
let activeTab = "전체";
let searchKeyword = "";

async function loadNews() {
  try {
    const res = await fetch(`data/news.json?t=${Date.now()}`);
    if (!res.ok) throw new Error("데이터 로드 실패");
    allData = await res.json();
    render();
  } catch (e) {
    document.getElementById("news-container").innerHTML =
      `<p class="empty">⚠️ 뉴스 데이터를 불러오지 못했습니다. (${e.message})<br>
       GitHub Actions가 최소 1회 실행된 후 표시됩니다.</p>`;
  }
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  if (isNaN(d)) return "";
  const now = new Date();
  const diffH = Math.floor((now - d) / 3600000);
  if (diffH < 1) return "방금 전";
  if (diffH < 24) return `${diffH}시간 전`;
  return d.toLocaleDateString("ko-KR", { month: "short", day: "numeric" });
}

function render() {
  if (!allData) return;

  document.getElementById("updated-at").textContent =
    new Date(allData.generated_at).toLocaleString("ko-KR");

  const categories = Object.keys(allData.categories);
  const tabsHtml = ["전체", ...categories]
    .map(c => `<button class="tab ${c === activeTab ? "active" : ""}" data-cat="${c}">${c}</button>`)
    .join("");
  document.getElementById("tabs").innerHTML = tabsHtml;
  document.querySelectorAll(".tab").forEach(btn => {
    btn.onclick = () => { activeTab = btn.dataset.cat; render(); };
  });

  const container = document.getElementById("news-container");
  const showCats = activeTab === "전체" ? categories : [activeTab];
  const kw = searchKeyword.toLowerCase().trim();

  let html = "";
  let totalShown = 0;

  for (const cat of showCats) {
    let items = allData.categories[cat] || [];
    if (kw) {
      items = items.filter(a => {
        const haystack = [a.title, a.summary, a.query].join(" ").toLowerCase();
        return haystack.includes(kw);
      });
    }
    if (!items.length) continue;
    totalShown += items.length;

    html += `<section class="category-block">
      <h2 class="category-title">${cat} <span class="count">(${items.length})</span></h2>
      <div class="news-list">`;

    for (const a of items) {
      const safeTitle = escapeHtml(a.title);
      const safeSummary = escapeHtml(a.summary || "");
      const safeSource = escapeHtml(a.source || "");
      const queryTag = a.query
        ? `<span class="query-tag" data-kw="${escapeHtml(a.query)}">#${escapeHtml(a.query)}</span>`
        : "";

      html += `<article class="news-card">
        <a class="news-title" href="${encodeURI(a.link)}" target="_blank" rel="noopener noreferrer">${safeTitle}</a>
        ${queryTag}
        <p class="news-summary">${safeSummary}</p>
        <div class="news-footer">
          <span>${safeSource}</span>
          <span>${formatDate(a.pub_date)}</span>
        </div>
      </article>`;
    }
    html += `</div></section>`;
  }

  container.innerHTML = totalShown ? html : `<p class="empty">검색 결과가 없습니다.</p>`;

  // 검색어 태그 클릭 → 필터링
  document.querySelectorAll(".query-tag").forEach(tag => {
    tag.onclick = () => {
      const kw = tag.dataset.kw;
      document.getElementById("search").value = kw;
      searchKeyword = kw;
      render();
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
  });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

document.getElementById("search").addEventListener("input", e => {
  searchKeyword = e.target.value;
  render();
});

loadNews();
