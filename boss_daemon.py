#!/usr/bin/env python3
# boss_daemon.py - Boss tourne en arriere-plan, supervise agents, envoie mails, meme PC ferme si deploye cloud
import time, json, datetime
from pathlib import Path

BASE = Path(__file__).parent
STATE = BASE / "KXDS_Project_State.json"
OUTPUTS = BASE / "outputs"

# Import mailer
import boss_mailer

POLL_SEC = 15*60  # 15 min
DAILY_HOUR = 18

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] BOSS: {msg}")
    (BASE / "boss.log").open("a", encoding="utf-8").write(f"{datetime.datetime.now()} - {msg}\n")

def check_and_report():
    if not STATE.exists():
        return
    state = json.loads(STATE.read_text(encoding="utf-8"))
    current = state.get("current_step", "?")
    history = state.get("validation_history", [])
    last = history[-1] if history else {}
    # Detecte NO-GO
    if last.get("decision") == "NO-GO":
        log(f"ALERTE NO-GO detecte {last}")
        boss_mailer.send_mail(
            to=None,
            subject=f"[KXDS-BOSS] ALERTE NO-GO - {current} - Rework requis",
            body=f"Le Guard a bloque {current}\n\nDecision: {json.dumps(last, indent=2, ensure_ascii=False)}\n\nDossier: {OUTPUTS}\n\nLe Boss va ordonner le rework.",
        )
    # Avancement quotidien check
    # Si nouveau fichier dans outputs/discussion_*/RESUME
    pass

def daemon_loop():
    log("Boss daemon demarre - poll 15min, rapport quotidien 18h")
    last_daily = None
    while True:
        try:
            check_and_report()
            now = datetime.datetime.now()
            if now.hour == DAILY_HOUR and (last_daily is None or last_daily.date() != now.date()):
                # Rapport quotidien
                try:
                    resume_files = list((OUTPUTS).rglob("RESUME_COURT.md"))
                    latest = max(resume_files, key=lambda p: p.stat().st_mtime) if resume_files else None
                    body = f"Rapport quotidien KXDS - {now.date()}\nEtat: {json.loads(STATE.read_text(encoding='utf-8')).get('current_step')}\n"
                    if latest:
                        body += "\n" + latest.read_text(encoding="utf-8")[:3000]
                    boss_mailer.send_mail(
                        to=None,
                        subject=f"[KXDS-BOSS] Rapport quotidien {now.date()} - {latest.parent.name if latest else 'en cours'}",
                        body=body,
                        attachments=[str(latest)] if latest else None
                    )
                    last_daily = now
                    log("Rapport quotidien envoye")
                except Exception as e:
                    log(f"Erreur rapport quotidien: {e}")
        except Exception as e:
            log(f"Erreur loop: {e}")
        time.sleep(POLL_SEC)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="Un seul check puis exit")
    ap.add_argument("--test-mail", action="store_true")
    args = ap.parse_args()
    if args.test_mail:
        boss_mailer.send_mail(None, "[KXDS-BOSS] Test Boss", "Test daemon - si tu recois ce mail, le Boss peut te parler.")
    elif args.once:
        check_and_report()
    else:
        daemon_loop()
