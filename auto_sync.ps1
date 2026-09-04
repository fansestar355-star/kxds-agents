# auto_sync.ps1 - Lance automatiquement au retour du courant, sans que tu tapes une commande
Set-Location "C:\Users\Kabakoo Apprenant.e\kxds-agents"
Add-Content -Path "boss.log" -Value "$(Get-Date) - [AUTO_SYNC] Retour courant detecte, sync..."

# 1. Git pull si repo existe
if (Test-Path ".git") {
    try {
        git pull --rebase 2>&1 | Add-Content -Path "boss.log"
        Add-Content -Path "boss.log" -Value "$(Get-Date) - git pull OK"
    } catch {
        Add-Content -Path "boss.log" -Value "$(Get-Date) - git pull fail: $_"
    }
} else {
    Add-Content -Path "boss.log" -Value "$(Get-Date) - Pas de repo git, mode mail seul"
}

# 2. Relance Boss une fois pour rattraper
try {
    $env:BOSS_SMTP_HOST="smtp.gmail.com"; $env:BOSS_SMTP_PORT="587"
    # lit .env
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#=]+?)\s*=\s*(.*)$") {
            $k=$Matches[1].Trim(); $v=$Matches[2].Trim()
            Set-Item -Path "env:$k" -Value $v
        }
    }
    python boss_daemon.py --once 2>&1 | Add-Content -Path "boss.log"
} catch {
    Add-Content -Path "boss.log" -Value "daemon fail $_"
}

# 3. Petite notif mail "Je suis de retour"
try {
    python boss_mailer.py --to "fansestar355@gmail.com" --subject "[KXDS-BOSS] PC de retour - Sync auto OK" --body "PC rallume apres coupure. Sync git + Boss relance auto. Tu n'as rien eu a faire. Dossier: $(Get-Location)" 2>&1 | Add-Content -Path "boss.log"
} catch {}
