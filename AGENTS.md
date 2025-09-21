# AGENTS

**Source of Truth**  
- Master agent prompt: `ai/ops/codex.md`  
- Task list: `docs/TODO.yaml`  
- Machine state: `ai/state/progress.json`  
- Journal: `ai/state/journal.md`

**Agents**
- **codex (work orchestrator):** Reads Context7, selects next task from `docs/TODO.yaml`, updates state + journal each session.
- **scoring-agent (internal):** Uses `ai/prompts/scoring_agent.md` to compute features → score → explain.
- **connector-agent (internal):** Uses `ai/prompts/connector_agent.md` to map raw → CES with tests.

**Run Loop (every session)**
1. Read: architecture, schema, scoring, correlation, Context7, TODO.yaml, progress.json, journal.md.  
2. Pick highest-priority task with no unmet deps.  
3. Plan ≤500-line PR, test-first.  
4. Implement; run fmt/lint/tests.  
5. Update `docs/TODO.yaml`, `ai/state/progress.json`, `ai/state/journal.md`; open PR.

> Canonical content lives in `ai/ops/codex.md`. Update that file only; this page is a directory.
