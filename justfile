set dotenv-load

template_url := "git+ssh://git@github.com/ramonidass/data-engineering-templates.git"

help:
    @just --list

[doc('Scaffold a new project from the published template. template is one of:
infra, dbt, fastapi, pyspark, python-lib.
Example: just new fastapi ../my-product-api')]
new template dest:
    copier copy --trust -d template_kind={{ template }} {{ template_url }} {{ dest }}

[doc('Scaffold from this checkout at committed HEAD, for testing template edits before
tagging. Copier clones a local repo, so edits must be committed to show up.
Generated projects will NOT be updatable — use `just new` for real projects.')]
new-local template dest:
    copier copy --trust --vcs-ref=HEAD -d template_kind={{ template }} . {{ dest }}

[doc('Scaffold every template into a throwaway directory to smoke-test them.
Runs against committed HEAD, so commit template edits before running this.')]
smoke-test:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    ref=(--vcs-ref=HEAD)
    copier copy --trust --defaults "${ref[@]}" -d template_kind=infra -d project_name=smoke-infra -d cloud=gcp . "$tmp/infra"
    copier copy --trust --defaults "${ref[@]}" -d template_kind=dbt -d project_name=smoke-dbt -d adapter=duckdb . "$tmp/dbt"
    for t in fastapi pyspark python-lib; do
        copier copy --trust --defaults "${ref[@]}" -d template_kind=$t -d project_name=smoke-$t . "$tmp/$t"
    done
    echo "All templates generated OK under $tmp"
    find "$tmp" -maxdepth 2 -type d | sort

pre-commit-setup:
    pre-commit install
    pre-commit install --hook-type commit-msg

pre-commit:
    pre-commit run --all-files
