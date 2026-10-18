"""Evidence-backed compliance report renderer.

The report is intentionally implemented with the Python standard library and
Pillow only. That keeps the local demo and the Render service in sync even
when optional PDF packages are unavailable. The structure follows the
officer-style reference report: report details, executive conclusion, AI
summary, detailed findings, enforcement context, image evidence, and an
important review note.
"""

from __future__ import annotations

import io
import textwrap
from datetime import datetime, timezone
from typing import Any

from PIL import Image, ImageOps


PAGE_WIDTH = 595.276
PAGE_HEIGHT = 841.89
LEFT = 48.0
RIGHT = 48.0
TOP = 790.0
BOTTOM = 58.0
CONTENT_WIDTH = PAGE_WIDTH - LEFT - RIGHT


def _safe_text(value: Any) -> str:
    """Keep generated PDFs searchable and safe for the built-in Helvetica font."""
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }
    text = str(value if value is not None else "")
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")


def _escape(value: Any) -> str:
    return _safe_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrapped(value: Any, width: int = 92) -> list[str]:
    lines: list[str] = []
    for raw in _safe_text(value).splitlines() or [""]:
        lines.extend(textwrap.wrap(raw, width=width, break_long_words=True, break_on_hyphens=False) or [""])
    return lines


def _status_label(status: Any) -> str:
    return {
        "PASS": "COMPLIANT",
        "CONFIRMED_VIOLATION": "NON-COMPLIANT",
        "UNRESOLVED": "UNRESOLVED - REVIEW REQUIRED",
        "NOT_APPLICABLE": "NOT APPLICABLE",
    }.get(str(status or "").upper(), str(status or "UNRESOLVED").replace("_", " "))


def _result(scan: Any) -> dict[str, Any]:
    value = getattr(scan, "result", None)
    return value if isinstance(value, dict) else {}


def _declarations(scan: Any) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for item in _result(scan).get("results", []):
        if not isinstance(item, dict):
            continue
        analysis = item.get("analysis") or {}
        for declaration in analysis.get("declarations", []) or []:
            if isinstance(declaration, dict):
                values.append(declaration)
    return values


def _product_name(scan: Any) -> str:
    for item in _declarations(scan):
        if str(item.get("tag", "")).upper() in {"COMMODITY_NAME", "PRODUCT_NAME"} and item.get("text"):
            return _safe_text(item["text"])
    return "Not identified from supplied evidence"


def _ocr_engines(scan: Any) -> str:
    names = sorted(
        {
            str((item.get("analysis") or {}).get("ocr_engine", "")).strip()
            for item in _result(scan).get("results", [])
            if isinstance(item, dict) and str((item.get("analysis") or {}).get("ocr_engine", "")).strip()
        }
    )
    return ", ".join(names) if names else "unavailable"


def _evidence_score(checks: list[dict[str, Any]]) -> str:
    applicable = [item for item in checks if item.get("status") != "NOT_APPLICABLE"]
    if not applicable:
        return "Not scored"
    passed = sum(item.get("status") == "PASS" for item in applicable)
    return f"{round((passed / len(applicable)) * 100):d}/100"


def _jpeg_payload(payload: bytes) -> tuple[bytes, int, int] | None:
    """Convert evidence to a bounded JPEG suitable for a PDF image stream."""
    try:
        with Image.open(io.BytesIO(payload)) as source:
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1500, 1100), Image.Resampling.LANCZOS)
            output = io.BytesIO()
            image.save(output, format="JPEG", quality=84, optimize=True)
            return output.getvalue(), image.width, image.height
    except Exception:
        return None


