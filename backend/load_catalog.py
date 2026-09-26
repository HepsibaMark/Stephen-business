"""
Bulk-loads the real product catalog (scraped from apjveg.com) into your
running backend via its API. Run this AFTER your backend is up at
http://localhost:8000.

Usage:
    python load_catalog.py
"""

import requests

API_BASE = "http://localhost:8000"
# (name_en, name_ta, unit_type, price, weight_options_grams or None)
PRODUCTS = [
    ("Onion (Big)", "பெரிய வெங்காயம்", "kg", 65.00, [250, 500, 750, 1000]),
    ("Small Onion (Shallots)", "சின்ன வெங்காயம்", "kg", 90.00, [250, 500, 750, 1000]),
    ("Potato - Kodaikanal", "உருளைக்கிழங்கு - கொடைக்கானல்", "kg", 35.00, [250, 500, 750, 1000]),
    ("Coconut Big", "தேங்காய் பெரியது", "piece", 40.00, None),
    ("Potato - Agra (Sweet Taste)", "உருளைக்கிழங்கு - ஆக்ரா", "kg", 20.00, [250, 500, 750, 1000]),
    ("Coconut Small", "தேங்காய் சிறியது", "piece", 32.00, None),
    ("Tomato", "தக்காளி", "kg", 30.00, [250, 500, 750, 1000]),
    ("Karunai Kizhangu", "கருணை கிழங்கு", "kg", 70.00, [250, 500, 750, 1000]),
    ("Elephant Foot Yam", "சேனைக்கிழங்கு", "kg", 65.00, [250, 500, 750, 1000]),
    ("Drumstick", "முருங்கைக்காய்", "piece", 6.00, None),
    ("Taro Root (Seppankizhangu)", "சேப்பங்கிழங்கு", "kg", 70.00, [250, 500, 750, 1000]),
    ("Ginger", "இஞ்சி", "kg", 190.00, [250, 500, 750, 1000]),
    ("Cabbage Small", "முட்டைக்கோஸ் சிறியது", "piece", 40.00, None),
    ("Cauliflower - Big", "காளிபிளவர் பெரியது", "piece", 50.00, None),
    ("Cabbage Big", "முட்டைக்கோஸ் பெரியது", "piece", 40.00, None),
    ("Cauliflower (Medium)", "காளிபிளவர் சிறியது", "piece", 32.00, None),
    ("Pumpkin", "மஞ்சள் பூசணி", "piece", 30.00, None),
    ("Ash Gourd", "வெள்ளை பூசணி", "piece", 30.00, None),
    ("Tapioca", "மரவள்ளி கிழங்கு", "kg", 50.00, [250, 500, 750, 1000]),
    ("Green Mango", "மாங்காய்", "kg", 110.00, [250, 500, 750, 1000]),
    ("Sweet Potato", "சர்க்கரைவள்ளி கிழங்கு", "kg", 80.00, [250, 500, 750, 1000]),
    ("Beetroot", "பீட்ரூட்", "kg", 60.00, [250, 500, 750, 1000]),
    ("Sampar Vellarikkai", "சாம்பார் வெள்ளரிக்காய்", "kg", 70.00, [250, 500, 750, 1000]),
    ("Chow Chow", "சௌ சௌ", "kg", 45.00, [250, 500, 750, 1000]),
    ("Bottle Gourd", "சுரைக்காய்", "piece", 30.00, None),
    ("Soya Beans", "சோயா பீன்ஸ்", "kg", 130.00, [250, 500, 750, 1000]),
    ("Broccoli", "ப்ரோக்கோலி", "piece", 150.00, None),
    ("Butter Beans", "பட்டர் பீன்ஸ்", "kg", 140.00, [250, 500, 750, 1000]),
    ("Green Peas", "பச்சை பட்டாணி", "kg", 170.00, [250, 500, 750, 1000]),
    ("Knol Khol (Kohlrabi)", "நூல்கோல்", "kg", 60.00, [250, 500, 750, 1000]),
    ("Turnip", "டர்னிப்", "kg", 150.00, [250, 500, 750, 1000]),
    ("Capsicum (Green)", "குடைமிளகாய்", "kg", 80.00, [250, 500, 750, 1000]),
    ("Carrot (Kodaikanal)", "கேரட் (கொடைக்கானல்)", "kg", 30.00, [250, 500, 750, 1000]),
    ("Broad Beans (Avarakkai)", "அவரைக்காய்", "kg", 100.00, [250, 500, 750, 1000]),
    ("Carrot (Ooty)", "கேரட் ஊட்டி", "kg", 80.00, [250, 500, 750, 1000]),
    ("Green Beans", "பச்சை பீன்ஸ்", "kg", 100.00, [250, 500, 750, 1000]),
    ("Amla Big (Gooseberry)", "நெல்லிக்காய்", "kg", 140.00, [250, 500, 750, 1000]),
    ("Murungai Beans", "முருங்கை பீன்ஸ்", "kg", 130.00, [250, 500, 750, 1000]),
    ("Lemon", "எலுமிச்சை", "kg", 250.00, [250, 500, 750, 1000]),
    ("Cluster Beans", "கொத்தவரை", "kg", 50.00, [250, 500, 750, 1000]),
    ("Green Chilli", "பச்சை மிளகாய்", "kg", 70.00, [250, 500, 750, 1000]),
    ("Ladies Finger (Okra)", "வெண்டைக்காய்", "kg", 60.00, [250, 500, 750, 1000]),
    ("Brinjal (Purple)", "கத்தரிக்காய்", "kg", 55.00, [250, 500, 750, 1000]),
    ("Snake Gourd", "புடலங்காய்", "kg", 50.00, [250, 500, 750, 1000]),
    ("Bitter Gourd", "பாகற்காய்", "kg", 90.00, [250, 500, 750, 1000]),
    ("Ivy Gourd (Kovakkai)", "கோவைக்காய்", "kg", 65.00, [250, 500, 750, 1000]),
    ("Radish", "முள்ளங்கி", "kg", 40.00, [250, 500, 750, 1000]),
    ("Ridge Gourd", "பீர்க்கங்காய்", "kg", 70.00, [250, 500, 750, 1000]),
    ("Mochai kai", "மொச்சைக்காய்", "kg", 0.00, [250, 500, 750, 1000]),
    ("Sweet Corn", "சோளம்", "piece", 22.00, None),
    ("Mushroom (Button)", "காளான்", "piece", 47.00, None),
    ("Red Cabbage", "சிவப்பு முட்டைக்கோஸ்", "piece", 80.00, None),
    ("Garlic (China - Big)", "சைனா பூண்டு பெரியது", "kg", 240.00, [250, 500, 750, 1000]),
    ("Garlic (China Small)", "சைனா பூண்டு சிறியது", "kg", 60.00, [250, 500, 750, 1000]),
    ("Garlic (Malai Poondu - Big)", "மலை பூண்டு பெரியது", "kg", 300.00, [250, 500, 750, 1000]),
    ("Thandu Keerai", "தண்டுக்கீரை", "kattu", 13.00, None),
    ("Milagu Thakkaali Keerai", "மிளகு தக்காளி கீரை", "kattu", 25.00, None),
    ("Butter Beans Striped", "வரி பட்டர் பீன்ஸ்", "kg", 120.00, [250, 500, 750, 1000]),
    ("Arai Keerai", "அரைக்கீரை", "kattu", 13.00, None),
    ("Vallarai", "வல்லாரை", "kattu", 70.00, None),
    ("Maruthaani", "மருதாணி இலை", "kattu", 15.00, None),
    ("Potato (Bengaluru)", "உருளைக்கிழங்கு (பெங்களுரு)", "kg", 25.00, [250, 500, 750, 1000]),
    ("Banana Pepper (Bajji Milakai)", "பஜ்ஜி மிளகாய்", "kg", 80.00, [250, 500, 750, 1000]),
    ("Curry Leaves", "கறிவேப்பிலை", "kg", 60.00, [50, 100, 250, 500, 750, 1000]),
    ("Coriander Leaves", "கொத்தமல்லி", "kg", 60.00, [50, 100, 250, 500, 750, 1000]),
    ("Mint Leaves", "புதினா", "kattu", 60.00, None),
    ("Carrot - Small", "கேரட் - பொடி", "kg", 20.00, [250, 500, 750, 1000]),
    ("Onion (Medium)", "பெரிய வெங்காயம் மீடியம்", "kg", 55.00, [250, 500, 750, 1000]),
    ("Potato Small", "உருளைக்கிழங்கு சிறியது", "kg", 15.00, [250, 500, 750, 1000]),
    ("Raw Banana", "வாழைக்காய்", "piece", 7.00, None),
    ("Small Onion Medium (Shallots)", "சின்ன வெங்காயம் மீடியம்", "kg", 65.00, [250, 500, 750, 1000]),
    ("Soya Beans (Medium)", "சோயா பீன்ஸ் மீடியம்", "kg", 120.00, [250, 500, 750, 1000]),
]


def main():
    created = 0
    failed = 0
    for name_en, name_ta, unit_type, price, weights in PRODUCTS:
        payload = {
            "name_en": name_en,
            "name_ta": name_ta,
            "unit_type": unit_type,
            "price_per_unit": price,
            "is_available": True,
        }
        if weights:
            payload["weight_options_grams"] = weights

        resp = requests.post(f"{API_BASE}/products/", json=payload)
        if resp.status_code == 201:
            created += 1
            print(f"✓ {name_en}")
        else:
            failed += 1
            print(f"✗ {name_en} — {resp.status_code}: {resp.text}")

    print(f"\nDone. Created {created}, failed {failed}.")


if __name__ == "__main__":
    main()
