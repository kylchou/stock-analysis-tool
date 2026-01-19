import csv

from stockanalyzer import report


def test_to_csv_writes_header_and_rows(tmp_path):
    rows = [{"ticker": "AAPL", "score": 80}, {"ticker": "MSFT", "score": 75}]
    out = tmp_path / "out.csv"
    report.to_csv(rows, str(out))

    with out.open(newline="") as f:
        reader = list(csv.DictReader(f))
    assert reader == [{"ticker": "AAPL", "score": "80"}, {"ticker": "MSFT", "score": "75"}]


def test_to_csv_empty_rows_writes_empty_file(tmp_path):
    out = tmp_path / "empty.csv"
    report.to_csv([], str(out))
    assert out.read_text() == ""


def test_to_html_contains_table_and_values(tmp_path):
    rows = [{"ticker": "AAPL", "score": 80}]
    out = tmp_path / "out.html"
    report.to_html(rows, str(out), title="Test Report")

    html = out.read_text()
    assert "<table>" in html
    assert "AAPL" in html
    assert "Test Report" in html


def test_to_html_empty_rows(tmp_path):
    out = tmp_path / "empty.html"
    report.to_html([], str(out), title="Empty")
    assert "No data." in out.read_text()
