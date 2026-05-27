import streamlit as st
from openai import OpenAI
import base64
import json
import re
import time
import urllib.parse
from duckduckgo_search import DDGS
from PIL import Image
import io

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PriceHunt – AI Price Comparison",
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
#MainMenu, footer, header { visibility: hidden; }

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
.ph-est { font-size: 0.73rem; color: #d97706; margin-left: 4px; }
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

[data-testid="stSidebar"] { background: #fdf8f2 !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input { background: #fff !important; }
</style>
""", unsafe_allow_html=True)

# ── OpenRouter config ─────────────────────────────────────────────────────────
OPENROUTER_BASE = "https://openrouter.ai/api/v1"
# Free models on OpenRouter (vision-capable)
VISION_MODEL   = "google/gemini-2.0-flash-exp:free"
TEXT_MODEL     = "google/gemini-2.0-flash-exp:free"  # same model, also great for text

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


def make_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)


def ai_call(client: OpenAI, messages: list, model: str = TEXT_MODEL) -> str:
    """Call OpenRouter API, returns response text."""
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=600)
    return resp.choices[0].message.content.strip()


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


def extract_price(text: str):
    for pat in [r'₹\s*([\d,]+(?:\.\d{1,2})?)', r'Rs\.?\s*([\d,]+)', r'INR\s*([\d,]+)']:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                p = float(m.group(1).replace(",", ""))
                if 1 < p < 1_000_000:
                    return p
            except ValueError:
                pass
    return None


def parse_json_response(raw: str, is_array: bool = False):
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
    pattern = r'\[.*\]' if is_array else r'\{.*\}'
    m = re.search(pattern, raw, re.DOTALL)
    return json.loads(m.group(0) if m else raw)


# ── AI: Identify product from IMAGE ──────────────────────────────────────────
def identify_from_image(client: OpenAI, image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    # Detect image type
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
    ], model=VISION_MODEL)
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


# ── AI: Fallback estimated prices ────────────────────────────────────────────
def ai_price_fallback(client: OpenAI, product: dict, stores: list) -> list:
    prompt = f"""Indian e-commerce pricing expert.
Product: {product['name']} {product.get('variant', '')}
Stores: {', '.join(stores)}

Return ONLY a JSON array (no markdown):
[{{"site":"StoreName","price":299,"link":"https://store.com/search?q=product","estimated":true}}]
Use realistic current INR prices. Only include stores that carry this product."""

    raw = ai_call(client, [{"role": "user", "content": prompt}])
    return parse_json_response(raw, is_array=True)


# ── Search: DuckDuckGo price lookup ──────────────────────────────────────────
def search_store_price(ddgs, store: str, query: str) -> dict:
    domain = STORE_DOMAINS.get(store, "")
    for q in [f'site:{domain} {query} price', f'{query} price {store} India']:
        try:
            for r in ddgs.text(q, max_results=6):
                price = extract_price(r.get("body", "") + " " + r.get("title", ""))
                if price:
                    url = r.get("href", "")
                    if not url or domain not in url:
                        url = build_search_url(store, query)
                    return {"site": store, "price": price, "link": url, "estimated": False}
        except Exception:
            time.sleep(0.4)
    return {"site": store, "price": None, "link": build_search_url(store, query), "estimated": False}


def fetch_prices(client: OpenAI, product: dict) -> list:
    stores = GROCERY_STORES if product.get("store_category") == "grocery_stores" else ELECTRONICS_STORES
    results, live_count = [], 0
    bar = st.progress(0, text="Searching stores…")
    with DDGS() as ddgs:
        for i, store in enumerate(stores):
            bar.progress((i + 1) / len(stores), text=f"Checking {store}…")
            r = search_store_price(ddgs, store, product["search_query"])
            results.append(r)
            if r.get("price"):
                live_count += 1
            time.sleep(0.35)
    bar.empty()

    if live_count < 3:
        st.info("⚡ Few live prices found — adding AI estimates…")
        try:
            fb = ai_price_fallback(client, product, stores)
            have = {r["site"] for r in results if r.get("price")}
            for f in fb:
                if f.get("site") not in have and f.get("price"):
                    results.append(f)
        except Exception:
            pass

    priced = sorted([r for r in results if r.get("price")], key=lambda x: x["price"])
    return priced[:6]


# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int):
    est  = '<span class="ph-est">(AI estimate)</span>' if item.get("estimated") else ""
    best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 else ""
    st.markdown(f"""
<div class="ph-card rank-{rank}">
  <div class="ph-card-inner">
    <div class="ph-rank">#{rank}</div>
    <div class="ph-info">
      <div class="ph-store">{item['site']}{best}</div>
      <div class="ph-price">₹{item['price']:,.0f}{est}</div>
    </div>
    <a href="{item['link']}" target="_blank" class="ph-buy">Buy Now →</a>
  </div>
</div>""", unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="ph-title">🛒 PriceHunt</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ph-subtitle">Type a product name or upload a photo '
        '→ AI finds the cheapest price across Indian stores</div>',
        unsafe_allow_html=True
    )

    # ── API Key ────────────────────────────────────────────────────────────────
    api_key = None
    try:
        api_key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass

    if not api_key:
        with st.sidebar:
            st.markdown("### 🔑 OpenRouter API Key")
            api_key = st.text_input("OpenRouter Key", type="password", placeholder="sk-or-v1-...")
            st.caption("[Get free key →](https://openrouter.ai/keys)  No credit card needed")
            st.markdown("**Free** · Vision support · Multiple models")

    if not api_key:
        st.markdown("""
<div class="ph-key-card">
  <div style="font-size:2.5rem;">🔑</div>
  <h3>Get Your FREE OpenRouter API Key</h3>
  <ol>
    <li>Go to <a href="https://openrouter.ai/keys" target="_blank">openrouter.ai/keys</a></li>
    <li>Click <strong>Sign in</strong> → use Google or GitHub (free)</li>
    <li>Click <strong>Create Key</strong></li>
    <li>Copy the key (starts with <code>sk-or-v1-</code>)</li>
    <li>Paste it in the sidebar 👈</li>
  </ol>
  <div class="ph-free-note">
    ✅ 100% Free &nbsp;·&nbsp; No credit card &nbsp;·&nbsp; Vision + Text AI &nbsp;·&nbsp; Multiple free models
  </div>
</div>""", unsafe_allow_html=True)
        st.stop()

    client = make_client(api_key)

    # ── Search Mode ────────────────────────────────────────────────────────────
    st.markdown('<div class="ph-section">How do you want to search?</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["📝 Type product name", "📸 Upload product image"],
                    horizontal=True, label_visibility="collapsed")

    text_query, uploaded_file, category = None, None, "Auto-detect"

    if mode == "📝 Type product name":
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
<div style="margin-top:0.4rem;">
  <span class="ph-chip">🥥 Coconut Water</span>
  <span class="ph-chip">🍜 Maggi Noodles</span>
  <span class="ph-chip">💻 HP Victus Laptop</span>
  <span class="ph-chip">📱 Samsung Galaxy S24</span>
  <span class="ph-chip">🧴 Dove Shampoo 650ml</span>
</div>""", unsafe_allow_html=True)
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
    can_search = bool(text_query and text_query.strip()) or bool(uploaded_file)
    go = st.button("🔍 Find Best Prices", disabled=not can_search, use_container_width=True)

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
        for col, (em, title, stores) in zip([d1, d2, d3], tiles):
            with col:
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #e8ddd0;border-radius:12px;
            padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="font-size:1.8rem;">{em}</div>
  <div style="font-weight:700;color:#1c1917;margin:0.3rem 0;">{title}</div>
  <div style="font-size:0.75rem;color:#78716c;">{stores}</div>
</div>""", unsafe_allow_html=True)
        return

    if not go:
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
    stores_txt = ("Zepto, Blinkit, Swiggy Instamart, BigBasket, JioMart, DMart"
                  if product.get("store_category") == "grocery_stores"
                  else "Amazon, Flipkart, Croma, Vijay Sales, Reliance Digital, Tata Cliq")

    st.markdown(f"""
<div class="ph-product">
  <div style="font-size:1.1rem;font-weight:700;">{cat_emoji} {product.get('name','—')}</div>
  <div style="font-size:0.85rem;margin-top:0.3rem;color:#78716c;">
    Brand: <strong>{product.get('brand') or '—'}</strong> &nbsp;·&nbsp;
    Variant: <strong>{product.get('variant') or '—'}</strong>
  </div>
  <div style="font-size:0.8rem;margin-top:0.3rem;color:#92400e;">🏪 Searching: {stores_txt}</div>
</div>""", unsafe_allow_html=True)

    # Fetch & show prices
    st.markdown('<div class="ph-section">Price Comparison — Cheapest First</div>', unsafe_allow_html=True)
    results = fetch_prices(client, product)

    if not results:
        st.error("😕 No prices found. Try a clearer / more specific query.")
        return

    st.markdown(
        f'<div style="color:#78716c;font-size:0.88rem;margin-bottom:0.8rem;">'
        f'Found <strong style="color:#1c1917;">{len(results)} stores</strong> with prices</div>',
        unsafe_allow_html=True
    )

    for i, item in enumerate(results, 1):
        result_card(item, i)

    if len(results) >= 2:
        save = results[-1]["price"] - results[0]["price"]
        pct  = save / results[-1]["price"] * 100
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
        '⚠️ Prices fetched live via web search. AI estimates are approximate. '
        'Verify on the retailer\'s website before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
