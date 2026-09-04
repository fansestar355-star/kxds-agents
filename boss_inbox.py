#!/usr/bin/env python3
# boss_inbox.py - Boss lit tes retours par mail et repond automatiquement
# Poll IMAP fansestar355@gmail.com et repond via Gemini + boss_mailer
import imaplib, email, os, json, re
from pathlib import Path
from email.header import decode_header
from email.utils import parseaddr

BASE = Path(__file__).parent
PROCESSED = BASE / "boss_processed_uids.json"
IMAP_HOST = "imap.gmail.com"

def load_env():
    env_path = BASE / ".env"
    if env_path.exists():
        for line in open(env_path, encoding="utf-8"):
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
EMAIL = os.getenv("BOSS_EMAIL", "fansestar355@gmail.com")
APP_PASS = os.getenv("BOSS_APP_PASSWORD", "").replace(" ","")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

def get_processed():
    if PROCESSED.exists():
        try: return set(json.loads(PROCESSED.read_text(encoding="utf-8")))
        except: return set()
    return set()

def save_processed(s):
    PROCESSED.write_text(json.dumps(list(s), indent=2), encoding="utf-8")

def decode_str(s):
    if not s: return ""
    parts = decode_header(s)
    out=""
    for txt, enc in parts:
        if isinstance(txt, bytes):
            out+=txt.decode(enc or "utf-8", errors="ignore")
        else:
            out+=txt
    return out

