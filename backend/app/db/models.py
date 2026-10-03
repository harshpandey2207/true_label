from sqlalchemy import Column, JSON, Integer, String, Boolean, ForeignKey, DateTime, Float
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

class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("user_accounts.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(String)
    details = Column(JSON)