class _Page:
    def __init__(self) -> None:
        self.y = TOP
        self.operations: list[str] = []
        self.images: dict[str, tuple[bytes, int, int]] = {}

    def text(self, x: float, y: float, value: Any, *, font: str = "F1", size: float = 9.5, color: tuple[float, float, float] = (0, 0, 0)) -> None:
        r, g, b = color
        self.operations.append(
            f"BT /{font} {size:g} Tf {r:g} {g:g} {b:g} rg {x:g} {y:g} Td ({_escape(value)}) Tj ET"
        )

    def rule(self, x: float, y: float, width: float, *, color: tuple[float, float, float] = (0.62, 0.62, 0.62), line_width: float = 0.6) -> None:
        r, g, b = color
        self.operations.append(f"{r:g} {g:g} {b:g} RG {line_width:g} w {x:g} {y:g} m {x + width:g} {y:g} l S")

    def rect(self, x: float, y: float, width: float, height: float, *, fill: tuple[float, float, float] | None = None, stroke: tuple[float, float, float] | None = None, line_width: float = 0.6) -> None:
        if fill is not None:
            r, g, b = fill
            self.operations.append(f"{r:g} {g:g} {b:g} rg {x:g} {y:g} {width:g} {height:g} re f")
        if stroke is not None:
            r, g, b = stroke
            self.operations.append(f"{r:g} {g:g} {b:g} RG {line_width:g} w {x:g} {y:g} {width:g} {height:g} re S")

    def image(self, payload: bytes, x: float, y: float, width: float, height: float) -> bool:
        converted = _jpeg_payload(payload)
        if converted is None:
            return False
        image_bytes, image_width, image_height = converted
        name = f"Im{len(self.images) + 1}"
        self.images[name] = (image_bytes, image_width, image_height)
        self.operations.append(f"q {width:g} 0 0 {height:g} {x:g} {y:g} cm /{name} Do Q")
        return True


