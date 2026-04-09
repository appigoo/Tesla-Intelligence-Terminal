import streamlit as st
from groq import Groq
import yfinance as yf
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import time

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tesla Intelligence Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Space+Grotesk:wght@300;400;600;700&display=swap');

:root {
    --bg-primary: #0a0c0f;
    --bg-card: #111318;
    --bg-card2: #161a22;
    --accent: #00ff88;
    --accent2: #00c4ff;
    --danger: #ff4757;
    --warning: #ffa502;
    --text: #e8eaf0;
    --text-dim: #6b7280;
    --border: #1f2937;
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* Hide Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

/* Title */
h1 { 
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--accent) !important;
    letter-spacing: -1px;
    font-size: 1.8rem !important;
}
h2, h3 { 
    font-family: 'JetBrains Mono', monospace !important;
    color: var(--accent2) !important;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}
div[data-testid="metric-container"] label {
    color: var(--text-dim) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.6rem !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00ff88 0%, #00c4ff 100%) !important;
    color: #0a0c0f !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    font-family: 'JetBrains Mono', monospace !important;
    letter-spacing: 0.5px;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 20px rgba(0,255,136,0.3) !important;
}

/* Text inputs */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 6px !important;
}
.stSelectbox > div > div {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* News card */
.news-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
    transition: border-color 0.2s;
}
.news-card:hover { border-left-color: var(--accent2); }
.news-title {
    font-weight: 600;
    font-size: 0.92rem;
    color: var(--text);
    margin-bottom: 4px;
    line-height: 1.4;
}
.news-meta {
    font-size: 0.72rem;
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
}
.news-desc {
    font-size: 0.82rem;
    color: #9ca3af;
    margin-top: 6px;
    line-height: 1.5;
}

/* Strategy box */
.strategy-box {
    background: var(--bg-card);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 24px;
    font-size: 0.9rem;
    line-height: 1.8;
    color: var(--text);
}

/* Signal badge */
.badge-bull { 
    background: rgba(0,255,136,0.15); 
    color: #00ff88; 
    padding: 3px 12px; 
    border-radius: 20px; 
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    border: 1px solid rgba(0,255,136,0.3);
}
.badge-bear { 
    background: rgba(255,71,87,0.15); 
    color: #ff4757; 
    padding: 3px 12px; 
    border-radius: 20px; 
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    border: 1px solid rgba(255,71,87,0.3);
}
.badge-neutral { 
    background: rgba(255,165,2,0.15); 
    color: #ffa502; 
    padding: 3px 12px; 
    border-radius: 20px; 
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    border: 1px solid rgba(255,165,2,0.3);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: var(--text-dim) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 6px !important;
    padding: 6px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #0a0c0f !important;
    font-weight: 700 !important;
}

