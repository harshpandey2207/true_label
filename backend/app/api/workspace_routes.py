from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.api.security import get_current_user, hash_password, require_roles
from backend.app.db.database import get_db
from backend.app.db.models import AuditEvent, ComplianceRule, LabelDraftRecord, NoticeRecord, PaymentRecord, ProductCategory, ProductRecord, ScanRecord, UserAccount

router = APIRouter(tags=["Workspace"])
class ProductInput(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    category: str = Field(min_length=2, max_length=120)
    sku: str | None = Field(default=None, max_length=120)
    declarations: dict[str, str] = Field(default_factory=dict)


class PaymentRecordInput(BaseModel):
    description: str = Field(min_length=3, max_length=240)
    amount_minor: int = Field(gt=0, le=100_000_000)


class ExternalPaymentInput(BaseModel):
    external_reference: str = Field(min_length=4, max_length=160)


class NoticeInput(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=3, max_length=4000)


class RuleUpdate(BaseModel):
    is_mandatory: bool | None = None
    legal_act_reference: str | None = Field(default=None, max_length=500)


class InspectorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=10, max_length=128)


def _payment_payload(record: PaymentRecord) -> dict:
    return {
        "id": record.id,
        "description": record.description,
        "amount_minor": record.amount_minor,
        "currency": record.currency,
        "status": record.status,
        "external_reference": record.external_reference,
        "created_at": record.created_at.isoformat() + "Z",
    }


def _product_payload(product: ProductRecord) -> dict:
    return {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "sku": product.sku,
        "declarations": product.declarations or {},
        "created_at": product.created_at.isoformat() + "Z",
        "updated_at": product.updated_at.isoformat() + "Z",
    }


