# Agent E1 - Cadrage

**Input:** Besoin, Public, Objectif, Contexte (fournir en JSON)
**Action:** Définir la pertinence du XR
**Output:** `outputs/E1_Experience_Brief.json`

## Tâche
1. Analyser : Le XR apporte-t-il une valeur vs vidéo/atelier présentiel ? Score pertinence 1-10
2. Définir public cible (âge, littératie numérique, accès device)
3. Définir objectif d'apprentissage mesurable
4. Lister contraintes (temps, budget, devices dispo)

## Prompt système pour LLM
Tu es strategist Kabakoo. Évalue si le XR est justifié. Privilégie la frugalité. Si le besoin peut être résolu sans XR, dis-le.

## Output schema
```json
{
  "e1_experience_brief": {
    "titre": "string",
    "pertinence_xr_score": 0,
    "justification": "string",
    "public_cible": {},
    "objectif_apprentissage": "string",
    "risques": []
  }
}
```
Écrire dans `outputs/E1_Experience_Brief.json` et mettre à jour `KXDS_Project_State.json`
