# Senior Data Engineer interview playbook

This is a last-day refresher for a collaborative live-coding and system-design
interview in a pricing/underwriting data domain. It is a priority list, not a
promise that every topic will appear.

## What to optimise for in the interview

Show a repeatable engineering loop:

1. Restate the goal, inputs, outputs, constraints, and ambiguous cases.
2. Write a tiny example and one happy-path test before choosing architecture.
3. Keep domain logic pure; place I/O, frameworks, clocks, and environment at edges.
4. Implement the smallest vertical slice that runs.
5. Add edge cases and narrate complexity, failure behaviour, and the next change.

For design questions, use this order:

1. Functional requirements and explicit non-goals.
2. Scale/SLOs: volume, rate, payload, latency, availability, retention, recovery.
3. Data contract and ownership.
4. Write path, storage/model, read/serving path.
5. Event time, retries, duplicates, ordering, late data, replay, and backfills.
6. Quality, security/governance, observability, and operations.
7. Cost, bottlenecks, trade-offs, and an incremental evolution plan.

Do not draw boxes until requirements and scale are clear. Do not claim “exactly
once” without defining the boundary and sink transaction/idempotency mechanism.

## Using these templates live

Ask first:

> I maintain a small Copier starter to avoid spending interview time on packaging
> boilerplate. Are you happy for me to scaffold the minimum project and then build
> and explain the solution from there?

Then use one starter only:

```sh
just new-local python-lib /tmp/interview-domain       # OOP/rules/algorithms
just new-local python-pipeline /tmp/interview-pipeline # small ETL
just new-local fastapi /tmp/interview-api              # HTTP service
just new-local pyspark /tmp/interview-spark             # distributed transforms
```

Good signal: explain every generated layer, delete irrelevant code, write the
domain logic and tests yourself, and keep the git diff small. Bad signal: hide
behind generated code, download a large platform, or spend time repairing setup.
Have a single-file fallback and pre-warm dependencies before the call.

You should be able to write without a template: a function/class and test,
`SparkSession` plus a DataFrame transform, a basic Pydantic model/FastAPI route,
and a SQL query with a join, aggregation, and window function. Memorising Docker,
Nix, packaging, or directory boilerplate is not the assessment.

## Python and domain modelling

Be fluent with:

- `dataclass(frozen=True)` or immutable Pydantic models for value objects.
- `Decimal` for money; never binary `float` for premiums. State the rounding rule.
- timezone-aware datetimes, event time versus processing/ingestion time.
- enums for closed vocabularies and validation at the boundary.
- composition over inheritance; `Protocol` for replaceable ports/adapters.
- pure functions for calculations, dependency injection for I/O and clocks.
- strategy/rule objects only when rules vary independently or need explanations.
- exceptions at boundaries; explicit result/violation values for expected failures.
- iterators/generators for bounded memory, and when materialisation is necessary.
- type hints, small functions, names that express intent, pytest parametrisation.

For an underwriting/rating exercise, separate:

```text
validated policy -> eligibility rules -> risk adjustments -> quoted premium
                         |                      |
                  explainable reasons     Decimal + rounding
```

Make rule precedence explicit. Decide whether to collect every rejection or stop
at the first. Avoid a long `if/elif` chain if new product/rule families are the
extension requirement, but begin with direct functions if the problem is small.

Complexity you should state naturally: dictionary/set lookup is average O(1),
sorting is O(n log n), a one-pass aggregation is O(n) time and O(k) state, and a
generator avoids O(n) materialisation when the algorithm permits it.

## SQL, warehousing, and modelling

Practise writing from memory:

- joins and their row-multiplication risk; verify cardinality before aggregating.
- `GROUP BY`, conditional aggregation, `HAVING`, null semantics and `COALESCE`.
- `row_number()` for latest-per-key with deterministic tie-breakers.
- running totals, `lag`/`lead`, session/gap logic, and top-N per group.
- CTEs for readable stages; query plans and indexes for operational databases.
- anti-joins for missing records and reconciliation.
- an as-of/point-in-time join: feature timestamp must be no later than prediction.

Know the modelling choices:

- grain first: say exactly what one row represents before naming columns.
- facts versus dimensions; surrogate keys; conformed dimensions.
- SCD1 overwrites; SCD2 preserves `valid_from`, `valid_to`, `is_current` history.
- star schemas optimise stable analytics; wide/denormalised products can improve
  usability; 3NF fits transactional consistency.
- Data Vault can help auditable multi-source history but adds modelling/query cost.
- PostgreSQL serves indexed low-latency transactions; Redshift serves columnar,
  distributed analytics. Distribution/sort choices follow joins and predicates.
- NoSQL is not one category: choose DynamoDB from access patterns/partition keys,
  not because data is “big” or JSON.

Performance discussion: scan less, project early, partition/prune, maintain useful
statistics, avoid accidental Cartesian/many-to-many joins, pre-aggregate where
valid, and inspect the plan rather than guessing.

## Spark batch processing

Be able to explain and code:

