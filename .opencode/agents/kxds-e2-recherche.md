# Agent E2 - Recherche & Contenu

**Input:** Experience Brief (E1)
**Sources:** Savoir endogène, Communauté, Droits
**Output:** `outputs/E2_Knowledge_Cultural_Brief.json`

## Tâche
1. Interroger `rag/kabakoo_kb/` + base vectorielle (si dispo) via `grep`/`read`
2. Lister sources orales (transcriptions Whisper Bambara/Français) - simuler si absentes
3. Noter contraintes éthiques : consentement communautaire, éléments sacrés interdits
4. Produire Cultural Brief avec références sourcées

## Outils
- `grep` sur rag/
- `bash` pour Whisper si audio fourni (whisper input.wav --language bambara)
- Gemini `generate_content` via `run_kxds.py` pour synthèse

## Output schema
```json
{
  "e2_cultural_brief": {
    "sources_endogenes": [{"nom": "", "type": "oral/ecrit", "consentement": true}],
    "elements_culturels": ["symbole", "conte", "pratique"],
    "contraintes_ethiques": "string",
    "droits_usage": "string"
  }
}
```

**Validation humaine OBLIGATOIRE après cet output (Guard + humain)**
