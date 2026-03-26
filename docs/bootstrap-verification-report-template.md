# Bootstrap Verification Report Template

Use this after running the second-machine verification flow for `TASK-024`.

## Copy/Paste Template

```md
## Bootstrap Verification Result

- machine: `<hostname or device name>`
- os: `<macOS / Linux / Windows>`
- install mode: `<dev|bootstrap>`
- repo source: `<clone|bootstrap-only>`

### Commands

```bash
python scripts/bootstrap_constellar.py --home ~/.constellar
~/.constellar/bin/constella verify bootstrap --profile <dev|bootstrap>
```

### Result

- status: `<pass|pass-with-gaps|fail>`
- verification artifact:
  - `~/.constellar/manifests/last-bootstrap-verification.json`
  - `~/.constellar/manifests/last-bootstrap-verification.md`

### Gaps

- `<none or one gap per bullet>`

### Gap Classification

- `<missing_artifact|profile_drift|runtime_gap|path_assumption|install_doc_gap>`

### Notes

- `<anything surprising, confusing, or manual>`
```

## Mapping Back

- GitHub: issue `#1`
- AgentHive: `constella-platform/TASK-024`
- Governance: repeated gaps should become lessons/guardrails

## Optional Helper

Instead of writing the report by hand, you can render a ready-to-paste comment from the generated JSON artifact:

```bash
python scripts/render_bootstrap_issue_comment.py \
  --verification-json ~/.constellar/manifests/last-bootstrap-verification.json
```