- immutable DataFrame transformations versus actions and lazy evaluation.
- narrow versus wide transformations and why shuffles dominate cost.
- explicit schemas, null handling, corrupt-record/quarantine strategy.
- deterministic latest-per-key with `Window.partitionBy(...).orderBy(...)` and
  `row_number`; pre-sorting then `dropDuplicates` does not select reliably.
- join types, broadcast join threshold/risks, partitioning, bucketing, and skew.
- built-in expressions before Python UDFs; Arrow/pandas UDFs only when justified.
- `repartition` causes shuffle; `coalesce` usually reduces partitions cheaply.
- cache only reused expensive intermediates and unpersist them.
- AQE, predicate/column pushdown, Parquet/Delta/Iceberg statistics and pruning.
- small-file problems, sensible output partitions, and compaction.
- `df.explain("formatted")`, Spark UI stages/tasks/shuffle/spill/skew diagnosis.

Testing hierarchy:

- unit-test pure DataFrame-to-DataFrame transforms on `local[2]` with tiny rows.
- compare rows explicitly and avoid relying on unspecified ordering.
- integration-test file/table contracts separately from business rules.
- run representative-volume/performance tests outside unit tests.

## Kafka, Structured Streaming, and Flink

Start with semantics, not product names:

- A partition is the unit of Kafka ordering and consumer parallelism.
- Key choice controls ordering, locality, skew, and maximum useful consumers.
- Consumer groups divide partitions; offsets represent progress and enable replay.
- At-least-once delivery means downstream writes must be idempotent/deduplicated.
- Kafka producer idempotence and transactions help only within their defined
  boundary; an external database still needs a transaction/upsert/idempotency key.
- Event time describes the business event; processing time describes observation.
- A watermark is a completeness/state-retention trade-off, not “drop everything
  older than now minus X” in all engines.
- Windows: tumbling, sliding/hopping, and session. Define allowed lateness and how
  corrections/retractions appear to consumers.
- Checkpoint operator state and source offsets durably; test restart/recovery.
- Poison records need schema validation, metrics, and quarantine/DLQ with replay.
- Schema evolution needs compatibility policy and a registry/contract process.
- Backpressure is a symptom: observe input rate, processing rate, lag, state size,
  checkpoint time, sink latency, and hot partitions.

Spark Structured Streaming is a good fit when batch/Spark integration and
micro-batch latency are acceptable. Flink is strong for low-latency, stateful
event-time processing and rich streaming semantics. Kafka is the durable log, not
the transformation engine. Kinesis may reduce AWS operations; MSK gives Kafka
ecosystem/API control. State the team/operational trade-off.

## AWS lakehouse/data platform

A defensible default architecture:

```text
sources -> Kafka/MSK or Kinesis -> raw S3 (immutable)
                                      |
                         Glue/EMR/Databricks/Flink
                                      |
                    Iceberg/Delta curated S3 tables
                            |                 |
                       Athena/Redshift    feature/API consumers
```

Know why each boundary exists:

- S3 is durable, cheap object storage; design prefixes/partitions and lifecycle.
- Glue Data Catalog provides shared metadata; Lake Formation centralises fine-
  grained permissions/governance but adds operational/process complexity.
- EMR offers control; Glue reduces operations; Databricks offers an integrated
  lakehouse/ML experience at platform/vendor cost.
- Athena is serverless scan-based SQL; Redshift is a managed warehouse for
  predictable, repeated analytical workloads and concurrency.
- Iceberg/Delta add atomic table commits, schema/partition evolution, snapshots,
  time travel, compaction/optimisation, and safer concurrent writers.
- Separate storage from compute where useful; isolate workloads and control spend.

AWS security points: least-privilege IAM roles, workload identity rather than
long-lived keys, KMS encryption, private networking/endpoints where appropriate,
Secrets Manager, CloudTrail/audit logs, account/environment separation, and PII
classification/masking/retention. Insurance data needs purpose limitation and
traceable access, not only encryption.

Reliability points: multi-AZ managed services where needed, immutable raw replay,
cross-region requirements only if the RTO/RPO justifies them, tested recovery,
DLQs/quarantine, idempotent writes, and runbooks/ownership.

## Data quality, contracts, and governance

Cover three layers:

- Schema: types, required fields, compatibility, allowed evolution.
- Semantics: uniqueness, referential integrity, ranges, valid categories,
  cross-field/rule invariants, and point-in-time correctness.
- Operations: freshness, volume, distribution drift, reconciliation, lineage,
  ownership, alert routing, and incident response.

Rejecting all data can protect correctness but damage availability; silently
accepting bad data damages trust. Explain the policy: fail critical contract
breaks, quarantine isolated bad records, publish quality metrics, and prevent
uncertified outputs from reaching consumers.

Use data-product language: owner, consumers, contract, SLO, documentation,
lineage, discoverability, access policy, deprecation/versioning, and feedback.

## Feature engineering and MLOps

Critical concepts for pricing/underwriting:

