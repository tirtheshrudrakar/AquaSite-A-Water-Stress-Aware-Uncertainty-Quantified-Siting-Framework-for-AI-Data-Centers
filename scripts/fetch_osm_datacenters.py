"""
Fetch real data center locations from OpenStreetMap via the Overpass API,
for a given list of US states, and write them to a CSV ready for Aqueduct's
point-based upload tool.

Usage:
    pip install requests
    python fetch_osm_datacenters.py

Output:
    data/raw/osm/us_datacenters_raw.csv
"""

import csv
import os
import time
import requests

# Tried in order; falls through to the next one on failure.
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]

HEADERS = {
    "User-Agent": "aqueduct-datacenter-fetch/1.0 (contact: rudrakartirth@gmail.com)",
    "Accept": "*/*",
}

# ISO 3166-2 codes for the pilot + hotspot states from the GAUGE roadmap.
# Add/remove codes here to change scope.
STATES = {
    "US-VA": "Virginia",
    "US-AZ": "Arizona",
    "US-GA": "Georgia",
    "US-TX": "Texas",
    "US-CA": "California",
    "US-IL": "Illinois",
}

OUT_PATH = "data/raw/osm/us_datacenters_raw.csv"


def build_query(state_code: str) -> str:
    return f"""
    [out:json][timeout:120];
    area["ISO3166-2"="{state_code}"]->.searchArea;
    nwr["telecom"="data_center"](area.searchArea);
    out center tags;
    """


def post_query(query: str) -> dict:
    """POST the query, trying each mirror, with a few retries on 429/504."""
    last_err = None
    for url in OVERPASS_URLS:
        for attempt in range(3):
            try:
                resp = requests.post(
                    url,
                    data={"data": query},   # form-encoded; requests sets Content-Type
                    headers=HEADERS,        # <-- this was missing before
                    timeout=180,
                )
                if resp.status_code in (429, 504):
                    time.sleep(10 * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as e:
                last_err = e
                time.sleep(5)
        print(f"  .. {url} failed, trying next mirror")
    raise RuntimeError(f"all Overpass endpoints failed: {last_err}")


def fetch_state(state_code: str, state_name: str) -> list[dict]:
    data = post_query(build_query(state_code))
    elements = data.get("elements", [])

    rows = []
    for el in elements:
        # Nodes have lat/lon directly; ways/relations have a "center" object.
        lat = el.get("lat", el.get("center", {}).get("lat"))
        lon = el.get("lon", el.get("center", {}).get("lon"))
        if lat is None or lon is None:
            continue
        tags = el.get("tags", {})
        rows.append({
            "name": tags.get("name", f"unnamed_dc_{el.get('id')}"),
            "latitude": lat,
            "longitude": lon,
            "state": state_name,
            "operator": tags.get("operator", ""),
            "osm_id": el.get("id"),
            "osm_type": el.get("type"),
        })
    return rows


def main():
    all_rows = []
    for code, name in STATES.items():
        print(f"Fetching {name} ({code})...")
        try:
            rows = fetch_state(code, name)
            print(f"  -> {len(rows)} facilities found")
            all_rows.extend(rows)
        except Exception as e:
            print(f"  !! failed for {name}: {e}")
        time.sleep(5)  # be polite to the free public Overpass instance

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["name", "latitude", "longitude", "state", "operator", "osm_id", "osm_type"],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nWrote {len(all_rows)} total facilities to {OUT_PATH}")
    print("Next: trim/dedupe this file, then upload lat/lon to Aqueduct's point-based tool.")


if __name__ == "__main__":
    main()