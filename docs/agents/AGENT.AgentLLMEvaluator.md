# AgentLLMEvaluator

## Role
Evalue les generations LLM.

## Inputs
- llm outputs
- schemas/contracts/agentllmevaluator_contract.json

## Outputs
- llm evaluation reports

## Event Topics
- llm.eval.completed
- llm.eval.flagged

## Guards
- tools/guards/qa_guard.ps1

## Notes
- Assure alignement avec `.codex` archive.
- Tenir a jour les schemas references.