- the same feature definition must serve training and inference (avoid skew).
- point-in-time correct joins prevent future leakage.
- distinguish event time, feature computation time, and observation/prediction time.
- offline store handles training/backfills; online store handles low-latency reads.
- materialise features with entity key, event timestamp, definition version, and
  provenance; make backfills reproducible.
- monitor freshness, null rate, distribution drift, training-serving skew, and
  model/business outcomes.
- version data/code/config/model together enough to reproduce a quote/decision.
- XGBoost/LightGBM/scikit-learn knowledge is useful, but the data engineer's key
  responsibility is reliable, leakage-free, governed features and serving paths.

## APIs and serving data products

For a small FastAPI exercise:

- validate request/response models at the edge and return intentional status codes.
- keep handlers thin; inject repositories/services; do not hide global mutable state.
- distinguish liveness from readiness and close clients/pools in lifespan handling.
- add timeouts, bounded retries with jitter only for transient/idempotent operations,
  pagination, request IDs, structured logs, metrics, and tracing as requirements grow.
- authenticate, authorise per resource/action, validate limits, avoid secret/PII logs.
- POST retry safety needs an idempotency key or natural request/decision key.
- document consistency and freshness: is the response transactional, cached, or an
  asynchronously refreshed analytical projection?

## DevOps, CI/CD, and infrastructure as code

Explain a safe delivery path:

```text
format/lint -> unit tests -> contract/integration tests -> build once
-> vulnerability/SBOM/signature -> deploy dev -> smoke/data checks
-> progressive prod rollout -> observe -> rollback/roll forward
```

Best practices:

- lock dependencies and pin CI actions/images to immutable digests/commit SHAs;
  automate reviewed upgrades rather than using floating latest tags.
- short-lived OIDC workload identity; no static cloud keys in CI.
- least-privilege job permissions, protected environments, approval for production.
- immutable artefact promoted between environments, provenance/SBOM, secret scanning.
- Terraform/OpenTofu state remote, encrypted, access-controlled, locked, backed up;
  separate state/blast radius per environment/domain.
- `plan` in pull requests, policy/security scans, reviewed plan, apply from CI; avoid
  console drift and never edit state casually.
- modules encapsulate stable boundaries; do not build a maze of premature modules.
- database/data migrations are backward-compatible and ordered with application jobs.

## Insurance-specific system-design prompts

### Near-real-time pricing features

Clarify quote latency and feature freshness separately. Partition events by stable
entity key, validate contracts, compute event-time stateful features, and publish a
versioned online view. Persist raw events for replay and an offline point-in-time
view for training. Define behaviour when a feature is late/unavailable: safe default,
last-known value, or fail closed. Make every quote reproducible from feature/model/
rule versions and record explainable decisions.

### New external source ingestion

Land immutable raw payload plus ingestion metadata, validate contract, quarantine
bad records, deduplicate with source key/sequence, standardise into a canonical
model, and publish a versioned data product. Discuss rate limits, snapshots versus
CDC, deletions, consent/licensing, PII, backfill, reconciliation, and ownership.

### Nightly batch missing its SLA

First locate time in queue/read/shuffle/skew/write/commit, compare input and plan
changes, and use Spark UI/metrics. Immediate mitigations might increase parallelism,
fix a hot join, broadcast a verified-small dimension, prune scans, or compact files.
Long-term fixes might make processing incremental, change partition/layout, split
critical from non-critical outputs, or renegotiate an evidence-based SLA. Preserve
correctness and make reruns idempotent.

### Self-service domain data products

Provide a paved road: contract/schema registration, ingestion SDK/template,
standard storage/table patterns, CI quality/security gates, catalogue/lineage,
observability/SLO dashboards, access-policy automation, and documented ownership.
Central platform owns reusable capabilities; domains own semantics and operations.
Avoid both a central-ticket bottleneck and ungoverned “self-service”.

## Questions to ask the interviewers

- What is the dominant boundary today between pricing data science and engineering?
- Which workloads are truly near-real-time, and what latency/freshness SLO drives them?
- How are feature definitions shared between training and online/batch inference?
- Which parts of the platform are team-owned versus centrally owned?
- What failure or scaling incident most influenced the current architecture?
- How do data-product teams own quality, governance, and on-call responsibilities?

## Final 24-hour drill

1. Implement one underwriting/rating domain exercise in plain Python with Decimal,
   explicit rules, extension points, and tests. Time-box: 45 minutes.
2. Implement Spark latest-per-key, join + aggregation, null/bad-row handling, and
   explain the physical plan. Time-box: 35 minutes.
3. Write two SQL problems: latest-per-key/SCD2 and point-in-time feature join.
   Time-box: 25 minutes.
4. Design near-real-time pricing features aloud using the seven-step design order.
   Include numbers, failures, replay, PII, SLOs, and cost. Time-box: 35 minutes.
5. Generate each likely starter once, run its tests, then stop changing tooling.
6. Before the call: verify screen sharing, editor font, terminal, Java/Python cache,
   network, and a blank single-file fallback. Sleep is higher value than one more tool.
