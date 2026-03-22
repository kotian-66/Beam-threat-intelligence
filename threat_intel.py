import requests
from elasticsearch import Elasticsearch
import time
import os

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Check Elasticsearch is acturlly running before starting
def check_elasticsearch():
    try:
        if es.ping():
            print("✅ Elasticsearch connected")
        else:
            print("❌ Elasticsearch not reachable — exiting")
            exit()
    except Exception as e:
        print(f"❌ Elasticsearch error: {e}")
        exit()

# Fetch threat feed
def fetch_otx():
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {"X-OTX-API-KEY": "YOUR_API_KEY"} # <- Replace this with your OTX-API key
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch OTX data: {e}")
        return {"results": []}

# Extract IOCs only ipv4 blocking
def extract_iocs(data):
    iocs = []
    for pulse in data.get("results", []):
        for ind in pulse.get("indicators", []):
            ioc_value = ind.get("indicator")
            ioc_type = ind.get("type")
            iocs.append({"value": ioc_value, "type": ioc_type})
    return iocs

# Send to SIEM
def push_to_siem(iocs):
    for ioc in iocs:
        try:
            es.index(index="threat-intel", document={
                "ioc": ioc["value"],
                "type": ioc["type"]
            })
        except Exception as e:
            print(f"❌ Failed to push to SIEM: {e}")

# Blocking only ipv4
def block_ip(ioc):
    if ioc["type"] == "IPv4":
        print(f"🚫 Blocking IP: {ioc['value']}")
    else:
        print(f"⚠️  Skipping: {ioc['value']} (type: {ioc['type']})")

# Automation Loop
check_elasticsearch()

while True:
    print("\n🔍 Fetching threat data...")
    data = fetch_otx()
    iocs = extract_iocs(data)
    print(f"✅ Found {len(iocs)} IOCs")
    push_to_siem(iocs)
    for ioc in iocs[:5]:
        block_ip(ioc)
    print("✅ Cycle complete. Waiting 5 minutes...\n")
    time.sleep(300)
