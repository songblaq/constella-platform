# Constella Platform

Constella Platform is the product repo for the shared capability/service core and the parallel CLI/API surfaces.

## Current scope

- capability registry
- program/history/governance domain
- CLI surface
- API surface
- file-backed audit/history store under `~/.constellar/`

## Surfaces

- CLI: `constella-platform ...`
- API: `python -m constella_platform.api`

## Verification and release

- Second-machine quickstart: [`docs/second-machine-quickstart.md`](docs/second-machine-quickstart.md)
- Multi-machine bootstrap runbook: [`docs/multi-machine-bootstrap.md`](docs/multi-machine-bootstrap.md)
- Bootstrap verification report template: [`docs/bootstrap-verification-report-template.md`](docs/bootstrap-verification-report-template.md)
- Release prep notes: [`docs/release-prep.md`](docs/release-prep.md)
- Local `.constellar` seed script: `python scripts/bootstrap_constellar.py --home ~/.constellar`
- Issue comment renderer: `python scripts/render_bootstrap_issue_comment.py --verification-json ~/.constellar/manifests/last-bootstrap-verification.json --output ~/.constellar/manifests/last-bootstrap-issue-comment.md`
- One-command verifier: `python scripts/bootstrap_verify_and_render.py --home ~/.constellar --profile dev`
- Optional issue poster: `python scripts/post_bootstrap_issue_comment.py --repo songblaq/constella-platform --issue 1 --comment-file ~/.constellar/manifests/last-bootstrap-issue-comment.md --dry-run`

## Public collaboration

- Repository: [songblaq/constella-platform](https://github.com/songblaq/constella-platform)
- Public feedback should come through GitHub issues and PRs
- Internal execution still maps back to AgentHive / Plaza / llm-collab
- For an external verification pass, start with [`docs/second-machine-quickstart.md`](docs/second-machine-quickstart.md)

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the public collaboration loop.
