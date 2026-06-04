import streamlit as st
from openai import OpenAI
import base64
import json
import re
import time
import urllib.parse
from PIL import Image
import requests

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PriceHunt – Live Price Comparison",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS — Cream/White Theme ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

.stApp { background-color: #fdf8f2 !important; }
.block-container { padding-top: 1.5rem !important; max-width: 820px !important; }
/* ── Hide ALL Streamlit branding ── */
#MainMenu                          { display: none !important; }
footer                             { display: none !important; }
header                             { display: none !important; }
.stDeployButton                    { display: none !important; }
#stDecoration                      { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stToolbarActions"]   { display: none !important; }
[data-testid="manage-app-button"]  { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
.viewerBadge_container__1QSob     { display: none !important; }
.styles_viewerBadge__CvC9N        { display: none !important; }
[data-testid="stAppViewBlockContainer"] > div:last-child [data-testid="stVerticalBlock"] > div:last-child { display: none !important; }
/* Remove top rainbow decoration line */
.stApp > header::before            { display: none !important; }
/* Remove bottom padding left by hidden footer */
.stApp { padding-bottom: 0 !important; }

.ph-title {
    font-size: 2.6rem; font-weight: 800; color: #92400e;
    text-align: center; letter-spacing: -1px; margin: 0 0 0.2rem 0;
}
.ph-subtitle { font-size: 1rem; color: #78716c; text-align: center; margin-bottom: 1.8rem; }

.ph-section {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.5px; color: #d97706; margin-bottom: 0.5rem;
}

.stRadio label p { color: #44403c !important; font-weight: 500 !important; }
div[role="radiogroup"] label { color: #44403c !important; }

.stTextInput > div > div > input {
    background: #ffffff !important; border: 1.5px solid #d6c9b8 !important;
    border-radius: 10px !important; color: #1c1917 !important;
    font-size: 1rem !important; padding: 0.6rem 0.9rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f59e0b !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important;
}
.stSelectbox > div > div {
    background: #ffffff !important; border: 1.5px solid #d6c9b8 !important;
    border-radius: 10px !important; color: #1c1917 !important;
}

.stButton > button {
    background: linear-gradient(90deg, #f59e0b, #d97706) !important;
    color: #ffffff !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.65rem 1.5rem !important;
    width: 100% !important; box-shadow: 0 3px 12px rgba(217,119,6,0.3) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }
.stButton > button:disabled {
    background: #e5e7eb !important; color: #9ca3af !important;
    box-shadow: none !important;
}

[data-testid="stFileUploader"] {
    background: #fffbeb !important; border: 2px dashed #fbbf24 !important;
    border-radius: 12px !important; padding: 0.5rem !important;
}
[data-testid="stFileUploader"] label { color: #92400e !important; }

.stProgress > div > div > div { background: #f59e0b !important; }

.ph-card {
    background: #ffffff; border: 1.5px solid #e8ddd0;
    border-radius: 14px; padding: 1rem 1.2rem 1rem 1.4rem;
    margin-bottom: 0.8rem; position: relative;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.ph-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0;
    width: 5px; border-radius: 5px 0 0 5px;
}
.rank-1.ph-card::before { background: #10b981; }
.rank-2.ph-card::before { background: #3b82f6; }
.rank-3.ph-card::before { background: #8b5cf6; }
.rank-4.ph-card::before { background: #f59e0b; }
.rank-5.ph-card::before { background: #ef4444; }
.rank-6.ph-card::before { background: #6366f1; }
.rank-7.ph-card::before { background: #ec4899; }
.rank-8.ph-card::before { background: #14b8a6; }

.ph-card-inner { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.ph-rank { font-size: 1.5rem; font-weight: 800; color: #d6cfc6; min-width: 2rem; }
.ph-thumb { width: 56px; height: 56px; object-fit: contain; border-radius: 8px; border: 1px solid #f0ece6; flex-shrink: 0; }
.ph-info { flex: 1; min-width: 160px; }
.ph-store { font-size: 1rem; font-weight: 700; color: #1c1917; }
.ph-title-small { font-size: 0.78rem; color: #78716c; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 340px; }
.ph-price { font-size: 1.5rem; font-weight: 800; color: #059669; }
.ph-best {
    display: inline-block; background: #10b981; color: #fff;
    font-size: 0.65rem; font-weight: 700; padding: 2px 8px;
    border-radius: 20px; margin-left: 6px; vertical-align: middle;
}
.ph-buy {
    display: inline-block; background: #f59e0b; color: #fff !important;
    font-weight: 700; font-size: 0.82rem; padding: 7px 18px;
    border-radius: 8px; text-decoration: none !important; white-space: nowrap;
}

.ph-product {
    background: #fffbeb; border: 1.5px solid #fcd34d;
    border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 1.2rem; color: #1c1917;
}

.ph-savings {
    background: #f0fdf4; border: 1.5px solid #86efac;
    border-radius: 12px; padding: 1.2rem; text-align: center; margin-top: 1.2rem;
}
.ph-savings-amt { font-size: 1.8rem; font-weight: 800; color: #15803d; }
.ph-savings-sub { font-size: 0.85rem; color: #6b7280; margin-top: 0.3rem; }

.ph-chip {
    display: inline-block; background: #fef3c7; border: 1px solid #fcd34d;
    border-radius: 20px; padding: 3px 12px; font-size: 0.77rem;
    color: #92400e; margin: 3px 3px 0 0;
}
.ph-hr {
    height: 1px; background: linear-gradient(90deg, transparent, #ddd, transparent);
    border: none; margin: 1.2rem 0;
}

.ph-key-card {
    background: #ffffff; border: 1.5px solid #e8ddd0; border-radius: 16px;
    padding: 2rem; max-width: 500px; margin: 2rem auto; text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.ph-key-card h3 { color: #1c1917; font-size: 1.2rem; margin-bottom: 0.6rem; }
.ph-key-card ol { text-align: left; color: #78716c; line-height: 2.2; padding-left: 1.2rem; }
.ph-key-card a { color: #d97706; font-weight: 600; }
.ph-free-note {
    background: #fef3c7; border-radius: 8px; padding: 0.5rem 0.8rem;
    font-size: 0.8rem; color: #92400e; margin-top: 1rem;
}
.ph-live-badge {
    display: inline-block; background: #dcfce7; border: 1px solid #86efac;
    border-radius: 20px; padding: 2px 10px; font-size: 0.72rem;
    color: #15803d; font-weight: 600; margin-left: 6px;
}

[data-testid="stSidebar"] { background: #fdf8f2 !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input { background: #fff !important; }
</style>
""", unsafe_allow_html=True)

# ── OpenRouter config ─────────────────────────────────────────────────────────
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

VISION_MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-nano-12b-v2-vl:free",
    "google/gemma-4-26b-a4b-it:free",
]
TEXT_MODELS = [
    "deepseek/deepseek-v4-flash:free",
    "google/gemma-4-31b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen/qwen3-coder:free",
]

SERPAPI_BASE = "https://serpapi.com/search"

# ── Store lists ───────────────────────────────────────────────────────────────
GROCERY_STORES    = ["Zepto", "Blinkit", "Swiggy Instamart", "BigBasket", "JioMart", "DMart Online"]
ELECTRONICS_STORES = ["Amazon India", "Flipkart", "Croma", "Vijay Sales", "Reliance Digital", "Tata Cliq"]

STORE_DOMAINS = {
    "Zepto": "zeptonow.com", "Blinkit": "blinkit.com",
    "Swiggy Instamart": "swiggy.com", "BigBasket": "bigbasket.com",
    "JioMart": "jiomart.com", "DMart Online": "dmart.in",
    "Amazon India": "amazon.in", "Flipkart": "flipkart.com",
    "Croma": "croma.com", "Vijay Sales": "vijaysales.com",
    "Reliance Digital": "reliancedigital.in", "Tata Cliq": "tatacliq.com",
}

STORE_NAME_MAP = {
    "amazon": "Amazon India", "amazon.in": "Amazon India",
    "flipkart": "Flipkart", "croma": "Croma",
    "vijay sales": "Vijay Sales", "vijaysales": "Vijay Sales",
    "reliance digital": "Reliance Digital", "reliancedigital": "Reliance Digital",
    "tata cliq": "Tata Cliq", "tatacliq": "Tata Cliq",
    "zepto": "Zepto", "blinkit": "Blinkit",
    "swiggy": "Swiggy Instamart", "instamart": "Swiggy Instamart",
    "bigbasket": "BigBasket", "big basket": "BigBasket",
    "jiomart": "JioMart", "jio mart": "JioMart",
    "dmart": "DMart Online", "d-mart": "DMart Online",
}


def make_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)


def ai_call(client: OpenAI, messages: list, is_vision: bool = False) -> str:
    """Call OpenRouter API with automatic model fallback on 429 rate limits."""
    fallback_list = list(VISION_MODELS if is_vision else TEXT_MODELS)
    last_error = None
    for m in fallback_list:
        try:
            resp = client.chat.completions.create(model=m, messages=messages, max_tokens=1200)
            if not resp or not resp.choices:
                last_error = Exception(f"Model {m} returned empty response")
                continue
            content = resp.choices[0].message.content
            if content is None:
                last_error = Exception(f"Model {m} returned null content")
                continue
            return content.strip()
        except Exception as e:
            last_error = e
            err_str = str(e)
            if "429" in err_str or "404" in err_str or "NoneType" in err_str:
                time.sleep(0.5)
                continue
            else:
                raise
    raise last_error or Exception("All free models are currently rate-limited. Please try again in a minute.")


def build_search_url(store: str, q: str) -> str:
    enc = urllib.parse.quote_plus(q)
    urls = {
        "Zepto":            f"https://www.zeptonow.com/search?query={enc}",
        "Blinkit":          f"https://blinkit.com/s/?q={enc}",
        "Swiggy Instamart": f"https://www.swiggy.com/instamart/search?query={enc}",
        "BigBasket":        f"https://www.bigbasket.com/ps/?q={enc}",
        "JioMart":          f"https://www.jiomart.com/search/{enc}",
        "DMart Online":     f"https://www.dmart.in/search?q={enc}",
        "Amazon India":     f"https://www.amazon.in/s?k={enc}",
        "Flipkart":         f"https://www.flipkart.com/search?q={enc}",
        "Croma":            f"https://www.croma.com/searchB?q={enc}",
        "Vijay Sales":      f"https://www.vijaysales.com/search/{enc}",
        "Reliance Digital": f"https://www.reliancedigital.in/search?q={enc}",
        "Tata Cliq":        f"https://www.tatacliq.com/search/?text={enc}",
    }
    return urls.get(store, f"https://www.google.com/search?q={enc}+{store}")


def parse_json_response(raw: str):
    cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw.strip()).strip()
    m = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return json.loads(cleaned)


# ── AI: Identify product from IMAGE ──────────────────────────────────────────
def identify_from_image(client: OpenAI, image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    sig = image_bytes[:4]
    mime = "image/png" if sig[:2] == b'\x89P' else "image/jpeg"

    prompt = """Analyze this product image. Return ONLY a raw JSON object, no markdown:
{
  "name": "brand + product name + variant",
  "brand": "brand name",
  "variant": "size or specs e.g. 1L / 8GB 512GB",
  "category": "grocery or electronics or other",
  "search_query": "specific search query for Indian e-commerce price comparison",
  "store_category": "grocery_stores or electronics_stores"
}
Groceries/food/beverages/household → grocery_stores. Electronics/gadgets/appliances → electronics_stores."""

    raw = ai_call(client, [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": prompt}
        ]}
    ], is_vision=True)
    return parse_json_response(raw)


# ── AI: Identify product from TEXT ───────────────────────────────────────────
def identify_from_text(client: OpenAI, query: str, category: str) -> dict:
    prompt = f"""User searching for: "{query}"
Category hint: {category}

Return ONLY a raw JSON object, no markdown:
{{
  "name": "brand + product name + variant",
  "brand": "brand name or empty string",
  "variant": "size/specs or empty string",
  "category": "grocery or electronics or other",
  "search_query": "specific search query for Indian e-commerce price comparison",
  "store_category": "grocery_stores or electronics_stores"
}}
If category is Grocery/Food → grocery_stores. If Electronics/Gadgets → electronics_stores. Else infer from product name."""

    raw = ai_call(client, [{"role": "user", "content": prompt}])
    return parse_json_response(raw)


# ── SerpAPI: Google Shopping price search ────────────────────────────────────
def _normalize_store(source_name: str, link: str) -> str | None:
    """Map a result source/link to a known store name."""
    combined = (source_name + " " + link).lower()
    for key, val in STORE_NAME_MAP.items():
        if key in combined:
            return val
    return None


def serpapi_google_shopping(query: str, serpapi_key: str, gl: str = "in", hl: str = "en") -> list:
    """
    Use SerpAPI Google Shopping to get real live prices.
    Returns list of dicts: {site, price, title, thumbnail, link}
    """
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": serpapi_key,
        "gl": gl,       # country = India
        "hl": hl,       # language = English
        "num": "20",
    }
    try:
        resp = requests.get(SERPAPI_BASE, params=params, timeout=15)
        if resp.status_code == 401:
            raise ValueError("Invalid SerpAPI key. Please check your key.")
        if resp.status_code == 429:
            raise ValueError("SerpAPI monthly limit reached. Upgrade plan or wait for reset.")
        if resp.status_code != 200:
            raise ValueError(f"SerpAPI error: HTTP {resp.status_code}")
        data = resp.json()
        results = []
        seen_stores = {}

        shopping_results = data.get("shopping_results", [])
        for item in shopping_results:
            price_str = item.get("price", "") or ""
            # Parse price — handle formats like "₹1,299", "Rs. 1299", "1,299.00"
            price_clean = re.sub(r'[₹Rs.,\s]', '', price_str, flags=re.IGNORECASE)
            try:
                price = float(price_clean) if price_clean else None
            except ValueError:
                price = None

            if not price or price < 10 or price > 10_000_000:
                continue

            source = item.get("source", "") or ""
            link = item.get("link", "") or ""
            title = item.get("title", "") or ""
            thumbnail = item.get("thumbnail", "") or ""

            store = _normalize_store(source, link)
            if not store:
                # Use the source name directly if it's a recognizable retailer
                store = source if source else "Unknown"

            # Keep only the cheapest per store
            if store not in seen_stores or price < seen_stores[store]["price"]:
                seen_stores[store] = {
                    "site": store,
                    "price": price,
                    "title": title,
                    "thumbnail": thumbnail,
                    "link": link,
                    "live": True,
                }

        results = sorted(seen_stores.values(), key=lambda x: x["price"])
        return results

    except (requests.RequestException, ValueError) as e:
        raise


def serpapi_google_search(query: str, serpapi_key: str) -> list:
    """
    Fallback: Use SerpAPI regular Google search for price snippets.
    """
    params = {
        "engine": "google",
        "q": query + " price India ₹",
        "api_key": serpapi_key,
        "gl": "in",
        "hl": "en",
        "num": "10",
    }
    try:
        resp = requests.get(SERPAPI_BASE, params=params, timeout=15)
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        seen_stores = {}

        organic = data.get("organic_results", [])
        for item in organic:
            snippet = item.get("snippet", "") or ""
            link = item.get("link", "") or ""
            title = item.get("title", "") or ""
            combined = snippet + " " + title

            # Extract price from snippet
            m = re.search(r'[₹Rs.]+\s*([\d,]+(?:\.\d{1,2})?)', combined, re.IGNORECASE)
            if not m:
                continue
            try:
                price = float(m.group(1).replace(",", ""))
            except ValueError:
                continue
            if price < 10 or price > 10_000_000:
                continue

            store = _normalize_store("", link)
            if not store:
                continue

            if store not in seen_stores or price < seen_stores[store]["price"]:
                seen_stores[store] = {
                    "site": store,
                    "price": price,
                    "title": title,
                    "thumbnail": "",
                    "link": link,
                    "live": True,
                }

        return sorted(seen_stores.values(), key=lambda x: x["price"])
    except Exception:
        return []


# ── Main price fetcher ───────────────────────────────────────────────────────
def fetch_prices(product: dict, serpapi_key: str) -> list:
    """
    Fetch live prices via SerpAPI Google Shopping.
    Primary: Google Shopping engine (returns actual store prices)
    Fallback: Google Search with price snippets
    """
    query = product.get("search_query", product.get("name", ""))
    query_india = f"{query} India"

    bar = st.progress(0, text="🔍 Searching Google Shopping for live prices…")

    try:
        bar.progress(30, text="🛍️ Fetching Google Shopping results…")
        results = serpapi_google_shopping(query_india, serpapi_key)
        bar.progress(70, text="📊 Processing results…")

        if not results:
            # Fallback to regular Google search
            bar.progress(80, text="🔎 Trying Google Search fallback…")
            results = serpapi_google_search(query_india, serpapi_key)

        bar.progress(100, text="✅ Done!")
        time.sleep(0.3)
        bar.empty()
        return results[:8]

    except ValueError as e:
        bar.empty()
        raise
    except Exception as e:
        bar.empty()
        # Fallback to regular Google search
        try:
            results = serpapi_google_search(query_india, serpapi_key)
            return results[:8]
        except Exception:
            return []


# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int):
    best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 else ""
    live_badge = '<span class="ph-live-badge">🟢 LIVE</span>'
    thumb_html = ""
    if item.get("thumbnail"):
        thumb_html = f'<img src="{item["thumbnail"]}" class="ph-thumb" alt="product" onerror="this.style.display=\'none\'">'
    title_short = (item.get("title", "") or "")[:80]
    title_html = f'<div class="ph-title-small">{title_short}</div>' if title_short else ""

    st.markdown(f"""
<div class="ph-card rank-{rank}">
  <div class="ph-card-inner">
    <div class="ph-rank">#{rank}</div>
    {thumb_html}
    <div class="ph-info">
      <div class="ph-store">{item['site']}{best}{live_badge}</div>
      {title_html}
      <div class="ph-price">₹{item['price']:,.0f}</div>
    </div>
    <a href="{item['link']}" target="_blank" class="ph-buy">Buy Now →</a>
  </div>
</div>""", unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="ph-title">🛒 PriceHunt</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ph-subtitle">Type a product name or upload a photo '
        '→ Find live prices across Indian stores via Google Shopping</div>',
        unsafe_allow_html=True
    )

    # ── API Keys ───────────────────────────────────────────────────────────────
    openrouter_key = None
    serpapi_key = None

    try:
        openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
        serpapi_key = st.secrets.get("SERPAPI_KEY")
    except Exception:
        pass

    with st.sidebar:
        st.markdown("### 🔑 API Keys")
        if not openrouter_key:
            openrouter_key = st.text_input("OpenRouter Key", type="password",
                                            placeholder="sk-or-v1-...",
                                            help="Free at openrouter.ai/keys")
            st.caption("[Get free OpenRouter key →](https://openrouter.ai/keys)")
        else:
            st.success("✅ OpenRouter key loaded")

        if not serpapi_key:
            serpapi_key = st.text_input("SerpAPI Key", type="password",
                                         placeholder="Your SerpAPI key…",
                                         help="250 free searches/month at serpapi.com")
            st.caption("[Get free SerpAPI key →](https://serpapi.com/users/sign_up) · 250 free/month · No credit card")
        else:
            st.success("✅ SerpAPI key loaded")

        st.markdown("---")
        st.markdown("**Why SerpAPI?**")
        st.markdown("- ✅ Real live prices from Google Shopping\n- ✅ 250 free searches/month\n- ✅ No credit card needed\n- ✅ Works for all Indian stores")

    # Show key setup instructions if missing
    missing_keys = []
    if not openrouter_key:
        missing_keys.append("openrouter")
    if not serpapi_key:
        missing_keys.append("serpapi")

    if missing_keys:
        st.markdown("""
<div class="ph-key-card">
  <div style="font-size:2.5rem;">🔑</div>
  <h3>Set Up Your FREE API Keys</h3>
  <ol>""" + ("""
    <li><strong>OpenRouter</strong> (for AI product identification):<br>
      Go to <a href="https://openrouter.ai/keys" target="_blank">openrouter.ai/keys</a> → Sign in (Google/GitHub) → Create Key</li>""" if "openrouter" in missing_keys else "") + ("""
    <li><strong>SerpAPI</strong> (for live Google Shopping prices):<br>
      Go to <a href="https://serpapi.com/users/sign_up" target="_blank">serpapi.com</a> → Sign up free → Copy API key<br>
      <em>250 free searches/month · No credit card required</em></li>""" if "serpapi" in missing_keys else "") + """
  </ol>
  <div class="ph-free-note">
    ✅ Both services are 100% Free &nbsp;·&nbsp; No credit card needed &nbsp;·&nbsp; Real live prices from Google Shopping
  </div>
</div>""", unsafe_allow_html=True)
        st.info("👈 Enter your API keys in the sidebar to get started")
        st.stop()

    client = make_client(openrouter_key)

    # ── Search Mode ────────────────────────────────────────────────────────────
    st.markdown('<div class="ph-section">How do you want to search?</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["📝 Type product name", "📸 Upload product image"],
                    horizontal=True, label_visibility="collapsed")

    text_query, uploaded_file, category = None, None, "Auto-detect"

    if mode == "📝 Type product name":
        with st.form("search_form", clear_on_submit=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                text_query = st.text_input(
                    "product",
                    placeholder="e.g.  Tropicana Orange Juice 1L  or  HP Victus i5 Laptop",
                    label_visibility="collapsed"
                )
            with c2:
                category = st.selectbox("cat",
                    ["Auto-detect", "Grocery / Food", "Electronics / Gadgets"],
                    label_visibility="collapsed"
                )
            st.markdown("""
<div style="margin-top:0.4rem; margin-bottom:1.2rem;">
  <span class="ph-chip">🥥 Coconut Water</span>
  <span class="ph-chip">🍜 Maggi Noodles</span>
  <span class="ph-chip">💻 HP Victus Laptop</span>
  <span class="ph-chip">📱 Samsung Galaxy S24</span>
  <span class="ph-chip">🧴 Dove Shampoo 650ml</span>
</div>""", unsafe_allow_html=True)
            go = st.form_submit_button("🔍 Find Live Prices", use_container_width=True)
        can_search = bool(text_query and text_query.strip()) and go
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            uploaded_file = st.file_uploader(
                "Upload image", type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed"
            )
        with c2:
            if uploaded_file:
                st.image(Image.open(uploaded_file), use_container_width=True)
        st.markdown("")
        can_search = bool(uploaded_file)
        go = st.button("🔍 Find Live Prices", disabled=not can_search, use_container_width=True)
        can_search = can_search and go

    if not can_search:
        st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
        st.markdown('<div class="ph-section" style="text-align:center;">What PriceHunt searches</div>',
                    unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        tiles = [
            ("🛒", "Groceries",   "Zepto · Blinkit · BigBasket · JioMart"),
            ("📱", "Electronics", "Amazon · Flipkart · Croma · Vijay Sales"),
            ("🏠", "Home & FMCG", "Swiggy Instamart · DMart · Reliance"),
        ]
        for col, (em, title, stores_list) in zip([d1, d2, d3], tiles):
            with col:
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #e8ddd0;border-radius:12px;
            padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="font-size:1.8rem;">{em}</div>
  <div style="font-weight:700;color:#1c1917;margin:0.3rem 0;">{title}</div>
  <div style="font-size:0.75rem;color:#78716c;">{stores_list}</div>
</div>""", unsafe_allow_html=True)

        st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
        st.markdown("""
<div style="text-align:center;padding:0.5rem;">
  <span style="font-size:0.85rem;color:#78716c;">
    🟢 <strong>Live prices</strong> via Google Shopping &nbsp;·&nbsp;
    🤖 <strong>AI product recognition</strong> &nbsp;·&nbsp;
    📸 <strong>Image search</strong> supported
  </span>
</div>""", unsafe_allow_html=True)
        return

    # ── Identify product ───────────────────────────────────────────────────────
    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
    product = None

    if mode == "📸 Upload product image" and uploaded_file:
        with st.spinner("🤖 AI is reading your image…"):
            try:
                product = identify_from_image(client, uploaded_file.read())
            except Exception as e:
                st.error(f"❌ Could not identify product: {e}")
                return

    elif mode == "📝 Type product name" and text_query:
        with st.spinner("🤖 AI is analysing your query…"):
            try:
                product = identify_from_text(client, text_query.strip(), category)
            except Exception as e:
                st.error(f"❌ Error: {e}")
                return

    if not product:
        st.error("❌ Could not identify product. Please try again.")
        return

    # Show product info
    cat_emoji = {"grocery": "🛒", "electronics": "📱", "fashion": "👗",
                 "home": "🏠", "beauty": "💄"}.get(product.get("category", ""), "📦")

    st.markdown(f"""
<div class="ph-product">
  <div style="font-size:1.1rem;font-weight:700;">{cat_emoji} {product.get('name','—')}</div>
  <div style="font-size:0.85rem;margin-top:0.3rem;color:#78716c;">
    Brand: <strong>{product.get('brand') or '—'}</strong> &nbsp;·&nbsp;
    Variant: <strong>{product.get('variant') or '—'}</strong>
  </div>
  <div style="font-size:0.8rem;margin-top:0.3rem;color:#92400e;">
    🔍 Search query: <em>{product.get('search_query', '—')}</em>
  </div>
</div>""", unsafe_allow_html=True)

    # Fetch & show prices
    st.markdown('<div class="ph-section">Live Price Comparison — Google Shopping</div>', unsafe_allow_html=True)

    try:
        results = fetch_prices(product, serpapi_key)
    except ValueError as e:
        st.error(f"❌ SerpAPI Error: {e}")
        return
    except Exception as e:
        st.error(f"❌ Could not fetch prices: {e}")
        return

    if not results:
        query = product.get("search_query", product.get("name", ""))
        st.warning("😕 No prices found on Google Shopping. Try a more specific product name.")
        stores = GROCERY_STORES if product.get("store_category") == "grocery_stores" else ELECTRONICS_STORES
        links_html = ""
        for store in stores:
            url = build_search_url(store, query)
            links_html += f'<a href="{url}" target="_blank" style="display:inline-block;background:#fef3c7;border:1px solid #fcd34d;border-radius:20px;padding:5px 14px;font-size:0.82rem;color:#92400e;text-decoration:none;margin:4px;">🔗 {store}</a>\n'
        st.markdown(f'<div style="margin-top:0.5rem;">{links_html}</div>', unsafe_allow_html=True)
        st.info('💡 Tip: Be specific — try "Samsung Galaxy S24 Ultra 256GB" instead of "Samsung phone"')
        return

    st.markdown(
        f'<div style="color:#78716c;font-size:0.88rem;margin-bottom:0.8rem;">'
        f'Found <strong style="color:#1c1917;">{len(results)} listings</strong> '
        f'with live prices from Google Shopping</div>',
        unsafe_allow_html=True
    )

    for i, item in enumerate(results, 1):
        result_card(item, i)

    if len(results) >= 2:
        save = results[-1]["price"] - results[0]["price"]
        pct  = save / results[-1]["price"] * 100
        if save > 0:
            st.markdown(f"""
<div class="ph-savings">
  <div class="ph-savings-amt">💰 Save ₹{save:,.0f} ({pct:.0f}%)</div>
  <div class="ph-savings-sub">
    Buy from <strong>{results[0]['site']}</strong>
    instead of <strong>{results[-1]['site']}</strong>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;color:#b8a99a;font-size:0.74rem;margin-top:1rem;">'
        '✅ Prices fetched live from Google Shopping. '
        'Prices may vary — verify on the retailer\'s website before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
