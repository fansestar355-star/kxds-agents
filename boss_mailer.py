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
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.login(BOSS_EMAIL, BOSS_APP_PASSWORD)
            s.send_message(msg)
        print(f"MAIL OK -> {to} | {subject}")
        return True
    except Exception as e:
        print(f"MAIL SMTP ECHEC (souvent bloque dans GitHub Actions): {e}")
        # Fallback HTTPS gratuit : cree une Issue GitHub (GitHub t'envoie un mail auto)
        try:
            import requests, os
            # Si on est dans GitHub Actions, cree une Issue
            if os.getenv("GITHUB_ACTIONS") == "true" and os.getenv("GITHUB_TOKEN"):
                import json, urllib.request, urllib.error
                repo = os.getenv("GITHUB_REPOSITORY", "fansestar355-star/kxds-agents")
                token = os.getenv("GITHUB_TOKEN")
                title = subject[:200]
                body_gh = f"**De:** {BOSS_EMAIL}\n**A:** {to}\n\n{body}\n\n---\n*Fallback HTTPS car SMTP bloque dans le cloud. Tu recois ce mail via notification GitHub. Reponds en commentant l'Issue.*"
                if attachments:
                    body_gh += f"\n\nPieces jointes: {', '.join([str(Path(p).name) for p in attachments])} (disponibles dans le repo)"
                data = json.dumps({"title": title, "body": body_gh, "labels": ["kxds-boss"]}).encode()
                req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues", data=data, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    print(f"ISSUE GITHUB CREEE -> {r.status} (tu vas recevoir un mail via GitHub)")
                    return True
        except Exception as e2:
            print(f"Fallback Issue echoue aussi: {e2}")
        import traceback; traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Boss mailer KXDS")
    ap.add_argument("--to", default=DEFAULT_TO)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--body", required=False, default="")
    ap.add_argument("--body-file", help="Fichier contenant le body")
    ap.add_argument("--attach", nargs="*", default=[])
    ap.add_argument("--test", action="store_true", help="Envoi test")
    args = ap.parse_args()
    body = args.body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    if not body:
        ap.error("--body ou --body-file requis")
    if args.test:
        body = "Test BOSS KXDS - Si tu reçois ceci, le mail pro fonctionne.\n\n" + body
    ok = send_mail(args.to, args.subject, body, args.attach)
    sys.exit(0 if ok else 1)
