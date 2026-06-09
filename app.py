import streamlit as st
from openai import OpenAI
import base64
import json
import re
import time
import urllib.parse
from PIL import Image
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings("ignore", message=".*langchain-community.*being sunset.*")
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

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

/* ── Hide ALL Streamlit branding (CSS layer) ── */
#MainMenu, footer, header          { display: none !important; }
.stDeployButton                    { display: none !important; }
#stDecoration                      { display: none !important; }
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="stToolbarActions"]   { display: none !important; }
[data-testid="manage-app-button"]  { display: none !important; }
[data-testid="stStatusWidget"]     { display: none !important; }
[data-testid="stActionButton"]     { display: none !important; }
.viewerBadge_container__1QSob,
.styles_viewerBadge__CvC9N,
.viewerBadge_link__qRIco           { display: none !important; }
/* emotion-cache class prefixes used for wand/crown badges */
[class*="badge"]                   { display: none !important; }
[class*="Badge"]                   { display: none !important; }
[class*="ActionButton"]            { display: none !important; }
/* Fixed-position overlays at bottom corners */
button[data-testid="baseButton-headerNoPadding"] { display: none !important; }
.stApp > header::before            { display: none !important; }
.stApp                             { padding-bottom: 0 !important; }

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

# ── HTTP headers — mimic a real browser ─────────────────────────────────────
SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
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
    if not text:
        return None
    patterns = [
        r'₹\s*([\d,]+(?:\.\d{1,2})?)',
        r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
        r'INR\s*([\d,]+(?:\.\d{1,2})?)',
        r'MRP[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'at\s*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'for\s*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'\?\s*([\d,]+(?:\.\d{1,2})?)',  # Handle DDG replacing rupee symbol with question mark
        r'"price"\s*:\s*"?([\d,.]+)',
        r'"selling_price"\s*:\s*"?([\d,.]+)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                p = float(m.group(1).replace(",", ""))
                if 5 < p < 10_000_000:
                    return p
            except ValueError:
                pass
    return None


def extract_price_from_json_ld(html: str) -> float | None:
    """Parse structured data (JSON-LD) to find the price."""
    if not html:
        return None
    try:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                if isinstance(data, list):
                    items = data
                else:
                    items = [data]
                    
                for item in items:
                    # Check offers
                    offers = item.get("offers")
                    if offers:
                        if isinstance(offers, list):
                            for off in offers:
                                price = off.get("price")
                                if price:
                                    return float(str(price).replace(",", ""))
                        elif isinstance(offers, dict):
                            price = offers.get("price")
                            if price:
                                return float(str(price).replace(",", ""))
                    
                    price = item.get("price")
                    if price:
                        return float(str(price).replace(",", ""))
            except Exception:
                pass
    except Exception:
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


# ── Per-store scrapers ───────────────────────────────────────────────────────

def _get(url: str, timeout: int = 12) -> requests.Response | None:
    """GET with browser headers. Returns None on any error."""
    try:
        r = requests.get(url, headers=SCRAPE_HEADERS, timeout=timeout, allow_redirects=True)
        return r if r.status_code == 200 else None
    except Exception:
        return None

def _scrape_amazon_direct(url: str) -> float | None:
    """Fetch Amazon product page and extract price."""
    r = _get(url)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    selectors = [
        "span.priceToPay span.a-offscreen",
        "span.apexPriceToPay span.a-offscreen",
        "span.a-price span.a-offscreen",
        "span.a-price-whole",
        "span.a-color-price",
        "span#priceblock_ourprice",
        "span#priceblock_dealprice"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            price = extract_price(el.get_text())
            if price:
                return price
    return None


def _scrape_flipkart_direct(url: str) -> float | None:
    """Fetch Flipkart product page and extract price."""
    r = _get(url)
    if not r:
        return None
    price = extract_price_from_json_ld(r.text)
    if price:
        return price
    soup = BeautifulSoup(r.text, "html.parser")
    selectors = [
        "div.Nx9bqj",
        "div._30jeq3",
        "div._1_WHN1",
        "div[class*='price']",
        "span[class*='price']"
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            price = extract_price(el.get_text())
            if price:
                return price
    return None


def _scrape_bigbasket_direct(url: str) -> float | None:
    """Fetch BigBasket product page and extract price."""
    r = _get(url)
    if not r:
        return None
    price = extract_price_from_json_ld(r.text)
    if price:
        return price
    price = extract_price(r.text[:80000])
    return price


def _scrape_generic_direct(url: str) -> float | None:
    """Fetch generic product page and search for price."""
    r = _get(url)
    if not r:
        return None
    price = extract_price_from_json_ld(r.text)
    if price:
        return price
    price = extract_price(r.text[:80000])
    return price


# ── Native search page scrapers (bypass DuckDuckGo for accuracy) ────────────
def _scrape_amazon_search(query: str) -> dict | None:
    """Scrape Amazon India search results page for the first matching product and price."""
    url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"
    r = _get(url, timeout=15)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    
    # Find product cards in search results
    cards = soup.select("div[data-component-type='s-search-result']")
    if not cards:
        # Fallback: look for result items
        cards = soup.select("div.s-result-item[data-asin]")
    
    accessory_words = [
        "cover", "case", "glass", "protector", "guard", "cable", "charger",
        "adapter", "strap", "pouch", "film", "skin", "sleeve", "tempered",
        "holder", "stand", "mount", "ring", "grip", "sticker", "decal"
    ]
    query_lower = query.lower()
    
    for card in cards[:10]:  # Check top 10 results
        # Skip sponsored/ad results
        if card.select_one("span.s-label-popover-default"):
            continue
        asin = card.get("data-asin", "")
        if not asin:
            continue
        
        # Get the title
        title_el = card.select_one("h2 a span") or card.select_one("h2 span") or card.select_one(".a-text-normal")
        title = title_el.get_text(strip=True) if title_el else ""
        title_lower = title.lower()
        
        # Skip accessories
        is_accessory = False
        for kw in accessory_words:
            if kw in title_lower and kw not in query_lower:
                is_accessory = True
                break
        if is_accessory:
            continue
        
        # Extract price
        price_el = (card.select_one("span.a-price span.a-offscreen") or
                    card.select_one("span.a-price-whole") or
                    card.select_one("span.a-color-price"))
        if price_el:
            price = extract_price(price_el.get_text())
            if price:
                # Build product URL
                link_el = card.select_one("h2 a")
                product_link = f"https://www.amazon.in/dp/{asin}" if asin else url
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    if not href.startswith("http"):
                        href = "https://www.amazon.in" + href
                    product_link = href
                return {"price": price, "link": product_link, "title": title}
    return None


def _scrape_flipkart_search(query: str) -> dict | None:
    """Scrape Flipkart search results page for the first matching product and price."""
    url = f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(query)}"
    r = _get(url, timeout=15)
    if not r:
        return None
    
    # Try JSON-LD first
    price_from_ld = extract_price_from_json_ld(r.text)
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    accessory_words = [
        "cover", "case", "glass", "protector", "guard", "cable", "charger",
        "adapter", "strap", "pouch", "film", "skin", "sleeve", "tempered",
        "holder", "stand", "mount", "ring", "grip", "sticker", "decal"
    ]
    query_lower = query.lower()
    
    # Flipkart uses various card structures - try multiple selectors
    # Method 1: Find product cards by link+price pattern
    product_links = soup.select("a[href*='/p/']")
    if not product_links:
        product_links = soup.select("a[href*='pid=']")
    
    for link_el in product_links[:15]:
        href = link_el.get("href", "")
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://www.flipkart.com" + href
        
        # Get the card container (parent of the link)
        card = link_el
        # Walk up to find the product card container
        for _ in range(5):
            parent = card.parent
            if parent:
                card = parent
            else:
                break
        
        card_text = card.get_text(" ", strip=True).lower()
        
        # Skip accessories
        is_accessory = False
        for kw in accessory_words:
            if kw in card_text and kw not in query_lower:
                is_accessory = True
                break
        if is_accessory:
            continue
        
        # Look for price in the card container
        price_el = (card.select_one("div.Nx9bqj") or
                    card.select_one("div._30jeq3") or
                    card.select_one("div._1_WHN1") or
                    card.select_one("div[class*='price']") or
                    card.select_one("span[class*='price']"))
        
        if price_el:
            price = extract_price(price_el.get_text())
            if price:
                title_el = (card.select_one("div.KzDlHZ") or
                            card.select_one("a.IRpwTa") or
                            card.select_one("div._4rR01T") or
                            card.select_one("a.s1Q9rs"))
                title = title_el.get_text(strip=True) if title_el else ""
                return {"price": price, "link": href, "title": title}
        
        # Try extracting price from card text
        price = extract_price(card.get_text())
        if price:
            return {"price": price, "link": href, "title": ""}
    
    # Fallback: try any price on the page with JSON-LD
    if price_from_ld:
        return {"price": price_from_ld, "link": url, "title": ""}
    
    return None


# Stores that have native search page scrapers (bypass DuckDuckGo)
NATIVE_SEARCH_SCRAPERS = {
    "Amazon India":  _scrape_amazon_search,
    "Flipkart":      _scrape_flipkart_search,
}

DIRECT_SCRAPERS = {
    "Amazon India":     _scrape_amazon_direct,
    "Flipkart":         _scrape_flipkart_direct,
    "BigBasket":        _scrape_bigbasket_direct,
}

STORE_DOMAINS = {
    "amazon.in":          "Amazon India",
    "flipkart.com":       "Flipkart",
    "croma.com":          "Croma",
    "reliancedigital.in": "Reliance Digital",
    "vijaysales.com":     "Vijay Sales",
    "tatacliq.com":       "Tata Cliq",
    "blinkit.com":        "Blinkit",
    "zeptonow.com":       "Zepto",
    "bigbasket.com":      "BigBasket",
    "swiggy.com":         "Swiggy Instamart",
    "jiomart.com":        "JioMart",
    "dmart.in":           "DMart Online",
}

# Price sanity bounds per category — skip results outside these ranges
PRICE_BOUNDS = {
    "electronics_stores": (500, 10_000_000),    # Electronics: ₹500 – ₹1Cr
    "grocery_stores":     (5, 50_000),           # Grocery: ₹5 – ₹50K
}

# ── LangChain DuckDuckGo Search helpers ──────────────────────────────────────

# Store domains for site-scoped targeted searches
STORE_SITE_DOMAINS = {
    "Amazon India": "amazon.in",
    "Flipkart": "flipkart.com",
    "Croma": "croma.com",
    "Vijay Sales": "vijaysales.com",
    "Reliance Digital": "reliancedigital.in",
    "Tata Cliq": "tatacliq.com",
    "Blinkit": "blinkit.com",
    "Zepto": "zeptonow.com",
    "BigBasket": "bigbasket.com",
    "Swiggy Instamart": "swiggy.com",
    "JioMart": "jiomart.com",
    "DMart Online": "dmart.in",
}

# Accessory keywords used for both query exclusion and result filtering
ACCESSORY_EXCLUDE_KEYWORDS = [
    "cover", "case", "protector", "guard", "tempered", "glass",
    "cable", "charger", "adapter", "strap", "pouch", "film",
    "skin", "sleeve", "holder", "stand", "mount", "sticker",
    "decal", "buds", "earbuds", "headphones", "tpu", "bumper",
    "folio", "wallet case", "flip cover", "lens protector",
    "camera protector", "back cover", "screen guard",
]


def _build_exclusion_string(query: str) -> str:
    """Build negative keyword string, skipping terms already in the user's query."""
    query_lower = query.lower()
    return " ".join(f"-{kw}" for kw in ACCESSORY_EXCLUDE_KEYWORDS if kw not in query_lower)


def _langchain_ddg_search(search_query: str, max_results: int = 10) -> list:
    """Perform search using LangChain's DuckDuckGoSearchResults tool.
    Returns a list of dicts with keys: snippet, title, link."""
    try:
        wrapper = DuckDuckGoSearchAPIWrapper(
            max_results=max_results,
            region="in-en",  # India region for relevant pricing
        )
        tool = DuckDuckGoSearchResults(
            api_wrapper=wrapper,
            output_format="list",
        )
        results = tool.invoke(search_query)
        return results if isinstance(results, list) else []
    except Exception:
        return []


def _is_accessory_result(text: str, query: str) -> bool:
    """Check if a search result is an accessory/irrelevant product."""
    text_lower = text.lower()
    query_lower = query.lower()
    return any(
        kw in text_lower and kw not in query_lower
        for kw in ACCESSORY_EXCLUDE_KEYWORDS
    )


def _search_store_targeted(query: str, store_name: str) -> dict | None:
    """Search for a product on a specific store using site-scoped LangChain search.
    Uses exact-quoted product name + negative keywords for maximum accuracy."""
    domain = STORE_SITE_DOMAINS.get(store_name)
    if not domain:
        return None

    exclusions = _build_exclusion_string(query)
    search_query = f'"{query}" price site:{domain} {exclusions}'

    results = _langchain_ddg_search(search_query, max_results=5)

    for r in results:
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        link = r.get("link", "")

        # Verify it's actually from the target domain
        if domain not in link.lower():
            continue

        # Skip accessory results
        combined = f"{title} {snippet}"
        if _is_accessory_result(combined, query):
            continue

        price = extract_price(title) or extract_price(snippet)
        return {"price": price, "link": link, "title": title}

    return None


# ── Main price fetcher — hybrid parallel scraping ─────────────────────────────
def _price_in_bounds(price: float | None, store_category: str) -> bool:
    """Check if a price falls within sane bounds for the product category."""
    if price is None:
        return True  # No price to check
    lo, hi = PRICE_BOUNDS.get(store_category, (5, 10_000_000))
    return lo <= price <= hi


def fetch_prices(product: dict) -> list:
    """
    Hybrid approach:
    1. For Amazon & Flipkart: scrape their native search pages directly (most accurate)
    2. For other stores: use DuckDuckGo to find product links, then scrape
    3. Apply price sanity bounds to filter out accessories/wrong products
    """
    store_category = product.get("store_category", "electronics_stores")
    category_stores = (GROCERY_STORES if store_category == "grocery_stores"
                       else ELECTRONICS_STORES)
    query = product.get("search_query", product.get("name", ""))
    
    bar = st.progress(0, text="🔍 Searching for best prices…")
    
    found_stores = {}
    
    # ── PHASE 1: Native search scrapers (Amazon, Flipkart) — most reliable ──
    native_stores = [s for s in category_stores if s in NATIVE_SEARCH_SCRAPERS]
    
    def scrape_native(store_name: str) -> tuple[str, dict | None]:
        fn = NATIVE_SEARCH_SCRAPERS[store_name]
        try:
            return store_name, fn(query)
        except Exception:
            return store_name, None
    
    if native_stores:
        bar.progress(5, text=f"🛒 Searching {', '.join(native_stores)} directly…")
        with ThreadPoolExecutor(max_workers=len(native_stores)) as ex:
            futures = {ex.submit(scrape_native, s): s for s in native_stores}
            for future in as_completed(futures):
                store_name, result = future.result()
                if result and result.get("price"):
                    price = result["price"]
                    if _price_in_bounds(price, store_category):
                        found_stores[store_name] = {
                            "site": store_name,
                            "link": result.get("link", STORE_SEARCH_URLS[store_name](query)),
                            "price": price,
                        }
    
    bar.progress(25, text="🔍 Searching via LangChain DuckDuckGo…")
    
    # ── PHASE 2a: LangChain broad search with smart query ───────────────────
    ddg_target_stores = [s for s in category_stores if s not in found_stores]
    
    # Build a smarter query: quoted product name + negative keywords to exclude accessories
    exclusions = _build_exclusion_string(query)
    search_q = f'"{query}" price buy online India {exclusions}'
    raw_results = _langchain_ddg_search(search_q, max_results=25)
    
    if not raw_results:
        st.warning("⚠️ Broad search returned no results, trying targeted searches…")
        
    bar.progress(40, text="🔗 Mapping results to stores…")
    
    user_query_lower = query.lower()
    
    for r in raw_results:
        href = r.get("link", "")
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        
        parsed_url = urllib.parse.urlparse(href)
        domain = parsed_url.netloc.replace("www.", "").lower()
        
        # Skip accessory results using centralized filter
        combined_text = f"{title} {href} {snippet}"
        if _is_accessory_result(combined_text, query):
            continue
            
        matched_store = None
        for d_key, store_name in STORE_DOMAINS.items():
            if d_key in domain:
                if store_name in ddg_target_stores:
                    matched_store = store_name
                    break
        
        if matched_store and matched_store not in found_stores:
            # Try to parse price from snippet
            price = extract_price(title) or extract_price(snippet)
            
            # Apply price sanity check on snippet prices
            if price and not _price_in_bounds(price, store_category):
                price = None  # Reject out-of-bounds prices (likely accessories)
            
            found_stores[matched_store] = {
                "site": matched_store,
                "link": href,
                "price": price,
            }
    
    # ── PHASE 2b: Targeted per-store site-scoped search for missing stores ──
    still_missing = [s for s in ddg_target_stores if s not in found_stores]
    
    if still_missing:
        bar.progress(45, text=f"🎯 Targeted search for {len(still_missing)} remaining stores…")
        
        def _targeted_search(store_name: str) -> tuple:
            return store_name, _search_store_targeted(query, store_name)
        
        with ThreadPoolExecutor(max_workers=min(3, len(still_missing))) as ex:
            futures = {ex.submit(_targeted_search, s): s for s in still_missing}
            done_targeted = 0
            for future in as_completed(futures):
                store_name, result = future.result()
                done_targeted += 1
                bar.progress(
                    45 + int(done_targeted / len(still_missing) * 10),
                    text=f"🎯 {done_targeted}/{len(still_missing)} targeted searches done…"
                )
                if result:
                    price = result.get("price")
                    if price and not _price_in_bounds(price, store_category):
                        price = None
                    found_stores[store_name] = {
                        "site": store_name,
                        "link": result.get("link", STORE_SEARCH_URLS[store_name](query)),
                        "price": price,
                    }
                
    # ── PHASE 3: Scrape direct pages for stores with no price yet ───────────
    stores_to_scrape = [item for item in found_stores.values() if item["price"] is None]
    
    done = 0
    total = len(stores_to_scrape)
    
    def scrape_store_page(item: dict) -> tuple[str, float | None]:
        store_name = item["site"]
        url = item["link"]
        fn = DIRECT_SCRAPERS.get(store_name, _scrape_generic_direct)
        try:
            price = fn(url)
            # Apply sanity bounds to scraped prices too
            if price and _price_in_bounds(price, store_category):
                return store_name, price
            return store_name, None
        except Exception:
            return store_name, None

    if total > 0:
        bar.progress(55, text=f"🔍 Fetching live prices from {total} stores…")
        with ThreadPoolExecutor(max_workers=min(6, total)) as ex:
            futures = {ex.submit(scrape_store_page, item): item for item in stores_to_scrape}
            for future in as_completed(futures):
                store_name, price = future.result()
                done += 1
                bar.progress(55 + int(done / total * 40),
                             text=f"✅ {done}/{total} stores checked…")
                if price:
                    found_stores[store_name]["price"] = price

    bar.progress(100, text="✅ Done!")
    time.sleep(0.3)
    bar.empty()
    
    # Ensure all top 6 trusted platforms are present in the results
    for store in category_stores:
        if store not in found_stores:
            found_stores[store] = {
                "site": store,
                "link": STORE_SEARCH_URLS[store](query),
                "price": None
            }
            
    # Convert dict to list
    results_list = list(found_stores.values())
    
    # Sort results:
    # 1. Items with prices sorted ascending
    # 2. Items without prices sorted by store name
    with_price = [r for r in results_list if r["price"] is not None]
    no_price = [r for r in results_list if r["price"] is None]
    
    sorted_with_price = sorted(with_price, key=lambda x: x["price"])
    sorted_no_price = sorted(no_price, key=lambda x: x["site"])
    
    return sorted_with_price + sorted_no_price



# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int):
    price_val = item.get("price")
    if price_val is not None:
        price_display = f"₹{price_val:,.0f}"
        best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 else ""
    else:
        price_display = '<span style="font-size: 1.1rem; color: #78716c; font-weight: 600;">Check Price</span>'
        best = ""
        
    st.markdown(f"""
<div class="ph-card rank-{rank}">
  <div class="ph-card-inner">
    <div class="ph-rank">#{rank}</div>
    <div class="ph-info">
      <div class="ph-store">{item['site']}{best}</div>
      <div class="ph-price">{price_display}</div>
    </div>
    <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="ph-buy">Buy Now →</a>
  </div>
</div>""", unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    # ── JS: Kill Streamlit badges that CSS can't reach (iframes / shadow DOM) ──
    st.markdown("""
<script>
(function hideSLBadges() {
    var selectors = [
        '[data-testid="stActionButton"]',
        '[data-testid="manage-app-button"]',
        '[data-testid="stStatusWidget"]',
        '.viewerBadge_link__qRIco',
        '.styles_viewerBadge__CvC9N',
        '.viewerBadge_container__1QSob',
        'button[kind="header"]',
        'a[href*="streamlit.io"]',
    ];
    function hide() {
        selectors.forEach(function(sel) {
            document.querySelectorAll(sel).forEach(function(el) {
                el.style.setProperty('display', 'none', 'important');
            });
        });
        // Also hide any fixed-position elements at bottom corners (crown/M badges)
        document.querySelectorAll('*').forEach(function(el) {
            var st = window.getComputedStyle(el);
            if (st.position === 'fixed' && (parseInt(st.bottom) < 80) &&
                (parseInt(st.right) < 120 || parseInt(st.left) < 120)) {
                var tag = el.tagName.toLowerCase();
                if (tag === 'button' || tag === 'a' || tag === 'div') {
                    el.style.setProperty('display', 'none', 'important');
                }
            }
        });
    }
    hide();
    setTimeout(hide, 500);
    setTimeout(hide, 1500);
    setTimeout(hide, 3000);
    new MutationObserver(hide).observe(document.documentElement,
        { childList: true, subtree: true });
})();
</script>
""", unsafe_allow_html=True)

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

    results_with_price = [r for r in results if r["price"] is not None]
    if len(results_with_price) >= 2:
        save = results_with_price[-1]["price"] - results_with_price[0]["price"]
        pct  = save / results_with_price[-1]["price"] * 100
        if save > 0:
            st.markdown(f"""
<div class="ph-savings">
  <div class="ph-savings-amt">💰 Save ₹{save:,.0f} ({pct:.0f}%)</div>
  <div class="ph-savings-sub">
    Buy from <strong>{results_with_price[0]['site']}</strong>
    instead of <strong>{results_with_price[-1]['site']}</strong>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;color:#b8a99a;font-size:0.74rem;margin-top:1rem;">'
        '⚠️ Prices sourced via web search. Always verify on the store before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
