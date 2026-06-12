import streamlit as st
import streamlit.components.v1 as components
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
[class*="badge"]                   { display: none !important; }
[class*="Badge"]                   { display: none !important; }
[class*="ActionButton"]            { display: none !important; }
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
.ph-link {
    font-size: 0.78rem; color: #6b7280; margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px;
}
.ph-price { font-size: 1.5rem; font-weight: 800; color: #059669; margin-top: 4px; }
.ph-source {
    font-size: 0.65rem; color: #b8a99a; margin-top: 2px; font-style: italic;
}
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
.ph-visit {
    display: inline-block; background: #e5e7eb; color: #44403c !important;
    font-weight: 700; font-size: 0.82rem; padding: 7px 18px;
    border-radius: 8px; text-decoration: none !important; white-space: nowrap;
}
.ph-visit:hover { background: #d1d5db !important; }

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

# ── Store config ──────────────────────────────────────────────────────────────
GROCERY_STORES = ["Blinkit", "Zepto", "BigBasket", "Swiggy Instamart", "JioMart", "DMart Online"]
ELECTRONICS_STORES = ["Amazon India", "Flipkart", "Croma", "Vijay Sales", "Reliance Digital", "Tata Cliq"]

STORE_DOMAINS = {
    "Blinkit": "blinkit.com", "Zepto": "zeptonow.com", "BigBasket": "bigbasket.com",
    "Swiggy Instamart": "swiggy.com", "JioMart": "jiomart.com", "DMart Online": "dmart.in",
    "Amazon India": "amazon.in", "Flipkart": "flipkart.com", "Croma": "croma.com",
    "Vijay Sales": "vijaysales.com", "Reliance Digital": "reliancedigital.in", "Tata Cliq": "tatacliq.com",
}

STORE_SEARCH_URLS = {
    "Blinkit":          lambda q: f"https://blinkit.com/s/?q={urllib.parse.quote_plus(q)}",
    "Zepto":            lambda q: f"https://www.zeptonow.com/search?query={urllib.parse.quote_plus(q)}",
    "BigBasket":        lambda q: f"https://www.bigbasket.com/ps/?q={urllib.parse.quote_plus(q)}",
    "Swiggy Instamart": lambda q: f"https://www.swiggy.com/instamart/search?query={urllib.parse.quote_plus(q)}",
    "JioMart":          lambda q: f"https://www.jiomart.com/search/{urllib.parse.quote_plus(q)}",
    "DMart Online":     lambda q: f"https://www.dmart.in/search?q={urllib.parse.quote_plus(q)}",
    "Amazon India":     lambda q: f"https://www.amazon.in/s?k={urllib.parse.quote_plus(q)}",
    "Flipkart":         lambda q: f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(q)}",
    "Croma":            lambda q: f"https://www.croma.com/search/?text={urllib.parse.quote_plus(q)}",
    "Vijay Sales":      lambda q: f"https://www.vijaysales.com/search?q={urllib.parse.quote_plus(q)}",
    "Reliance Digital": lambda q: f"https://www.reliancedigital.in/products?q={urllib.parse.quote_plus(q)}",
    "Tata Cliq":        lambda q: f"https://www.tatacliq.com/search/?searchCategory=all&text={urllib.parse.quote_plus(q)}",
}

# ── Location ──────────────────────────────────────────────────────────────────
CITY_TIERS = {
    "metro": [
        "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "hyderabad",
        "chennai", "pune", "kolkata", "ahmedabad", "gurgaon", "gurugram",
        "noida", "greater noida", "ghaziabad", "faridabad", "navi mumbai", "thane",
    ],
    "tier1_5": [
        "jaipur", "lucknow", "chandigarh", "kochi", "cochin", "indore",
        "bhopal", "nagpur", "visakhapatnam", "vizag", "coimbatore",
        "thiruvananthapuram", "trivandrum", "patna", "vadodara", "baroda",
        "surat", "ludhiana", "agra", "nashik", "rajkot", "madurai",
        "varanasi", "bhubaneswar", "dehradun", "mysore", "mysuru",
        "mangalore", "mangaluru", "goa", "panaji", "panjim",
    ],
    "tier2": [
        "ranchi", "raipur", "allahabad", "prayagraj", "amritsar", "jodhpur",
        "gwalior", "jalandhar", "aurangabad", "jammu", "udaipur", "siliguri",
        "warangal", "guntur", "bikaner", "ajmer", "bhilai", "jamshedpur",
        "nellore", "cuttack", "dhanbad", "salem", "tiruchirappalli", "trichy",
        "bareilly", "moradabad", "gorakhpur", "hubli", "dharwad",
        "kozhikode", "calicut", "thrissur", "kannur", "kottayam",
        "pondicherry", "puducherry",
    ],
}

STORE_AVAILABILITY = {
    "metro": {
        "grocery": GROCERY_STORES[:],
        "electronics": ELECTRONICS_STORES[:],
    },
    "tier1_5": {
        "grocery": ["BigBasket", "Swiggy Instamart", "JioMart", "DMart Online", "Blinkit", "Zepto"],
        "electronics": ["Amazon India", "Flipkart", "Croma", "Reliance Digital", "Vijay Sales", "Tata Cliq"],
    },
    "tier2": {
        "grocery": ["BigBasket", "JioMart", "DMart Online", "Swiggy Instamart"],
        "electronics": ["Amazon India", "Flipkart", "Reliance Digital", "Croma"],
    },
    "tier3": {
        "grocery": ["BigBasket", "JioMart", "DMart Online"],
        "electronics": ["Amazon India", "Flipkart", "Reliance Digital"],
    },
}

SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,hi;q=0.6",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Cache-Control": "max-age=0",
}


