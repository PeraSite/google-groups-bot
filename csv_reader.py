import csv
from pathlib import Path


def extract_emails(csv_path: str | Path) -> list[str]:
    """Read a Google Groups member CSV and return a list of email addresses."""
    csv_path = Path(csv_path)
    emails: list[str] = []

    with csv_path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        _ = next(reader)  # skip "그룹의 회원" title row
        headers = next(reader)  # "이메일 주소", "닉네임", ...
        email_idx = headers.index("이메일 주소")

        for row in reader:
            if len(row) > email_idx and row[email_idx].strip():
                emails.append(row[email_idx].strip())

    return emails


if __name__ == "__main__":
    csv_file = Path(__file__).parent / "downloads" / "didtest2.csv"
    emails = extract_emails(csv_file)
    print(emails)
