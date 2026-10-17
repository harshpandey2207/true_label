from sqlalchemy import Column, JSON, Integer, String, Boolean, ForeignKey, DateTime, Float, LargeBinary
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.db.database import Base

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    rules = relationship("ComplianceRule", back_populates="category")
    scans = relationship("ScanHistory", back_populates="category")

class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    tag = Column(String, index=True) # e.g., MRP, NET_QUANTITY, MANUFACTURER
    is_mandatory = Column(Boolean, default=True)
    legal_act_reference = Column(String) # e.g., "Legal Metrology Rule 6(1)(a)"
    source_url = Column(String, nullable=True)
    rule_version = Column(String, default="prototype-2026-10")
    effective_from = Column(String, nullable=True)
    review_status = Column(String, default="needs_legal_review")
    evidence_requirement = Column(String, default="Readable declaration text or a manual confirmation")
    
    category = relationship("ProductCategory", back_populates="rules")
    overrides = relationship("SectoralOverride", back_populates="rule")
    exemptions = relationship("ExemptionClause", back_populates="rule")

class SectoralOverride(Base):
    """
    Handles cases where another Act (e.g., FSSAI, Medical Devices Rules 2017) 
    supersedes the Legal Metrology PCR.
    """
    __tablename__ = "sectoral_overrides"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"))
    override_condition = Column(String) # e.g., "IS_MEDICAL_DEVICE"
    override_action = Column(String) # e.g., "DISABLE_RULE_7_FONT_SIZE"
    statutory_reference = Column(String) # e.g., "Medical Devices Rules, 2017 (2025 Amendment)"
    
    rule = relationship("ComplianceRule", back_populates="overrides")

class ExemptionClause(Base):
    """
    Handles Rule 26/32 (<10g), Rule 33 (Emergencies/GST), and Institutional Consumers.
    """
    __tablename__ = "exemption_clauses"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("compliance_rules.id"))
    exemption_condition = Column(String) # e.g., "IS_INSTITUTIONAL_CONSUMER", "WEIGHT_UNDER_10G", "RULE_33_ACTIVE"
    alternative_requirement = Column(String, nullable=True) # e.g., "MUST_HAVE_NOT_FOR_RETAIL_SALE"
    statutory_reference = Column(String) # e.g., "Rule 33 / Rule 2(bb)"

    rule = relationship("ComplianceRule", back_populates="exemptions")

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    is_compliant = Column(Boolean, default=False)
    missing_tags = Column(String) # Comma-separated list of missing tags
    confidence_score = Column(Float)
    
    category = relationship("ProductCategory", back_populates="scans")



class UserAccount(Base):
    __tablename__ = "user_accounts"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="business_owner")
    organization_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class LabelDraftRecord(Base):
    __tablename__ = "label_draft_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    product_name = Column(String)
    category = Column(String)
    source_scan_id = Column(String)
    label_data = Column(JSON)
    warnings = Column(JSON)
    pdf_payload = Column(LargeBinary, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NoticeRecord(Base):
    __tablename__ = "notice_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    title = Column(String)
    body = Column(String)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class PaymentRecord(Base):
    __tablename__ = "payment_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    description = Column(String)
    amount_minor = Column(Integer)
    currency = Column(String, default="INR")
    status = Column(String, default="pending_confirmation")
    external_reference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ProductRecord(Base):
    __tablename__ = "product_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    name = Column(String)
    category = Column(String)
    sku = Column(String, nullable=True)
    declarations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScanRecord(Base):
    __tablename__ = "scan_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    category = Column(String)
    status = Column(String)
    result = Column(JSON)
    image_names = Column(JSON, default=list)
    rule_engine_version = Column(String, default="prototype-2026-10")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    evidence = relationship("ScanEvidence", back_populates="scan", cascade="all, delete-orphan")


class ScanEvidence(Base):
    """Original upload retained for a demo scan and its clarification attempts.

    This database-backed storage is intentionally a demo fallback. Production
    deployments need private object storage with lifecycle/retention controls.
    """

    __tablename__ = "scan_evidence"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_records.id"), nullable=False, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    sha256 = Column(String(64), nullable=False, index=True)
    size_bytes = Column(Integer, nullable=False)
    payload = Column(LargeBinary, nullable=False)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    scan = relationship("ScanRecord", back_populates="evidence")


class ComplianceReportRecord(Base):
    __tablename__ = "compliance_report_records"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_records.id"), nullable=False, index=True)
    report_code = Column(String, unique=True, nullable=False, index=True)
    content = Column(JSON, nullable=False)
    pdf_payload = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class EscalationCase(Base):
    """A review request raised from an evidence-backed scan.

    This is deliberately a small, persistent workflow record.  It is not an
    enforcement notice and must not be presented as one by the client.
    """

    __tablename__ = "escalation_cases"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scan_records.id"), nullable=False, index=True)
    created_by_user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False, index=True)
    status = Column(String, default="open", nullable=False, index=True)
    note = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
