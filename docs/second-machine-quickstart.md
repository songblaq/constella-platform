# Second-Machine Quickstart

Use this when you want to validate `Constella Platform` on another machine for `TASK-024`.

## Fast Path

```bash
git clone https://github.com/songblaq/constella-platform
cd constella-platform
python scripts/bootstrap_verify_and_render.py --home ~/.constellar --profile dev
```

## What This Does

The command above performs all three steps in sequence:

1. Seed a local `~/.constellar/`
2. Run bootstrap verification for the chosen profile
3. Render a ready-to-paste GitHub issue comment

## Resulting Artifacts

After the command finishes, these files should exist:

- `~/.constellar/manifests/last-bootstrap-verification.json`
- `~/.constellar/manifests/last-bootstrap-verification.md`
- `~/.constellar/manifests/last-bootstrap-issue-comment.md`

## Post Result

1. Open GitHub issue `#1`
2. Paste or attach `~/.constellar/manifests/last-bootstrap-issue-comment.md`
3. If there are problems, classify them using:
   - `missing_artifact`
   - `profile_drift`
   - `runtime_gap`
   - `path_assumption`
   - `install_doc_gap`

## If You Want More Detail

- Full runbook: [`multi-machine-bootstrap.md`](multi-machine-bootstrap.md)
- Report template: [`bootstrap-verification-report-template.md`](bootstrap-verification-report-template.md)
- Public collaboration notes: [`../CONTRIBUTING.md`](../CONTRIBUTING.md)
