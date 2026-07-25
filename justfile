set dotenv-load

template_url := "git+ssh://git@github.com/ramonidass/data-engineering-templates.git"

help:
    @just --list

[doc('Scaffold a new project from the published template. template is one of:
infra, dbt, fastapi, pyspark, python-pipeline, python-lib.
Example: just new fastapi ../my-product-api')]
new template dest:
    copier copy --trust -d template_kind={{ template }} {{ template_url }} {{ dest }}

[doc('Scaffold from a snapshot of this checkout, including uncommitted edits.
Generated projects will NOT be updatable — use `just new` for real projects.')]
new-local template dest:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    mkdir -p "$tmp/source"
    tar --exclude='./.git' --exclude='./.direnv' --exclude='./.venv' -cf "$tmp/source.tar" .
    tar -xf "$tmp/source.tar" -C "$tmp/source"
    copier copy --trust -d template_kind={{ template }} "$tmp/source" {{ dest }}

[doc('Render every branch from the current checkout and compile generated Python.')]
smoke-test:
    #!/usr/bin/env bash
    set -euo pipefail
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    source="$tmp/source"
    mkdir -p "$source"
    tar --exclude='./.git' --exclude='./.direnv' --exclude='./.venv' -cf "$tmp/source.tar" .
    tar -xf "$tmp/source.tar" -C "$source"

    for cloud in gcp aws azure; do
        for iac in opentofu terraform; do
            name="infra-$cloud-$iac"
            copier copy --quiet --trust --defaults -d template_kind=infra -d project_name="smoke-$name" -d cloud="$cloud" -d iac_tool="$iac" "$source" "$tmp/$name"
        done
    done

    for adapter in bigquery snowflake databricks duckdb; do
        name="dbt-$adapter"
        copier copy --quiet --trust --defaults -d template_kind=dbt -d project_name="smoke-$name" -d adapter="$adapter" "$source" "$tmp/$name"
    done

    copier copy --quiet --trust --defaults -d template_kind=fastapi -d project_name=smoke-fastapi "$source" "$tmp/fastapi"
    copier copy --quiet --trust --defaults -d template_kind=python-pipeline -d project_name=smoke-python-pipeline "$source" "$tmp/python-pipeline"
    for spark in 3.5 4.2; do
        project_name="smoke-pyspark-${spark//./-}"
        copier copy --quiet --trust --defaults -d template_kind=pyspark -d project_name="$project_name" -d spark_version="$spark" "$source" "$tmp/pyspark-$spark"
    done
    for cli in true false; do
        copier copy --quiet --trust --defaults -d template_kind=python-lib -d project_name="smoke-python-lib-$cli" -d include_cli="$cli" "$source" "$tmp/python-lib-$cli"
    done

    for project in fastapi python-pipeline pyspark-3.5 pyspark-4.2 python-lib-true python-lib-false; do
        python -m compileall -q "$tmp/$project/src" "$tmp/$project/tests"
    done
    echo "All template variants rendered; generated Python compiles."

pre-commit-setup:
    pre-commit install
    pre-commit install --hook-type commit-msg

pre-commit:
    pre-commit run --all-files
