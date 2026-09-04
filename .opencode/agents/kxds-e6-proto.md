# Agent E6 - Prototypage & production

**Input:** DA + Spatial & Sound Guide (E5)
**Pipeline:** Assets 3D, Intégration, Optimisation
**Output:** `outputs/E6_Release_Candidate.json`

## Tâche
1. Via `blender_execute_blender_code` : générer/importer assets (Poly Pizza / Hyper3D) et optimiser (decimate, WebP)
2. Via `bash` : pack glTF + Draco `gltfpack -i model.glb -o model-draco.glb`
3. Vérifier `constraints.json` : si >80k poly → optimiser, sinon REWORK
4. Produire RC noté

## Outils
- `blender_download_polyhaven_asset`, `blender_download_polypizza_model`, `blender_generate_hyper3d_model_via_text`
- `blender_execute_blender_code` pour optimisation
- `bash` pour Unity build si présent

## Output schema
```json
{
  "e6_release_candidate": {
    "build_path": "outputs/RC_v01/",
    "stats": {"poly_count": 75000, "draw_calls": 28, "size_mb": 120},
    "check_constraints": "pass"
  }
}
```
