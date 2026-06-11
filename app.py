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
.ph-link {
    font-size: 0.78rem; color: #6b7280; margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 300px;
}
.ph-price { font-size: 1.5rem; font-weight: 800; color: #059669; margin-top: 4px; }
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

.ph-loc-bar {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1.5px solid #fcd34d; border-radius: 12px;
    padding: 0.7rem 1.2rem; margin-bottom: 1rem;
    display: flex; align-items: center; gap: 0.6rem; flex-wrap: wrap;
}
.ph-loc-icon { font-size: 1.3rem; }
.ph-loc-city { font-weight: 700; color: #1c1917; font-size: 0.95rem; }
.ph-loc-meta { font-size: 0.78rem; color: #78716c; }
.ph-loc-stores { font-size: 0.75rem; color: #92400e; }
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

# Store domain names for DDG searches
STORE_DOMAINS = {
    "Blinkit": "blinkit.com",
    "Zepto": "zeptonow.com",
    "BigBasket": "bigbasket.com",
    "Swiggy Instamart": "swiggy.com",
    "JioMart": "jiomart.com",
    "DMart Online": "dmart.in",
    "Amazon India": "amazon.in",
    "Flipkart": "flipkart.com",
    "Croma": "croma.com",
    "Vijay Sales": "vijaysales.com",
    "Reliance Digital": "reliancedigital.in",
    "Tata Cliq": "tatacliq.com",
}

# Direct search URLs — used for every "Buy Now" button
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

# ── Comprehensive location-based store availability ───────────────────────────
CITY_TIERS = {
    "metro": [
        "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "hyderabad",
        "chennai", "pune", "kolkata", "ahmedabad", "gurgaon", "gurugram",
        "noida", "greater noida", "ghaziabad", "faridabad", "navi mumbai",
        "thane",
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
        "grocery": ["Blinkit", "Zepto", "BigBasket", "Swiggy Instamart", "JioMart", "DMart Online"],
        "electronics": ["Amazon India", "Flipkart", "Croma", "Vijay Sales", "Reliance Digital", "Tata Cliq"],
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


# ── Geolocation: reverse geocode lat/lng to city name ────────────────────────
def reverse_geocode(lat: float, lng: float) -> str:
    """Use OpenStreetMap Nominatim to convert coordinates to city name."""
    try:
        url = (
            f"https://nominatim.openstreetmap.org/reverse"
            f"?lat={lat}&lon={lng}&format=json&addressdetails=1&zoom=12"
        )
        headers = {"User-Agent": "PriceHunt/1.0 (price-comparison-app)"}
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            addr = data.get("address", {})
            city = (
                addr.get("city")
                or addr.get("town")
                or addr.get("village")
                or addr.get("county")
                or addr.get("state_district")
                or addr.get("state")
                or ""
            )
            return city.strip()
    except Exception:
        pass
    return ""


# ── Get stores available in user's location ─────────────────────────────────
def get_city_tier(city: str) -> str:
    """Determine the tier for a given Indian city."""
    city_lower = city.lower().strip()
    city_lower = city_lower.replace(" city", "").replace(" urban", "").strip()

    for tier, cities in CITY_TIERS.items():
        for known_city in cities:
            if known_city in city_lower or city_lower in known_city:
                return tier
    return "tier2" if len(city_lower) > 2 else "tier3"


def get_available_stores(city: str, category: str) -> list:
    """Return list of stores available in the given city for the category."""
    tier = get_city_tier(city)
    store_type = "grocery" if category == "grocery_stores" else "electronics"
    return STORE_AVAILABILITY.get(tier, STORE_AVAILABILITY["tier3"]).get(store_type, [])


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
        r'price[:\s]*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'at\s*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'for\s*₹?\s*([\d,]+(?:\.\d{1,2})?)',
        r'\?\s*([\d,]+(?:\.\d{1,2})?)',
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


def clean_search_query(query: str) -> str:
    """Strip filler words from search queries to make them more accurate."""
    filler_words = [
        "price", "buy", "online", "india", "best", "cheapest", "lowest",
        "offer", "deal", "discount", "shop", "purchase", "order",
        "compare", "comparison", "check", "find", "get", "new", "latest",
    ]
    words = query.split()
    cleaned = [w for w in words if w.lower() not in filler_words]
    result = " ".join(cleaned).strip()
    return result if result else query


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
  "search_query": "concise search terms: brand model variant ONLY",
  "store_category": "grocery_stores or electronics_stores"
}
IMPORTANT: search_query must be SHORT. Example: "Samsung Galaxy S24 Ultra 256GB" NOT "Samsung Galaxy S24 Ultra 256GB price buy online".
Groceries/food/beverages/household → grocery_stores. Electronics/gadgets/appliances → electronics_stores."""

    raw = ai_call(client, [
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": prompt}
        ]}
    ], is_vision=True)
    result = parse_json_response(raw)
    if "search_query" in result:
        result["search_query"] = clean_search_query(result["search_query"])
    return result


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
  "search_query": "concise search terms: brand + model + key spec ONLY",
  "store_category": "grocery_stores or electronics_stores"
}}

search_query rules:
- SHORT: "OnePlus Nord CE 5" NOT "OnePlus Nord CE 5 price buy online India"
- Brand + model + key spec only
- For grocery: "Maggi 2-Minute Noodles 840g"
- For electronics: "iPhone 16 128GB"

Grocery/Food → grocery_stores. Electronics/Gadgets → electronics_stores."""

    raw = ai_call(client, [{"role": "user", "content": prompt}])
    result = parse_json_response(raw)
    if "search_query" in result:
        result["search_query"] = clean_search_query(result["search_query"])
    return result


# ── Per-store scrapers ───────────────────────────────────────────────────────

def _get(url: str, timeout: int = 12) -> requests.Response | None:
    """GET with browser headers. Returns None on any error."""
    try:
        r = requests.get(url, headers=SCRAPE_HEADERS, timeout=timeout, allow_redirects=True)
        return r if r.status_code == 200 else None
    except Exception:
        return None


def _scrape_amazon_search(query: str) -> dict | None:
    """Scrape Amazon India search results for the first matching product and price."""
    url = f"https://www.amazon.in/s?k={urllib.parse.quote_plus(query)}"
    r = _get(url, timeout=15)
    if not r:
        return None
    soup = BeautifulSoup(r.text, "html.parser")

    cards = soup.select("div[data-component-type='s-search-result']")
    if not cards:
        cards = soup.select("div.s-result-item[data-asin]")

    accessory_words = [
        "cover", "case", "glass", "protector", "guard", "cable", "charger",
        "adapter", "strap", "pouch", "film", "skin", "sleeve", "tempered",
        "holder", "stand", "mount", "ring", "grip", "sticker", "decal"
    ]
    query_lower = query.lower()
    query_keywords = [w for w in query_lower.split() if len(w) > 2]

    for card in cards[:10]:
        if card.select_one("span.s-label-popover-default"):
            continue
        asin = card.get("data-asin", "")
        if not asin:
            continue

        title_el = card.select_one("h2 a span") or card.select_one("h2 span") or card.select_one(".a-text-normal")
        title = title_el.get_text(strip=True) if title_el else ""
        title_lower = title.lower()

        if query_keywords:
            matches_query = sum(1 for kw in query_keywords if kw in title_lower)
            if matches_query < len(query_keywords) // 2:
                continue

        is_accessory = False
        for kw in accessory_words:
            if kw in title_lower and kw not in query_lower:
                is_accessory = True
                break
        if is_accessory:
            continue

        price_el = (card.select_one("span.a-price span.a-offscreen") or
                    card.select_one("span.a-price-whole") or
                    card.select_one("span.a-color-price"))
        if price_el:
            price = extract_price(price_el.get_text())
            if price:
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
    """Scrape Flipkart search results for the first matching product and price."""
    url = f"https://www.flipkart.com/search?q={urllib.parse.quote_plus(query)}"
    r = _get(url, timeout=15)
    if not r:
        return None

    price_from_ld = extract_price_from_json_ld(r.text)
    soup = BeautifulSoup(r.text, "html.parser")

    accessory_words = [
        "cover", "case", "glass", "protector", "guard", "cable", "charger",
        "adapter", "strap", "pouch", "film", "skin", "sleeve", "tempered",
        "holder", "stand", "mount", "ring", "grip", "sticker", "decal"
    ]
    query_lower = query.lower()
    query_keywords = [w for w in query_lower.split() if len(w) > 2]

    product_links = soup.select("a[href*='/p/']")
    if not product_links:
        product_links = soup.select("a[href*='pid=']")

    for link_el in product_links[:15]:
        href = link_el.get("href", "")
        if not href:
            continue
        if not href.startswith("http"):
            href = "https://www.flipkart.com" + href

        card = link_el
        for _ in range(5):
            parent = card.parent
            if parent:
                card = parent
            else:
                break

        card_text = card.get_text(" ", strip=True).lower()

        if query_keywords:
            matches_query = sum(1 for kw in query_keywords if kw in card_text)
            if matches_query < len(query_keywords) // 2:
                continue

        is_accessory = False
        for kw in accessory_words:
            if kw in card_text and kw not in query_lower:
                is_accessory = True
                break
        if is_accessory:
            continue

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

        price = extract_price(card.get_text())
        if price:
            return {"price": price, "link": href, "title": ""}

    if price_from_ld:
        return {"price": price_from_ld, "link": url, "title": ""}
    return None


# Price sanity bounds per category
PRICE_BOUNDS = {
    "electronics_stores": (500, 10_000_000),
    "grocery_stores":     (5, 50_000),
}

# ── DuckDuckGo Search ──────────────────────────────────────────────────
def _ddg_search(query: str, max_results: int = 10) -> list:
    """DuckDuckGo search with retries. Returns list of {title, snippet, link} dicts."""
    for attempt in range(3):
        try:
            if attempt > 0:
                time.sleep(1.5 * attempt)
            wrapper = DuckDuckGoSearchAPIWrapper(
                max_results=max_results,
                region="in-en",
            )
            tool = DuckDuckGoSearchResults(
                api_wrapper=wrapper,
                output_format="list",
            )
            results = tool.invoke(query)
            if isinstance(results, list) and results:
                return results
        except Exception:
            pass
    return []


def fetch_prices(product: dict, client: OpenAI = None, user_city: str = None) -> list:
    """
    Multi-strategy price fetching:
    1. Broad DDG web searches to collect real price snippets
    2. Try direct store scraping (Amazon, Flipkart)
    3. AI analyzes ALL collected data + uses training knowledge
    4. Filter by location availability
    """
    store_category = product.get("store_category", "electronics_stores")

    all_category_stores = (GROCERY_STORES if store_category == "grocery_stores"
                           else ELECTRONICS_STORES)

    # Filter by location
    if user_city:
        available_stores = get_available_stores(user_city, store_category)
        category_stores = [s for s in all_category_stores if s in available_stores]
    else:
        category_stores = all_category_stores

    query = product.get("search_query", product.get("name", ""))
    query = clean_search_query(query)
    product_name = product.get("name", query)

    bar = st.progress(0, text="Searching for best prices...")
    found_stores = {}

    # ── Step 1: Broad DDG searches to collect price data ──
    bar.progress(10, text="Searching the web for prices...")

    all_snippets = []
    store_snippets = {}  # per-store snippets

    # Search 1: General price search (most likely to return actual prices)
    search_queries = [
        f"{query} price India",
        f"{query} buy Amazon Flipkart Croma",
    ]
    if store_category == "grocery_stores":
        search_queries = [
            f"{query} price India",
            f"{query} BigBasket Blinkit JioMart",
        ]

    for sq in search_queries:
        try:
            results = _ddg_search(sq, max_results=10)
            for r in results:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                link = r.get("link", "")
                combined = f"{title} | {snippet}"
                all_snippets.append(combined)

                # Attribute snippet to a store if its domain appears in the link
                for store, domain in STORE_DOMAINS.items():
                    if domain in link:
                        if store not in store_snippets:
                            store_snippets[store] = []
                        store_snippets[store].append({
                            "text": combined,
                            "link": link,
                            "price": extract_price(combined),
                        })
                        break
            if all_snippets:
                break  # Got results, no need for more searches
        except Exception:
            pass

    # Search 2: Store-specific searches for stores we didn't find yet
    bar.progress(30, text="Checking specific stores...")
    missing_stores = [s for s in category_stores if s not in store_snippets]

    for store in missing_stores[:3]:  # Limit to avoid rate-limiting
        domain = STORE_DOMAINS.get(store, "")
        if not domain:
            continue
        try:
            results = _ddg_search(f"{query} site:{domain}", max_results=5)
            for r in results:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                link = r.get("link", "")
                combined = f"{title} | {snippet}"
                all_snippets.append(combined)
                if store not in store_snippets:
                    store_snippets[store] = []
                store_snippets[store].append({
                    "text": combined,
                    "link": link,
                    "price": extract_price(combined),
                })
            time.sleep(0.3)  # Small delay to avoid rate-limiting
        except Exception:
            pass

    # ── Step 2: Direct store scraping ──
    bar.progress(50, text="Scraping store pages...")

    if store_category == "electronics_stores":
        # Try Amazon direct scraping
        if "Amazon India" in category_stores and "Amazon India" not in found_stores:
            try:
                result = _scrape_amazon_search(query)
                if result and result.get("price"):
                    found_stores["Amazon India"] = {
                        "site": "Amazon India",
                        "link": result.get("link", STORE_SEARCH_URLS["Amazon India"](query)),
                        "price": result["price"],
                        "source": "direct",
                    }
            except Exception:
                pass

        # Try Flipkart direct scraping
        if "Flipkart" in category_stores and "Flipkart" not in found_stores:
            try:
                result = _scrape_flipkart_search(query)
                if result and result.get("price"):
                    found_stores["Flipkart"] = {
                        "site": "Flipkart",
                        "link": result.get("link", STORE_SEARCH_URLS["Flipkart"](query)),
                        "price": result["price"],
                        "source": "direct",
                    }
            except Exception:
                pass

    # ── Step 2b: Use DDG snippet prices ──
    for store in category_stores:
        if store in found_stores:
            continue
        if store in store_snippets:
            for s in store_snippets[store]:
                if s.get("price"):
                    lo, hi = PRICE_BOUNDS.get(store_category, (5, 10_000_000))
                    if lo <= s["price"] <= hi:
                        found_stores[store] = {
                            "site": store,
                            "link": s.get("link", STORE_SEARCH_URLS[store](query)),
                            "price": s["price"],
                            "source": "ddg",
                        }
                        break

    # ── Step 3: AI to fill ALL remaining gaps using snippets + knowledge ──
    bar.progress(70, text="AI analyzing prices...")

    stores_needing_price = [s for s in category_stores if s not in found_stores]

    if client and stores_needing_price:
        try:
            # Build context from all collected data
            snippet_context = "\n".join(f"  - {s[:250]}" for s in all_snippets[:15]) if all_snippets else "  No web results found."

            # Show what we already found
            found_context = ""
            if found_stores:
                found_lines = [f"  {s}: Rs.{d['price']:,.0f} (verified from {d['source']})"
                               for s, d in found_stores.items()]
                found_context = "\nALREADY VERIFIED PRICES:\n" + "\n".join(found_lines)

            stores_needed = ", ".join(stores_needing_price)

            prompt = f"""You are an Indian e-commerce price expert. Return CURRENT real prices for this product.

PRODUCT: "{product_name}"
SEARCH QUERY: "{query}"
CATEGORY: {"Electronics" if store_category == "electronics_stores" else "Grocery"}

WEB SEARCH DATA:
{snippet_context}
{found_context}

I NEED PRICES FOR THESE STORES: {stores_needed}

INSTRUCTIONS:
1. Use the web search data above if it contains prices for the correct product
2. If web data is missing for a store, use your TRAINING KNOWLEDGE of current Indian market prices
3. Most popular products are sold at similar prices across stores (within 5-15% range)
4. For electronics: Amazon and Flipkart usually have the best prices, Croma/Reliance are slightly higher
5. For grocery: prices are usually very similar across Blinkit/Zepto/BigBasket
6. If you found verified prices above, other stores should be in a similar range
7. ONLY set null if you truly have NO idea about this product's price
8. Prices must be in INR

Return ONLY a valid JSON array, no markdown, no explanation:
[{{"store": "StoreName", "price": 25000}}, {{"store": "Store2", "price": null}}]

Return ONLY entries for: {stores_needed}"""

            raw = ai_call(client, [{"role": "user", "content": prompt}])
            cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw.strip()).strip()
            # Remove thinking tags if present
            cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
            m = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if m:
                store_data = json.loads(m.group(0))

                for item in store_data:
                    store_name = item.get("store", "")
                    price = item.get("price")

                    matched = None
                    for cs in category_stores:
                        if cs.lower() in store_name.lower() or store_name.lower() in cs.lower():
                            matched = cs
                            break

                    if not matched:
                        continue

                    # Don't overwrite direct/ddg results
                    if matched in found_stores:
                        continue

                    if price is not None:
                        try:
                            price = float(price)
                            lo, hi = PRICE_BOUNDS.get(store_category, (5, 10_000_000))
                            if lo <= price <= hi:
                                found_stores[matched] = {
                                    "site": matched,
                                    "link": STORE_SEARCH_URLS[matched](query),
                                    "price": price,
                                    "source": "ai",
                                }
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass

    bar.progress(100, text="Done!")
    time.sleep(0.3)
    bar.empty()

    # ── Build final results ──
    for store in category_stores:
        if store not in found_stores:
            found_stores[store] = {
                "site": store,
                "link": STORE_SEARCH_URLS[store](query),
                "price": None,
                "source": None,
            }

    results_list = list(found_stores.values())
    with_price = sorted([r for r in results_list if r["price"] is not None], key=lambda x: x["price"])
    no_price   = sorted([r for r in results_list if r["price"] is None], key=lambda x: x["site"])
    return with_price + no_price


# ── UI: Result card ───────────────────────────────────────────────────────────
def result_card(item: dict, rank: int):
    price_val = item.get("price")
    link = item.get("link", "#")

    try:
        parsed = urllib.parse.urlparse(link)
        display_domain = parsed.netloc.replace("www.", "")
    except Exception:
        display_domain = ""

    if price_val is not None:
        price_display = f'Rs.{price_val:,.0f}'
        best = '<span class="ph-best">BEST PRICE</span>' if rank == 1 else ""
    else:
        price_display = '<span style="font-size: 0.95rem; color: #b8a99a; font-weight: 600;">Click to check price on store</span>'
        best = ""

    st.markdown(f"""
<div class="ph-card rank-{rank}">
  <div class="ph-card-inner">
    <div class="ph-rank">#{rank}</div>
    <div class="ph-info">
      <div class="ph-store">{item['site']}{best}</div>
      <div class="ph-link">🔗 {display_domain}</div>
      <div class="ph-price">{price_display}</div>
    </div>
    <a href="{link}" target="_blank" rel="noopener noreferrer" class="ph-buy">Buy Now &rarr;</a>
  </div>
</div>""", unsafe_allow_html=True)


# ── Main App ──────────────────────────────────────────────────────────────────
def main():
    # ── JS: Kill Streamlit badges ──
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
        '&rarr; compare prices across Indian stores instantly</div>',
        unsafe_allow_html=True
    )

    # ── API Key ───────────────────────────────────────────────────────────────
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
            st.success("OpenRouter key loaded")

        st.markdown("---")
        st.markdown("**How it works**")
        st.markdown(
            "- AI identifies your product\n"
            "- Shows stores in your city\n"
            "- Searches each store directly\n"
            "- Shows cheapest prices\n"
            "- Buy Now goes direct to store"
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
  <div class="ph-free-note">
    100% Free &middot; No credit card &middot; No SerpAPI needed
  </div>
</div>""", unsafe_allow_html=True)
        st.stop()

    client = make_client(openrouter_key)

    # ── LOCATION: Auto-detect via browser geolocation popup ──────────────────
    # Initialize session state for location
    if "detected_city" not in st.session_state:
        st.session_state.detected_city = ""
    if "geo_requested" not in st.session_state:
        st.session_state.geo_requested = False

    # Check if coordinates came back via query params
    params = st.query_params
    lat_param = params.get("lat")
    lng_param = params.get("lng")

    if lat_param and lng_param and not st.session_state.detected_city:
        try:
            lat = float(lat_param)
            lng = float(lng_param)
            city = reverse_geocode(lat, lng)
            if city:
                st.session_state.detected_city = city
                st.session_state.geo_requested = True
        except (ValueError, TypeError):
            pass

    # Inject geolocation JavaScript (only once, if not already detected)
    if not st.session_state.detected_city and not st.session_state.geo_requested:
        components.html("""
        <script>
        (function() {
            // Only request if we haven't already
            var params = new URLSearchParams(window.parent.location.search);
            if (params.has('lat') && params.has('lng')) return;

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        var lat = pos.coords.latitude.toFixed(4);
                        var lng = pos.coords.longitude.toFixed(4);
                        var url = new URL(window.parent.location);
                        url.searchParams.set('lat', lat);
                        url.searchParams.set('lng', lng);
                        window.parent.location.href = url.toString();
                    },
                    function(err) {
                        // User denied or error — do nothing, they can type manually
                        console.log('Geolocation denied or failed:', err.message);
                    },
                    { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }
                );
            }
        })();
        </script>
        """, height=0)

    # Location display — above search bar
    st.markdown('<div class="ph-section">📍 Your Location</div>', unsafe_allow_html=True)

    loc_col1, loc_col2 = st.columns([3, 1])
    with loc_col1:
        user_city = st.text_input(
            "location_input",
            value=st.session_state.detected_city,
            placeholder="Detecting your location... or type your city",
            label_visibility="collapsed",
            key="user_city_input",
        )
    with loc_col2:
        if user_city:
            tier = get_city_tier(user_city)
            tier_labels = {
                "metro": "🟢 All stores",
                "tier1_5": "🟡 Most stores",
                "tier2": "🟠 Major stores",
                "tier3": "🔴 Online only",
            }
            st.markdown(
                f'<div style="padding:0.45rem 0; font-size:0.82rem; color:#78716c;">'
                f'{tier_labels.get(tier, "Major stores")}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div style="padding:0.45rem 0; font-size:0.82rem; color:#b8a99a;">'
                'Detecting...</div>',
                unsafe_allow_html=True
            )

    # Update session state if user manually types
    if user_city and user_city != st.session_state.detected_city:
        st.session_state.detected_city = user_city

    if user_city:
        avail_grocery = get_available_stores(user_city, "grocery_stores")
        avail_elec = get_available_stores(user_city, "electronics_stores")
        auto_tag = " (auto-detected)" if lat_param and lng_param else ""
        st.markdown(
            f'<div style="font-size:0.78rem; color:#78716c; margin-bottom:0.8rem;">'
            f'📍 <strong style="color:#1c1917;">{user_city}</strong>{auto_tag} — '
            f'{len(avail_grocery)} grocery stores · {len(avail_elec)} electronics stores available</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div style="font-size:0.78rem; color:#b8a99a; margin-bottom:0.8rem;">'
            'Allow location access or type your city to see stores in your area</div>',
            unsafe_allow_html=True
        )

    st.markdown('<hr class="ph-hr">', unsafe_allow_html=True)

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

    # Show product info
    cat_emoji = {"grocery": "🛒", "electronics": "📱", "fashion": "👗",
                 "home": "🏠", "beauty": "💄"}.get(product.get("category", ""), "📦")

    if user_city:
        available_stores = get_available_stores(user_city, product.get("store_category", "electronics_stores"))
        stores_label = ", ".join(available_stores) if available_stores else "No stores in your area"
        location_tag = f" in {user_city}"
    else:
        stores_label = (
            "Blinkit, Zepto, BigBasket, Swiggy Instamart, JioMart, DMart"
            if product.get("store_category") == "grocery_stores"
            else "Amazon, Flipkart, Croma, Vijay Sales, Reliance Digital, Tata Cliq"
        )
        location_tag = ""

    st.markdown(f"""
<div class="ph-product">
  <div style="font-size:1.1rem;font-weight:700;">{cat_emoji} {product.get('name','--')}</div>
  <div style="font-size:0.85rem;margin-top:0.3rem;color:#78716c;">
    Brand: <strong>{product.get('brand') or '--'}</strong> &nbsp;&middot;&nbsp;
    Variant: <strong>{product.get('variant') or '--'}</strong>
  </div>
  <div style="font-size:0.8rem;margin-top:0.3rem;color:#92400e;">Searching{location_tag}: {stores_label}</div>
</div>""", unsafe_allow_html=True)

    # Fetch & show prices
    st.markdown('<div class="ph-section">Price Comparison &mdash; Cheapest First</div>', unsafe_allow_html=True)
    results = fetch_prices(product, client=client, user_city=user_city)

    if not results:
        query = product.get("search_query", product.get("name", ""))
        stores = (GROCERY_STORES if product.get("store_category") == "grocery_stores"
                  else ELECTRONICS_STORES)
        st.warning("Could not fetch prices automatically. Browse stores directly:")
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
        return

    results_with_price = [r for r in results if r["price"] is not None]

    st.markdown(
        f'<div style="color:#78716c;font-size:0.88rem;margin-bottom:0.8rem;">'
        f'Found prices at <strong style="color:#1c1917;">{len(results_with_price)} of {len(results)} stores</strong></div>',
        unsafe_allow_html=True
    )

    for i, item in enumerate(results, 1):
        result_card(item, i)

    if len(results_with_price) >= 2:
        save = results_with_price[-1]["price"] - results_with_price[0]["price"]
        pct  = save / results_with_price[-1]["price"] * 100
        if save > 0:
            st.markdown(f"""
<div class="ph-savings">
  <div class="ph-savings-amt">Save Rs.{save:,.0f} ({pct:.0f}%)</div>
  <div class="ph-savings-sub">
    Buy from <strong>{results_with_price[0]['site']}</strong>
    instead of <strong>{results_with_price[-1]['site']}</strong>
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center;color:#b8a99a;font-size:0.74rem;margin-top:1rem;">'
        'Prices sourced via web search + AI. Always verify on the store before purchasing.</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