class _Composer:
    def __init__(self) -> None:
        self.pages: list[_Page] = [_Page()]
        self.current = self.pages[0]

    def new_page(self) -> None:
        self.current = _Page()
        self.pages.append(self.current)

    def ensure(self, height: float) -> None:
        if self.current.y - height < BOTTOM:
            self.new_page()

    def lines(self, values: list[str], *, font: str = "F1", size: float = 9.5, leading: float = 13.0, color: tuple[float, float, float] = (0, 0, 0), x: float = LEFT) -> None:
        for value in values:
            self.ensure(leading)
            self.current.text(x, self.current.y, value, font=font, size=size, color=color)
            self.current.y -= leading

    def paragraph(self, value: Any, *, font: str = "F1", size: float = 9.5, leading: float = 13.0, width: int = 92, color: tuple[float, float, float] = (0, 0, 0), x: float = LEFT) -> None:
        self.lines(_wrapped(value, width), font=font, size=size, leading=leading, color=color, x=x)

    def section(self, number: int, title: str) -> None:
        self.ensure(34)
        self.current.y -= 5
        self.current.text(LEFT, self.current.y, f"{number}. {title.upper()}", font="F2", size=13.5, color=(0.03, 0.03, 0.03))
        self.current.y -= 23

    def key_value(self, label: str, value: Any, *, width: int = 92) -> None:
        self.paragraph(f"{label}: {_safe_text(value)}", size=9.4, leading=12.5, width=width)

    def details_table(self, rows: list[tuple[str, str]]) -> None:
        label_width = 138.0
        value_width = CONTENT_WIDTH - label_width
        for label, value in rows:
            label_lines = _wrapped(label, 20)
            value_lines = _wrapped(value, 62)
            row_lines = max(len(label_lines), len(value_lines), 1)
            row_height = max(22.0, row_lines * 13.0 + 9.0)
            self.ensure(row_height + 3)
            top = self.current.y
            bottom = top - row_height
            self.current.rect(LEFT, bottom, label_width, row_height, fill=(0.83, 0.83, 0.83), stroke=(0.42, 0.42, 0.42))
            self.current.rect(LEFT + label_width, bottom, value_width, row_height, stroke=(0.42, 0.42, 0.42))
            for index, line in enumerate(label_lines):
                self.current.text(LEFT + 7, top - 15 - index * 13, line, font="F2", size=9.2)
            for index, line in enumerate(value_lines):
                self.current.text(LEFT + label_width + 7, top - 15 - index * 13, line, size=9.2)
            self.current.y = bottom

    def status_box(self, status: str) -> None:
        self.ensure(36)
        palette = {
            "COMPLIANT": ((0.91, 0.97, 0.92), (0.10, 0.42, 0.20)),
            "NON-COMPLIANT": ((0.99, 0.92, 0.91), (0.62, 0.12, 0.08)),
            "UNRESOLVED - REVIEW REQUIRED": ((1.0, 0.96, 0.86), (0.60, 0.37, 0.02)),
            "NOT APPLICABLE": ((0.93, 0.95, 0.97), (0.20, 0.30, 0.45)),
        }.get(status, ((0.95, 0.95, 0.95), (0.18, 0.18, 0.18)))
        top = self.current.y
        self.current.rect(LEFT, top - 30, CONTENT_WIDTH, 30, fill=palette[0], stroke=palette[1], line_width=1.0)
        self.current.text(LEFT + 10, top - 19, status, font="F2", size=10.5, color=palette[1])
        self.current.y = top - 38

    def finding(self, index: int, check: dict[str, Any]) -> None:
        tag = str(check.get("tag", "CHECK")).replace("_", " ").title()
        status = _status_label(check.get("status"))
        reference = check.get("legal_reference") or "Prototype rule reference requires legal review."
        self.ensure(70)
        self.current.text(LEFT, self.current.y, f"{index}. {tag} - {status}", font="F4", size=10.5)
        self.current.y -= 17
        self.key_value("Status", status)
        self.key_value("Act", "See the recorded legal reference; verify the current text before action.")
        self.key_value("Section", check.get("section_reference") or "Not recorded in the prototype rule metadata.")
        self.key_value("Rules / regulations", reference)
        self.key_value("Rule", f"Stored requirement tag: {tag}")
        self.key_value("Clause", check.get("clause_reference") or "Not recorded; legal review required.")
        self.key_value("Rule version", check.get("rule_version") or "prototype-2026-10")
        self.key_value("Evidence requirement", check.get("evidence_requirement") or "Readable declaration text or manual confirmation")
        self.key_value("Finding", check.get("reason") or "No additional reasoning was recorded.")
        evidence = check.get("evidence") or []
        if evidence:
            excerpts = [f"{item.get('text', '')} (confidence {item.get('confidence', 'n/a')})" for item in evidence[:2]]
            self.key_value("Observed evidence", "; ".join(excerpts))
        elif check.get("status") == "UNRESOLVED":
            self.key_value("Review action", "Upload a clearer close-up of this declaration or confirm it manually. It is not a confirmed absence.")
        elif check.get("status") == "CONFIRMED_VIOLATION":
            self.key_value("Review action", "Confirm the physical package and current applicable provision before enforcement action.")
        self.current.y -= 5

    def evidence_record(self, evidence_rows: list[Any]) -> None:
        # Keep the section heading with the first evidence item. This mirrors
        # the reference report and avoids a stranded heading at a page bottom.
        if evidence_rows and self.current.y < 450:
            self.new_page()
        elif not evidence_rows and self.current.y < 360:
            self.new_page()
        self.section(6, "Image evidence record")
        self.paragraph("EVIDENCE MANIFEST", font="F2", size=9.5, leading=13)
        if not evidence_rows:
            self.paragraph("No image payload is attached to this report.", color=(0.35, 0.35, 0.35))
            return
        for index, evidence in enumerate(evidence_rows, start=1):
            filename = getattr(evidence, "filename", None) or f"image-{index}.jpg"
            payload = getattr(evidence, "payload", b"") or b""
            converted = _jpeg_payload(payload)
            # Keep an image caption and its image together. A page break
            # before the caption is clearer than a caption stranded at the
            # bottom of the preceding page.
            self.ensure(360 if converted is not None else 74)
            self.current.text(LEFT, self.current.y, f"{index}. {_safe_text(filename)}", size=9.5)
            self.current.y -= 18
            self.current.text(LEFT, self.current.y, f"Evidence Image {index}", font="F4", size=10)
            self.current.y -= 13
            if converted is None:
                self.paragraph("Image payload could not be rendered; the stored evidence hash remains available below.", color=(0.45, 0.12, 0.08))
            else:
                _, image_width, image_height = converted
                max_width = CONTENT_WIDTH - 28
                max_height = 300.0
                scale = min(max_width / image_width, max_height / image_height)
                draw_width = image_width * scale
                draw_height = image_height * scale
                self.ensure(draw_height + 28)
                self.current.rect(LEFT + 14, self.current.y - draw_height - 8, draw_width, draw_height, stroke=(0.60, 0.60, 0.60))
                if self.current.image(payload, LEFT + 14, self.current.y - draw_height - 8, draw_width, draw_height):
                    self.current.y -= draw_height + 16
            self.key_value("SHA-256", getattr(evidence, "sha256", "not recorded"), width=92)
            self.key_value("Stored size", f"{getattr(evidence, 'size_bytes', 0)} bytes")
            self.current.y -= 5

    def finish(self) -> None:
        total = len(self.pages)
        for index, page in enumerate(self.pages, start=1):
            page.rule(LEFT, 34, CONTENT_WIDTH, color=(0.72, 0.72, 0.72))
            page.text(LEFT, 21, "True Label - automated packaging-compliance screening", size=7.5, color=(0.35, 0.35, 0.35))
            page.text(PAGE_WIDTH - 125, 21, f"Page {index} of {total}", size=7.5, color=(0.35, 0.35, 0.35))


