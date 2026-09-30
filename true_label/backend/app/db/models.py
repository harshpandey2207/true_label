from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
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
    legal_act_reference = Column(String) # e.g., "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a)"
    
    category = relationship("ProductCategory", back_populates="rules")

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("product_categories.id"))
    is_compliant = Column(Boolean, default=False)
    missing_tags = Column(String) # Comma-separated list of missing tags
    confidence_score = Column(Float)
    
    category = relationship("ProductCategory", back_populates="scans")

