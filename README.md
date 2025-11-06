# 🌩️ Cloud-Lite Monitoring

A lightweight, end-to-end **cloud security monitoring demo** built with Docker Compose.  
It showcases **log collection, alerting, AI-based summarization**, and a themed **web front-end** simulating an MLG-style eSports site under test.

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

```text
[ PHP / Apache Demo WebApp ]
        │ writes JSON logs
        ▼
[ Promtail ] → pushes → [ Loki ]
        │                        ▲
        ▼                        │
  Grafana Dashboards  ←──────────┘
        │ alerts → Discord Webhook
        ▼
[ AI Summarizer (Python + OpenAI API) ]
```

---

## ⚙️ Prerequisites

| Tool                 | Version               | Notes                       |
| -------------------- | --------------------- | --------------------------- |
| Docker Desktop       | 4.x+                  | Compose v2 enabled          |
| PowerShell (Windows) | 5.1 + or PowerShell 7 | used for automation scripts |
| Python 3.10 +        | for the AI summarizer |                             |
| OpenAI account       | optional              | required for GPT summaries  |
| Discord Webhook      | optional              | for alert notifications     |

---

## 📂 Project Structure

```
cloud-lite-monitoring/
├─ apache-php/
│  ├─ src/            → web app source (index.html, login.php, logs/)
│  ├─ apache-logs/    → access/error logs
│  ├─ Dockerfile
│
├─ promtail/          → Promtail config (YAML)
├─ grafana/           → auto-provisioned datasources
├─ ai/                → Python AI summarizer + ML state
├─ scripts/           → PowerShell utilities
│     ├─ start.ps1          → start stack (build + wait)
│     ├─ stop.ps1           → stop stack safely
│     ├─ clean-logs.ps1     → clear app + apache logs
│     ├─ demo-bruteforce.ps1→ simulate brute-force attack
│     ├─ demo-5xx.ps1       → simulate HTTP 5xx errors
│     ├─ demo-all.ps1       → run all demos + AI summary
│     └─ run.bat            → one-click Windows launcher
│
├─ docker-compose.yml
├─ .gitignore / .gitattributes
└─ README.md
```

---

## 🧠 AI Summarizer

### What it does

* Pulls the last 15 minutes of logs from Loki  
* Analyzes patterns (failed logins, 5xx spikes, IP origins)  
* If OpenAI API key is configured, sends the data to gpt-4o-mini  
* Posts an “AI Log Summary” to Discord and saves it as summary.txt  

### Example output

```
AI Log Summary
Window: last 15 minutes
- Failed logins: 12 (Top IPs: 8.8.8.8 (12))
- Top countries: US (12)
- HTTP 5xx lines: 3
Assessment: Brute-force activity likely; minor 5xx spike from form errors.
```

---

## 🧪 Quick Start

### 1️⃣ Clone & enter

```sh
git clone https://github.com/garrettchristina-cybr/cloud-lite-monitoring.git
cd cloud-lite-monitoring
```

### 2️⃣ Configure environment

Copy the example and add your keys:

```sh
cp ai/.env.example ai/.env
```

Edit `ai/.env`:

```
OPENAI_API_KEY=sk-...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
LOKI_URL=http://localhost:3100
```

### 3️⃣ Launch the stack

```sh
.\scripts\start.ps1
```

Wait until both:

- http://localhost:8080 → demo web app  
- http://localhost:3000 → Grafana (admin / admin)

### 4️⃣ Run a demo attack

```sh
.\scripts\demo-bruteforce.ps1
```

or run everything:

```sh
.\scripts\demo-all.ps1
```

You should see:

* Alerts firing in Grafana  
* Discord notifications  
* AI summary auto-posted  

### 5️⃣ Stop & clean

```sh
.\scripts\clean-logs.ps1
.\scripts\stop.ps1
```

---

## 🖥️ Grafana Dashboards

### Panels

* Failed logins per minute (by IP)  
* HTTP 5xx spikes  
* AI Summary (Text Panel)  
* (optional) GeoMap – plot IP sources by latitude/longitude  

### Alerts

* **Brute Force Detection** → triggers ≥ 10 failed logins / 5 min  
* **HTTP 5xx Spike** → triggers ≥ 10 errors / min  

Both forward to your Discord webhook.

---

## 🎮 Web App Theme

* Tailwind CSS  
* Background: `mlg-bg-halo.jpg`  
* Team logos: Classic / Final Boss / Instinct / Str8 Rippin  
* Designed as an eSports event portal under security monitoring.

---

## 🤖 Local Machine Learning (optional)

Stores anomaly-tracking state in:

```
ai/model_state.json
```

This helps detect:

> “New high: failed logins +50% vs previous average.”

Reset it:

```sh
python ai/reset_model_state.py
```

---

## 💬 Discord Integration

Color-coded embeds:

* 🟥 Red → Brute force / 5xx  
* 🟨 Yellow → Suspicious  
* 🟩 Green → Normal  

Disable by leaving webhook empty.

---

## 🧰 Maintenance Scripts

| Script                | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `start.ps1`           | Build + start all containers                          |
| `stop.ps1`            | Gracefully stop containers                            |
| `clean-logs.ps1`      | Clear logs while Promtail paused                      |
| `demo-bruteforce.ps1` | Simulate 12 failed logins from a test IP              |
| `demo-5xx.ps1`        | Trigger HTTP 5xx spike                                |
| `demo-all.ps1`        | Run all demos + AI summary                            |
| `ai-summary.ps1`      | Generate AI summary manually                          |

---

## 📊 Data Retention

Volumes:

* `loki_data`  
* `promtail_positions`

Wipe:

```sh
docker volume rm cloud-lite-monitoring_loki_data cloud-lite-monitoring_promtail_positions
```

---

## 🔒 Security & Secrets

* `.env` files ignored  
* Use `.env.example` templates  
* Never commit API keys  

---

## 🧾 License

MIT License

---

## 🙌 Credits

* Garrett Christina — Developer  
* OpenAI GPT-4o mini — AI summarizer  
* Grafana Labs — Loki/Promtail/Grafana  
* MLG & Halo assets for educational demo only  

---

## 🧠 Future Ideas

* React SIEM-style UI  
* TI (Threat Intelligence) ingestion  
* ML anomaly scoring upgrade  
* Multi-user dashboards + token auth  