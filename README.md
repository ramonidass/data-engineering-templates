# Data Engineering Templates

A collection of [copier](https://copier.readthedocs.io/) templates for data engineering
projects. Every template ships the same foundation:

- **Nix flake** dev shell (reproducible toolchain, no global installs)
- **direnv** integration (`.envrc` auto-loads the shell + `.env`)
- **uv** for Python dependency management
- **just** as the task runner (every project answers to the same verbs)
- **pre-commit** hooks with git-secrets
- **ruff + mypy + pytest** for Python quality

## Templates

| Template | Use it for |
|---|---|
| `templates/infra` | Terraform infrastructure, cloud-agnostic (GCP / AWS / Azure) |
| `templates/dbt` | dbt pipelines (BigQuery / Snowflake / Databricks / DuckDB) |
| `templates/fastapi` | HTTP services and data APIs |
| `templates/pyspark` | Spark batch jobs with testable pure transforms |
| `templates/python-lib` | Shared libraries, typed pydantic models, CLIs |


## Quick start

```sh
nix develop            # or `direnv allow` once
just new infra ../my-product-infra
just new dbt ../my-product-pipeline
just new fastapi ../my-product-api
just new pyspark ../my-product-jobs
just new python-lib ../my-product-models
```

Then inside the generated project:

```sh
cd ../my-product-api
just dev-setup         # builds nix shell, uv sync, installs pre-commit hooks
nix develop            # or `direnv allow`
just ci                # lint + type-check + test, same entry point CI uses
```

## Conventions shared by every generated project

- `just dev-setup` is the only bootstrap command a new contributor needs.
- `just ci` runs exactly what CI runs. If it passes locally, CI passes.
- Configuration comes from the environment via pydantic-settings; `.env` is local-only
  and gitignored, `just create-env-file` writes a documented skeleton.
- `src/` layout for all Python; tests never import through the package under `sys.path`
  hacks.
- Secrets never live in the repo. git-secrets runs in pre-commit.

## Updating generated projects

Templates are versioned with git tags. Generated projects keep a
`.copier-answers.yml`, so they can pull template improvements with:

```sh
copier update --trust
```

Tag releases of this repo (`git tag v0.1.0`) so `copier update` has stable
references.
