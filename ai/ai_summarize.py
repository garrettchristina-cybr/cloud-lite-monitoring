# ai/ai_summarize.py
import os, time, json, math, datetime, requests
from collections import Counter, defaultdict

# Optional: load env from .env when running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ---- Config ----
LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

# Time window: last 15 minutes
END_NS = int(time.time() * 1e9)         # ns
START_NS = END_NS - 15 * 60 * int(1e9)  # 15m
STEP = "30s"

# Loki queries
Q_FAILED = r'{job="app"} |= "login_failed" | json'
Q_5XX    = r'{job="apache"} |~ " 5\\d\\d "'

STATE_PATH = os.path.join(os.path.dirname(__file__), "model_state.json")

# --------- tiny running stats (Welford + EWMA) ----------
class RunningStats:
    def __init__(self, mean=0.0, m2=0.0, n=0, ewma=None, alpha=0.3):
        self.mean = mean
        self.m2 = m2
        self.n = n
        self.ewma = ewma
        self.alpha = alpha

    def update(self, x):
        # EWMA
        self.ewma = x if self.ewma is None else (self.alpha * x + (1 - self.alpha) * self.ewma)
        # Welford for mean/std
        self.n += 1
        delta = x - self.mean
        self.mean += delta / max(self.n, 1)
        delta2 = x - self.mean
        self.m2 += delta * delta2

    def std(self):
        return math.sqrt(self.m2 / self.n) if self.n > 0 else 0.0

    def to_dict(self):
        return {"mean": self.mean, "m2": self.m2, "n": self.n, "ewma": self.ewma, "alpha": self.alpha}

    @classmethod
    def from_dict(cls, d):
        return cls(d.get("mean",0.0), d.get("m2",0.0), d.get("n",0), d.get("ewma",None), d.get("alpha",0.3))