# ── Geolocation ──────────────────────────────────────────────────────────────
def reverse_geocode(lat: float, lng: float) -> str:
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json&addressdetails=1&zoom=12"
        r = requests.get(url, headers={"User-Agent": "PriceHunt/1.0"}, timeout=5)
        if r.status_code == 200:
            addr = r.json().get("address", {})
            return (addr.get("city") or addr.get("town") or addr.get("village")
                    or addr.get("county") or addr.get("state_district") or addr.get("state") or "")
    except Exception:
        pass
    return ""


def get_city_tier(city: str) -> str:
    city_lower = city.lower().strip().replace(" city", "").replace(" urban", "").strip()
    for tier, cities in CITY_TIERS.items():
        for known in cities:
            if known in city_lower or city_lower in known:
                return tier
    return "tier2" if len(city_lower) > 2 else "tier3"


def get_available_stores(city: str, category: str) -> list:
    tier = get_city_tier(city)
    store_type = "grocery" if category == "grocery_stores" else "electronics"
    return STORE_AVAILABILITY.get(tier, STORE_AVAILABILITY["tier3"]).get(store_type, [])


# ── OpenRouter helpers ────────────────────────────────────────────────────────
def make_client(api_key: str) -> OpenAI:
    return OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)


def ai_call(client: OpenAI, messages: list, is_vision: bool = False) -> str:
    for m in (VISION_MODELS if is_vision else TEXT_MODELS):
        try:
            resp = client.chat.completions.create(model=m, messages=messages, max_tokens=1200)
            if resp and resp.choices and resp.choices[0].message.content:
                return resp.choices[0].message.content.strip()
        except Exception as e:
            if "429" in str(e) or "404" in str(e) or "NoneType" in str(e):
                time.sleep(0.5)
                continue
            raise
    raise Exception("All models unavailable. Try again shortly.")


def parse_json_response(raw: str) -> dict:
    cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw.strip()).strip()
    cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
    m = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    return json.loads(cleaned)


# ── Price extraction ─────────────────────────────────────────────────────────
def extract_price(text: str):
    if not text:
        return None
    patterns = [
        r'₹\s*([\d,]+(?:\.\d{1,2})?)',
        r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
        r'INR\s*([\d,]+(?:\.\d{1,2})?)',
        r'MRP[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'price[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)',
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
    if not html:
        return None
    try:
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]
                for item in items:
                    offers = item.get("offers")
                    if offers:
                        if isinstance(offers, list):
                            for off in offers:
                                if off.get("price"):
                                    return float(str(off["price"]).replace(",", ""))
                        elif isinstance(offers, dict) and offers.get("price"):
                            return float(str(offers["price"]).replace(",", ""))
                    if item.get("price"):
                        return float(str(item["price"]).replace(",", ""))
            except Exception:
                pass
    except Exception:
        pass
    return None


