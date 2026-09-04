# Skill: kxds-validation

Use when validating any KXDS gate.

## Instructions
1. Read `outputs/E{n}_*.json` + `constraints.json`
2. Score 5 critères transversaux
3. Return JSON décision GO / GO_WITH_CONDITIONS / NO-GO
4. Write `outputs/Guard_E{n}_Validation.json`
5. Update `KXDS_Project_State.json`

## Resources
- `constraints.json` : limites poly, fps, devices
- `rag/kabakoo_kb/` : charte culturelle
- Template: `.opencode/agents/kxds-guard-validation.md`

## Workflow HITL
- E2 et E5 : après Guard, attendre validation humaine (question tool)
- Autres : Guard suffit si GO
