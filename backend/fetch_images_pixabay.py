"""
Fetches a real photo for each product from Pixabay — a stock photo
library (much cleaner results than Wikipedia or Openverse, since it's
curated stock photography rather than random personal uploads).

Run this AFTER your backend is up and load_catalog.py has already been run.
Safe to run again — it overwrites existing image_urls with new matches.

Usage:
    python fetch_images_pixabay.py

Your Pixabay API key is set below. If you ever want to move it out of
this file (e.g. before sharing this project on GitHub), set it as
PIXABAY_API_KEY in your .env file instead — this script checks there
first.
"""

import os
import re
import time
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE = "https://stephen-business.onrender.com"
PIXABAY_API = "https://pixabay.com/api/"
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

def simplify_name(name_en: str) -> str:
    """Strips size/variety descriptors so the search term is a clean,
    generic vegetable/fruit name, e.g. 'Onion (Big)' -> 'onion'."""
    name = re.sub(r"\(.*?\)", "", name_en)
    name = re.sub(
        r"\b(Big|Small|Medium|Striped|Kodaikanal|Agra|Ooty|Bengaluru|China|Malai Poondu)\b",
        "",
        name,
        flags=re.IGNORECASE,
    )
    return name.strip(" -").lower()


# Manual overrides for regional/Tamil names that generic search won't
# match well on their own — add more here as you spot bad results.
SEARCH_OVERRIDES = {
    "karunai kizhangu": "elephant foot yam",
    "seppankizhangu": "taro root",
    "sampar vellarikkai": "cucumber",
    "mochai kai": "hyacinth beans",
    "thandu keerai": "amaranth leaves",
    "milagu thakkaali keerai": "spinach leaves",
    "arai keerai": "amaranth leaves",
    "vallarai": "centella asiatica",
    "maruthaani": "henna leaves",
    "murungai beans": "moringa pods",
    "avarakkai": "broad beans",
    "kovakkai": "ivy gourd",
}


def find_pixabay_image(search_term: str) -> tuple[str | None, str | None]:
    """Returns (image_url, error_message)."""
    query = SEARCH_OVERRIDES.get(search_term, search_term)
    try:
        resp = requests.get(
            PIXABAY_API,
            params={
                "key": PIXABAY_KEY,
                "q": query,
                "image_type": "photo",
                "category": "food",
                "safesearch": "true",
                "per_page": 3,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        if hits:
            return hits[0].get("webformatURL"), None
        return None, None
    except requests.RequestException as e:
        return None, str(e)


def main():
    if PIXABAY_KEY.startswith("YOUR_"):
        print("Set your Pixabay API key first (see top of this file).")
        return

    products = requests.get(f"{API_BASE}/products/").json()
    print(f"Found {len(products)} products.\n")

    updated = 0
    no_image = 0
    errors = 0

    for product in products:
        search_term = simplify_name(product["name_en"])
        image_url, error = find_pixabay_image(search_term)

        if image_url:
            resp = requests.patch(
                f"{API_BASE}/products/{product['id']}",
                json={**product, "image_url": image_url},
            )
            if resp.status_code == 200:
                print(f"✓ {product['name_en']} -> {image_url}")
                updated += 1
            else:
                print(f"✗ {product['name_en']} -> found image but failed to save ({resp.status_code})")
                errors += 1
        elif error:
            print(f"! {product['name_en']} -> REQUEST FAILED: {error}")
            errors += 1
        else:
            print(f"— {product['name_en']} -> no image found (searched '{search_term}')")
            no_image += 1

        time.sleep(0.3)

    print(f"\nDone. Updated {updated}, no image {no_image}, errors {errors}.")


if __name__ == "__main__":
    main()
