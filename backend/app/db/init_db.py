from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule, ScanHistory

def init_db(db: Session):
    # For prototype deployment: Drop and recreate to ensure exact 2011 Categories
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # --- Seed Product Categories ---
    # 1. General Packaged Commodity (Rule 6 Default)
    cat_general = ProductCategory(name="General Packaged Commodity", description="Standard consumer goods (Rule 6)")
    # 2. Food & Beverages
    cat_food = ProductCategory(name="Food & Beverages", description="Edible goods (Legal Metrology + FSSAI Act)")
    # 3. Electronics & Appliances
    cat_electronics = ProductCategory(name="Electronics & Appliances", description="Electronic devices (Legal Metrology + BIS/E-Waste)")
    # 4. Cosmetics & Toiletries
    cat_cosmetics = ProductCategory(name="Cosmetics & Toiletries", description="Personal care items (Drugs & Cosmetics Act + Metrology)")
    # 5. Apparel & Textiles
    cat_textiles = ProductCategory(name="Apparel & Textiles", description="Clothing and garments")

    db.add_all([cat_general, cat_food, cat_electronics, cat_cosmetics, cat_textiles])
    db.commit()

    rules = []
    
    # Rule 6(1) Common Rules for ALL categories
    for cat in [cat_general, cat_food, cat_electronics, cat_cosmetics, cat_textiles]:
        rules.extend([
            ComplianceRule(category_id=cat.id, tag="MANUFACTURER", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a): Name & Address of Manufacturer/Packer"),
            ComplianceRule(category_id=cat.id, tag="NET_QUANTITY", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(b): Net quantity in standard units"),
            ComplianceRule(category_id=cat.id, tag="MANUFACTURING_DATE", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(d): Month & Year of Manufacture/Packing"),
            ComplianceRule(category_id=cat.id, tag="MRP", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(e): Maximum Retail Price (Incl. of all taxes)"),
            ComplianceRule(category_id=cat.id, tag="CONSUMER_CARE", is_mandatory=True, legal_act_reference="Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(g): Customer Care Contact Details"),
        ])

    # Specific Additions: Food & Beverages
    rules.extend([
        ComplianceRule(category_id=cat_food.id, tag="FSSAI_LICENSE", is_mandatory=True, legal_act_reference="FSSAI (Packaging and Labelling) Regulations, 2011 - FSSAI License Number"),
        ComplianceRule(category_id=cat_food.id, tag="BEST_BEFORE_DATE", is_mandatory=True, legal_act_reference="FSSAI Regulations - Best Before or Expiry Date"),
        ComplianceRule(category_id=cat_food.id, tag="VEG_NON_VEG_LOGO", is_mandatory=True, legal_act_reference="FSSAI Regulations - Vegetarian/Non-Vegetarian Declaration Logo"),
    ])

    # Specific Additions: Electronics & Appliances
    rules.extend([
        ComplianceRule(category_id=cat_electronics.id, tag="BIS_MARK", is_mandatory=True, legal_act_reference="BIS Act, 2016 - ISI Mark or CRS Registration"),
        ComplianceRule(category_id=cat_electronics.id, tag="VOLTAGE_POWER_RATING", is_mandatory=True, legal_act_reference="General Safety Requirements - Power and Voltage specifications"),
    ])

    # Specific Additions: Cosmetics & Toiletries
    rules.extend([
        ComplianceRule(category_id=cat_cosmetics.id, tag="BATCH_CODE", is_mandatory=True, legal_act_reference="Drugs & Cosmetics Rules, 1945 - Rule 148: Batch Number / Lot Number"),
        ComplianceRule(category_id=cat_cosmetics.id, tag="INGREDIENTS_LIST", is_mandatory=True, legal_act_reference="Drugs & Cosmetics Rules, 1945 - List of ingredients"),
    ])

    # Specific Additions: Apparel & Textiles
    rules.extend([
        ComplianceRule(category_id=cat_textiles.id, tag="SIZE_DIMENSIONS", is_mandatory=True, legal_act_reference="Legal Metrology Rules, 2011 - Rule 6: Size or dimensions of the garment"),
        ComplianceRule(category_id=cat_textiles.id, tag="MATERIAL_COMPOSITION", is_mandatory=False, legal_act_reference="Textile (Consumer Protection) Regulation - Fiber composition details"),
    ])

    db.add_all(rules)
    db.commit()

