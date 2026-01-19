"""Write analysis results out to CSV or a simple standalone HTML report."""
from __future__ import annotations

import csv
from pathlib import Path


def to_csv(rows: list[dict], path: str) -> None:
    path_obj = Path(path)
    if not rows:
        path_obj.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path_obj.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def to_html(rows: list[dict], path: str, title: str = "Stock Analysis Report") -> None:
    path_obj = Path(path)
    if not rows:
        path_obj.write_text(f"<h1>{title}</h1><p>No data.</p>", encoding="utf-8")
        return

    headers = list(rows[0].keys())
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{row.get(h, '')}</td>" for h in headers) + "</tr>"
        for row in rows
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{title}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: right; }}
    th {{ background: #222; color: #fff; }}
    td:first-child, th:first-child {{ text-align: left; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <table>
    <thead><tr>{header_html}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</body>
</html>
"""
    path_obj.write_text(html, encoding="utf-8")
