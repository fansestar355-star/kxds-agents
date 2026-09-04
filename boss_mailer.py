#!/usr/bin/env python3
# boss_mailer.py - Envoi mail pro du BOSS KXDS
import os, smtplib, mimetypes, sys
from pathlib import Path
from email.message import EmailMessage

# Config via env ou fichier .env
# BOSS_SMTP_HOST, BOSS_SMTP_PORT, BOSS_EMAIL, BOSS_APP_PASSWORD, BOSS_TO
def load_env():
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in open(env_path, encoding="utf-8"):
            line=line.strip()
            if not line or line.startswith("#") or "=" not in line: continue
            k,v=line.split("=",1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()

SMTP_HOST = os.getenv("BOSS_SMTP_HOST", "smtp.gmail.com")  # ou smtp.office365.com, smtp.kabakoo.africa
SMTP_PORT = int(os.getenv("BOSS_SMTP_PORT", "587"))
BOSS_EMAIL = os.getenv("BOSS_EMAIL", "")
BOSS_APP_PASSWORD = os.getenv("BOSS_APP_PASSWORD", "")
DEFAULT_TO = os.getenv("BOSS_TO", BOSS_EMAIL)

def send_mail(to, subject, body, attachments=None, html=False):
    if not BOSS_EMAIL or not BOSS_APP_PASSWORD:
        print("ERREUR: BOSS_EMAIL / BOSS_APP_PASSWORD manquants. Configure .env")
        print("Exemple .env:")
        print("BOSS_SMTP_HOST=smtp.gmail.com")
        print("BOSS_SMTP_PORT=587")
        print("BOSS_EMAIL=ton.mail.pro@gmail.com")
        print("BOSS_APP_PASSWORD=ton_mot_de_passe_application_16_chars")
        print("BOSS_TO=destinataire@kabakoo.africa")
        return False
    msg = EmailMessage()
    msg["From"] = f"KXDS Boss <{BOSS_EMAIL}>"
    msg["To"] = to or DEFAULT_TO
    msg["Subject"] = subject
    if html:
        msg.set_content(body + "\n\n(version texte)")
        msg.add_alternative(f"<html><body><pre>{body}</pre></body></html>", subtype="html")
    else:
        msg.set_content(body)
    if attachments:
        for p in attachments:
            p = Path(p)
            if not p.exists():
                print(f"Attachment manquant: {p}")
                continue
            ctype, _ = mimetypes.guess_type(str(p))
            maintype, subtype = (ctype or "application/octet-stream").split("/",1)
            msg.add_attachment(p.read_bytes(), maintype=maintype, subtype=subtype, filename=p.name)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
            s.ehlo()
            s.starttls()
            s.login(BOSS_EMAIL, BOSS_APP_PASSWORD)
            s.send_message(msg)
        print(f"MAIL OK -> {to} | {subject}")
        return True
    except Exception as e:
        print(f"MAIL ECHEC: {e}")
        import traceback; traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Boss mailer KXDS")
    ap.add_argument("--to", default=DEFAULT_TO)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=True)
    ap.add_argument("--body-file", help="Fichier contenant le body")
    ap.add_argument("--attach", nargs="*", default=[])
    ap.add_argument("--test", action="store_true", help="Envoi test")
    args = ap.parse_args()
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if args.test:
        body = "Test BOSS KXDS - Si tu reçois ceci, le mail pro fonctionne.\n\n" + body
    ok = send_mail(args.to, args.subject, body, args.attach)
    sys.exit(0 if ok else 1)
