# Setup Gratuit 100% - Résiste aux coupures

## Problème
- PC éteint / coupure électricité / pas de connexion → agents locaux s'arrêtent.

## Solution gratuite (GitHub Cloud)
Tes agents tournent **dans le cloud GitHub, pas sur ton PC**. Même si Bamako n'a plus de courant, le Boss continue toutes les 2h et t'envoie un mail.

**Coût: 0€** (GitHub Actions gratuit pour repo public = illimité, privé = 2000min/mois mais on ne consomme que ~720min/mois)

### Étapes (5 min, une fois)

#### 1. Crée un mot de passe d'application Gmail (gratuit)
- Va sur https://myaccount.google.com/apppasswords (connecté avec fansestar355@gmail.com)
- Sélectionne "Mail" + "Autre" → tape "KXDS Boss"
- Google te donne 16 lettres `abcd efgh ijkl mnop` → **copie-les**
- Colle dans `kxds-agents/.env` à la ligne `BOSS_APP_PASSWORD=`

#### 2. Crée un repo GitHub (gratuit)
- Va sur https://github.com/new → Nom `kxds-agents` → **Public** (pour minutes illimitées) → Create
- Dans ton PC :
```powershell
cd C:\Users\KabakooApprenant.e\kxds-agents
git init
git add .
git commit -m "KXDS Boss initial"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/kxds-agents.git
git push -u origin main
```

#### 3. Ajoute les secrets (mots de passe cachés)
- Sur GitHub → Settings → Secrets and variables → Actions → New repository secret
- Ajoute 5 secrets :
```
BOSS_SMTP_HOST = smtp.gmail.com
BOSS_SMTP_PORT = 587
BOSS_EMAIL = fansestar355@gmail.com
BOSS_APP_PASSWORD = abcd efgh ijkl mnop  (ton 16 chars, sans espaces)
BOSS_TO = fansestar355@gmail.com
GEMINI_API_KEY = AQ.Ab8RN6...
```

#### 4. Teste
- GitHub → Actions → KXDS-Boss → Run workflow → vert = mail reçu !

### Après ?
- Tu peux éteindre ton PC, débrancher, partir. Le Boss tourne toutes les 2h dans le cloud.
- Dès que tu rallumes et fais `git pull`, tu récupères les `outputs/` générés dans le cloud.
- Pour forcer un run : GitHub → Actions → Run workflow

### Mode hybride coupure
- **Avec courant** : `auto_discuss.py` tourne local + Blender pour 3D
- **Sans courant** : GitHub Actions prend le relais (recherche, docs, mails)

### Alternative 100% locale si tu refuses le cloud
- `boss_daemon.py` + Tâche planifiée Windows → tourne quand PC allumé, se met en pause à la coupure et **reprend seul au retour du courant** (Windows relance la tâche). Pas besoin de payer, mais pas de mail pendant la coupure.
```powershell
schtasks /create /tn "KXDS-Boss" /tr "python C:\Users\KabakooApprenant.e\kxds-agents\boss_daemon.py --once" /sc minute /mo 60 /ru SYSTEM
```

Besoin d'aide pour le push GitHub ? Dis-moi ton username GitHub.
