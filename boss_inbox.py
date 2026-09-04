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
        m = imaplib.IMAP4_SSL(IMAP_HOST)
        m.login(EMAIL, APP_PASS)
        m.select("INBOX")
        # Cherche mails non lus OU tous les recents (pour test)
        typ, data = m.search(None, '(UNSEEN)')
        if not data[0]:
            print("Aucun nouveau mail")
            # Cherche aussi les 5 derniers pour debug
            typ, data = m.search(None, 'ALL')
            uids = data[0].split()[-5:]
            print(f"Debug: 5 derniers UIDs {uids}")
            m.logout()
            return
        uids = data[0].split()
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
            print(f"--- MAIL de {frm} subj={subj} ---\n{body[:500]}")
            if dry:
                print("DRY - pas d'envoi")
                continue
            # Boss genere reponse
            if client:
                prompt = f"""Tu es le KXDS Boss, chef du workflow Baobab Cosmique. L'utilisateur t'a envoye ce retour par mail.

Sujet: {subj}
Message: {body}

Contexte: Tu supervises 8 agents (E1-E8) + Guard. Tu dois repondre de facon pro, concise, en disant quelle action tu vas ordonner aux agents suite a son retour. Si c'est un feedback positif, remercie et dis prochaine etape. Si c'est une correction, dis que tu ordonnes le rework a l'agent concerne.

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
            # Envoi reponse
            reply_subj = f"Re: {subj}" if not subj.startswith("Re:") else subj
            if not reply_subj.startswith("[KXDS-BOSS]"):
                reply_subj = f"[KXDS-BOSS] {reply_subj}"
            full_body = f"{reply}\n\n---\nTon message d'origine:\n{body[:1000]}\n\n---\nBoss KXDS - reponds a ce mail pour continuer la discussion. Dossier: {BASE}/outputs"
            ok = boss_mailer.send_mail(frm, reply_subj, full_body)
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
