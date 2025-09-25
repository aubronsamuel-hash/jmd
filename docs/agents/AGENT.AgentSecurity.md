# AgentSecurity

## Role
Supervise securite et conformite SOC.

## Inputs
- security events
- schemas/contracts/agentsecurity_contract.json

## Outputs
- security advisories

## Event Topics
- security.alert
- security.clearance

## Guards
- tools/guards/security_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
