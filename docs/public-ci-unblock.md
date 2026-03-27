# Public CI Unblock

`Constella Platform` already has a local baseline GitHub Actions workflow at [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

The remaining blocker is **GitHub auth scope**.

## Current Block

Pushing workflow-file changes requires a token with `workflow` scope.

Current local diagnosis command:

```bash
python scripts/check_github_workflow_scope.py
```

If the output says `workflow scope missing`, the workflow file cannot be pushed yet.

## Unblock Path

Refresh GitHub auth with workflow scope, then retry the push.

Example:

```bash
gh auth refresh -h github.com -s workflow
git push origin main
```

Or use the helper:

```bash
python scripts/publish_public_ci.py --repo-path . --dry-run
```

## Local State

The local commit currently waiting on auth is:

- `a692f68` `ci: add public baseline workflow`

## Verification

Even before the push is unblocked, the local repo is verified with:

```bash
uv run --project /Users/lucablaq/_/projects/constella-platform --with pytest --with httpx python -m pytest tests -q
```
