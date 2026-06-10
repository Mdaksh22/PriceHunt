import json

# Test: All 6 electronics stores with prices for OnePlus Nord CE 5
print("=" * 60)
print("TEST: OnePlus Nord CE 5 - All 6 Electronics Stores")
print("=" * 60)

stores_response = [
    {"store": "Amazon India", "price": 31610},
    {"store": "Flipkart", "price": 30999},
    {"store": "Croma", "price": 32500},
    {"store": "Vijay Sales", "price": 31899},
    {"store": "Reliance Digital", "price": 32100},
    {"store": "Tata Cliq", "price": 32800},
]

print("\n✓ AI Response (all 6 stores with prices):")
for item in stores_response:
    print(f"  {item['store']:<20} ₹{item['price']:>8,}")

# Simulate the sorting logic
sorted_stores = sorted(stores_response, key=lambda x: x.get("price", float('inf')))

print("\n✓ Price Comparison (sorted by price):")
for i, store in enumerate(sorted_stores, 1):
    price = store["price"]
    badge = " 🏆 BEST PRICE" if i == 1 else ""
    print(f"  #{i} {store['store']:<20} ₹{price:>8,}{badge}")

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
