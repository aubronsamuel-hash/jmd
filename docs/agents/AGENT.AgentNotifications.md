# AgentNotifications

## Role
Diffusion notifications multicanal.

## Inputs
- notification queue
- schemas/contracts/agentnotifications_contract.json

## Outputs
- delivery receipts

## Event Topics
- notification.dispatch
- notification.error

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