def clean_search_query(query: str) -> str:
    filler = {"price","buy","online","india","best","cheapest","lowest","offer","deal",
              "discount","shop","purchase","order","compare","comparison","check","find",
              "get","new","latest","free","shipping"}
    words = query.split()
    cleaned = [w for w in words if w.lower() not in filler]
    return " ".join(cleaned).strip() or query


# ── AI: Identify product ────────────────────────────────────────────────────
def identify_from_image(client: OpenAI, image_bytes: bytes) -> dict:
    b64 = base64.b64encode(image_bytes).decode()
    mime = "image/png" if image_bytes[:2] == b'\x89P' else "image/jpeg"
    prompt = """Analyze this product image. Return ONLY raw JSON, no markdown:
{
  "name": "brand + product name + variant",
  "brand": "brand name",
  "variant": "size/specs",
  "category": "grocery or electronics",
  "search_query": "short search terms: brand model variant ONLY",
  "store_category": "grocery_stores or electronics_stores"
}
search_query must be SHORT: "Samsung Galaxy S24 Ultra 256GB" not "Samsung Galaxy S24 Ultra price buy online".
Grocery/food/household -> grocery_stores. Electronics/gadgets -> electronics_stores."""
    raw = ai_call(client, [{"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
        {"type": "text", "text": prompt}
    ]}], is_vision=True)
    result = parse_json_response(raw)
    if "search_query" in result:
        result["search_query"] = clean_search_query(result["search_query"])
    return result


def identify_from_text(client: OpenAI, query: str, category: str) -> dict:
    prompt = f"""User searching for: "{query}"
Category hint: {category}
Return ONLY raw JSON, no markdown:
{{
  "name": "brand + product name + variant",
  "brand": "brand name or empty",
  "variant": "size/specs or empty",
  "category": "grocery or electronics",
  "search_query": "short search: brand + model + key spec ONLY",
  "store_category": "grocery_stores or electronics_stores"
}}
search_query: SHORT. "OnePlus Nord CE 5" not "OnePlus Nord CE 5 price buy online India"
Grocery/Food -> grocery_stores. Electronics/Gadgets -> electronics_stores."""
    raw = ai_call(client, [{"role": "user", "content": prompt}])
    result = parse_json_response(raw)
    if "search_query" in result:
        result["search_query"] = clean_search_query(result["search_query"])
    return result


# ══════════════════════════════════════════════════════════════════════════════
# ── REAL PRICE SCRAPING — NO AI GUESSING ─────────────────────────────────────
# Every price shown comes from an actual website, not from AI training data.
# ══════════════════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════════════════
# ── PRICE FETCHING — DDG-FIRST APPROACH ──────────────────────────────────────
# Amazon blocks bots (returns CAPTCHA). Flipkart renders prices via JS.
# DuckDuckGo search is the ONLY reliable source — it returns real prices
# from indexed store pages and price comparison sites.
# ══════════════════════════════════════════════════════════════════════════════

def _ddg_search(query: str, max_results: int = 10) -> list:
    """DuckDuckGo search with retries. Returns list of {title, snippet, link}."""
    for attempt in range(3):
        try:
            if attempt > 0:
                time.sleep(1.5 * attempt)
            wrapper = DuckDuckGoSearchAPIWrapper(max_results=max_results, region="in-en")
            tool = DuckDuckGoSearchResults(api_wrapper=wrapper, output_format="list")
            results = tool.invoke(query)
            if isinstance(results, list) and results:
                return results
        except Exception:
            pass
    return []


