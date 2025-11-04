# Cloud-Lite Security Monitoring

A lightweight, cloud-style monitoring stack built for a cybersecurity internship project.  
Runs fully in Docker, detects brute-force login attempts and HTTP 5xx spikes, and sends alerts to Discord.

---

## 🧠 Overview
This project demonstrates real-world security monitoring using only free, open-source tools.

**Architecture**
- **PHP-Apache (LAMP app):** demo web app that logs login attempts
- **MariaDB:** stores events
- **Promtail:** tails Apache and app logs
- **Loki:** central log database
- **Grafana:** dashboards and alerting (Discord webhook)
- **Discord:** receives alert notifications

---

## ⚙️ Setup & Run

```bash
git clone https://github.com/garrettchristina-cybr/cloud-lite-monitoring.git
cd cloud-lite-monitoring
docker compose up -d --build