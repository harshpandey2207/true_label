from sqlalchemy.orm import Session
from backend.app.db.models import ScanHistory

def log_scan_result(db: Session, category_id: int, is_compliant: bool, missing_tags: list, confidence_score: float):
    """
    Logs the result of a metrology scan to the database for regulatory repository history.
    """
    db_scan = ScanHistory(
        category_id=category_id,
        is_compliant=is_compliant,
        missing_tags=",".join(missing_tags) if missing_tags else None,
        confidence_score=confidence_score
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

