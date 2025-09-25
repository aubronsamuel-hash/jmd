# AgentCompliance

## Role
Supervise conformite.

## Inputs
- regulatory rules
- schemas/contracts/agentcompliance_contract.json

## Outputs
- compliance reports

## Event Topics
- compliance.check.passed
- compliance.check.failed

## Guards
- tools/guards/security_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
