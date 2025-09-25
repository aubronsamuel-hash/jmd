# AgentFinance

## Role
Coordonne operations comptables.

## Inputs
- payroll packets
- schemas/contracts/agentfinance_contract.json

## Outputs
- finance journals

## Event Topics
- finance.entry.created
- finance.audit.flagged

## Guards
- tools/guards/security_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