class _PdfDocument:
    def __init__(self, pages: list[_Page]) -> None:
        self.pages = pages
        self.objects: list[bytes] = [b"", b""]
        self.objects.extend(
            [
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique >>",
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-BoldOblique >>",
            ]
        )

    def build(self) -> bytes:
        page_numbers: list[int] = []
        for page in self.pages:
            image_numbers: dict[str, int] = {}
            for name, (payload, width, height) in page.images.items():
                image_number = len(self.objects) + 1
                image_numbers[name] = image_number
                self.objects.append(
                    f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(payload)} >>\nstream\n".encode("latin-1")
                    + payload
                    + b"\nendstream"
                )
            stream = "\n".join(page.operations).encode("latin-1", "replace")
            content_number = len(self.objects) + 1
            self.objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
            xobjects = ""
            if image_numbers:
                xobjects = " /XObject << " + " ".join(f"/{name} {number} 0 R" for name, number in image_numbers.items()) + " >>"
            page_number = len(self.objects) + 1
            page_numbers.append(page_number)
            self.objects.append(
                (
                    "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.276 841.89] "
                    "/Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >>"
                    + xobjects
                    + f" >> /Contents {content_number} 0 R >>"
                ).encode("latin-1")
            )
        self.objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
        self.objects[1] = (
            "<< /Type /Pages /Kids [" + " ".join(f"{number} 0 R" for number in page_numbers) + f"] /Count {len(page_numbers)} >>"
        ).encode("latin-1")
        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for number, value in enumerate(self.objects, start=1):
            offsets.append(len(output))
            output.extend(f"{number} 0 obj\n".encode("ascii"))
            output.extend(value)
            output.extend(b"\nendobj\n")
        xref = len(output)
        output.extend(f"xref\n0 {len(self.objects) + 1}\n0000000000 65535 f \n".encode("ascii"))
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        output.extend(
            f"trailer\n<< /Size {len(self.objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii")
        )
        return bytes(output)


def _first_page_header(composer: _Composer) -> None:
    page = composer.current
    page.text(PAGE_WIDTH / 2 - 34, page.y, "TrueLabel", font="F2", size=19)
    page.y -= 31
    page.text(PAGE_WIDTH / 2 - 190, page.y, "OFFICIAL PRODUCT COMPLIANCE INSPECTION REPORT", font="F2", size=13)
    page.y -= 18
    page.text(PAGE_WIDTH / 2 - 92, page.y, "PRELIMINARY COMPLIANCE REPORT", font="F4", size=9.5, color=(0.20, 0.20, 0.20))
    page.y -= 16
    page.text(PAGE_WIDTH / 2 - 136, page.y, "Prepared by True Label for inspection and review", size=9.5, color=(0.20, 0.20, 0.20))
    page.y -= 25
    page.rule(LEFT, page.y, CONTENT_WIDTH, color=(0.35, 0.35, 0.35), line_width=1.0)
    page.y -= 18


