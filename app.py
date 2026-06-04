import streamlit as st
from openai import OpenAI
import base64
import json
import re
import time
import urllib.parse
from PIL import Image
from duckduckgo_search import DDGS

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PriceHunt – Price Comparison India",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
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
.stApp > header::before            { display: none !important; }
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

.ph-card-inner { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; }
.ph-rank { font-size: 1.5rem; font-weight: 800; color: #d6cfc6; min-width: 2rem; }
.ph-info { flex: 1; min-width: 160px; }
.ph-store { font-size: 1rem; font-weight: 700; color: #1c1917; }
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
.ph-buy:hover { background: #d97706 !important; }

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
    color: #92400e; margin: 3px 3px 0 0; cursor: pointer;
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
[data-testid="stSidebar"] { background: #fdf8f2 !important; }
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

# ── Store config — strict category separation ─────────────────────────────────
GROCERY_STORES = ["Blinkit", "Zepto", "BigBasket", "Swiggy Instamart", "JioMart", "DMart Online"]
ELECTRONICS_STORES = ["Amazon India", "Flipkart", "Croma", "Vijay Sales", "Reliance Digital", "Tata Cliq"]

# Direct search URLs — used for every "Buy Now" button (guaranteed clean URLs, no redirects)
STORE_SEARCH_URLS = {
    "Blinkit":          lambda q: f"https://blinkit.com/s/?q={urllib.parse.quote_plus(q)}",
    "Zepto":            lambda q: f"https://www.zeptonow.com/search?query={urllib.parse.quote_plus(q)}",
    "BigBasket":        lambda q: f"https://www.bigbasket.com/ps/?q={urllib.parse.quote_plus(q)}",
    "Swiggy Instamart": lambda q: f"https://www.swiggy.com/instamart/search?query={urllib.parse.quote_plus(q)}",
    "JioMart":          lambda q: f"https://www.jiomart.com/search/{urllib.parse.quote_plus(q)}",
    "DMart Online":     lambda q: f"https://www.dmart.in/search?q={urllib.parse.quote_plus(q)}",
    "Amazon India":     lambda q: f"https://www.amazon.in/s?k={urllib.parse.quote_plus(q)}",
    "Flipkart":         lambda q: f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(q)}",
    "Croma":            lambda q: f"https://www.croma.com/searchB?q={urllib.parse.quote_plus(q)}",
    "Vijay Sales":      lambda q: f"https://www.vijaysales.com/search/{urllib.parse.quote_plus(q)}",
    "Reliance Digital": lambda q: f"https://www.reliancedigital.in/search?q={urllib.parse.quote_plus(q)}",
    "Tata Cliq":        lambda q: f"https://www.tatacliq.com/search/?text={urllib.parse.quote_plus(q)}",
}

# DuckDuckGo site: filter domains — for price searching
STORE_DDG_DOMAINS = {
    "Blinkit":          "blinkit.com",
    "Zepto":            "zeptonow.com",
    "BigBasket":        "bigbasket.com",
    "Swiggy Instamart": "swiggy.com",
    "JioMart":          "jiomart.com",
    "DMart Online":     "dmart.in",
    "Amazon India":     "amazon.in",
    "Flipkart":         "flipkart.com",
    "Croma":            "croma.com",
    "Vijay Sales":      "vijaysales.com",
    "Reliance Digital": "reliancedigital.in",
    "Tata Cliq":        "tatacliq.com",
}


def make_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)


def ai_call(client: OpenAI, messages: list, is_vision: bool = False) -> str:
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
            if "429" in str(e) or "404" in str(e) or "NoneType" in str(e):
                time.sleep(0.5)
                continue
            else:
                raise
    raise last_error or Exception("All free models rate-limited. Try again in a minute.")


def parse_json_response(raw: str) -> dict:
    cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw.strip()).strip()
    m = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return json.loads(cleaned)


def extract_price(text: str):
    """Extract the first reasonable INR price from text."""
    patterns = [
        r'₹\s*([\d,]+(?:\.\d{1,2})?)',
        r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
        r'INR\s*([\d,]+(?:\.\d{1,2})?)',
        r'MRP[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'"price"\s*:\s*"?([\d,.]+)',
        r'"selling_price"\s*:\s*"?([\d,.]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                p = float(m.group(1).replace(",", ""))
                if 50 < p < 10_000_000:
                    return p
            except ValueError:
                pass
    return None


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
Grocery/Food → grocery_stores. Electronics/Gadgets/Phones/Laptops → electronics_stores."""

    raw = ai_call(client, [{"role": "user", "content": prompt}])
    return parse_json_response(raw)


# ── DuckDuckGo per-store price search ────────────────────────────────────────
def _ddg_price_for_store(ddgs: DDGS, store: str, query: str) -> float | None:
    """
    Search DuckDuckGo restricted to a single store's domain and extract a price.
    Uses multiple query strategies for best hit rate.
    """
    domain = STORE_DDG_DOMAINS.get(store, "")
    if not domain:
        return None

    # Try progressively broader queries
    queries = [
        f'site:{domain} "{query}" price',
        f'site:{domain} {query} ₹',
        f'site:{domain} {query} buy',
    ]

    for q in queries:
        try:
            for r in ddgs.text(q, max_results=8):
                combined = (
                    r.get("title", "") + " " +
                    r.get("body", "") + " " +
                    r.get("href", "")
                )
                price = extract_price(combined)
                if price:
                    return price
            time.sleep(0.2)
        except Exception:
            time.sleep(0.3)

    return None


# ── Main price fetcher ────────────────────────────────────────────────────────
def fetch_prices(product: dict) -> list:
    """
    Fetch prices using DuckDuckGo, one query per store.
    Buy Now links are ALWAYS our own direct store search URLs — never DDG/redirect URLs.
    """
    stores = (GROCERY_STORES if product.get("store_category") == "grocery_stores"
              else ELECTRONICS_STORES)
    query = product.get("search_query", product.get("name", ""))

    results = []
    bar = st.progress(0, text="🔍 Searching stores…")

    try:
        with DDGS() as ddgs:
            for i, store in enumerate(stores):
                pct = int((i / len(stores)) * 100)
                bar.progress(pct, text=f"🔎 Checking {store}…")

                price = _ddg_price_for_store(ddgs, store, query)

                if price:
                    # ✅ Always use our own direct store search URL — NEVER a redirect
                    buy_url = STORE_SEARCH_URLS[store](query)
                    results.append({
                        "site": store,
                        "price": price,
                        "link": buy_url,
                    })

                time.sleep(0.2)

    except Exception:
        pass

    bar.progress(100, text="✅ Done!")
    time.sleep(0.3)
    bar.empty()

    # Sort cheapest first
    return sorted(results, key=lambda x: x["price"])


# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int):
    best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 else ""
    st.markdown(f"""
<div class="ph-card rank-{rank}">
  <div class="ph-card-inner">
    <div class="ph-rank">#{rank}</div>
    <div class="ph-info">
      <div class="ph-store">{item['site']}{best}</div>
      <div class="ph-price">₹{item['price']:,.0f}</div>
    </div>
    <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="ph-buy">Buy Now →</a>
  </div>
</div>""", unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="ph-title">🛒 PriceHunt</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ph-subtitle">Type a product or upload a photo '
        '→ compare prices across Indian stores instantly</div>',
        unsafe_allow_html=True
    )

    # ── API Key (only OpenRouter needed now) ──────────────────────────────────
    openrouter_key = None
    try:
        openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        pass

    with st.sidebar:
        st.markdown("### 🔑 OpenRouter API Key")
        if not openrouter_key:
            openrouter_key = st.text_input(
                "OpenRouter Key", type="password",
                placeholder="sk-or-v1-...",
                help="Free key at openrouter.ai/keys"
            )
            st.caption("[Get free key →](https://openrouter.ai/keys)  No credit card needed")
        else:
            st.success("✅ OpenRouter key loaded")

        st.markdown("---")
        st.markdown("**How it works**")
        st.markdown(
            "- 🤖 AI identifies your product\n"
            "- 🔍 Searches each store directly\n"
            "- 🛒 Shows cheapest prices\n"
            "- ✅ No API key for price search\n"
            "- 🔗 Buy Now → goes direct to store"
        )

    if not openrouter_key:
        st.markdown("""
<div class="ph-key-card">
  <div style="font-size:2.5rem;">🔑</div>
  <h3>Get Your FREE OpenRouter API Key</h3>
  <ol>
    <li>Go to <a href="https://openrouter.ai/keys" target="_blank">openrouter.ai/keys</a></li>
    <li>Sign in with Google or GitHub (free)</li>
    <li>Click <strong>Create Key</strong></li>
    <li>Paste it in the sidebar 👈</li>
  </ol>
  <div class="ph-free-note">
    ✅ 100% Free &nbsp;·&nbsp; No credit card &nbsp;·&nbsp; No SerpAPI needed
  </div>
</div>""", unsafe_allow_html=True)
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
                    placeholder="e.g.  Maggi Noodles 12-pack  or  OnePlus Nord CE 5",
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
            go = st.form_submit_button("🔍 Find Best Prices", use_container_width=True)
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
        go = st.button("🔍 Find Best Prices", disabled=not can_search, use_container_width=True)
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
        for col, (em, title, stores_txt) in zip([d1, d2, d3], tiles):
            with col:
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #e8ddd0;border-radius:12px;
            padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="font-size:1.8rem;">{em}</div>
  <div style="font-weight:700;color:#1c1917;margin:0.3rem 0;">{title}</div>
  <div style="font-size:0.75rem;color:#78716c;">{stores_txt}</div>
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
    stores_label = (
        "Blinkit, Zepto, BigBasket, Swiggy Instamart, JioMart, DMart"
        if product.get("store_category") == "grocery_stores"
        else "Amazon, Flipkart, Croma, Vijay Sales, Reliance Digital, Tata Cliq"
    )

    st.markdown(f"""
<div class="ph-product">
  <div style="font-size:1.1rem;font-weight:700;">{cat_emoji} {product.get('name','—')}</div>
  <div style="font-size:0.85rem;margin-top:0.3rem;color:#78716c;">
    Brand: <strong>{product.get('brand') or '—'}</strong> &nbsp;·&nbsp;
    Variant: <strong>{product.get('variant') or '—'}</strong>
  </div>
  <div style="font-size:0.8rem;margin-top:0.3rem;color:#92400e;">🏪 Searching: {stores_label}</div>
</div>""", unsafe_allow_html=True)

    # Fetch & show prices
    st.markdown('<div class="ph-section">Price Comparison — Cheapest First</div>', unsafe_allow_html=True)
    results = fetch_prices(product)

    if not results:
        query = product.get("search_query", product.get("name", ""))
        stores = (GROCERY_STORES if product.get("store_category") == "grocery_stores"
                  else ELECTRONICS_STORES)
        st.warning("😕 Could not fetch prices automatically. Browse stores directly:")
        links_html = ""
        for store in stores:
            url = STORE_SEARCH_URLS[store](query)
            links_html += (
                f'<a href="{url}" target="_blank" rel="noopener noreferrer" '
                f'style="display:inline-block;background:#fef3c7;border:1px solid #fcd34d;'
                f'border-radius:20px;padding:5px 14px;font-size:0.82rem;color:#92400e;'
                f'text-decoration:none;margin:4px;">🔗 {store}</a>\n'
            )
        st.markdown(f'<div style="margin-top:0.5rem;">{links_html}</div>', unsafe_allow_html=True)
        st.info('💡 Tip: Be specific — "Samsung Galaxy S24 Ultra 256GB" not "Samsung phone"')
        return

    st.markdown(
        f'<div style="color:#78716c;font-size:0.88rem;margin-bottom:0.8rem;">'
        f'Found prices at <strong style="color:#1c1917;">{len(results)} stores</strong></div>',
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
        '⚠️ Prices sourced via web search. Always verify on the store before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
