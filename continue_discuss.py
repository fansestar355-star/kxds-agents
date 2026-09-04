from pathlib import Path
import datetime
BASE = Path(r"C:\Users\Kabakoo Apprenant.e\kxds-agents")
TRANSCRIPT = BASE / "outputs" / "discussion_20260904_204336" / "transcript_discussion.md"
OUTPUT_DIR = BASE / "outputs" / "discussion_20260904_204336"

KEY = open(r"C:\Users\Kabakoo Apprenant.e\AppData\Local\Temp\opencode\gemini_key.txt", encoding="utf-8").read().strip()
from google import genai
client = genai.Client(api_key=KEY)

# Lire existant
existing = TRANSCRIPT.read_text(encoding="utf-8")
# Agents restants à partir de E5 (on va refaire E5 complet)
agents_rest = [
    ("E5-DA", "Tu es Agent E5 DA Kabakoo. Style bogolan + afrofuturiste, Highdigenous. Propose palette + sound Kora/Balafon. Concis 5 phrases + 1 action."),
    ("E6-Proto", "Tu es Agent E6 Dev 3D. Tu optimises pour Quest2 (80k poly, 30 draw calls). Propose pipeline Blender/Unity."),
    ("E7-Test", "Tu es Agent E7 QA. Tu testes confort, framerate, engagement sur Quest2 hors ligne."),
    ("E8-Doc", "Tu es Agent E8 Scribe. Tu penses credits communautaires, post-mortem."),
    ("Guard", "Tu es Comite des Sages. Evalue la discussion avec les 5 criteres (Utile, Accessible, Culturel, Technique, Highdigenous) et donne GO/CONDITIONS/NO-GO."),
]

# Contexte pour chaque: 2 derniers messages du fichier
import re
# Extraire derniers 2 blocs
blocks = re.findall(r"## (.*?)\n(.*?)\n---", existing, re.DOTALL)
ctx = "\n".join([f"{n}: {m[:500]}" for n,m in blocks[-2:]])

sujet = "Projet Baobab Cosmique - Question: Highdigenous sans exotisation ?"

for nom, role in agents_rest:
    prompt = f"{role}\nContexte: {sujet}\nHistorique:\n{ctx}\n\nIntervention {nom} (5 phrases max + 1 action concrete):"
    print(f"Calling {nom}...")
    resp = client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
    msg = resp.text.strip()
    print(f"{nom}: {msg[:400]}")
    # Append
    with open(TRANSCRIPT, "a", encoding="utf-8") as f:
        f.write(f"\n## {nom}\n{msg}\n\n---\n")
    ctx = f"{nom}: {msg[:500]}"
    # Maj blocks
    blocks.append((nom, msg))

# Recherche
print("Recherche...")
research_prompt = "Synthese 3 sources sur symbolisme Baobab Bambara + droits usage. JSON: sources + synthese 200 mots."
r = client.models.generate_content(model="gemini-3.6-flash", contents=research_prompt)
research = r.text
(OUTPUT_DIR / "recherches" / "baobab_culturel.md").write_text(research, encoding="utf-8")
print(research[:600])

# Images
from PIL import Image, ImageDraw, ImageFont
def gen_image(text, path, color):
    img = Image.new('RGB', (1024, 768), color)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 28)
        font2 = ImageFont.truetype("arial.ttf", 18)
    except:
        font = ImageFont.load_default(); font2=font
    d.rectangle([20,20,1004,100], fill=(0,0,0))
    d.text((30,35), text, fill=(255,255,255), font=font)
    d.text((30,120), "Kabakoo XR - Highdigenous", fill=(255,255,255), font=font2)
    d.text((30,700), "Genere automatiquement", fill=(200,200,200), font=font2)
    img.save(path)
    print(f"Image {path.name}")

try:
    gen_image("E4 - Blockout Spatial Baobab 3x3m", OUTPUT_DIR / "images" / "E4_blockout.png", (34,70,60))
    gen_image("E5 - DA Bogolan Futuriste", OUTPUT_DIR / "images" / "E5_DA.png", (120,45,30))
    gen_image("E6 - Asset Baobab LowPoly 12k", OUTPUT_DIR / "images" / "E6_asset.png", (60,60,90))
    (OUTPUT_DIR / "videos" / "placeholder.txt").write_text("Videos XR a generer via Blender\n", encoding="utf-8")
except Exception as e:
    print(f"Image err {e}")

# Resume court
full = TRANSCRIPT.read_text(encoding="utf-8")
resume_prompt = f"Resume en 15 lignes max cette discussion KXDS (idees cles, tensions, decisions, actions). Discussion:\n{full[:8000]}"
r = client.models.generate_content(model="gemini-3.6-flash", contents=resume_prompt)
resume = r.text
resume_path = OUTPUT_DIR / "RESUME_COURT.md"
resume_path.write_text(f"# RESUME COURT - KXDS\nDate: {datetime.datetime.now()}\n\n{resume}\n\n---\n{full}\n", encoding="utf-8")
print("\n=== RESUME ===\n")
print(resume)
print(f"\nSaved {resume_path}")
