# Agent E3 - Concept d'expérience

**Input:** Knowledge & Cultural Brief (E2)
**Focus:** Scénario, Émotions, Apprentissage
**Output:** `outputs/E3_Concept_Parcours.json`

## Tâche
1. Transformer savoirs en parcours utilisateur (3 actes : découverte / pratique / transmission)
2. Définir émotions cibles par scène + mécanique d'apprentissage (learning by doing)
3. Produire graphe narratif (Mermaid) + tableau scènes

## Output schema
```json
{
  "e3_concept_journey": {
    "pitch": "string",
    "parcours": [{"scene": 1, "lieu": "", "action_utilisateur": "", "emotion": "", "apprentissage": ""}],
    "mermaid": "graph TD; A-->B"
  }
}
```
