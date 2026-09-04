#!/usr/bin/env python3
# auto_discuss.py - Agents KXDS discutent entre eux, generent dossiers/images/videos/recherche, doc resume
import os, json, datetime
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).parent
KEY = open(r"C:\Users\Kabakoo Apprenant.e\AppData\Local\Temp\opencode\gemini_key.txt", encoding="utf-8").read().strip()
from google import genai
client = genai.Client(api_key=KEY)

OUTPUT_DIR = BASE / "outputs" / f"discussion_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Création arborescence autonome
for i in range(1,9):
    (BASE / "outputs" / f"E{i}").mkdir(exist_ok=True)
    (BASE / f"projets" / f"E{i}").mkdir(parents=True, exist_ok=True)
for d in ["videos", "images", "recherches"]:
    (OUTPUT_DIR / d).mkdir(parents=True, exist_ok=True)

AGENTS = [
    ("E1-Cadrage", "Tu es Agent E1 Strategist. Tu analyses la pertinence XR. Sois concis, critique."),
    ("E2-Recherche", "Tu es Agent E2 Ethnologue. Tu defends la justesse culturelle et les savoirs endogenes Bambara. Tu cites sources."),
    ("E3-Concept", "Tu es Agent E3 Narrative Designer. Tu proposes scenario emotion + apprentissage."),
    ("E4-Spatial", "Tu es Agent E4 Spatial Architect. Tu penses organisation 3x3m, UI diegetique, contraintes Quest2."),
    ("E5-DA", "Tu es Agent E5 DA. Tu incarnes Identite Kabakoo, palette bogolan, Highdigenous."),
    ("E6-Proto", "Tu es Agent E6 Dev 3D. Tu parles optimisation poly, draw calls, glTF."),
    ("E7-Test", "Tu es Agent E7 QA. Tu es severe sur confort, framerate, accessibilite."),
    ("E8-Doc", "Tu es Agent E8 Scribe. Tu penses credits communautaires et transmission."),
    ("Guard", "Tu es le Comite des Sages. Tu arbitres avec les 5 criteres transversaux."),
]

transcript = []
transcript_path = OUTPUT_DIR / "transcript_discussion.md"

# Sujet commun
sujet = """Projet: Experience XR Kabakoo 'Le Baobab Cosmique' - Faire decouvrir la cosmogonie Bambara aux 15-25 ans de Bamako.
Contrainte: Quest 2, 15 min max, hors ligne.
Objectif: Comprendre le Baobab comme arbre-memoire via interaction.
Question pour tous: Comment garantir Highdigenous (fusion savoir + techno) sans tomber dans l'exotisation ?"""

# Discussion tour par tour
print("=== DISCUSSION AUTONOME KXDS ===")
for idx, (nom, role) in enumerate(AGENTS):
    # Contexte: 2 derniers messages + sujet
    ctx = "\n".join([f"{n}: {m[:600]}" for n,m in transcript[-2:]])
    prompt = f"{role}\n\nContexte projet: {sujet}\n\nHistorique recent:\n{ctx}\n\nA toi ({nom}). Donne ton intervention concise (4-6 phrases max) sur le projet. Si tu es Guard, evalue rapidement la discussion precedente. Sois concret, propose 1 action."
    try:
        resp = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
        msg = resp.text.strip()
    except Exception as e:
        msg = f"[Erreur Gemini: {e}]"
    transcript.append((nom, msg))
    print(f"\n--- {nom} ---\n{msg[:500]}")
    # Sauve incrementiel
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write(f"# Discussion KXDS Autonome - {datetime.datetime.now()}\n\nSujet: {sujet}\n\n")
        for n,m in transcript:
            f.write(f"## {n}\n{m}\n\n---\n\n")

