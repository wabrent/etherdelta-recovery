"""Запуск BigQuery-запросов с локальными учётными данными Google.

Требуется (один раз, 3 минуты, без карты):
    1. Установить Google Cloud CLI:  https://cloud.google.com/sdk/docs/install
       (winget install Google.CloudSDK  или  инсталлятор с сайта)
    2. Войти:  gcloud auth application-default login   (откроется браузер)
    3. Создать проект (бесплатно):  gcloud projects create <любое-имя>

Запуск:
    python bq_run.py
    python bq_run.py --query queries/cluster.sql

Результат: scanner/results.csv (кандидаты) или stdout для cluster.sql.
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

    print(f"Запуск запроса: {args.query}", flush=True)
    print("Это займёт 30–120 сек и ~200–400 ГБ из бесплатного тира 1 ТБ/мес.\n", flush=True)

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
        print(f"Готово: {n} строк -> {args.out}")
        print("Дальше: python rank.py results.csv")
    else:
        for r in rows:
            print(dict(r))


if __name__ == "__main__":
    main()
