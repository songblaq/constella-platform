# Multi-Machine Bootstrap Verification

## Goal

Validate that `constella-platform` and the `.constellar` bootstrap flow work on a second machine with the public repository.

## Target scenarios

### Scenario A — Repo-backed dev install

1. Clone `https://github.com/songblaq/constella-platform`
2. Create/use a local `~/.constellar/`
3. Run:

```bash
~/.constellar/bin/constella verify bootstrap --profile dev
```

4. Confirm:
- manifests readable
- profiles readable
- runtime family list present
- required repos listed for `dev`

### Scenario B — Clone-less bootstrap verification

1. Provision `~/.constellar/` only
2. Ensure manifests/profiles exist
3. Run:

```bash
~/.constellar/bin/constella verify bootstrap --profile bootstrap
```

4. Confirm:
- no repo requirement
- bootstrap profile surfaces are readable

## Evidence to capture

- machine name / OS
- verification command output
- missing files or missing runtimes
- any profile mismatch
- screenshots only if the issue is UI-specific

## Gap classification

- `missing_artifact`
- `profile_drift`
- `runtime_gap`
- `path_assumption`
- `install_doc_gap`

## Feedback loop

- GitHub issue: use or update issue #1
- AgentHive: map findings back to `TASK-024`
- Governance: lessons should become guardrails if repeated
