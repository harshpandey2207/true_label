from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule

def init_db(db: Session):
    # Create missing tables without deleting scan history or existing records.
    Base.metadata.create_all(bind=engine)

    category_descriptions = {
        "General Packaged Commodity": "Standard consumer goods",
        "Food & Beverages": "Food and beverages",
        "Electronics & Appliances": "Electronic devices and appliances",
        "Cosmetics, Ointments & Pharma Goods": "Cosmetics and pharmaceutical goods",
        "Apparel & Textiles": "Clothing and textile products",
        "Medical Devices": "Medical devices",
    }
    categories = {}
    for name, description in category_descriptions.items():
        category = db.query(ProductCategory).filter(ProductCategory.name == name).first()
        if category is None:
            category = ProductCategory(name=name, description=description)
            db.add(category)
        categories[name] = category
    db.commit()

    cat_general = categories["General Packaged Commodity"]
    cat_food = categories["Food & Beverages"]
    cat_electronics = categories["Electronics & Appliances"]
    cat_cosmetics = categories["Cosmetics, Ointments & Pharma Goods"]
    cat_textiles = categories["Apparel & Textiles"]
    cat_medical = categories["Medical Devices"]

    rules = []
    
    # Rule 6(1) Common Rules for ALL categories
    for cat in [cat_general, cat_food, cat_electronics, cat_cosmetics, cat_textiles, cat_medical]:
        rules.extend([
            ComplianceRule(category_id=cat.id, tag="MANUFACTURER", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(a)"),
            ComplianceRule(category_id=cat.id, tag="NET_QUANTITY", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(c)"),
            ComplianceRule(category_id=cat.id, tag="MANUFACTURING_DATE", is_mandatory=True, legal_act_reference="Rule 6(1)(d), subject to product-specific provisions and exceptions"),
            ComplianceRule(category_id=cat.id, tag="MRP", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(f)"),
            ComplianceRule(category_id=cat.id, tag="CONSUMER_CARE", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(2)"),
            # Applicability depends on package type and declared quantity; the
            # current prototype does not evaluate those conditions.
            ComplianceRule(category_id=cat.id, tag="UNIT_SALE_PRICE", is_mandatory=False, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(11), check applicability"),
            ComplianceRule(category_id=cat.id, tag="LANGUAGE_CHECK", is_mandatory=True, legal_act_reference="Applicable declaration-language requirements; verify sector-specific rules"),
        ])

    # Specific Additions: Food & Beverages
    rules.extend([
        ComplianceRule(category_id=cat_food.id, tag="FSSAI_LICENSE", is_mandatory=True, legal_act_reference="Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended"),
        ComplianceRule(category_id=cat_food.id, tag="BEST_BEFORE_DATE", is_mandatory=True, legal_act_reference="Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended"),
        ComplianceRule(category_id=cat_food.id, tag="VEG_NON_VEG_LOGO", is_mandatory=True, legal_act_reference="Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended"),
    ])

    # Specific Additions: Electronics
    rules.extend([
        ComplianceRule(category_id=cat_electronics.id, tag="BIS_MARK", is_mandatory=False, legal_act_reference="Applicable BIS / quality-control requirements, if the product is covered"),
    ])
    
    # Specific Additions: Cosmetics
    rules.extend([
        ComplianceRule(category_id=cat_cosmetics.id, tag="BATCH_CODE", is_mandatory=True, legal_act_reference="Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
    ])

    # Seed/update only the known starter rows. Existing scans and unrelated
    # records are preserved; no broad table reset runs during application boot.
    for rule in rules:
        current = db.query(ComplianceRule).filter(
            ComplianceRule.category_id == rule.category_id,
            ComplianceRule.tag == rule.tag,
        ).first()
        if current is None:
            db.add(rule)
        else:
            current.is_mandatory = rule.is_mandatory
            current.legal_act_reference = rule.legal_act_reference
    db.commit()