/* Divider */
hr { border-color: var(--border) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Expander */
details {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Helpers ────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_tsla_data(period="5d", interval="15m"):
    ticker = yf.Ticker("TSLA")
    hist = ticker.history(period=period, interval=interval)
    info = ticker.fast_info
    return hist, info

@st.cache_data(ttl=300)
def fetch_spy_data():
    spy = yf.Ticker("SPY")
    hist = spy.history(period="5d", interval="15m")
    return hist

@st.cache_data(ttl=600)
def fetch_news(api_key: str, query: str, page_size: int = 10):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "language": "en",
        "apiKey": api_key,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        if data.get("status") == "ok":
            return data.get("articles", [])
        else:
            st.warning(f"NewsAPI error: {data.get('message', 'Unknown error')}")
            return []
    except Exception as e:
        st.error(f"News fetch failed: {e}")
        return []

def build_chart(hist_tsla, hist_spy):
    fig = go.Figure()

    # TSLA candlestick
    fig.add_trace(go.Candlestick(
        x=hist_tsla.index,
        open=hist_tsla["Open"],
        high=hist_tsla["High"],
        low=hist_tsla["Low"],
        close=hist_tsla["Close"],
        name="TSLA",
        increasing_line_color="#00ff88",
        decreasing_line_color="#ff4757",
        increasing_fillcolor="rgba(0,255,136,0.3)",
        decreasing_fillcolor="rgba(255,71,87,0.3)",
    ))

    # SPY normalized overlay
    spy_norm = hist_spy["Close"] / hist_spy["Close"].iloc[0] * hist_tsla["Close"].iloc[0]
    fig.add_trace(go.Scatter(
        x=hist_spy.index,
        y=spy_norm,
        name="SPY (normalized)",
        line=dict(color="#00c4ff", width=1.5, dash="dot"),
        opacity=0.7,
    ))

    fig.update_layout(
        paper_bgcolor="#0a0c0f",
        plot_bgcolor="#0a0c0f",
        font=dict(family="JetBrains Mono", color="#6b7280"),
        xaxis=dict(
            showgrid=True, gridcolor="#1f2937",
            showline=False, zeroline=False,
            rangeslider=dict(visible=False),
        ),
        yaxis=dict(showgrid=True, gridcolor="#1f2937", showline=False, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9ca3af")),
        margin=dict(l=10, r=10, t=10, b=10),
        height=380,
        hovermode="x unified",
    )
    return fig

def render_news_cards(articles, max_cards=8):
    if not articles:
        st.info("No articles found. Check your NewsAPI key or query.")
        return

    for i, art in enumerate(articles[:max_cards]):
        title = art.get("title", "No title") or "No title"
        source = art.get("source", {}).get("name", "Unknown")
        pub = art.get("publishedAt", "")[:16].replace("T", "  ")
        desc = art.get("description", "") or ""
        url = art.get("url", "#")

        st.markdown(f"""
        <div class="news-card">
            <div class="news-title"><a href="{url}" target="_blank" style="color:inherit;text-decoration:none;">{title}</a></div>
            <div class="news-meta">📰 {source} &nbsp;|&nbsp; 🕐 {pub} UTC</div>
            {"<div class='news-desc'>" + desc[:200] + "...</div>" if desc else ""}
        </div>
        """, unsafe_allow_html=True)

def summarize_articles(articles, max_items=10):
    summaries = []
    for art in articles[:max_items]:
        t = art.get("title", "")
        d = art.get("description", "") or ""
        s = art.get("source", {}).get("name", "")
        summaries.append(f"[{s}] {t}. {d[:200]}")
    return "\n".join(summaries)

def generate_strategy(
    client: Groq,
    tsla_news_text: str,
    market_news_text: str,
    tsla_price: float,
    tsla_change_pct: float,
    spy_change_pct: float,
    extra_notes: str = "",
):
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = f"""你是一位专业的美股量化交易分析师，专注于 Tesla (TSLA)。
今天日期：{today}

=== TSLA 实时行情 ===
当前价格: ${tsla_price:.2f}
今日涨跌: {tsla_change_pct:+.2f}%
SPY今日涨跌: {spy_change_pct:+.2f}%

=== Tesla / Elon Musk 最新资讯 ===
{tsla_news_text}

=== 美股大盘宏观资讯 ===
{market_news_text}

=== 额外备注 ===
{extra_notes if extra_notes else "无"}

请根据以上资讯，提供：

**1. 市场情绪评估（多/空/中性）**
- Tesla 相关情绪：X/10 分（0=极度悲观, 10=极度乐观）
- 大盘宏观情绪：X/10 分
- 综合信号：🟢做多 / 🔴做空 / 🟡观望

**2. 关键风险与催化剂**
列出今日最重要的 3-5 个做多催化剂和风险因素

**3. 今日 TSLA 交易策略**
- 短线策略（日内）：具体的进场价、止损价、目标价
- 中线策略（本周）：仓位建议及方向
- 期权策略（可选）：如有合适机会请列出

**4. 需关注的技术水平**
- 关键支撑位：
- 关键阻力位：
- 今日操作建议：

请用繁體中文回答，格式清晰，重点突出。"""

    with st.spinner("⚡ AI 正在分析市場數據（Groq · llama-3.3-70b）..."):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2000,
            messages=[
                {"role": "system", "content": "你是一位專業的美股交易分析師，回答請使用繁體中文，格式清晰。"},
                {"role": "user", "content": prompt},
            ],
        )
    return response.choices[0].message.content


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ Tesla Intel Terminal")
    st.markdown("---")

    groq_key = st.text_input(
        "Groq API Key（免費）",
        type="password",
        placeholder="gsk_...",
        help="從 console.groq.com 免費獲取，無需信用卡",
    )
    news_api_key = st.text_input(
        "NewsAPI Key",
        type="password",
        placeholder="your_newsapi_key",
        help="從 newsapi.org 免費獲取",
    )

    st.markdown("---")
    st.markdown("**📊 圖表設置**")
    chart_period = st.selectbox("K線週期", ["1d", "5d", "1mo"], index=1)
    chart_interval = st.selectbox("K線時距", ["5m", "15m", "1h", "1d"], index=1)

    st.markdown("---")
    st.markdown("**📰 新聞設置**")
    news_count = st.slider("每類新聞數量", 5, 20, 10)
    extra_notes = st.text_area(
        "今日備注（可選）",
        placeholder="例：FOMC會議、財報週、持倉情況...",
        height=100,
    )

    st.markdown("---")
    run_btn = st.button("🚀 開始分析", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.7rem;color:#4b5563;line-height:1.6;">
    ⚠️ 本工具僅供資訊參考<br>
    不構成投資建議<br>
    交易決策請自行判斷
    </div>
    """, unsafe_allow_html=True)


# ─── Main ─────────────────────────────────────────────────────────────────────
st.markdown("# ⚡ Tesla Intelligence Terminal")
st.markdown(f"<span style='font-family:JetBrains Mono;color:#4b5563;font-size:0.8rem;'>📅 {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC+8 &nbsp;|&nbsp; 自動化晨間分析工作站</span>", unsafe_allow_html=True)
st.markdown("---")

# ─── Live Price Strip ──────────────────────────────────────────────────────
try:
    hist_tsla, tsla_info = fetch_tsla_data(chart_period, chart_interval)
    hist_spy = fetch_spy_data()

    tsla_price = hist_tsla["Close"].iloc[-1]
    tsla_open = hist_tsla["Open"].iloc[0]
    tsla_change = tsla_price - tsla_open
    tsla_change_pct = (tsla_change / tsla_open) * 100
    tsla_high = hist_tsla["High"].max()
    tsla_low = hist_tsla["Low"].min()
    tsla_vol = hist_tsla["Volume"].sum()

    spy_open = hist_spy["Open"].iloc[0]
    spy_price = hist_spy["Close"].iloc[-1]
    spy_change_pct = (spy_price - spy_open) / spy_open * 100

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("TSLA", f"${tsla_price:.2f}", f"{tsla_change_pct:+.2f}%")
    with col2:
        st.metric("區間高", f"${tsla_high:.2f}")
    with col3:
        st.metric("區間低", f"${tsla_low:.2f}")
    with col4:
        vol_m = tsla_vol / 1_000_000
        st.metric("成交量", f"{vol_m:.1f}M")
    with col5:
        st.metric("SPY", f"${spy_price:.2f}", f"{spy_change_pct:+.2f}%")

except Exception as e:
    st.error(f"行情數據加載失敗: {e}")
    hist_tsla, hist_spy = None, None
    tsla_price, tsla_change_pct, spy_change_pct = 0, 0, 0

st.markdown("---")

# ─── Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 K線圖", "🔍 Tesla資訊", "🌍 大盤資訊", "🧠 AI交易策略"])

# ── Tab 1: Chart ──────────────────────────────────────────────────────────
with tab1:
    if hist_tsla is not None and not hist_tsla.empty:
        fig = build_chart(hist_tsla, hist_spy)
        st.plotly_chart(fig, use_container_width=True)
        
        # Volume bar
        fig_vol = go.Figure()
        colors = ["#00ff88" if c >= o else "#ff4757" 
                  for c, o in zip(hist_tsla["Close"], hist_tsla["Open"])]
        fig_vol.add_trace(go.Bar(
            x=hist_tsla.index,
            y=hist_tsla["Volume"],
            marker_color=colors,
            name="Volume",
            opacity=0.8,
        ))
        fig_vol.update_layout(
            paper_bgcolor="#0a0c0f", plot_bgcolor="#0a0c0f",
            font=dict(family="JetBrains Mono", color="#6b7280"),
            xaxis=dict(showgrid=False, showline=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="#1f2937", showline=False, zeroline=False),
            height=150, margin=dict(l=10, r=10, t=5, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    else:
        st.info("行情數據加載中...")

# ── Tab 2 & 3: News ───────────────────────────────────────────────────────
tsla_articles, market_articles = [], []

with tab2:
    st.subheader("🔍 Tesla / TSLA / Elon Musk 最新資訊")
    if not news_api_key:
        st.warning("👈 請在側邊欄輸入 NewsAPI Key（免費：newsapi.org）")
    else:
        with st.spinner("正在抓取 Tesla 相關資訊..."):
            tsla_articles = fetch_news(
                news_api_key,
                query="Tesla OR TSLA OR \"Elon Musk\"",
                page_size=news_count
            )
        st.markdown(f"<span style='font-family:JetBrains Mono;color:#00ff88;font-size:0.8rem;'>✅ 找到 {len(tsla_articles)} 篇文章</span>", unsafe_allow_html=True)
        render_news_cards(tsla_articles, news_count)

with tab3:
    st.subheader("🌍 美股大盤宏觀資訊")
    if not news_api_key:
        st.warning("👈 請在側邊欄輸入 NewsAPI Key")
    else:
        with st.spinner("正在抓取大盤資訊..."):
            market_articles = fetch_news(
                news_api_key,
                query="US stock market OR Fed OR S&P500 OR Nasdaq OR economy inflation interest rate",
                page_size=news_count
            )
        st.markdown(f"<span style='font-family:JetBrains Mono;color:#00c4ff;font-size:0.8rem;'>✅ 找到 {len(market_articles)} 篇文章</span>", unsafe_allow_html=True)
        render_news_cards(market_articles, news_count)

# ── Tab 4: AI Strategy ────────────────────────────────────────────────────
with tab4:
    st.subheader("🧠 AI 交易策略分析")

    if not groq_key:
        st.warning("👈 請在側邊欄輸入 Groq API Key（免費：console.groq.com）")
    elif run_btn or st.button("▶ 生成今日交易策略", key="gen_btn"):
        if not news_api_key:
            st.warning("需要 NewsAPI Key 才能獲取最新資訊")
        else:
            # Fetch news if not yet loaded
            if not tsla_articles:
                tsla_articles = fetch_news(news_api_key, "Tesla OR TSLA OR \"Elon Musk\"", news_count)
            if not market_articles:
                market_articles = fetch_news(
                    news_api_key,
                    "US stock market OR Fed OR S&P500 OR Nasdaq OR economy inflation",
                    news_count
                )
            
            client = Groq(api_key=groq_key)
            tsla_text = summarize_articles(tsla_articles)
            market_text = summarize_articles(market_articles)

            try:
                strategy = generate_strategy(
                    client,
                    tsla_news_text=tsla_text,
                    market_news_text=market_text,
                    tsla_price=tsla_price,
                    tsla_change_pct=tsla_change_pct,
                    spy_change_pct=spy_change_pct,
                    extra_notes=extra_notes,
                )

                # Detect signal for badge
                sig_lower = strategy.lower()
                if "🟢" in strategy or "做多" in strategy[:300]:
                    badge = '<span class="badge-bull">🟢 做多信號</span>'
                elif "🔴" in strategy or "做空" in strategy[:300]:
                    badge = '<span class="badge-bear">🔴 做空信號</span>'
                else:
                    badge = '<span class="badge-neutral">🟡 觀望信號</span>'

                st.markdown(f"""
                <div style="margin-bottom:16px;">
                    <span style="font-family:JetBrains Mono;font-size:0.75rem;color:#4b5563;">
                    分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M')}
                    </span> &nbsp; {badge}
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f'<div class="strategy-box">{strategy.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

                # Download button
                st.download_button(
                    label="💾 下載今日策略報告",
                    data=f"Tesla Intelligence Terminal - {datetime.now().strftime('%Y-%m-%d')}\n\n{strategy}",
                    file_name=f"TSLA_strategy_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                )

            except Exception as e:
                st.error(f"AI 分析失敗: {e}")
    else:
        st.markdown("""
        <div style="background:#111318;border:1px dashed #1f2937;border-radius:10px;padding:32px;text-align:center;">
            <div style="font-size:2rem;margin-bottom:12px;">🧠</div>
            <div style="color:#4b5563;font-family:JetBrains Mono;font-size:0.85rem;">
                配置好 API Keys 後，點擊「開始分析」<br>
                或側邊欄的「🚀 開始分析」按鈕<br><br>
                <span style="color:#00ff88;">AI 將自動整合所有資訊，生成今日交易策略</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
