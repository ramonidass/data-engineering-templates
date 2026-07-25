set dotenv-load

help:
    @just --list

[doc('Scaffold a new project. template is one of: infra, dbt, fastapi, pyspark, python-lib.
Example: just new fastapi ../my-product-api')]
new template dest:
    copier copy templates/{{ template }} {{ dest }}

[doc('Scaffold every template into a throwaway directory to smoke-test them.')]
smoke-test:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    copier copy --defaults --data project_name=smoke-infra --data cloud=gcp templates/infra "$tmp/infra"
    copier copy --defaults --data project_name=smoke-dbt --data adapter=duckdb templates/dbt "$tmp/dbt"
    for t in fastapi pyspark python-lib; do
        copier copy --defaults --data project_name=smoke-$t templates/$t "$tmp/$t"
    done
    echo "All templates generated OK under $tmp"
    find "$tmp" -maxdepth 2 -type d | sort

pre-commit-setup:
    pre-commit install
    pre-commit install --hook-type commit-msg

pre-commit:
    pre-commit run --all-files