@router.get("/summary")
def workspace_summary(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role in {"admin", "inspector"}:
        scan_query = db.query(ScanRecord)
        product_query = db.query(ProductRecord)
        user_count = db.query(func.count(UserAccount.id)).filter(UserAccount.is_active.is_(True)).scalar() or 0
    else:
        scan_query = db.query(ScanRecord).filter(ScanRecord.user_id == user.id)
        product_query = db.query(ProductRecord).filter(ProductRecord.user_id == user.id)
        user_count = None
    total_scans = scan_query.count()
    flagged_scans = scan_query.filter(ScanRecord.status == "POTENTIAL_ISSUES").count()
    product_count = product_query.count()
    result = {
        "scan_count": total_scans,
        "flagged_scan_count": flagged_scans,
        "no_flags_scan_count": total_scans - flagged_scans,
        "product_count": product_count,
        "generated_label_count": db.query(LabelDraftRecord).filter(LabelDraftRecord.user_id == user.id).count(),
    }
    if user_count is not None:
        result["active_user_count"] = user_count
    return result


@router.get("/scans")
def list_scans(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 100):
    query = db.query(ScanRecord)
    if user.role not in {"admin", "inspector"}:
        query = query.filter(ScanRecord.user_id == user.id)
    records = query.order_by(ScanRecord.created_at.desc()).limit(min(max(limit, 1), 200)).all()
    return {"items": [{
        "id": row.id,
        "user_id": row.user_id,
        "category": row.category,
        "status": row.status,
        "result": row.result,
        "image_names": row.image_names,
        "created_at": row.created_at.isoformat() + "Z",
    } for row in records]}


@router.get("/products")
def list_products(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    products = db.query(ProductRecord).filter(ProductRecord.user_id == user.id).order_by(ProductRecord.updated_at.desc()).all()
    return {"items": [_product_payload(product) for product in products]}


@router.post("/products", status_code=201)
def create_product(payload: ProductInput, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    product = ProductRecord(
        user_id=user.id,
        name=payload.name.strip(),
        category=payload.category.strip(),
        sku=payload.sku.strip() if payload.sku else None,
        declarations=payload.declarations,
    )
    db.add(product)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="product.created", entity_type="product", entity_id=str(product.id), details={"name": product.name}))
    db.commit()
    db.refresh(product)
    return _product_payload(product)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(ProductRecord).filter(ProductRecord.id == product_id, ProductRecord.user_id == user.id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    db.add(AuditEvent(user_id=user.id, action="product.deleted", entity_type="product", entity_id=str(product.id), details={"name": product.name}))
    db.delete(product)
    db.commit()


@router.get("/labels")
def list_label_drafts(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(LabelDraftRecord).filter(LabelDraftRecord.user_id == user.id).order_by(LabelDraftRecord.created_at.desc()).limit(100).all()
    return {"items": [{
        "id": row.id,
        "product_name": row.product_name,
        "category": row.category,
        "source_scan_id": row.source_scan_id,
        "label_data": row.label_data,
        "warnings": row.warnings,
        "created_at": row.created_at.isoformat() + "Z",
    } for row in rows]}


@router.get("/audit")
def list_audit_events(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db), limit: int = 100):
    query = db.query(AuditEvent)
    if user.role not in {"admin", "inspector"}:
        query = query.filter(AuditEvent.user_id == user.id)
    rows = query.order_by(AuditEvent.created_at.desc()).limit(min(max(limit, 1), 200)).all()
    return {"items": [{
        "id": row.id,
        "action": row.action,
        "entity_type": row.entity_type,
        "entity_id": row.entity_id,
        "details": row.details,
        "created_at": row.created_at.isoformat() + "Z",
    } for row in rows]}


@router.get("/admin/users")
def admin_list_users(user: UserAccount = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rows = db.query(UserAccount).order_by(UserAccount.created_at.desc()).limit(500).all()
    return {"items": [{
        "id": row.id,
        "full_name": row.full_name,
        "email": row.email,
        "role": row.role,
        "organization_name": row.organization_name,
        "is_active": row.is_active,
        "created_at": row.created_at.isoformat() + "Z",
    } for row in rows]}


@router.post("/admin/inspectors", status_code=201)
def admin_create_inspector(payload: InspectorCreate, user: UserAccount = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(status_code=422, detail="Enter a valid email address.")
    if db.query(UserAccount.id).filter(UserAccount.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists.")
    account = UserAccount(full_name=payload.full_name.strip(), email=email, password_hash=hash_password(payload.password), role="inspector")
    db.add(account)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="inspector.created", entity_type="account", entity_id=str(account.id), details={"email": email}))
    db.commit()
    db.refresh(account)
    return {"id": account.id, "full_name": account.full_name, "email": account.email, "role": account.role, "is_active": account.is_active}


@router.patch("/admin/users/{account_id}/active")
def admin_set_user_active(account_id: int, is_active: bool, user: UserAccount = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    account = db.query(UserAccount).filter(UserAccount.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found.")
    if account.id == user.id and not is_active:
        raise HTTPException(status_code=422, detail="You cannot disable your own administrator account.")
    account.is_active = is_active
    db.add(AuditEvent(user_id=user.id, action="account.access_updated", entity_type="account", entity_id=str(account.id), details={"is_active": is_active}))
    db.commit()
    return {"id": account.id, "is_active": account.is_active}


@router.get("/admin/rules")
def admin_list_rules(user: UserAccount = Depends(require_roles("admin", "inspector")), db: Session = Depends(get_db)):
    categories = db.query(ProductCategory).order_by(ProductCategory.name).all()
    rules = db.query(ComplianceRule).order_by(ComplianceRule.category_id, ComplianceRule.tag).all()
    names = {category.id: category.name for category in categories}
    return {"items": [{
        "id": rule.id,
        "category_id": rule.category_id,
        "category": names.get(rule.category_id, "Uncategorised"),
        "tag": rule.tag,
        "is_mandatory": rule.is_mandatory,
        "legal_act_reference": rule.legal_act_reference,
        "source_url": "https://fssai.gov.in/food-law/regulations/amendments/labelling-display" if names.get(rule.category_id) == "Food & Beverages" else "https://consumeraffairs.gov.in/pages/legal-metrology-act",
        "automated_scope": "OCR checks for the presence of declaration text; applicability, exemptions, exact format, prominence and current amendments require review.",
    } for rule in rules]}


@router.patch("/admin/rules/{rule_id}")
def admin_update_rule(rule_id: int, payload: RuleUpdate, user: UserAccount = Depends(require_roles("admin")), db: Session = Depends(get_db)):
    rule = db.query(ComplianceRule).filter(ComplianceRule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found.")
    changes = {}
    if payload.is_mandatory is not None:
        rule.is_mandatory = payload.is_mandatory
        changes["is_mandatory"] = payload.is_mandatory
    if payload.legal_act_reference is not None:
        rule.legal_act_reference = payload.legal_act_reference.strip()
        changes["legal_act_reference"] = payload.legal_act_reference.strip()
    if not changes:
        raise HTTPException(status_code=422, detail="Provide a rule setting to update.")
    db.add(AuditEvent(user_id=user.id, action="compliance_rule.updated", entity_type="compliance_rule", entity_id=str(rule.id), details=changes))
    db.commit()
    return {"id": rule.id, "tag": rule.tag, "is_mandatory": rule.is_mandatory, "legal_act_reference": rule.legal_act_reference}


@router.get("/notices")
def list_notices(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(NoticeRecord).filter(NoticeRecord.user_id == user.id).order_by(NoticeRecord.created_at.desc()).all()
    return {"items": [{
        "id": row.id,
        "title": row.title,
        "body": row.body,
        "status": row.status,
        "created_at": row.created_at.isoformat() + "Z",
    } for row in rows]}


@router.post("/notices", status_code=201)
def create_notice(payload: NoticeInput, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    notice = NoticeRecord(user_id=user.id, title=payload.title.strip(), body=payload.body.strip())
    db.add(notice)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="review_note.created", entity_type="review_note", entity_id=str(notice.id), details={}))
    db.commit()
    db.refresh(notice)
    return {"id": notice.id, "title": notice.title, "body": notice.body, "status": notice.status, "created_at": notice.created_at.isoformat() + "Z"}


@router.get("/billing/plans")
def billing_plans():
    return {"items": [], "gateway_configured": False, "message": "Online payment processing is not configured."}


@router.get("/billing/records")
def list_payment_records(user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(PaymentRecord).filter(PaymentRecord.user_id == user.id).order_by(PaymentRecord.created_at.desc()).all()
    return {"items": [_payment_payload(row) for row in rows], "gateway_configured": False}


@router.post("/billing/records", status_code=201)
def create_payment_record(payload: PaymentRecordInput, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    record = PaymentRecord(
        user_id=user.id,
        description=payload.description.strip(),
        amount_minor=payload.amount_minor,
        currency="INR",
        status="pending_confirmation",
    )
    db.add(record)
    db.flush()
    db.add(AuditEvent(user_id=user.id, action="billing.record_created", entity_type="payment_record", entity_id=str(record.id), details={"amount_minor": payload.amount_minor}))
    db.commit()
    db.refresh(record)
    result = _payment_payload(record)
    result["gateway_configured"] = False
    return result


@router.post("/billing/records/{record_id}/external-reference")
def record_external_payment(record_id: int, payload: ExternalPaymentInput, user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(PaymentRecord).filter(PaymentRecord.id == record_id, PaymentRecord.user_id == user.id).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Billing record not found.")
    if record.status not in {"pending_confirmation", "reported_unverified"}:
        raise HTTPException(status_code=409, detail="This billing record is no longer awaiting confirmation.")
    record.external_reference = payload.external_reference.strip()
    record.status = "reported_unverified"
    db.add(AuditEvent(user_id=user.id, action="billing.external_payment_reported", entity_type="payment_record", entity_id=str(record.id), details={"verification": "pending"}))
    db.commit()
    db.refresh(record)
    return _payment_payload(record)
