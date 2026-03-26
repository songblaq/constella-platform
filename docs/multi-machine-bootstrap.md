# Multi-Machine Bootstrap Verification

## Goal

Validate that `constella-platform` and the `.constellar` bootstrap flow work on a second machine with the public repository.

## Target scenarios

### Scenario A — Repo-backed dev install

1. Clone `https://github.com/songblaq/constella-platform`
2. Seed a local `~/.constellar/`

```bash
python scripts/bootstrap_constellar.py --home ~/.constellar
```

3. Run:

```bash
~/.constellar/bin/constella verify bootstrap --profile dev
```

4. Confirm:
- manifests readable
- profiles readable
- runtime family list present
- required repos listed for `dev`
- generated artifacts exist:
  - `~/.constellar/manifests/last-bootstrap-verification.json`
  - `~/.constellar/manifests/last-bootstrap-verification.md`

### Scenario B — Clone-less bootstrap verification

1. Provision `~/.constellar/` only

```bash
python scripts/bootstrap_constellar.py --home ~/.constellar
```

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
- Attach the generated JSON or Markdown verification artifact to the issue comment when possible
- Use [`docs/bootstrap-verification-report-template.md`](bootstrap-verification-report-template.md) when posting the result
- Or render a ready-to-paste issue comment:

```bash
python scripts/render_bootstrap_issue_comment.py \
  --verification-json ~/.constellar/manifests/last-bootstrap-verification.json
```

- Or run the whole preflight in one command:

```bash
python scripts/bootstrap_verify_and_render.py --home ~/.constellar --profile dev
```
