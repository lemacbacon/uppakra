#!/usr/bin/env python3
"""Check Uppåkra sofa availability at IKEA Toulon - La Valette-du-Var."""

import os
import sys
from datetime import datetime

import requests

STORE_CODE = "315"      # Toulon - La Valette-du-Var
COUNTRY_CODE = "fr"
IKEA_CLIENT_ID = "da465052-7912-43b2-82fa-9dc39cdccef8"

# Article numbers -> model names (complete sofa configurations, not individual modules)
# Remove any models you're not interested in
PRODUCTS: dict[str, str] = {
    "09614047": "UPPÅKRA 3-seat sofa, Johanneshov brown-beige",
    "99613005": "UPPÅKRA 3-seat sofa, Samsala rust",
    "99614175": "UPPÅKRA 3-seat sofa with chaise lounges, Samsala rust",
    "59613074": "UPPÅKRA 3-seat sofa with left chaise, Axvall off-white",
    "99614199": "UPPÅKRA 3-seat sofa with right chaise + footrest, Axvall off-white",
    "19614056": "UPPÅKRA 3-seat sofa with left chaise, Axvall off-white (2)",
    "09613019": "UPPÅKRA 3-seat sofa with right chaise, Axvall off-white",
    "69614172": "UPPÅKRA 3-seat sofa with 2 chaise lounges, Axvall off-white",
    "69614073": "UPPÅKRA 4.5-seat sofa, Axvall off-white",
    "99614076": "UPPÅKRA 4.5-seat sofa, Samsala rust",
    "99614081": "UPPÅKRA 4.5-seat sofa with left chaise, Axvall off-white",
    "99614142": "UPPÅKRA 4.5-seat sofa with right chaise, Axvall off-white",
    "79613167": "UPPÅKRA U-shaped 4.5-seat sofa, Samsala grey-beige",
    "89614208": "UPPÅKRA U-shaped 4.5-seat sofa with left chaise",
    "99614217": "UPPÅKRA U-shaped 4.5-seat sofa with right chaise",
    "99612713": "UPPÅKRA corner 3-seat sofa, Johanneshov brown-beige",
    "99613958": "UPPÅKRA corner 6-seat sofa, Samsala yellow-brown",
}


def check_availability() -> list[dict]:
    resp = requests.get(
        f"https://api.ingka.ikea.com/cia/availabilities/ru/{COUNTRY_CODE}",
        headers={
            "x-client-id": IKEA_CLIENT_ID,
            "Accept": "application/json;version=1",
        },
        params={
            "itemNos": ",".join(PRODUCTS.keys()),
            "expand": "StoresList,Restocks",
        },
        timeout=15,
    )
    resp.raise_for_status()

    available = []
    for item in resp.json().get("availabilities", []):
        unit = item.get("classUnitKey", {})
        if unit.get("classUnitType") != "STO" or unit.get("classUnitCode") != STORE_CODE:
            continue
        if not item.get("availableForCashCarry"):
            continue

        product_id = item.get("itemKey", {}).get("itemNo", "")
        quantity = (
            item.get("buyingOption", {})
            .get("cashCarry", {})
            .get("availability", {})
            .get("quantity", 0)
        ) or 0

        if int(quantity) > 0:
            available.append({
                "id": product_id,
                "name": PRODUCTS.get(product_id, f"Uppåkra {product_id}"),
                "quantity": int(quantity),
                "url": f"https://www.ikea.com/fr/fr/p/-s{product_id}/",
            })

    return available


def send_notification(available: list[dict]) -> None:
    topic = os.environ["NTFY_TOPIC"]

    lines = []
    for item in available:
        lines.append(f"• {item['name']} ({item['quantity']} in stock)")
        lines.append(f"  {item['url']}")
    lines += [
        "",
        "Call the store to confirm a display unit is set up.",
        "IKEA Toulon · 09 69 36 20 06",
    ]

    requests.post(
        f"https://ntfy.sh/{topic}",
        data="\n".join(lines).encode("utf-8"),
        headers={
            "Title": f"Uppåkra in stock at IKEA Toulon ({len(available)} model(s))",
            "Priority": "high",
            "Tags": "couch",
        },
        timeout=10,
    )
    print(f"Notification sent to ntfy.sh/{topic}")


def main() -> None:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{ts}] Checking Uppåkra availability at IKEA Toulon (store {STORE_CODE})...")

    try:
        available = check_availability()
    except requests.RequestException as e:
        print(f"IKEA API error: {e}", file=sys.stderr)
        sys.exit(1)

    if available:
        print(f"✓ {len(available)} model(s) in stock!")
        for item in available:
            print(f"  - {item['name']}: {item['quantity']} unit(s)")
        send_notification(available)
    else:
        print("✗ No Uppåkra models currently in stock at Toulon.")


if __name__ == "__main__":
    main()
