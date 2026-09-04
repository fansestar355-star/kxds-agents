# Agent E8 - Finalisation & documentation

**Input:** Test Report + Corrections priorisées (E7)
**Finalisation:** Version stable, Crédits, Post-Mortem
**Output:** `outputs/E8_Final_Package.json` + `outputs/README_Experience.md`

## Tâche
1. Si corrections P0 → renvoyer à E6, sinon finaliser
2. Générer crédits : citer communautés sources (E2), équipe, licences CC
3. Générer documentation (usage pédagogique, install)
4. Post-mortem : ce qui a marché / à améliorer

## Output schema
```json
{
  "e8_final_package": {
    "version": "1.0.0",
    "credits": ["Communauté X (consentement)", "Artiste Y"],
    "doc_path": "outputs/README_Experience.md",
    "post_mortem": {"succes": [], "lecons": []}
  }
}
```