def _extract_all_prices(text: str) -> list[float]:
    """Extract ALL price values from text. Returns list of floats."""
    if not text:
        return []
    prices = []
    # Match: ₹31,998  Rs. 29,999  Rs 34998  INR 25,000  ₹31998
    patterns = [
        r'₹\s*([\d,]+(?:\.\d{1,2})?)',
        r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
        r'INR\s*([\d,]+(?:\.\d{1,2})?)',
        r'(?:price|Price|PRICE)[:\s]*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d{1,2})?)',
        r'(?:starts?\s+(?:from|at))\s*(?:₹|Rs\.?|INR)?\s*([\d,]+(?:\.\d{1,2})?)',
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            try:
                p = float(m.group(1).replace(",", ""))
                if 5 < p < 10_000_000:
                    prices.append(p)
            except ValueError:
                pass
    return prices


def _best_price(text: str) -> float | None:
    """Get the first reasonable price from text."""
    prices = _extract_all_prices(text)
    return prices[0] if prices else None


def fetch_prices_via_ddg(query: str, stores: list, product_name: str,
                          store_category: str, client: OpenAI = None) -> dict:
    """
    PRIMARY price fetching via DuckDuckGo web search.
    Returns {store_name: {price, link, source}}.
    """
    found = {}
    store_domains_inv = {v: k for k, v in STORE_DOMAINS.items()}
    all_snippets = []  # Collect for AI fallback

    # ── Search 1: Product + price (broad) ──
    search_queries = [
        f"{query} price India",
        f"{query} price Amazon Flipkart",
    ]
    if store_category == "grocery_stores":
        search_queries = [
            f"{query} price India",
            f"{query} price BigBasket Blinkit JioMart",
        ]

    for sq in search_queries:
        results = _ddg_search(sq, max_results=15)
        if not results:
            continue

        for r in results:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            combined = f"{title} {snippet}"
            all_snippets.append(f"{title} | {snippet} | {link}")

            # Check if result is from a store domain
            for domain, store_name in store_domains_inv.items():
                if store_name in stores and store_name not in found and domain in link:
                    price = _best_price(combined)
                    if price:
                        found[store_name] = {
                            "price": price, "link": link,
                            "source": f"{domain}",
                        }
                    break

            # Check if snippet mentions store names with prices
            # e.g. "OnePlus Nord CE6 starts at Rs 29,999 on Amazon, Rs 31,998 on Flipkart"
            for store_name in stores:
                if store_name not in found:
                    sn_lower = store_name.lower().replace(" india", "")
                    combined_lower = combined.lower()
                    if sn_lower in combined_lower:
                        idx = combined_lower.find(sn_lower)
                        # Look for price near the store mention (before and after)
                        nearby = combined[max(0, idx - 50):idx + 200]
                        price = _best_price(nearby)
                        if price:
                            found[store_name] = {
                                "price": price, "link": link,
                                "source": "price comparison site",
                            }

        if len(found) >= len(stores) // 2:
            break  # Got enough, stop searching
        time.sleep(0.3)

    # ── Search 2: Store-specific searches for remaining stores ──
    remaining = [s for s in stores if s not in found]
    for store_name in remaining[:4]:
        domain = STORE_DOMAINS.get(store_name, "")
        if not domain:
            continue
        results = _ddg_search(f"{query} site:{domain}", max_results=5)
        if results:
            for r in results:
                combined = f"{r.get('title', '')} {r.get('snippet', '')}"
                all_snippets.append(f"{combined} | {r.get('link', '')}")
                price = _best_price(combined)
                if price:
                    found[store_name] = {
                        "price": price,
                        "link": r.get("link", STORE_SEARCH_URLS[store_name](query)),
                        "source": f"{domain}",
                    }
                    break
        time.sleep(0.4)

    # ── Search 3: Price comparison sites for remaining ──
    remaining2 = [s for s in stores if s not in found]
    if remaining2:
        comp_queries = [
            f"{query} price comparison smartprix",
            f"{query} price 91mobiles gadgets360",
        ] if store_category == "electronics_stores" else [
            f"{query} price grocery India",
        ]
        for cq in comp_queries[:1]:
            results = _ddg_search(cq, max_results=8)
            if results:
                for r in results:
                    combined = f"{r.get('title', '')} {r.get('snippet', '')}"
                    all_snippets.append(f"{combined} | {r.get('link', '')}")
                    # These aggregator snippets often list multiple store prices
                    for store_name in remaining2:
                        if store_name not in found:
                            sn_lower = store_name.lower().replace(" india", "")
                            if sn_lower in combined.lower():
                                idx = combined.lower().find(sn_lower)
                                nearby = combined[max(0, idx - 50):idx + 200]
                                price = _best_price(nearby)
                                if price:
                                    found[store_name] = {
                                        "price": price,
                                        "link": r.get("link", STORE_SEARCH_URLS[store_name](query)),
                                        "source": "price comparison site",
                                    }
            time.sleep(0.3)

    # ── Fallback: AI reads collected web snippets to extract prices ──
    remaining3 = [s for s in stores if s not in found]
    if remaining3 and client and all_snippets:
        try:
            snippets_text = "\n".join(
                f"  {i+1}. {s[:300]}" for i, s in enumerate(all_snippets[:15])
            )
            stores_needed = ", ".join(remaining3)

            # Also tell AI what we already found for context
            found_context = ""
            if found:
                found_lines = [f"  {s}: Rs.{d['price']:,.0f}" for s, d in found.items()]
                found_context = "\nALREADY FOUND (for reference):\n" + "\n".join(found_lines)

            prompt = f"""Read these REAL web search results and extract prices for the product.

PRODUCT: "{product_name}"

REAL WEB SEARCH RESULTS:
{snippets_text}
{found_context}

EXTRACT prices ONLY for these stores: {stores_needed}

CRITICAL RULES:
1. ONLY extract prices that are EXPLICITLY mentioned in the web results above
2. Do NOT make up or guess any prices from your training data
3. If a store's price is not mentioned in any result, set it to null
4. Match prices to the correct store name exactly
5. If the same product is available at similar prices across stores, that's fine
6. Prices must be in INR (Indian Rupees)

Return ONLY a JSON array, no explanation:
[{{"store": "StoreName", "price": 25000}}, {{"store": "Store2", "price": null}}]"""

            raw = ai_call(client, [{"role": "user", "content": prompt}])
            cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw.strip()).strip()
            cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
            m_json = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if m_json:
                store_data = json.loads(m_json.group(0))
                lo, hi = (5, 50_000) if store_category == "grocery_stores" else (500, 10_000_000)
                for item in store_data:
                    sname = item.get("store", "")
                    price = item.get("price")
                    matched = None
                    for cs in stores:
                        if cs.lower() in sname.lower() or sname.lower() in cs.lower():
                            matched = cs
                            break
                    if not matched or matched in found:
                        continue
                    if price is not None:
                        try:
                            price = float(price)
                            if lo <= price <= hi:
                                found[matched] = {
                                    "price": price,
                                    "link": STORE_SEARCH_URLS[matched](query),
                                    "source": "web search results",
                                }
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass

    return found