# Recherche autonome simulee (Gemini fait la recherche)
print("\n=== RECHERCHE AUTONOME ===")
research_prompt = "Fais une recherche synthetique (3 sources citees) sur : symbolisme du Baobab en cosmogonie Bambara + references culturelles verifiables + droits d'usage. Format JSON: {sources:[{nom, type, resume}], synthese:''}"
try:
    r = client.models.generate_content(model="gemini-3.6-flash", contents=research_prompt)
    research = r.text
    (OUTPUT_DIR / "recherches" / "baobab_culturel.json").write_text(json.dumps({"research": research}, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUTPUT_DIR / "recherches" / "baobab_culturel.md").write_text(research, encoding="utf-8")
    print(research[:800])
except Exception as e:
    research = f"Erreur recherche: {e}"

# Generation images autonomes (PIL placeholder Highdigenous)
print("\n=== GENERATION IMAGES ===")
def gen_image(text, path, color):
    img = Image.new('RGB', (1024, 768), color)
    d = ImageDraw.Draw(img)
    # Titre
    try:
        font = ImageFont.truetype("arial.ttf", 28)
        font2 = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        font2 = font
    d.rectangle([20,20,1004,100], fill=(0,0,0))
    d.text((30,35), text, fill=(255,255,255), font=font)
    d.text((30,120), "Kabakoo XR - Highdigenous", fill=(255,255,255), font=font2)
    d.text((30,700), "Genere automatiquement par Agent KXDS", fill=(200,200,200), font=font2)
    img.save(path)
    print(f"Image {path.name}")

gen_image("E4 - Blockout Spatial Baobab 3x3m", OUTPUT_DIR / "images" / "E4_blockout.png", (34, 70, 60))
gen_image("E5 - DA Bogolan Futuriste", OUTPUT_DIR / "images" / "E5_DA.png", (120, 45, 30))
gen_image("E6 - Asset Baobab LowPoly 12k", OUTPUT_DIR / "images" / "E6_asset.png", (60, 60, 90))

# Generation video placeholder (dossier + script)
(OUTPUT_DIR / "videos" / "placeholder.txt").write_text("Videos XR generees par agents - pipeline Unity/Blender\nE6: Baobab_animation_15s.mp4 (a generer via Blender)\n", encoding="utf-8")
# Cree aussi un .bat qui simule generation
(BOUTPUT := BASE / "outputs").mkdir(exist_ok=True)

# Resume court avec discussion (via Gemini)
print("\n=== RESUME COURT ===")
resume_prompt = f"""Tu es le Griot Orchestrateur. Resume en 15 lignes max la discussion suivante entre 9 agents KXDS, en gardant les desaccords et decisions.

Discussion:
{chr(10).join([f'{n}: {m}' for n,m in transcript])}

Recherche: {research[:1000]}

Structure ton resume:
1. Idees cles (3 bullets)
2. Tensions/Desaccords
3. Decisions prises
4. Prochaines actions autonomes (dossiers/images/videos deja crees)

Sois synthetique, style Kabakoo.
"""
try:
    r = client.models.generate_content(model="gemini-3.6-flash", contents=resume_prompt)
    resume = r.text
except Exception as e:
    resume = f"Erreur resume: {e}"

resume_path = OUTPUT_DIR / "RESUME_COURT.md"
resume_path.write_text(f"# RESUME COURT - Discussion KXDS\n\nDate: {datetime.datetime.now()}\nDossier: {OUTPUT_DIR}\n\n{resume}\n\n---\n\n# TRANSCRIPT COMPLET\n\n" + "\n".join([f"## {n}\n{m}\n" for n,m in transcript]) + f"\n\n# RECHERCHE\n{research}\n", encoding="utf-8")

# MAJ KXDS state
state_path = BASE / "KXDS_Project_State.json"
state = json.loads(state_path.read_text(encoding="utf-8"))
state["e3_concept_journey"] = {"discussion_autonome": str(OUTPUT_DIR), "agents": len(transcript)}
state["validation_history"].append({"gate": "DISCUSSION_AUTO", "resume": resume[:500]})
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

print(resume)
print(f"\n=== TERMINE ===\nDossier: {OUTPUT_DIR}\nResume: {resume_path}\nTranscript: {transcript_path}")
