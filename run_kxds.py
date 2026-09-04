#!/usr/bin/env python3
# run_kxds.py - Orchestrateur Gemini pour KXDS (utilise ta clé)
import json, os, sys
from pathlib import Path

# Charge clé
key_path = Path(r"C:\Users\Kabakoo Apprenant.e\AppData\Local\Temp\opencode\gemini_key.txt")
if not key_path.exists():
    key_path = Path.home() / ".gemini_key"
if os.getenv("GEMINI_API_KEY"):
    key = os.getenv("GEMINI_API_KEY")
else:
    key = open(key_path, encoding="utf-8").read().strip()

from google import genai
client = genai.Client(api_key=key)

BASE = Path(__file__).parent
STATE = BASE / "KXDS_Project_State.json"
CONSTRAINTS = BASE / "constraints.json"

def call_gemini(prompt, model="gemini-3.6-flash"):
    resp = client.models.generate_content(model=model, contents=prompt)
    return resp.text

def step_e1(brief_inputs):
    prompt = f"""Tu es Agent E1 Cadrage Kabakoo. 
    Inputs: {json.dumps(brief_inputs, ensure_ascii=False)}
    Contraintes: {open(CONSTRAINTS, encoding='utf-8').read()}
    Produis un Experience Brief JSON strict selon schema E1."""
    text = call_gemini(prompt)
    # Sauve brut + tente parse
    (BASE/"outputs"/"E1_Experience_Brief.json").write_text(text, encoding="utf-8")
    print("E1 fait")
    return text

# Exemple usage
if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="test":
        print(call_gemini("bojour c'est juste un teste - reponds en 1 phrase"))
    else:
        print("Usage: python run_kxds.py test")
        print("Ou importe step_e1() dans ton orchestrateur")
        # Demo E1
        demo = {"besoin": "Faire decouvrir la cosmogonie Bambara aux jeunes", "public": "15-25 ans Bamako", "objectif": "Comprendre le role du Baobab", "contexte": "Quest 2 disponible"}
        print(step_e1(demo)[:2000])
