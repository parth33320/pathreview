## Week 7 — Issue selection

**Issue link:** https://github.com/ascherj/pathreview/issues/54

**Issue title:** Add a plan validation step that checks tool prerequisites before executing the plan

**Tier:** [ ] Tier 1  [ ] Tier 2  [x] Tier 3

**Problem summary:**
Currently, the `agent` subsystem's orchestrator in `agent/orchestrator.py` plans and runs analysis tools sequentially without checking if each tool's data and sequence prerequisites are actually met. This absence of validation means that tools like the `market_analyzer` or `skill_extractor` might run even when preceding, required stages such as tech stack detection or document ingestion have failed or are missing entirely, leading to broken executions or meaningless blank outputs. A successful fix will resolve this by introducing a DAG-based validation engine in `agent/tools/tool_dependencies.py` to assert that all tool dependency prerequisites are fully satisfied and logically ordered before the orchestrator starts execution.

**Branch name:** feat/54-plan-validation-tool-prerequisites

**Setup confirmation:** [x] App runs locally at localhost:5173

**Cohort ledger:** [x] Issue added to cohort ledger

**Selection notes / "Is this right for me?" Checklist:**
- **Codebase Familiarity:** Although I am a basic Python intern, I have reviewed the `agent/orchestrator.py` module and understand its sequential execution logic.
- **Local Setup:** Verified and fully working.
- **Scope Fit:** This is a Tier 3 issue, which is a stretch but highly valuable for learning how tools and contexts interact. The scope is well-defined and confined to validation before orchestrator execution, preventing massive sprawl.
- **Definition of Success:** A clear validation error is raised during cycle or missing dependency detection before execution starts.
