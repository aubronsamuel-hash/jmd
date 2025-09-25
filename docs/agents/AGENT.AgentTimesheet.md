# AgentTimesheet

## Role
Controle et valide les heures travaillees.

## Inputs
- timesheet submissions
- schemas/contracts/agenttimesheet_contract.json

## Outputs
- timesheet approvals

## Event Topics
- timesheet.submitted
- timesheet.approved

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
