"""Run BigQuery queries with local Google credentials.

Required (once, 3 minutes, no credit card):
    1. Install Google Cloud CLI:  https://cloud.google.com/sdk/docs/install
       (winget install Google.CloudSDK  or  the installer from the site)
    2. Log in:  gcloud auth application-default login   (opens a browser)
    3. Create a project (free):  gcloud projects create <any-name>

Run:
    python bq_run.py
    python bq_run.py --query queries/cluster.sql

Result: scanner/results.csv (candidates) or stdout for cluster.sql.
"""

import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent

DEFAULT_QUERY = HERE / "queries" / "stuck_contracts.sql"
OUT_CSV = HERE / "results.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default=str(DEFAULT_QUERY))
    parser.add_argument("--project", default=None, help="GCP project id")
    parser.add_argument("--out", default=str(OUT_CSV))
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project) if args.project else bigquery.Client()
    sql = Path(args.query).read_text(encoding="utf-8")

    print(f"Running query: {args.query}", flush=True)
    print("This will take 30–120 sec and ~200–400 GB from the free 1 TB/month tier.\n", flush=True)

    job = client.query(sql)
    rows = job.result()

    if "candidates" in sql.lower() or job._query_results.schema:
        schema = [f.name for f in job._query_results.schema]
        with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(schema)
            n = 0
            for r in rows:
                w.writerow([r[f] for f in schema])
                n += 1
        print(f"Done: {n} rows -> {args.out}")
        print("Next: python rank.py results.csv")
    else:
        for r in rows:
            print(dict(r))


if __name__ == "__main__":
    main()
