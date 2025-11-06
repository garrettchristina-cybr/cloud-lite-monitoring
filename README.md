# 🌩️ Cloud-Lite Monitoring

A lightweight, end-to-end **cloud security monitoring demo** built with Docker Compose.  
It showcases **log collection, alerting, AI/ML summarization**, and a themed **web front-end** simulating an MLG-style eSports site under test.

---

## 🚀 Overview

Cloud-Lite Monitoring demonstrates how a modern SOC (Security Operations Center) might monitor application activity and detect threats in real time — all using open-source tools.

It includes:

- A **PHP + Apache demo web app** (the simulated target)
- **MariaDB** for event persistence  
- **Promtail + Loki** for log aggregation  
- **Grafana** dashboards + alerting + Discord notifications  
- **Python AI summarizer** that reviews logs via the OpenAI API and posts natural-language security summaries
- **Automation scripts** to start, stop, clean, and simulate attacks  
- **Esports-themed UI** for the demo website (MLG inspired)

This project is ideal for cybersecurity students, SOC analyst training, and hands-on demonstrations of monitoring pipelines.

---

## 🧩 Stack Architecture

[ PHP / Apache Demo WebApp ]
│ writes JSON logs
▼
[ Promtail ] → pushes → [ Loki ]
│ ▲
▼ │
Grafana Dashboards ←──────────┘
│ alerts → Discord Webhook
▼
[ AI Summarizer (Python + OpenAI API, or local ML) ]


---

## ⚙️ Stack Components

| Component | Purpose | Notes |
|------------|----------|--------|
| **Apache + PHP App** | Simulated login portal that produces structured logs (`app_events.log`) | Used for failed logins & 5xx demos |
| **MariaDB** | Demo database for app events | Optional, used in example PHP |
| **Promtail** | Collects & forwards logs to Loki | JSON pipeline stages configured |
| **Loki** | Centralized log storage | Queried by Grafana & AI |
| **Grafana** | Dashboards + alerting | Includes brute-force & 5xx rules |
| **AI Summarizer (Python)** | Generates human-readable security reports | Local ML + optional GPT |
| **Discord Webhook** | Alert + summary output destination | Optional |
| **Tailwind Frontend** | Themed “MLG Invitational” web page for demo display | Educational theme |

---

## 🧰 Prerequisites

Before running the project, ensure you have the following installed and configured:

| Tool | Version | Purpose |
|------|----------|----------|
| **Docker Desktop** | 4.x+ | Required for running the full monitoring stack |
| **Docker Compose v2** | Included with Docker Desktop | Or use `docker compose` CLI |
| **PowerShell** (Windows) | 5.1+ or PowerShell 7+ | For running the demo/automation scripts |
| **Python** | 3.10+ | Required for AI summarizer |
| **OpenAI API key** | Optional | Enables GPT-powered summaries |
| **Discord Webhook URL** | Optional | Sends Grafana alerts & AI summaries |
| **Grafana** | Bundled | Accessible at http://localhost:3000 |
| **Promtail + Loki** | Bundled | Handles log collection and querying |

---

### 🔑 Environment Variables (optional)

To use AI summaries and Discord notifications, copy the example file into `.env` and edit it with your keys.

