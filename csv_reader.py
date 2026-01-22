import csv
import logging
from pathlib import Path


def extract_emails(csv_path: str | Path) -> list[str]:
    """Read a Google Groups member CSV and return a list of email addresses."""
    logging.debug(f"🚀 [extract_emails] 시작 - csv_path: {csv_path}")
    
    csv_path = Path(csv_path)
    logging.debug(f"📂 CSV 파일 경로 변환 완료: {csv_path.absolute()}")
    
    if not csv_path.exists():
        logging.error(f"❌ CSV 파일이 존재하지 않습니다: {csv_path}")
        raise FileNotFoundError(f"CSV 파일을 찾을 수 없습니다: {csv_path}")
    
    logging.debug(f"✅ CSV 파일 존재 확인 완료 (크기: {csv_path.stat().st_size} bytes)")
    
    emails: list[str] = []

    logging.debug(f"📖 CSV 파일 열기 중...")
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        
        logging.debug(f"📝 타이틀 행 건너뛰기...")
        title_row = next(reader)  # skip "그룹의 회원" title row
        logging.debug(f"📝 타이틀 행: {title_row}")
        
        logging.debug(f"📋 헤더 행 읽기...")
        headers = next(reader)  # "이메일 주소", "닉네임", ...
        logging.debug(f"📋 헤더: {headers}")
        
        logging.debug(f"🔍 '이메일 주소' 컬럼 인덱스 찾기...")
        email_idx = headers.index("이메일 주소")
        logging.debug(f"✅ '이메일 주소' 컬럼 인덱스: {email_idx}")

        logging.debug(f"📧 이메일 데이터 추출 시작...")
        row_count = 0
        for row in reader:
            row_count += 1
            if len(row) > email_idx and row[email_idx].strip():
                email = row[email_idx].strip()
                emails.append(email)
                if row_count % 10 == 0:  # 10개마다 로그
                    logging.debug(f"⏳ {row_count}번째 행 처리 중... (추출된 이메일: {len(emails)}개)")
        
        logging.debug(f"✅ CSV 처리 완료 - 총 {row_count}개 행, {len(emails)}개 이메일 추출")

    logging.debug(f"✅ [extract_emails] 완료 - 추출된 이메일 수: {len(emails)}")
    return emails


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    csv_file = Path(__file__).parent / "downloads" / "didtest2.csv"
    emails = extract_emails(csv_file)
    logging.info(f"추출된 이메일: {emails}")