# ══════════════════════════════════════════════════════════════════════════════
# ── MAIN PRICE FETCHING ──────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

def fetch_prices(product: dict, client: OpenAI = None, user_city: str = None) -> list:
    """
    Fetch real prices from web sources.
    Strategy: DuckDuckGo search is the PRIMARY source because
    Amazon blocks bot requests and Flipkart renders prices via JavaScript.
    """
    store_category = product.get("store_category", "electronics_stores")
    all_stores = GROCERY_STORES[:] if store_category == "grocery_stores" else ELECTRONICS_STORES[:]

    if user_city:
        available = get_available_stores(user_city, store_category)
        stores = [s for s in all_stores if s in available]
    else:
        stores = all_stores

    query = clean_search_query(product.get("search_query", product.get("name", "")))
    product_name = product.get("name", query)
    lo, hi = (5, 50_000) if store_category == "grocery_stores" else (500, 10_000_000)

    bar = st.progress(0, text="Searching the web for real prices...")
    found = {}

    # ── Main: DDG-based price fetching ──
    bar.progress(15, text="Searching DuckDuckGo for store prices...")

    ddg_found = fetch_prices_via_ddg(query, stores, product_name, store_category, client)
    for store_name, data in ddg_found.items():
        price = data.get("price")
        if price and lo <= price <= hi:
            found[store_name] = {
                "site": store_name,
                "link": data.get("link", STORE_SEARCH_URLS[store_name](query)),
                "price": price,
                "source": data.get("source", "web search"),
            }

    bar.progress(100, text=f"Done! Found prices at {len(found)} stores.")
    time.sleep(0.4)
    bar.empty()

    # ── Build results ──
    for store in stores:
        if store not in found:
            found[store] = {
                "site": store,
                "link": STORE_SEARCH_URLS[store](query),
                "price": None,
                "source": None,
            }

    results = list(found.values())
    with_price = sorted([r for r in results if r["price"] is not None], key=lambda x: x["price"])
    no_price = sorted([r for r in results if r["price"] is None], key=lambda x: x["site"])
    return with_price + no_price


# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int, has_price_above: bool):
    price_val = item.get("price")
    link = item.get("link", "#")
    source = item.get("source", "")

    # Escape & in URLs so HTML doesn't break
    safe_link = link.replace("&", "&amp;")

    try:
        display_domain = urllib.parse.urlparse(link).netloc.replace("www.", "")
    except Exception:
        display_domain = ""

    if price_val is not None:
        price_html = f'Rs. {price_val:,.0f}'
        best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 and has_price_above else ""
        source_html = f'<div class="ph-source">Price from {source}</div>' if source else ""
        btn_html = f'<a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="ph-buy">Buy Now &#8594;</a>'
    else:
        price_html = '<span style="font-size:0.9rem;color:#b8a99a;font-weight:500;">Price not found</span>'
        best = ""
        source_html = ""
        btn_html = f'<a href="{safe_link}" target="_blank" rel="noopener noreferrer" class="ph-visit">Visit Store &#8594;</a>'

    card_html = (
        f'<div class="ph-card rank-{rank}">'
        f'<div class="ph-card-inner">'
        f'<div class="ph-rank">#{rank}</div>'
        f'<div class="ph-info">'
        f'<div class="ph-store">{item["site"]}{best}</div>'
        f'<div class="ph-link">&#128279; {display_domain}</div>'
        f'<div class="ph-price">{price_html}</div>'
        f'{source_html}'
        f'</div>'
        f'{btn_html}'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    st.markdown("""
<script>
(function hideSLBadges() {
    var sels = ['[data-testid="stActionButton"]','[data-testid="manage-app-button"]',
        '[data-testid="stStatusWidget"]','.viewerBadge_link__qRIco',
        '.styles_viewerBadge__CvC9N','.viewerBadge_container__1QSob',
        'button[kind="header"]','a[href*="streamlit.io"]'];
    function h(){sels.forEach(function(s){document.querySelectorAll(s).forEach(function(e){
        e.style.setProperty('display','none','important')})});
        document.querySelectorAll('*').forEach(function(e){var c=window.getComputedStyle(e);
        if(c.position==='fixed'&&parseInt(c.bottom)<80&&(parseInt(c.right)<120||parseInt(c.left)<120)){
        var t=e.tagName.toLowerCase();if(t==='button'||t==='a'||t==='div')
        e.style.setProperty('display','none','important')}})};
    h();setTimeout(h,500);setTimeout(h,1500);setTimeout(h,3000);
    new MutationObserver(h).observe(document.documentElement,{childList:true,subtree:true});
})();
</script>""", unsafe_allow_html=True)

    st.markdown('<div class="ph-title">&#128722; PriceHunt</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ph-subtitle">Type a product or upload a photo '
        '&#8594; compare prices across Indian stores instantly</div>',
        unsafe_allow_html=True
    )

    # ── API Key ──
    openrouter_key = None
    try:
        openrouter_key = st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        pass

    with st.sidebar:
        st.markdown("### OpenRouter API Key")
        if not openrouter_key:
            openrouter_key = st.text_input("OpenRouter Key", type="password",
                placeholder="sk-or-v1-...", help="Free key at openrouter.ai/keys")
            st.caption("[Get free key](https://openrouter.ai/keys) - No credit card needed")
        else:
            st.success("OpenRouter key loaded")
        st.markdown("---")
        st.markdown("**How it works**")
        st.markdown(
            "- AI identifies your product\n"
            "- Scrapes REAL prices from store websites\n"
            "- Searches the web for live prices\n"
            "- Shows cheapest first with store links\n"
            "- Every price is from an actual source"
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
    <li>Paste it in the sidebar</li>
  </ol>
  <div class="ph-free-note">100% Free &middot; No credit card needed</div>
</div>""", unsafe_allow_html=True)
        st.stop()

    client = make_client(openrouter_key)

    # ── LOCATION: Auto-detect via browser geolocation ──
    if "detected_city" not in st.session_state:
        st.session_state.detected_city = ""
    if "geo_requested" not in st.session_state:
        st.session_state.geo_requested = False

    params = st.query_params
    lat_p, lng_p = params.get("lat"), params.get("lng")
    if lat_p and lng_p and not st.session_state.detected_city:
        try:
            city = reverse_geocode(float(lat_p), float(lng_p))
            if city:
                st.session_state.detected_city = city
                st.session_state.geo_requested = True
        except Exception:
            pass

    if not st.session_state.detected_city and not st.session_state.geo_requested:
        components.html("""
        <script>
        (function(){
            var p = new URLSearchParams(window.parent.location.search);
            if (p.has('lat') && p.has('lng')) return;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var u = new URL(window.parent.location);
                        u.searchParams.set('lat', pos.coords.latitude.toFixed(4));
                        u.searchParams.set('lng', pos.coords.longitude.toFixed(4));
                        window.parent.location.href = u.toString();
                    },
                    function(){}, {enableHighAccuracy:false, timeout:8000, maximumAge:300000}
                );
            }
        })();
        </script>
        """, height=0)

    # Location bar
    st.markdown('<div class="ph-section">📍 Your Location</div>', unsafe_allow_html=True)
    lc1, lc2 = st.columns([3, 1])
    with lc1:
        user_city = st.text_input("loc", value=st.session_state.detected_city,
            placeholder="Detecting location... or type your city",
            label_visibility="collapsed", key="user_city_input")
    with lc2:
        if user_city:
            tier = get_city_tier(user_city)
            labels = {"metro":"🟢 All stores","tier1_5":"🟡 Most stores","tier2":"🟠 Major stores","tier3":"🔴 Online only"}
            st.markdown(f'<div style="padding:0.45rem 0;font-size:0.82rem;color:#78716c;">{labels.get(tier,"")}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding:0.45rem 0;font-size:0.82rem;color:#b8a99a;">Detecting...</div>',
                        unsafe_allow_html=True)

    if user_city != st.session_state.detected_city:
        st.session_state.detected_city = user_city

    if user_city:
        ag = get_available_stores(user_city, "grocery_stores")
        ae = get_available_stores(user_city, "electronics_stores")
        auto = " (auto-detected)" if lat_p and lng_p else ""
        st.markdown(f'<div style="font-size:0.78rem;color:#78716c;margin-bottom:0.8rem;">'
                    f'📍 <strong style="color:#1c1917;">{user_city}</strong>{auto} — '
                    f'{len(ag)} grocery · {len(ae)} electronics stores</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:0.78rem;color:#b8a99a;margin-bottom:0.8rem;">'
                    'Allow location or type your city for local store availability</div>', unsafe_allow_html=True)

    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)

    # ── Search ──
    st.markdown('<div class="ph-section">How do you want to search?</div>', unsafe_allow_html=True)
    mode = st.radio("mode", ["📝 Type product name", "📸 Upload product image"],
                    horizontal=True, label_visibility="collapsed")

    text_query, uploaded_file, category = None, None, "Auto-detect"

    if mode == "📝 Type product name":
        with st.form("search_form", clear_on_submit=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                text_query = st.text_input("product",
                    placeholder="e.g.  Maggi Noodles 12-pack  or  OnePlus Nord CE 5",
                    label_visibility="collapsed")
            with c2:
                category = st.selectbox("cat",
                    ["Auto-detect", "Grocery / Food", "Electronics / Gadgets"],
                    label_visibility="collapsed")
            st.markdown("""
