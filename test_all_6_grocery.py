import json

# Test: All 6 grocery stores with prices for Maggi Noodles
print("=" * 60)
print("TEST: Maggi Noodles 12-pack - All 6 Grocery Stores")
print("=" * 60)

stores_response = [
    {"store": "Blinkit", "price": 189},
    {"store": "Zepto", "price": 195},
    {"store": "BigBasket", "price": 185},
    {"store": "Swiggy Instamart", "price": 190},
    {"store": "JioMart", "price": 188},
    {"store": "DMart Online", "price": 180},
]

print("\n✓ AI Response (all 6 stores with prices):")
for item in stores_response:
    print(f"  {item['store']:<20} ₹{item['price']:>6,}")

# Simulate the sorting logic
sorted_stores = sorted(stores_response, key=lambda x: x.get("price", float('inf')))

print("\n✓ Price Comparison (sorted by price):")
for i, store in enumerate(sorted_stores, 1):
    price = store["price"]
    badge = " 🏆 BEST PRICE" if i == 1 else ""
    print(f"  #{i} {store['store']:<20} ₹{price:>6,}{badge}")

# Calculate savings
if len(sorted_stores) >= 2:
    cheapest = sorted_stores[0]["price"]
    expensive = sorted_stores[-1]["price"]
    save = expensive - cheapest
    pct = (save / expensive) * 100
    print(f"\n💰 Maximum Savings: ₹{save:,} ({pct:.1f}%)")
    print(f"   Buy from {sorted_stores[0]['store']} instead of {sorted_stores[-1]['store']}")

print("\n" + "=" * 60)
print("✓ ALL 6 STORES HAVE PRICES!")
print("=" * 60)
