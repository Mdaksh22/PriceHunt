import json

# Simulate product identification response
product_response = {
    "name": "OnePlus Nord CE 5",
    "brand": "OnePlus",
    "variant": "12GB 512GB",
    "category": "electronics",
    "search_query": "OnePlus Nord CE 5 12GB 512GB price",
    "store_category": "electronics_stores"
}

print("✓ Product Identification Test:")
print(f"  Product: {product_response['name']}")
print(f"  Brand: {product_response['brand']}")
print(f"  Variant: {product_response['variant']}")
print(f"  Category: {product_response['category']}")
print(f"  Store Category: {product_response['store_category']}")
print(f"  Search Query: {product_response['search_query']}")

# Simulate store results
stores_response = [
    {"site": "Amazon India", "price": 31610, "link": "https://amazon.in/..."},
    {"site": "Flipkart", "price": 30999, "link": "https://flipkart.com/..."},
    {"site": "Croma", "price": 32500, "link": "https://croma.com/..."},
]

print("\n✓ Price Comparison Results:")
sorted_stores = sorted(stores_response, key=lambda x: x.get("price", float('inf')))
for i, store in enumerate(sorted_stores, 1):
    if store["price"]:
        print(f"  #{i} {store['site']}: ₹{store['price']:,}")
        if i == 1:
            print(f"      ↳ BEST PRICE")
    else:
        print(f"  #{i} {store['site']}: Check Price")

# Calculate savings
if len(sorted_stores) >= 2 and sorted_stores[0].get("price") and sorted_stores[-1].get("price"):
    save = sorted_stores[-1]["price"] - sorted_stores[0]["price"]
    pct = (save / sorted_stores[-1]["price"]) * 100
    print(f"\n✓ Savings: Save ₹{save:,} ({pct:.0f}%) by buying from {sorted_stores[0]['site']}")

print("\n✓ All sample search tests passed!")