def load_state():
    if os.path.exists(STATE_PATH):
        try:
            with open(STATE_PATH, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # top-level keys: total_failed, total_5xx, per_ip:{ip:stats}
            s = {
                "total_failed": RunningStats.from_dict(raw.get("total_failed", {})),
                "total_5xx":    RunningStats.from_dict(raw.get("total_5xx", {})),
                "per_ip":       {ip: RunningStats.from_dict(d) for ip, d in raw.get("per_ip", {}).items()}
            }
            return s
        except Exception:
            pass
    return {"total_failed": RunningStats(), "total_5xx": RunningStats(), "per_ip": {}}

def save_state(state):
    out = {
        "total_failed": state["total_failed"].to_dict(),
        "total_5xx": state["total_5xx"].to_dict(),
        "per_ip": {ip: rs.to_dict() for ip, rs in state["per_ip"].items()}
    }
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

# --------- Loki helpers ----------
def query_range(query):
    params = {
        "query": query,
        "start": str(START_NS),
        "end": str(END_NS),
        "step": STEP,
        "direction": "backward"
    }
    r = requests.get(f"{LOKI_URL}/loki/api/v1/query_range", params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def extract_stream_values(result_json):
    out = []
    for item in result_json.get("data", {}).get("result", []):
        labels = item.get("stream", {})
        for ts, line in item.get("values", []):
            out.append((labels, line))
    return out

def parse_login_failed(rows):
    events = []
    for labels, line in rows:
        try:
            j = json.loads(line)
        except Exception:
            continue
        if j.get("event_type") != "login_failed":
            continue
        events.append({
            "ts": j.get("ts"),
            "source_ip": j.get("source_ip"),
            "geo_country": j.get("geo_country"),
            "geo_city": j.get("geo_city")
        })
    return events

# --------- tiny ML scoring ----------
def zscore(x, mean, std):
    if std <= 1e-6:
        return 0.0
    return (x - mean) / std

def ml_score(failed_events, five_xx_lines, state):
    # current window features
    total_failed = len(failed_events)
    total_5xx = len(five_xx_lines)
    per_ip_counts = Counter([e["source_ip"] for e in failed_events if e.get("source_ip")])

    # compute z-scores vs learned baselines
    tf_mean, tf_std = state["total_failed"].mean, state["total_failed"].std()
    t5_mean, t5_std = state["total_5xx"].mean, state["total_5xx"].std()

    total_failed_z = zscore(total_failed, tf_mean, tf_std)
    total_5xx_z = zscore(total_5xx, t5_mean, t5_std)

    # per-IP anomalies
    anomalous_ips = []
    for ip, c in per_ip_counts.items():
        if ip not in state["per_ip"]:
            state["per_ip"][ip] = RunningStats()
        ip_mean = state["per_ip"][ip].mean
        ip_std  = state["per_ip"][ip].std()
        ip_z = zscore(c, ip_mean, ip_std)
        if c >= max(10, ip_mean + 3*max(ip_std,1)):  # simple threshold with guard
            anomalous_ips.append((ip, c, round(ip_z,2)))

    # update baselines AFTER scoring (so detection looks at prior)
    state["total_failed"].update(total_failed)
    state["total_5xx"].update(total_5xx)
    for ip, c in per_ip_counts.items():
        state["per_ip"][ip].update(c)

    # form verdict text
    verdict_bits = []
    if total_failed_z >= 2 or any(c >= 10 for _, c, _ in anomalous_ips):
        verdict_bits.append("possible brute-force (failed logins abnormal)")
    if total_5xx_z >= 2 or total_5xx >= 5:
        verdict_bits.append("possible app error (5xx spike)")

    ml_verdict = "normal traffic"
    if verdict_bits:
        ml_verdict = "; ".join(verdict_bits)

    return {
        "total_failed": total_failed, "total_failed_z": round(total_failed_z,2),
        "total_5xx": total_5xx, "total_5xx_z": round(total_5xx_z,2),
        "anomalous_ips": anomalous_ips,
        "ml_verdict": ml_verdict
    }

# --------- summaries / outputs ----------
def local_summary(failed, five_xx, ml):
    by_ip = Counter([e["source_ip"] for e in failed if e.get("source_ip")])
    by_country = Counter([e.get("geo_country") for e in failed if e.get("geo_country")])
    by_city = Counter([f"{e.get('geo_country','?')}/{e.get('geo_city','?')}" for e in failed])

    top_ip = ", ".join([f"{ip}({cnt})" for ip, cnt in by_ip.most_common(3)]) or "n/a"
    top_country = ", ".join([f"{c or 'Unknown'}({cnt})" for c, cnt in by_country.most_common(3)]) or "n/a"
    top_city = ", ".join([f"{c}({cnt})" for c, cnt in by_city.most_common(3)]) or "n/a"

    lines = [
        "AI Summary (local + tiny ML)",
        "Window: last 15 minutes",
        f"- Failed logins: {ml['total_failed']}  (z≈{ml['total_failed_z']})   Top IPs: {top_ip}",
        f"- Top countries: {top_country}",
        f"- Top cities: {top_city}",
        f"- HTTP 5xx lines: {ml['total_5xx']}  (z≈{ml['total_5xx_z']})",
    ]
    if ml["anomalous_ips"]:
        lines.append("- Anomalous IPs: " + ", ".join([f"{ip}({c})" for ip,c,_ in ml["anomalous_ips"]]))
    lines.append(f"ML verdict: {ml['ml_verdict']}")
    return "\n".join(lines)

def summarize_with_openai(failed, five_xx, ml):
    # If you want to keep OpenAI, we pass the ML pre-summary as context
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        context = {
            "ml_features": ml,
            "sample_failed": failed[:50],
            "sample_5xx": five_xx[:50]
        }
        prompt = (
            "You are a SOC assistant. Using the ML pre-summary and samples, produce 4–6 concise bullets. "
            "Mention volumes, geos, and notable IPs. End with a one-line risk verdict.\n\n"
            f"ML pre-summary:\n{json.dumps(context, ensure_ascii=False)[:9000]}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a precise SOC assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2,
            max_tokens=300,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return local_summary(failed, five_xx, ml) + f"\n\n(Note: OpenAI unavailable: {e})"

def post_to_discord(text, is_alert=False):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        # simple embed for nicer formatting + red color when risk
        payload = {
            "embeds": [
                {
                    "title": "AI Log Summary",
                    "description": text,
                    "color": 15158332 if is_alert else 5793266  # red / green-ish
                }
            ]
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    except Exception:
        pass

def write_to_web(text):
    try:
        with open(os.path.join(os.path.dirname(__file__), "..", "apache-php", "src", "summary.txt"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass

def main():
    # Pull from Loki
    r_failed = query_range(Q_FAILED)
    rows_failed = extract_stream_values(r_failed)
    failed = parse_login_failed(rows_failed)

    r_5xx = query_range(Q_5XX)
    rows_5xx = extract_stream_values(r_5xx)

    # Load/update state + score
    state = load_state()
    ml = ml_score(failed, rows_5xx, state)
    save_state(state)

    # Summarize
    if OPENAI_API_KEY:
        summary = summarize_with_openai(failed, rows_5xx, ml)
    else:
        summary = local_summary(failed, rows_5xx, ml)

    print("\n" + summary + "\n")
    post_to_discord(summary, is_alert=("brute-force" in ml["ml_verdict"] or "5xx spike" in ml["ml_verdict"]))
    write_to_web(summary)

if __name__ == "__main__":
    main()