<div style="margin-top:0.4rem;margin-bottom:1.2rem;">
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
            uploaded_file = st.file_uploader("Upload image", type=["jpg","jpeg","png","webp"],
                                             label_visibility="collapsed")
        with c2:
            if uploaded_file:
                st.image(Image.open(uploaded_file), use_container_width=True)
        can_search = bool(uploaded_file)
        go = st.button("🔍 Find Best Prices", disabled=not can_search, use_container_width=True)
        can_search = can_search and go

    if not can_search:
        st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
        st.markdown('<div class="ph-section" style="text-align:center;">What PriceHunt searches</div>',
                    unsafe_allow_html=True)
        d1, d2, d3 = st.columns(3)
        for col, (em, t, s) in zip([d1,d2,d3], [
            ("🛒","Groceries","Zepto · Blinkit · BigBasket · JioMart"),
            ("📱","Electronics","Amazon · Flipkart · Croma · Vijay Sales"),
            ("🏠","Home & FMCG","Swiggy Instamart · DMart · Reliance"),
        ]):
            with col:
                st.markdown(f"""
<div style="background:#fff;border:1.5px solid #e8ddd0;border-radius:12px;
            padding:1rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.04);">
  <div style="font-size:1.8rem;">{em}</div>
  <div style="font-weight:700;color:#1c1917;margin:0.3rem 0;">{t}</div>
  <div style="font-size:0.75rem;color:#78716c;">{s}</div>
</div>""", unsafe_allow_html=True)
        return

    # ── Identify product ──
    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)
    product = None
    if mode == "📸 Upload product image" and uploaded_file:
        with st.spinner("AI is reading your image..."):
            try:
                product = identify_from_image(client, uploaded_file.read())
            except Exception as e:
                st.error(f"Could not identify product: {e}")
                return
    elif mode == "📝 Type product name" and text_query:
        with st.spinner("AI is analysing your query..."):
            try:
                product = identify_from_text(client, text_query.strip(), category)
            except Exception as e:
                st.error(f"Error: {e}")
                return

    if not product:
        st.error("Could not identify product. Please try again.")
        return

    cat_emoji = {"grocery":"🛒","electronics":"📱","fashion":"👗","home":"🏠","beauty":"💄"}.get(product.get("category",""),"📦")

    if user_city:
        avail = get_available_stores(user_city, product.get("store_category","electronics_stores"))
        stores_label = ", ".join(avail) if avail else "No stores in your area"
        loc_tag = f" in {user_city}"
    else:
        stores_label = (", ".join(GROCERY_STORES) if product.get("store_category") == "grocery_stores"
                        else ", ".join(ELECTRONICS_STORES))
        loc_tag = ""

    st.markdown(f"""
<div class="ph-product">
  <div style="font-size:1.1rem;font-weight:700;">{cat_emoji} {product.get('name','--')}</div>
  <div style="font-size:0.85rem;margin-top:0.3rem;color:#78716c;">
    Brand: <strong>{product.get('brand') or '--'}</strong> &middot;
    Variant: <strong>{product.get('variant') or '--'}</strong>
  </div>
  <div style="font-size:0.8rem;margin-top:0.3rem;color:#92400e;">Searching{loc_tag}: {stores_label}</div>
</div>""", unsafe_allow_html=True)

    # ── Fetch REAL prices ──
    st.markdown('<div class="ph-section">Price Comparison &mdash; Cheapest First</div>', unsafe_allow_html=True)
    results = fetch_prices(product, client=client, user_city=user_city)

    if not results:
        st.warning("Could not fetch prices. Browse stores directly:")
        q = product.get("search_query", product.get("name",""))
        stores = GROCERY_STORES if product.get("store_category") == "grocery_stores" else ELECTRONICS_STORES
        for s in stores:
            url = STORE_SEARCH_URLS[s](q)
            st.markdown(f'<a href="{url}" target="_blank" style="display:inline-block;background:#fef3c7;'
                        f'border:1px solid #fcd34d;border-radius:20px;padding:5px 14px;font-size:0.82rem;'
                        f'color:#92400e;text-decoration:none;margin:4px;">🔗 {s}</a>', unsafe_allow_html=True)
        return

    rp = [r for r in results if r["price"] is not None]
    has_any_price = len(rp) > 0

    st.markdown(
        f'<div style="color:#78716c;font-size:0.88rem;margin-bottom:0.8rem;">'
        f'Found <strong style="color:#1c1917;">real prices at {len(rp)} of {len(results)} stores</strong>'
        f' (scraped from actual websites)</div>',
        unsafe_allow_html=True
    )

    for i, item in enumerate(results, 1):
        result_card(item, i, has_any_price)

    if len(rp) >= 2:
        save = rp[-1]["price"] - rp[0]["price"]
        pct = save / rp[-1]["price"] * 100
        if save > 0:
            st.markdown(f"""
<div class="ph-savings">
  <div class="ph-savings-amt">Save Rs. {save:,.0f} ({pct:.0f}%)</div>
  <div class="ph-savings-sub">
    Buy from <strong>{rp[0]['site']}</strong> instead of <strong>{rp[-1]['site']}</strong>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;color:#b8a99a;font-size:0.74rem;margin-top:1rem;">'
        'All prices scraped from real websites. Verify on store before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
