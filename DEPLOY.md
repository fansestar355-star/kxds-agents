# Déploiement Boss 24/7 - PC fermé

Ton PC éteint = les agents s'arrêtent. Pour qu'ils bossent même PC fermé, déploie le Boss sur Cloud.

## Option 1 - VPS pas cher (recommandé, 5€/mois)
1. Loue VPS chez Hostinger/OVH/DigitalOcean (Ubuntu 22.04)
2. `git clone` ou `scp -r kxds-agents` vers VPS
3. `pip install google-genai Pillow trimesh`
4. Crée `.env` avec BOSS_EMAIL + GEMINI_API_KEY
5. `nohup python boss_daemon.py > boss.log 2>&1 &`  → tourne 24/7
6. Pour redémarrage auto : `crontab -e` → `@reboot cd ~/kxds-agents && python boss_daemon.py`

## Option 2 - GitHub Actions (gratuit, sans serveur)
Crée `.github/workflows/kxds-boss.yml` :
```yaml
on:
  schedule: [{cron: "*/15 * * * *"}]  # toutes les 15 min
  workflow_dispatch:
jobs:
  boss:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install google-genai Pillow
      - run: python boss_daemon.py --once
        env:
          BOSS_EMAIL: ${{ secrets.BOSS_EMAIL }}
          BOSS_APP_PASSWORD: ${{ secrets.BOSS_APP_PASSWORD }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
```

## Option 3 - Windows local (PC doit rester allumé)
```powershell
# Tâche planifiée toutes les 15 min même écran verrouillé
$Action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Kabakoo Apprenant.e\kxds-agents\boss_daemon.py --once"
$Trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15)
Register-ScheduledTask -TaskName "KXDS-Boss" -Action $Action -Trigger $Trigger -Description "Boss KXDS 24/7"
```

## Test mail
```powershell
python boss_mailer.py --to ton@mail --subject "[KXDS-BOSS] Test" --body "Test" --test
python boss_daemon.py --test-mail
```
