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

`just new` scaffolds from the **published** template on GitHub, which is what makes the
generated project updatable later. To try out uncommitted template edits, use
`just new-local <template> <dest>`; those projects are pinned to a local path and
cannot be updated.

You can also scaffold without cloning this repo at all:

```sh
copier copy --trust -d template_kind=fastapi \
  git+ssh://git@github.com/ramonidass/data-engineering-templates.git ../my-product-api
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

Two conditions have to hold for that to work, and both are easy to trip over:

1. **The generated project must be a git repo with a clean working tree.** Copier
   updates by diffing and three-way merging, so it needs git. Otherwise you get
   `Updating is only supported in git-tracked subprojects.` Run `git init && git add -A
   && git commit` in the generated project before your first update.
2. **`_src_path` in `.copier-answers.yml` must be the GitHub URL**, not a local path
   like `templates/python-lib`. Projects scaffolded with `just new` get this right;
   older ones can be fixed by editing that one line.

Tag releases of this repo (`git tag v0.2.0 && git push --tags`) so `copier update` has
stable references — copier resolves the newest PEP 440 tag by default, and ignores
untagged commits on `main`.

## Repository layout

Copier only reads the `copier.yml` at the **root** of a repository, so a single repo
that holds several templates needs one root questionnaire that dispatches to the right
template body:

```yaml
_subdirectory: "templates/{{ template_kind }}/template"
```

That is why every question lives in the root `copier.yml`, gated with
`when: "{{ template_kind == '...' }}"`, and why the template directories hold only a
`template/` body. `template_kind` is recorded in each generated project's answers file,
so `copier update` keeps pulling from the same template it was created from.
