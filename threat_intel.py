import requests
from elasticsearch import Elasticsearch
import time
import os

es = Elasticsearch("http://localhost:9200")

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

def fetch_otx():
    url = "https://otx.alienvault.com/api/v1/pulses/subscribed"
    headers = {"X-OTX-API-KEY": "e04b4b90762226c1e337fda7ed7453ea5ca744111cfd20a4be455dec15e3ff59"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch OTX data: {e}")
        return {"results": []}

def extract_iocs(data):
    iocs = []
    for pulse in data.get("results", []):
        for ind in pulse.get("indicators", []):
            ioc_value = ind.get("indicator")
            ioc_type = ind.get("type")
            iocs.append({"value": ioc_value, "type": ioc_type})
    return iocs

def push_to_siem(iocs):
    for ioc in iocs:
        try:
            es.index(index="threat-intel", document={
                "ioc": ioc["value"],
                "type": ioc["type"]
            })
        except Exception as e:
            print(f"❌ Failed to push to SIEM: {e}")

def handle_ioc(ioc):
    if ioc["type"] == "IPv4":
        print(f"🚫 Blocking IP:              {ioc['value']}")
    elif ioc["type"] == "domain":
        print(f"🌐 Malicious Domain flagged: {ioc['value']}")
    elif ioc["type"] == "URL":
        print(f"🔗 Malicious URL flagged:    {ioc['value']}")
    elif "FileHash" in ioc["type"]:
        print(f"🧬 Malicious Hash flagged:   {ioc['value']}")
    elif ioc["type"] == "hostname":
        print(f"🖥️  Malicious Hostname:       {ioc['value']}")
    elif ioc["type"] == "CVE":
        print(f"🔴 CVE Vulnerability found:  {ioc['value']}")
    else:
        print(f"📌 IOC logged:               {ioc['value']} (type: {ioc['type']})")
check_elasticsearch()

while True:
    print("\n🔍 Fetching threat data...")
    data = fetch_otx()
    iocs = extract_iocs(data)
    print(f"✅ Found {len(iocs)} IOCs")
    push_to_siem(iocs)
    for ioc in iocs:
        handle_ioc(ioc)
    print("✅ Cycle complete. Waiting 5 minutes...\n")
    time.sleep(300)