def render_compliance_report(scan: Any) -> tuple[bytes, dict[str, Any]]:
    """Render an officer-style A4 report from one persisted scan."""
    result = _result(scan)
    checks = [item for item in result.get("checks", []) if isinstance(item, dict)]
    overall = str(result.get("overall_status", "UNRESOLVED"))
    status = _status_label(overall)
    evidence_rows = list(getattr(scan, "evidence", []) or [])
    composer = _Composer()
    _first_page_header(composer)

    composer.section(1, "Report details")
    created_at = getattr(scan, "created_at", None)
    inspection_date = created_at.strftime("%d %B %Y, %I:%M %p") if created_at else datetime.now(timezone.utc).strftime("%d %B %Y, %I:%M %p")
    composer.details_table(
        [
            ("Product", _product_name(scan)),
            ("Product category", getattr(scan, "category", "Not specified")),
            ("Scan ID", str(getattr(scan, "id", "Not recorded"))),
            ("Report type", "Automated screening - officer / manufacturer review"),
            ("Images inspected", f"{len(evidence_rows)} / {len(evidence_rows)}"),
            ("Inspection date", inspection_date),
            ("Evidence score", _evidence_score(checks)),
            ("Overall status", status),
        ]
    )
    composer.current.y -= 15

    composer.section(2, "Executive conclusion")
    confirmed = sum(item.get("status") == "CONFIRMED_VIOLATION" for item in checks)
    unresolved = sum(item.get("status") == "UNRESOLVED" for item in checks)
    if confirmed:
        conclusion = f"{confirmed} evidence-backed non-compliant parameter(s) were detected. Confirm the physical package and current legal provision before enforcement action."
    elif unresolved:
        conclusion = f"{unresolved} parameter(s) could not be verified from the supplied evidence. They are unresolved, not confirmed missing declarations."
    else:
        conclusion = "The configured checks did not identify an evidence-backed violation in the images supplied. This does not establish legal compliance."
    composer.paragraph(conclusion, size=10, leading=14)
    composer.status_box(status)

    composer.section(3, "AI product intelligence summary")
    composer.key_value("AI category assessment", getattr(scan, "category", "Not specified"))
    composer.key_value("OCR engine(s)", _ocr_engines(scan))
    attention = [
        f"{str(item.get('tag', 'CHECK')).replace('_', ' ').title()}: {item.get('reason', '')}"
        for item in checks
        if item.get("status") in {"CONFIRMED_VIOLATION", "UNRESOLVED"}
    ]
    if attention:
        composer.paragraph("Observations requiring attention:", font="F2", size=9.5, leading=13)
        for item in attention[:8]:
            composer.paragraph(f"- {item}", size=9.2, leading=12.5, width=94)
    else:
        composer.key_value("Observations requiring attention", "None identified by the configured checks.")
    composer.key_value("Overall AI confidence", "Not used as a legal conclusion; see evidence and limitations below.")

    composer.section(4, "Detailed compliance findings")
    if checks:
        for index, check in enumerate(checks, start=1):
            composer.finding(index, check)
    else:
        composer.paragraph("No configured checks were available for this category.", color=(0.45, 0.12, 0.08))

    composer.section(5, "Penalty / enforcement summary")
    composer.key_value("Confirmed non-compliant parameters", str(confirmed))
    if confirmed:
        composer.paragraph("Applicable enforcement provisions must be confirmed against the current statute, product classification, facts, and competent authority. This prototype does not calculate a monetary penalty.")
        composer.key_value("Non-monetary review action", "Human legal and package review before any notice or enforcement decision.")
    else:
        composer.paragraph("No evidence-backed enforcement finding was produced. Unresolved checks require clearer evidence or manual confirmation; they must not be treated as violations.")
    composer.paragraph("Any amount or action shown in a reviewed report is a screening aid only, not a prediction of an adjudicated outcome.", color=(0.25, 0.25, 0.25))

    composer.evidence_record(evidence_rows)

    composer.section(7, "Important note")
    composer.paragraph(
        "Prototype decision support only - this report is an automated packaging-compliance screening report generated from the supplied product images and extracted information. It is not a judicial determination, official certificate, or enforcement notice. An authorised reviewer should verify the physical package, complete package-side coverage, applicable product-specific law, current rules, and facts before taking formal action."
    )
    limitations = result.get("limitations", []) or []
    requests = result.get("clarification_requests", []) or []
    if limitations:
        composer.paragraph("Recorded limitations:", font="F2", size=9.5, leading=13)
        for item in limitations:
            composer.paragraph(f"- {item}", size=9, leading=12)
    if requests:
        composer.paragraph("Clarification requests:", font="F2", size=9.5, leading=13)
        for item in requests[:8]:
            composer.paragraph(f"- {item}", size=9, leading=12)

    composer.finish()
    payload = _PdfDocument(composer.pages).build()
    metadata = {
        "overall_status": overall,
        "check_count": len(checks),
        "evidence_count": len(evidence_rows),
        "page_count": len(composer.pages),
        "template": "officer-compliance-v2",
    }
    return payload, metadata
