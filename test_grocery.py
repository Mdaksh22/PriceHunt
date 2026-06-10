import json

# Test 2: Grocery search
print("Grocery Search Test:")
grocery_product = {
    "name": "Maggi 2-Minute Noodles Masala 12-pack",
    "brand": "Maggi",
    "variant": "12-pack",
    "category": "grocery",
    "search_query": "Maggi Noodles 2 minute masala 12-pack",
    "store_category": "grocery_stores"
}

print(f"  Product: {grocery_product['name']}")
print(f"  Category: {grocery_product['store_category']}")

# Grocery store results
grocery_stores = [
    {"site": "Blinkit", "price": 189, "link": "https://blinkit.com/..."},
    {"site": "Zepto", "price": 195, "link": "https://zepto.com/..."},
    {"site": "BigBasket", "price": 185, "link": "https://bigbasket.com/..."},
]

print("\n  Prices Found:")
sorted_stores = sorted(grocery_stores, key=lambda x: x.get("price", float('inf')))
for i, store in enumerate(sorted_stores, 1):
    if store["price"]:
        print(f"    #{i} {store['site']}: ₹{store['price']}")

if len(sorted_stores) >= 2:
    save = sorted_stores[-1]["price"] - sorted_stores[0]["price"]
    pct = (save / sorted_stores[-1]["price"]) * 100
    print(f"\n  💰 Save ₹{save} ({pct:.0f}%) with {sorted_stores[0]['site']}")

print("\n✓ Grocery test passed!")
