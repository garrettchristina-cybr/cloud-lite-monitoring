# ai/reset_model_state.py
import os, json
STATE_PATH = os.path.join(os.path.dirname(__file__), "model_state.json")
open(STATE_PATH, "w", encoding="utf-8").write("{}")
print("Reset ai/model_state.json")