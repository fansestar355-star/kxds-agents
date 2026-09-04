# KXDS Agents - Kabakoo XR Design System

Scaffold multi-agents généré (Muse Spark + Gemini 3.6-flash).

## Structure
```
kxds-agents/
├── opencode.json                    # 10 agents déclarés
├── KXDS_Project_State.json          # Mémoire globale
├── constraints.json                 # Limites XR frugales
├── run_kxds.py                      # Pont Gemini API (clé dans Temp/opencode/gemini_key.txt)
├── .opencode/agents/
│   ├── kxds-orchestrator.md         # Griot
│   ├── kxds-e1-cadrage.md
│   ├── kxds-e2-recherche.md  [HITL]
│   ├── kxds-e3-concept.md
│   ├── kxds-e4-spatial.md
│   ├── kxds-e5-da.md         [HITL]
│   ├── kxds-e6-proto.md
│   ├── kxds-e7-test.md
│   ├── kxds-e8-finalisation.md
│   └── kxds-guard-validation.md     # Comité des Sages
├── .opencode/skills/kxds-validation/
├── rag/kabakoo_kb/                  # Dépose charte, lexique, transcriptions ici
└── outputs/                         # E1...E8 + Guard JSON
```

## Lancer
```powershell
# Test API (déjà configurée)
python run_kxds.py test

# Via OpenCode
opencode run kxds-orchestrator  # pilote E1->E8
opencode run kxds-e1            # test unitaire E1
```

## Workflow
E1 → Guard → E2 [HITL] → Guard → E3 → Guard → ... → E8
Portes: GO / GO_WITH_CONDITIONS / NO-GO (max 3 rework)

## Prochaines étapes
1. Remplir `rag/kabakoo_kb/` avec savoirs endogènes
2. Lancer E1 avec ton vrai Besoin/Public/Objectif
3. Valider E2 manuellement (justesse culturelle)
