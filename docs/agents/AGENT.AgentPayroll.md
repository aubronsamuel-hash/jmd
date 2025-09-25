# AgentPayroll

## Role
Produit elements de paie a partir des timesheets.

## Inputs
- timesheet approvals
- schemas/contracts/agentpayroll_contract.json

## Outputs
- payroll ready packets

## Event Topics
- payroll.ready
- payroll.error

## Guards
- tools/guards/qa_guard.ps1
- tools/guards/security_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
