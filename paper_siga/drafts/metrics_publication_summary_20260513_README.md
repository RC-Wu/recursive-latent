# Publication Metrics Summary 20260513

This draft is a review layer over the offline mesh-metrics dry-run manifest. It
aggregates existing CSV metric tables into compact numeric summaries for paper
table triage. It does not modify active LaTeX tables.

## Commands

```bash
python3 scripts/metrics_mesh_pipeline_validate_20260513.py drafts/metrics_mesh_pipeline_dryrun_20260513.json
python3 scripts/metrics_publication_summary_20260513.py --manifest drafts/metrics_mesh_pipeline_dryrun_20260513.json --output-json drafts/metrics_publication_summary_20260513.json --output-csv drafts/metrics_publication_summary_20260513.csv
python3 scripts/metrics_publication_summary_20260513_test.py
```

## Outputs

- `drafts/metrics_publication_summary_20260513.json`: full manifest with source
  metadata, skipped-table reasons, and all summary rows.
- `drafts/metrics_publication_summary_20260513.csv`: flat table for spreadsheet
  review. Each row reports one numeric metric column, optionally grouped by an
  available column such as `method`, `variant`, `family`, `case`, `block`,
  `status`, or `label`.

Summary rows include `n`, `mean`, `median`, `min`, and `max`.

## Safe Use

Use this draft to identify candidate values for publication tables, then trace
each candidate row back through `source_table`, `group_by`, `group_value`, and
`column` before editing any active paper table. These are deterministic
aggregations over existing CSVs.
