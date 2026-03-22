# 🛡️ Real-Time Threat Intelligence Integration Script

**Beam Cybersecurity | AlienVault OTX → Elasticsearch Pipeline**

---

## 📌 What This Script Does

This Python script automates the full threat intelligence pipeline in 5 steps:

```
AlienVault OTX API  →  Extract IOCs  →  Push to Elasticsearch  →  Block IPv4  →  Repeat every 5 min
```

1. **Fetches** live threat data from AlienVault OTX
2. **Extracts** Indicators of Compromise (IOCs) — IPs, domains, URLs, file hashes
3. **Pushes** every IOC into Elasticsearch (your SIEM)
4. **Blocks** any IPv4 addresses via iptables (optional, commented out for safety)
5. **Repeats** automatically every 5 minutes, 24/7

---

## 📋 Prerequisites

Make sure you have the following before running:

- Python 3.9+
- Elasticsearch running on `localhost:9200`
- A free AlienVault OTX account and API key → [Get it here](https://otx.alienvault.com)

---

## ⚙️ Installation

### Step 1 — Clone or download this file

```bash
git clone https://github.com/YOUR_USERNAME/beam-threat-intelligence.git
cd beam-threat-intelligence
```

### Step 2 — Install dependencies

```bash
pip install requests elasticsearch
```

### Step 3 — Set your API key as an environment variable

**Linux / macOS:**
```bash
export OTX_API_KEY="your_actual_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set OTX_API_KEY=your_actual_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:OTX_API_KEY="your_actual_api_key_here"
```

> ⚠️ Never hardcode your API key directly in the script. Always use environment variables.

### Step 4 — Start Elasticsearch

Using Docker (easiest):
```bash
docker run -d --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.9.0
```

Or if you have Elasticsearch installed locally:
```bash
sudo systemctl start elasticsearch
```

### Step 5 — Run the script

```bash
python threat_intel.py
```

---

## 🚀 Expected Output

When running correctly, you should see:

```
✅ Elasticsearch connected

🔍 Fetching threat data...
✅ Found 47 IOCs
🚫 Blocking IP: 185.220.101.45
⚠️  Skipping non-IP IOC: malware.domain.xyz (type: domain)
⚠️  Skipping non-IP IOC: abc123...def (type: FileHash-SHA256)
🚫 Blocking IP: 198.51.100.22
⚠️  Skipping non-IP IOC: http://evil.site/payload (type: URL)
✅ Cycle complete. Waiting 5 minutes...
```

---

## 🗂️ How Data is Stored in Elasticsearch

Each IOC is saved as a document in the `threat-intel` index with this structure:

```json
{
  "ioc": "185.220.101.45",
  "type": "IPv4",
  "timestamp": "2025-06-10T14:32:01.123456+00:00"
}
```

To view your data, open Kibana at `http://localhost:5601` or query directly:

```bash
curl http://localhost:9200/threat-intel/_search?pretty
```

---

## 🔧 Configuration Options

| Setting | Where to change | Default |
|---------|----------------|---------|
| OTX API Key | `OTX_API_KEY` env variable | `"YOUR_API_KEY"` |
| Elasticsearch URL | Line 9 in script | `http://localhost:9200` |
| Polling interval | `time.sleep(300)` | 300 seconds (5 min) |
| IOC demo limit | `iocs[:5]` | 5 IOCs per cycle |
| Real IP blocking | Uncomment `os.system(...)` line | Disabled by default |

---

## ⚠️ Important Notes

**IP Blocking (iptables)** is disabled by default. To enable real blocking, uncomment this line:

```python
# os.system(f"sudo iptables -A INPUT -s {ioc['value']} -j DROP")
```

Make sure you understand the consequences before enabling this — blocking the wrong IP can affect legitimate traffic.

**Demo limit** — the script currently only processes the first 5 IOCs per cycle (`iocs[:5]`). To run on all IOCs, change it to:

```python
for ioc in iocs:  # remove [:5] for full run
    block_ip(ioc)
```

---

## 📦 Dependencies

```
requests==2.31.0
elasticsearch==8.9.0
```

Install:
```bash
pip install requests elasticsearch
```

---

## 🧪 Testing

To test without a real API key, you can mock the response by replacing `fetch_otx()` with:

```python
def fetch_otx():
    return {
        "results": [{
            "indicators": [
                {"indicator": "185.220.101.45", "type": "IPv4"},
                {"indicator": "malware.example.com", "type": "domain"},
            ]
        }]
    }
```

---

## 📜 License

MIT License — free to use, modify, and distribute.
