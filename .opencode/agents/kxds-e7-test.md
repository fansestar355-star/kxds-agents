# Agent E7 - Test utilisateur & QA

**Input:** Release Candidate (E6)
**Tests:** Engagement, Confort, Framerate
**Output:** `outputs/E7_Test_Report.json`

## Tâche
1. Simuler ou collecter tests (5 utilisateurs cible) : temps session, confort (nausée 1-5), framerate mesuré
2. Vérifier 5 critères transversaux : Utile, Accessible, Culturellement juste, Tech excellent, Highdigenous (score 1-10 chaque)
3. Lister corrections priorisées (P0 bloquant / P1 important / P2 mineur)

## Output schema
```json
{
  "e7_test_report": {
    "scores": {"utile": 8, "accessible": 7, "culturel": 9, "technique": 6, "highdigenous": 8},
    "perf": {"fps_moyen": 68, "drop_frames": 2},
    "corrections": [{"id": "C1", "priorite": "P0", "desc": "Framerate chute à 45fps en scène 2", "cible": "E6"}]
  }
}
```
