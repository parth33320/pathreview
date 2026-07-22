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

---

## Week 8 — Issue Reproduction and Solution Planning

**Issue Link:** https://github.com/ascherj/pathreview/issues/54

**Reproduction Test File:** [tests/unit/test_tool_dependencies.py](./tests/unit/test_tool_dependencies.py)

**Reproduction Commit Link:** [Reproduction Commit (feat/54-plan-validation-tool-prerequisites)](https://github.com/ascherj/pathreview/commit/reproduction-placeholder)

**PLAN.md Link:** [Technical Execution Plan (PLAN.md)](./PLAN.md)

### Reproduction Summary:
We created a tight, red-capable unit test feedback loop in `tests/unit/test_tool_dependencies.py` to prove the Orchestrator currently runs tools sequentially without satisfying prerequisites. The tests assert that:
1. Running `market_analyzer` directly (without preceding skill extraction or language detection tools in the plan) proceeds successfully with empty inputs rather than raising a plan validation error, returning a useless market alignment score of `0.0`.
2. Running tools in an invalid topological order (e.g. running the dependent `market_analyzer` before the prerequisite `skill_extractor`) completes sequentially without any validation check, causing downstream tools to execute with unpopulated inputs.

### Alignment Summary:
Through a `/grill-with-docs` session, we refined the DAG-based validation strategy and established our Ubiquitous Language in [CONTEXT.md](./CONTEXT.md). We mapped explicit dependencies (such as `market_analyzer` depending on `skill_extractor`, and `skill_extractor` depending on `tech_detector`) and designed a non-disruptive `PlanValidator` to validate topological order and detect circular dependency cycles before starting the execution loop.
