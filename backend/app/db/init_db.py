from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule

def init_db(db: Session):
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if we already seeded the database
    if db.query(ProductCategory).first():
        return
        
    # --- Seed Product Categories ---
    cat_general = ProductCategory(name="General Packaged Commodity", description="Standard packaged goods under Legal Metrology Rules")
    cat_cosmetics = ProductCategory(name="Cosmetics / Ointments", description="Cosmetics governed by Drugs and Cosmetics Act & Legal Metrology")
    cat_electronics = ProductCategory(name="Electronics", description="Electronic goods requiring E-Waste and Metrology declarations")
    
    db.add_all([cat_general, cat_cosmetics, cat_electronics])
    db.commit()
    
    # --- Seed Legal Metrology (Packaged Commodities) Rules, 2011 ---
    rules = [
        ComplianceRule(category_id=cat_general.id, tag="MANUFACTURER", is_mandatory=True, legal_act_reference="Rule 6(1)(a): Name and address of manufacturer/packer/importer"),
        ComplianceRule(category_id=cat_general.id, tag="NET_QUANTITY", is_mandatory=True, legal_act_reference="Rule 6(1)(b): Net quantity in standard units of weight or measure"),
        ComplianceRule(category_id=cat_general.id, tag="MANUFACTURING_DATE", is_mandatory=True, legal_act_reference="Rule 6(1)(d): Month and year of manufacture or pre-packing"),
        ComplianceRule(category_id=cat_general.id, tag="MRP", is_mandatory=True, legal_act_reference="Rule 6(1)(e): Maximum Retail Price (inclusive of all taxes)"),
        ComplianceRule(category_id=cat_general.id, tag="CONSUMER_CARE", is_mandatory=True, legal_act_reference="Rule 6(1)(g): Name, address, telephone no, e-mail of consumer care"),
        
        # Cosmetics specific additional rules
        ComplianceRule(category_id=cat_cosmetics.id, tag="BATCH_CODE", is_mandatory=True, legal_act_reference="Drugs & Cosmetics Rules, 1945 - Rule 148: Batch Number"),
        ComplianceRule(category_id=cat_cosmetics.id, tag="STORAGE", is_mandatory=False, legal_act_reference="Best practices for temperature-sensitive ointments")
    ]
    
    db.add_all(rules)
    db.commit()

