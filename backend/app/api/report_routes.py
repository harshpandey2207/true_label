from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.api.security import get_optional_user
from backend.app.db.database import get_db
from backend.app.db.models import ComplianceReportRecord, ScanRecord, UserAccount
from backend.app.services.report_generator import render_compliance_report

router = APIRouter(tags=["Reports"])


def _can_access(scan: ScanRecord, user: UserAccount | None) -> bool:
    return scan.user_id is None or (user is not None and (scan.user_id == user.id or user.role in {"admin", "inspector"}))


def _report_payload(report: ComplianceReportRecord) -> dict:
    return {
        "id": report.id,
        "report_code": report.report_code,
        "scan_id": report.scan_id,
        "created_at": report.created_at.isoformat() + "Z" if report.created_at else None,
        "summary": report.content,
        "download_url": f"/reports/{report.id}/download",
    }


@router.post("/scans/{scan_id}", status_code=201)
def create_report(scan_id: int, user: UserAccount | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    scan = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if scan is None or not _can_access(scan, user):
        raise HTTPException(status_code=404, detail="Scan not found.")
    pdf, summary = render_compliance_report(scan)
    report = ComplianceReportRecord(scan_id=scan.id, report_code=f"TLR-{scan.id}-{len(pdf):x}", content=summary, pdf_payload=pdf)
    db.add(report)
    db.commit()
    db.refresh(report)
    return {"id": report.id, "report_code": report.report_code, "scan_id": report.scan_id, **summary, "download_url": f"/reports/{report.id}/download"}


@router.get("")
def list_reports(user: UserAccount | None = Depends(get_optional_user), db: Session = Depends(get_db), limit: int = 100):
    """List persisted reports visible to the caller without exposing PDFs."""
    rows = db.query(ComplianceReportRecord).order_by(ComplianceReportRecord.created_at.desc()).limit(min(max(limit, 1), 200)).all()
    visible = []
    for report in rows:
        scan = db.query(ScanRecord).filter(ScanRecord.id == report.scan_id).first()
        if scan is not None and _can_access(scan, user):
            visible.append(_report_payload(report))
    return {"items": visible}


@router.get("/{report_id}/download")
def download_report(report_id: int, user: UserAccount | None = Depends(get_optional_user), db: Session = Depends(get_db)):
    report = db.query(ComplianceReportRecord).filter(ComplianceReportRecord.id == report_id).first()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found.")
    scan = db.query(ScanRecord).filter(ScanRecord.id == report.scan_id).first()
    if scan is None or not _can_access(scan, user):
        raise HTTPException(status_code=404, detail="Report not found.")
    return Response(report.pdf_payload, media_type="application/pdf", headers={"Content-Disposition": f'attachment; filename="{report.report_code}.pdf"'})
