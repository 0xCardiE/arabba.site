#!/usr/bin/env python3
"""Fetch Google rating/review count via Places API and write data/google-reviews.json.

Usage:
    GOOGLE_PLACES_API_KEY=your_key python3 scripts/fetch-google-reviews.py

Manual override (when API key unavailable):
    python3 scripts/fetch-google-reviews.py --rating 4.9 --count 38
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "data", "google-reviews.json")

PLACE_QUERY = "ARABBA d.o.o. Crnčićeva 4 Rijeka"
MAPS_URL = "https://www.google.com/maps/search/?api=1&query=Crn%C4%8Di%C4%87eva+4,+51000+Rijeka"


def fetch_from_places_api(api_key):
    params = urllib.parse.urlencode(
        {
            "input": PLACE_QUERY,
            "inputtype": "textquery",
            "fields": "name,rating,user_ratings_total,url",
            "key": api_key,
        }
    )
    url = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?{params}"
    with urllib.request.urlopen(url, timeout=20) as resp:
        data = json.load(resp)
    if data.get("status") != "OK" or not data.get("candidates"):
        raise RuntimeError(f"Places API: {data.get('status')} — {data.get('error_message', '')}")
    place = data["candidates"][0]
    return {
        "placeName": place.get("name", "ARABBA d.o.o."),
        "rating": place.get("rating"),
        "reviewCount": place.get("user_ratings_total"),
        "googleMapsUrl": place.get("url") or MAPS_URL,
        "updatedAt": date.today().isoformat(),
        "source": "google_places_api",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rating", type=float, help="Manual star rating (e.g. 4.9)")
    parser.add_argument("--count", type=int, help="Manual review count")
    args = parser.parse_args()

    if args.rating is not None and args.count is not None:
        payload = {
            "placeName": "ARABBA d.o.o.",
            "rating": args.rating,
            "reviewCount": args.count,
            "googleMapsUrl": MAPS_URL,
            "updatedAt": date.today().isoformat(),
            "source": "manual_cli",
        }
    else:
        api_key = os.environ.get("GOOGLE_PLACES_API_KEY") or os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            print(
                "No GOOGLE_PLACES_API_KEY set. Use --rating and --count, or set the env var.",
                file=sys.stderr,
            )
            sys.exit(1)
        payload = fetch_from_places_api(api_key)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {OUT_PATH}: {payload.get('rating')} ({payload.get('reviewCount')} reviews)")


if __name__ == "__main__":
    main()
