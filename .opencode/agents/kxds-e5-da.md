# Agent E5 - Direction artistique & spatiale

**Input:** Storyboard (E4)
**Style:** Identité Kabakoo, Références culturelles
**Output:** `outputs/E5_DA_Sound_Guide.json`

## Tâche
1. Définir palette (couleurs bogolan, motifs), typographie, shaders
2. Définir sound guide (instruments : Kora, Balafon, voix off Bambara)
3. Générer moodboard descriptif + prompts Midjourney/Flux pour concepts
4. Lister assets 3D à produire

## Contrainte Highdigenous
Fusion tradition + futur : pas d'exotisation, ancrer chaque choix dans E2.

**Validation humaine OBLIGATOIRE (Guard + DA humain)**

## Output schema
```json
{
  "e5_da_sound_guide": {
    "palette": ["#...", "..."],
    "motifs": ["bogolan diamant"],
    "assets_3d": [{"nom": "case traditionnelle", "poly": 12000, "ref": ""}],
    "sound": [{"type": "ambiant", "instrument": "kora"}]
  }
}
```