def poll_and_reply(dry=False):
    if not APP_PASS:
        print("APP_PASSWORD manquant")
        return
    print(f"[BOSS INBOX] Connexion IMAP {EMAIL}...")
    try:
        # Dans GitHub Actions, IMAP (993) est bloque comme SMTP, on passe en mode GitHub Issues
        if os.getenv("GITHUB_ACTIONS") == "true":
            print("GitHub Actions detecte -> IMAP bloque, on passe en mode Issues GitHub (HTTPS)")
            # Cherche les commentaires non lus sur les Issues Boss via API GitHub
            try:
                import urllib.request, json
                repo = os.getenv("GITHUB_REPOSITORY", "fansestar355-star/kxds-agents")
                token = os.getenv("GITHUB_TOKEN")
                if token:
                    # Liste les 5 dernieres Issues Boss
                    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?state=open&labels=kxds-boss&per_page=5", headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"})
                    with urllib.request.urlopen(req, timeout=10) as r:
                        issues = json.loads(r.read().decode())
                        print(f"{len(issues)} Issues Boss ouvertes")
                        for iss in issues:
                            print(f"Issue #{iss['number']}: {iss['title']}")
                            # Cherche commentaires
                            # Pour simplifier, on ne repond pas auto ici, juste log
                    print("Mode Issues OK - reponds en commentant l'Issue sur GitHub, Kélé te lira")
            except Exception as e:
                print(f"Issues API echec: {e}")
            return
        m = imaplib.IMAP4_SSL(IMAP_HOST, timeout=10)
        m.login(EMAIL, APP_PASS)
        m.select("INBOX")
        # Cherche uniquement les retours pour Boss (evite les 4000 spams Instagram)
        # On cherche UNSEEN qui contiennent KXDS-BOSS ou qui sont une reponse (In-Reply-To)
        # Cherche uniquement les REPONSES a Kélé (evite Canva etc.)
        typ, data = m.search(None, '(UNSEEN SUBJECT "KXDS-BOSS")')
        uids_boss = data[0].split() if data[0] else []
        uids = uids_boss
        if not uids:
            print("Aucune reponse a Kélé (UNSEEN KXDS-BOSS)")
            m.logout()
            return
        print(f"Reponses Kélé à traiter: {uids}")
        print(f"{len(uids)} nouveau(x) mail(s) : {uids}")
        processed = get_processed()
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None
        import boss_mailer
        for uid in uids:
            if uid.decode() in processed:
                print(f"UID {uid.decode()} deja traite")
                continue
            typ, msg_data = m.fetch(uid, '(RFC822)')
            msg = email.message_from_bytes(msg_data[0][1])
            subj = decode_str(msg["Subject"])
            frm = parseaddr(msg["From"])[1]
            to = parseaddr(msg["To"])[1] if msg["To"] else ""
            # Ignore les mails envoyes par Boss lui-meme sauf si c'est une reponse utilisateur (on verifie que le mail n'est pas un [KXDS-BOSS] original sans In-Reply-To)
            # Si l'utilisateur repond a un mail Boss, le mail aura In-Reply-To
            in_reply = msg["In-Reply-To"]
            # On ne repond pas aux mails que Boss vient d'envoyer (sauf si reply)
            if frm.lower() == EMAIL.lower() and not in_reply:
                print(f"Ignore auto-mail Boss UID {uid.decode()} subj={subj}")
                processed.add(uid.decode())
                continue
            # Extrait body
            body=""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type()=="text/plain" and not part.get_filename():
                        body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                        break
            else:
                body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
            body = body[:3000]
            print(f"--- MAIL de {frm} subj={subj} ---")
            try:
                print(body[:500])
            except:
                print(body[:500].encode("utf-8", errors="ignore").decode("utf-8", errors="ignore"))
            if dry:
                print("DRY - pas d'envoi")
                continue
            # --- COMMANDES FICHIERS : Kélé peut créer/prendre des fichiers même PC éteint (via cloud) ---
            import re, requests
            boss_files = BASE / "outputs" / "boss_files"
            boss_files.mkdir(parents=True, exist_ok=True)
            actions_done = []
            # 1. "crée un fichier X avec contenu Y" ou "cree un fichier"
            m_create = re.search(r"cr[eé]e?\s+un\s+fichier\s+([^\s]+)\s*(avec\s+contenu\s*[:\"]?\s*(.+))?", body, re.I)
            if m_create:
                fname = m_create.group(1).strip().strip('"').strip("'")
                fcontent = m_create.group(3) or f"Fichier {fname} cree par Kélé le {__import__('datetime').datetime.now()}"
                fpath = boss_files / fname
                fpath.parent.mkdir(parents=True, exist_ok=True)
                fpath.write_text(fcontent.strip()[:5000], encoding="utf-8")
                actions_done.append(f"Fichier créé: outputs/boss_files/{fname} ({len(fcontent)} car)")
                # git add/push sera fait par le workflow cloud, ici on le fait local aussi
                try:
                    import subprocess
                    subprocess.run(["git","add",str(fpath)], cwd=BASE, capture_output=True)
                    subprocess.run(["git","commit","-m",f"Boss: crée {fname}"], cwd=BASE, capture_output=True)
                    subprocess.run(["git","push"], cwd=BASE, capture_output=True)
                except: pass
            # 2. "prends ce fichier / telecharge ce glb/image/video : URL"
            m_url = re.search(r"(https?://\S+\.(glb|gltf|obj|png|jpg|jpeg|mp4|mov|pdf))", body, re.I)
            if m_url:
                url = m_url.group(1).strip().strip('.,"\'')
                ext = m_url.group(2).lower()
                fname = Path(url).name or f"fichier_{__import__('datetime').datetime.now().strftime('%H%M%S')}.{ext}"
                fpath = boss_files / fname
                try:
                    r = requests.get(url, timeout=20)
                    r.raise_for_status()
                    fpath.write_bytes(r.content)
                    actions_done.append(f"Fichier téléchargé: {url} -> outputs/boss_files/{fname} ({len(r.content)} bytes)")
                    import subprocess
                    subprocess.run(["git","add",str(fpath)], cwd=BASE, capture_output=True)
                    subprocess.run(["git","commit","-m",f"Boss: telecharge {fname}"], cwd=BASE, capture_output=True)
                    subprocess.run(["git","push"], cwd=BASE, capture_output=True)
                except Exception as e:
                    actions_done.append(f"Echec téléchargement {url}: {e}")

            # Boss genere reponse
            if client:
                prompt = f"""Tu es Kélé - Le Griot Suprême, chef du workflow KXDS. L'utilisateur t'a envoye ce retour par mail.

Sujet: {subj}
Message: {body}
Actions fichiers deja executes: {actions_done if actions_done else "aucune"}

Contexte: Tu supervises Awa(E1), Fatoumata(E2), Seydou(E3), Mamadou(E4), Aïssata(E5), Ibrahim(E6), Mariam(E7), Boubacar(E8) + Conseil des Sages. Tu dois repondre de facon pro, concise, en disant quelle action tu vas ordonner aux agents suite a son retour. Si c'est une commande fichier, confirme ce que tu as fait et ou est le fichier (meme PC eteint, via cloud GitHub, il apparaitra au retour). 

Reponds en 6-8 phrases max, ton Boss."""
                try:
                    # Essaie 3.5-flash d'abord (quota 3.6 epuise)
                    for model in ["gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash-lite"]:
                        try:
                            resp = client.models.generate_content(model=model, contents=prompt)
                            reply = resp.text.strip()
                            break
                        except Exception as e:
                            if "429" in str(e):
                                continue
                            raise
                    else:
                        reply = "Merci pour ton retour, je transmets aux agents."
                except Exception as e:
                    reply = f"Merci pour ton retour : {body[:200]} - Je transmets aux agents. (Erreur Gemini: {e})"
            else:
                reply = f"Merci pour ton retour, je transmets aux agents. (GEMINI_KEY manquant)"
            # Envoi reponse (mail + WhatsApp/Call)
            reply_subj = f"Re: {subj}" if not subj.startswith("Re:") else subj
            if not reply_subj.startswith("[KXDS-BOSS]"):
                reply_subj = f"[KXDS-BOSS] {reply_subj}"
            full_body = f"{reply}\n\n---\nTon message d'origine:\n{body[:1000]}\n\n---\nBoss KXDS - reponds a ce mail pour continuer la discussion. Dossier: {BASE}/outputs"
            ok = boss_mailer.send_mail(frm, reply_subj, full_body)
            # + WhatsApp/Call en parallele (meme PC eteint via cloud si possible)
            try:
                import boss_whatsapp, boss_call
                # Tronque pour WhatsApp 1k chars
                wa_text = f"Kele repond: {reply[:800]}"
                try: boss_whatsapp.send_whatsapp(wa_text)
                except: pass
                try: pass # call desactive pour economiser (WhatsApp reste gratuit)
                except: pass
            except: pass
            if ok:
                print(f"Reponse envoyee a {frm}")
                processed.add(uid.decode())
                # Marque comme lu
                try: m.store(uid, '+FLAGS', '\\Seen')
                except: pass
            else:
                print("Echec envoi reponse")
        save_processed(processed)
        m.logout()
    except Exception as e:
        print(f"IMAP erreur: {e}")
        import traceback; traceback.print_exc()

if __name__ == "__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="Ne pas envoyer, juste lire")
    ap.add_argument("--loop", action="store_true", help="Boucle infinie poll 5min")
    args=ap.parse_args()
    if args.loop:
        import time
        while True:
            poll_and_reply(dry=args.dry)
            print("Attente 5min...")
            time.sleep(300)
    else:
        poll_and_reply(dry=args.dry)
