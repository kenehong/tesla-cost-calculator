#!/usr/bin/env python3
"""
Tesla Price Scraper
Scrapes current Tesla pricing from tesla.com and outputs prices.json
Runs weekly via GitHub Actions.
"""

import json
import sys
import os
from datetime import datetime, timezone

MODELS = {
    "model3": {
        "url": "https://www.tesla.com/model3/design",
        "name": "Model 3",
        "wt": 38,
    },
    "modelY": {
        "url": "https://www.tesla.com/modely/design",
        "name": "Model Y",
        "wt": 53,
    },
    "modelS": {
        "url": "https://www.tesla.com/models/design",
        "name": "Model S",
        "wt": 65,
    },
    "modelX": {
        "url": "https://www.tesla.com/modelx/design",
        "name": "Model X",
        "wt": 72,
    },
    "cybertruck": {
        "url": "https://www.tesla.com/cybertruck/design",
        "name": "Cybertruck",
        "wt": 92,
    },
}

TRIM_KEY_MAP = {
    "Model 3": {
        "rwd": "standard",
        "standard range": "standard",
        "long range": "longRange",
        "long range awd": "longRange",
        "performance": "performance",
    },
    "Model Y": {
        "rwd": "standard",
        "standard range": "standard",
        "awd": "awd",
        "all-wheel drive": "awd",
        "long range": "longRange",
        "long range awd": "longRange",
        "performance": "performance",
    },
    "Model S": {
        "awd": "awd",
        "all-wheel drive": "awd",
        "dual motor": "awd",
        "plaid": "plaid",
    },
    "Model X": {
        "awd": "awd",
        "all-wheel drive": "awd",
        "dual motor": "awd",
        "plaid": "plaid",
    },
    "Cybertruck": {
        "awd": "awd",
        "all-wheel drive": "awd",
        "foundation": "awd",
        "long range": "awd",
        "premium": "premium",
        "cyberbeast": "cyberbeast",
    },
}


def parse_price(text: str) -> int | None:
    """Extract numeric price from text like '$41,990' or 'From $41,990'."""
    import re
    match = re.search(r"\$[\d,]+", text)
    if match:
        return int(match.group().replace("$", "").replace(",", ""))
    return None


def match_trim_key(model_name: str, trim_text: str) -> str | None:
    """Map scraped trim name to our internal key."""
    mapping = TRIM_KEY_MAP.get(model_name, {})
    lower = trim_text.lower().strip()
    for pattern, key in mapping.items():
        if pattern in lower:
            return key
    return None


def scrape_with_playwright() -> dict:
    """Scrape Tesla prices using Playwright."""
    from playwright.sync_api import sync_playwright

    result = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        for model_key, model_info in MODELS.items():
            print(f"Scraping {model_info['name']}...")
            trims = {}

            try:
                page.goto(model_info["url"], wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(3000)

                # Strategy 1: Look for trim cards/options with prices
                # Tesla design pages typically show trim options with prices
                price_elements = page.query_selector_all(
                    "[data-trim], .trim-option, .group--options_block, "
                    ".configurator-trim, .trim-card, .option-card"
                )

                if price_elements:
                    for el in price_elements:
                        text = el.inner_text()
                        price = parse_price(text)
                        if price and price > 20000:
                            trim_key = match_trim_key(model_info["name"], text)
                            if trim_key and trim_key not in trims:
                                # Extract display name
                                lines = [l.strip() for l in text.split("\n") if l.strip()]
                                display_name = lines[0] if lines else trim_key
                                trims[trim_key] = {
                                    "name": display_name,
                                    "price": price,
                                }

                # Strategy 2: Broader search for price-like elements
                if not trims:
                    all_elements = page.query_selector_all(
                        "button, [role='option'], .option, a[href*='design']"
                    )
                    for el in all_elements:
                        text = el.inner_text()
                        price = parse_price(text)
                        if price and 25000 < price < 200000:
                            trim_key = match_trim_key(model_info["name"], text)
                            if trim_key and trim_key not in trims:
                                lines = [l.strip() for l in text.split("\n") if l.strip()]
                                display_name = lines[0] if lines else trim_key
                                trims[trim_key] = {
                                    "name": display_name,
                                    "price": price,
                                }

                # Strategy 3: Check page text for "Starting at $XX,XXX" patterns
                if not trims:
                    body_text = page.inner_text("body")
                    import re
                    prices_found = re.findall(
                        r"([\w\s]+?)[\s:]*\$(\d{2,3},\d{3})", body_text
                    )
                    for label, price_str in prices_found:
                        price = int(price_str.replace(",", ""))
                        if 25000 < price < 200000:
                            trim_key = match_trim_key(model_info["name"], label)
                            if trim_key and trim_key not in trims:
                                trims[trim_key] = {
                                    "name": label.strip(),
                                    "price": price,
                                }

            except Exception as e:
                print(f"  Error scraping {model_info['name']}: {e}")

            if trims:
                result[model_key] = {
                    "name": model_info["name"],
                    "wt": model_info["wt"],
                    "trims": trims,
                }
                print(f"  Found {len(trims)} trims: {list(trims.keys())}")
            else:
                print(f"  No trims found, will keep existing data")

        browser.close()

    return result


def main():
    prices_path = os.path.join(os.path.dirname(__file__), "..", "prices.json")
    prices_path = os.path.normpath(prices_path)

    # Load existing prices as fallback
    existing = {}
    if os.path.exists(prices_path):
        with open(prices_path) as f:
            existing = json.load(f)

    # Scrape
    scraped = scrape_with_playwright()

    if not scraped:
        print("Scraping returned no data. Keeping existing prices.json.")
        sys.exit(0)

    # Merge: use scraped data where available, keep existing for missing models
    existing_models = existing.get("models", {})
    merged = {}

    for key in set(list(existing_models.keys()) + list(scraped.keys())):
        if key in scraped:
            # Use scraped data but merge with existing trims if scraped is incomplete
            scraped_trims = scraped[key].get("trims", {})
            existing_trims = existing_models.get(key, {}).get("trims", {})

            # If scraped has fewer trims than existing, merge
            final_trims = {**existing_trims, **scraped_trims}

            merged[key] = {
                "name": scraped[key]["name"],
                "wt": scraped[key]["wt"],
                "trims": final_trims,
            }
        elif key in existing_models:
            merged[key] = existing_models[key]

    output = {
        "lastUpdated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "tesla.com",
        "models": merged,
    }

    with open(prices_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nUpdated {prices_path}")
    print(f"Models: {list(merged.keys())}")
    for k, v in merged.items():
        trims_info = ", ".join(
            f"{tn}=${tv['price']:,}" for tn, tv in v.get("trims", {}).items()
        )
        print(f"  {v['name']}: {trims_info}")


if __name__ == "__main__":
    main()
