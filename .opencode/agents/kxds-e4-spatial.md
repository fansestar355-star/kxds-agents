# Agent E4 - Design spatial & interaction

**Input:** Concept + Parcours (E3)
**Design:** Organisation spatiale, UI, Feedback
**Output:** `outputs/E4_Storyboard_Interaction.json` + `outputs/E4_flow.mmd`

## Tâche
1. Définir zones spatiales (échelle humaine, 3x3m play area)
2. Définir interactions (grab, pointeur, gaze) + feedback haptique/audio
3. Générer storyboard spatial (vues top) via `blender_execute_blender_code` pour blockout
4. Vérifier `constraints.json` (max 80k poly scene)

## Outils
- `blender_execute_blender_code` pour blockout rapide (cubes proxy)
- `write` Mermaid flow

## Output schema
```json
{
  "e4_storyboard_flow": {
    "zones": [{"nom": "", "dimensions": "", "assets": []}],
    "interactions": [{"action": "grab", "feedback": "vibration + son kora"}],
    "ui": "diegetic"
  }
}
```
