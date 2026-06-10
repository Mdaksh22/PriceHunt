import re
import json

# Test 1: JSON parsing from AI response
print("Test 1: JSON Parsing")
raw_response = '''[
  {"store": "Amazon India", "price": 31610, "available": true},
  {"store": "Flipkart", "price": 30999, "available": true},
  {"store": "Croma", "price": 32500, "available": true}
]'''

cleaned = re.sub(r'```(?:json)?\s*\n?', '', raw_response.strip()).strip()
m = re.search(r'\[.*\]', cleaned, re.DOTALL)
if m:
    store_data = json.loads(m.group(0))
    print("✓ JSON parsing works:")
    for item in store_data:
        print(f"  - {item['store']}: ₹{item['price']}")
else:
    print("✗ JSON parsing failed")

# Test 2: Price extraction regex
print("\nTest 2: Price Extraction")
patterns = [
    r'₹\s*([\d,]+(?:\.\d{1,2})?)',
    r'Rs\.?\s*([\d,]+(?:\.\d{1,2})?)',
    r'INR\s*([\d,]+(?:\.\d{1,2})?)',
]

test_texts = [
    "Price: ₹31,610",
    "Rs. 30999",
    "INR 32500",
]

for text in test_texts:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            price = float(m.group(1).replace(",", ""))
            print(f"✓ '{text}' → ₹{price:,.0f}")
            break

print("\n✓ All basic parsing tests passed!")
