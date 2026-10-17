"""Small dependency-free PDF report renderer for persisted prototype scans."""

from __future__ import annotations

from datetime import datetime, timezone
from textwrap import wrap
from typing import Any


def _pdf_text(value: Any) -> str:
    return str(value or "").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")


def _line_blocks(scan: Any) -> list[str]:
    result = scan.result or {}
    lines = [
        "TRUE LABEL | PRELIMINARY COMPLIANCE REPORT",
        "Prototype decision support only — not an official certificate, notice, or legal determination.",
        "",
        f"Scan ID: {scan.id}    Category: {scan.category}",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"Analysis version: {scan.rule_engine_version or 'prototype-2026-10'}",
        f"Overall status: {result.get('overall_status', 'UNRESOLVED')}",
        "",
        "APPLICABLE CHECKS",
    ]
    for check in result.get("checks", []):
        lines.extend([
            f"{check.get('tag', 'CHECK')}: {check.get('status', 'UNRESOLVED')}",
            f"  Reference: {check.get('legal_reference') or 'Prototype rule reference requires legal review.'}",
            f"  Source: {check.get('source_url') or 'No source URL recorded'}",
            f"  Reason: {check.get('reason') or 'No reasoning recorded.'}",
        ])
        for evidence in check.get("evidence", [])[:3]:
            lines.append(f"  Evidence: image {evidence.get('image_index', '?')} — {evidence.get('text', '')} (confidence {evidence.get('confidence', 'n/a')})")
    lines.extend(["", "EVIDENCE MANIFEST"])
    for evidence in scan.evidence:
        lines.append(f"{evidence.filename} | {evidence.size_bytes} bytes | SHA-256 {evidence.sha256}")
    lines.extend(["", "LIMITATIONS AND REVIEW"])
    lines.extend(result.get("limitations", []))
    lines.extend(result.get("clarification_requests", []))
    return lines


def render_compliance_report(scan: Any) -> tuple[bytes, dict[str, Any]]:
    """Render a searchable A4 PDF without external service or binary dependency."""
    logical_lines: list[str] = []
    for value in _line_blocks(scan):
        logical_lines.extend(wrap(value, width=108, break_long_words=True, break_on_hyphens=False) or [""])
    per_page = 46
    page_groups = [logical_lines[index:index + per_page] for index in range(0, len(logical_lines), per_page)] or [[]]
    objects: list[bytes] = []
    # Catalog and Pages are filled after content/page objects are allocated.
    objects.extend([b"", b""])
    page_object_numbers: list[int] = []
    for page_number, lines in enumerate(page_groups, start=1):
        body = ["BT", "/F1 10 Tf", "50 790 Td", "14 TL"]
        for index, line in enumerate(lines):
            if index == 0:
                body.extend(["0.05 0.2 0.35 rg", f"({_pdf_text(line)}) Tj", "0 g"])
            elif line.startswith("Overall status:"):
                body.extend(["0.55 0.15 0.05 rg", f"T* ({_pdf_text(line)}) Tj", "0 g"])
            else:
                body.append(f"T* ({_pdf_text(line)}) Tj")
        body.extend(["ET", f"BT /F1 8 Tf 50 28 Td (True Label prototype report | page {page_number} of {len(page_groups)}) Tj ET"])
        stream = "\n".join(body).encode("latin-1", "replace")
        content_number = len(objects) + 1
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
        page_number_object = len(objects) + 1
        page_object_numbers.append(page_number_object)
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents {content_number} 0 R >>".encode())
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = ("<< /Type /Pages /Kids [" + " ".join(f"{number} 0 R" for number in page_object_numbers) + f"] /Count {len(page_object_numbers)} >>").encode()
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode())
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode())
    output.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    metadata = {
        "overall_status": (scan.result or {}).get("overall_status", "UNRESOLVED"),
        "check_count": len((scan.result or {}).get("checks", [])),
        "evidence_count": len(scan.evidence),
        "page_count": len(page_groups),
    }
    return bytes(output), metadata