**Windows (PowerShell):**
```powershell
Copy-Item ai\.env.example ai\.env
notepad ai\.env   # edit with your keys (do NOT commit)

**macOS / Linux:**
cp ai/.env.example ai/.env
nano ai/.env      # edit with your keys (do NOT commit)

Fill values (example):
OPENAI_API_KEY=sk-yourkeyhere
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
LOKI_URL=http://localhost:3100
Important: ai/.env is listed in .gitignore and must not be committed. Keep your real API keys private.

---

## 🗂️ Project Structure

cloud-lite-monitoring/
│
├── ai/
│ ├── ai_summarize.py # Main AI summarizer (OpenAI + local ML)
│ ├── requirements.txt # Python dependencies
│ ├── model_state.json # Local ML model state (ignored by Git)
│ ├── reset_model_state.py # Resets ML baselines
│ ├── .env # Local secrets (ignored)
│ └── .env.example # Template for safe sharing
│
├── apache-php/
│ ├── Dockerfile # PHP + Apache build file
│ ├── apache-logs/ # Raw web logs (ignored by Git)
│ └── src/
│ ├── index.html # Esports-themed front-end
│ ├── login.php # Simulated login endpoint
│ ├── error.php # Simulated 5xx error page
│ ├── summary.txt # Latest AI summary (auto-updated)
│ ├── tail.php # Displays last few logs dynamically
│ └── static/ # All images and CSS backgrounds
│ ├── mlg-bg-halo.jpg
│ ├── mlg-symbol.png
│ ├── logo-classic.jpg
│ ├── logo-finalboss.jpg
│ ├── logo-instinct.jpg
│ └── logo-str8.jpg
│
├── promtail/
│ └── promtail-config.yml # Log scraping + label rules
│
├── scripts/
│ ├── start.ps1 # Launch containers
│ ├── stop.ps1 # Stop stack
│ ├── clean-logs.ps1 # Wipe old logs safely
│ ├── demo-bruteforce.ps1 # Simulate login brute-force
│ ├── demo-5xx.ps1 # Simulate HTTP 5xx spike
│ ├── demo-all.ps1 # Combined full demo
│ └── ai-summary.ps1 # Fetch AI summary via CLI
│
├── docker-compose.yml # Defines full container stack
├── .gitignore # Ensures sensitive & log files aren’t tracked
└── README.md # This documentation

---

## ⚙️ Installation & Setup

Follow these steps from your project root. Commands assume Windows PowerShell; macOS/Linux notes included where different.

### 1) Clone the repo
```bash
git clone https://github.com/<YOUR_GH_USER>/cloud-lite-monitoring.git
cd cloud-lite-monitoring

2) Copy environment template (optional, for AI + Discord)
Windows (PowerShell):
Copy-Item ai\.env.example ai\.env
notepad ai\.env   # edit with your keys (do NOT commit)

macOS / Linux:
cp ai/.env.example ai/.env
nano ai/.env

Fill values:
OPENAI_API_KEY=sk-...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
LOKI_URL=http://localhost:3100

Important: ai/.env is ignored by Git. Keep your real keys private.

3) (Optional) Create Python venv for AI scripts
Windows:
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r ai/requirements.txt

macOS / Linux:
python3 -m venv .venv
source .venv/bin/activate
pip install -r ai/requirements.txt

If you don't plan to run AI features, you can skip the Python step.

4) Start the Docker stack
# Windows PowerShell
.\scripts\start.ps1

Or manually:
docker compose up -d --build

Wait until:
http://localhost:8080 loads the demo web app
http://localhost:3000 opens Grafana (default admin / admin if first run)

5) Run a quick demo (smoke test)
PowerShell:
# Send a few failed logins from a test IP
.\scripts\demo-bruteforce.ps1 -Ip "8.8.8.8" -Count 5 -DelayMs 300

# Or full demo (brute + 5xx + AI summary)
.\scripts\demo-all.ps1

6) Stop & clean when finished
.\scripts\clean-logs.ps1   # clears logs so old data doesn't trigger alerts later
.\scripts\stop.ps1

7) Optional: Reset Loki & Promtail volumes (clears all historical data)
docker compose down
docker volume rm cloud-lite-monitoring_loki_data cloud-lite-monitoring_promtail_positions
docker compose up -d --build

Tips:
If Grafana shows missing data for geo fields, ensure login.php is writing geo_country, geo_city, geo_lat, and geo_lon and Promtail's json pipeline includes them.
If Git warns about CRLF/LF, run the included .gitattributes commit to normalize EOLs (already present in repo).

---

## 🚀 Demo Summary

Once the stack is running, use the provided PowerShell scripts to simulate attacks and view alerts in Grafana and Discord.

- **Brute-force demo:** `.\scripts\demo-bruteforce.ps1`
- **HTTP 5xx demo:** `.\scripts\demo-5xx.ps1`
- **AI summary:** `python ai/ai_summarize.py`

The AI will summarize the past 15 minutes of activity (e.g., “Multiple failed logins from Germany, minor 5xx spike detected.”).