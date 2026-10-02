from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule, ScanHistory, SectoralOverride, ExemptionClause

def init_db(db: Session):
    # Drop and recreate to ensure the 3-Tier Architecture is applied
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # --- Seed Product Categories ---
    cat_general = ProductCategory(name="General Packaged Commodity", description="Standard consumer goods (Rule 6)")
    cat_food = ProductCategory(name="Food & Beverages", description="Edible goods (Legal Metrology + FSSAI Act)")
    cat_electronics = ProductCategory(name="Electronics & Appliances", description="Electronic devices (Legal Metrology + BIS/E-Waste)")
    cat_cosmetics = ProductCategory(name="Cosmetics, Ointments & Pharma Goods", description="Personal care items (Drugs & Cosmetics Act + Metrology)")
    cat_textiles = ProductCategory(name="Apparel & Textiles", description="Clothing and garments")
    cat_medical = ProductCategory(name="Medical Devices", description="Medical Devices (MDR 2017 + Legal Metrology)")

    db.add_all([cat_general, cat_food, cat_electronics, cat_cosmetics, cat_textiles, cat_medical])
    db.commit()

    rules = []
    
    # Rule 6(1) Common Rules for ALL categories
    for cat in [cat_general, cat_food, cat_electronics, cat_cosmetics, cat_textiles, cat_medical]:
        rules.extend([
            ComplianceRule(category_id=cat.id, tag="MANUFACTURER", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(a)"),
            ComplianceRule(category_id=cat.id, tag="NET_QUANTITY", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(b)"),
            ComplianceRule(category_id=cat.id, tag="MANUFACTURING_DATE", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(d)"),
            ComplianceRule(category_id=cat.id, tag="MRP", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(e)"),
            ComplianceRule(category_id=cat.id, tag="CONSUMER_CARE", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(g)"),
            ComplianceRule(category_id=cat.id, tag="UNIT_SALE_PRICE", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 6(1)(e) (2021 Amendment)"),
            ComplianceRule(category_id=cat.id, tag="LANGUAGE_CHECK", is_mandatory=True, legal_act_reference="Legal Metrology PCR, 2011 - Rule 4 (Hindi in Devanagari or English)"),
        ])

    # Specific Additions: Food & Beverages
    rules.extend([
        ComplianceRule(category_id=cat_food.id, tag="FSSAI_LICENSE", is_mandatory=True, legal_act_reference="FSSAI Regulations, 2011 - License Number"),
        ComplianceRule(category_id=cat_food.id, tag="BEST_BEFORE_DATE", is_mandatory=True, legal_act_reference="FSSAI Regulations - Best Before/Expiry"),
        ComplianceRule(category_id=cat_food.id, tag="VEG_NON_VEG_LOGO", is_mandatory=True, legal_act_reference="FSSAI Regulations - Veg/Non-Veg Logo"),
    ])

    # Specific Additions: Electronics
    rules.extend([
        ComplianceRule(category_id=cat_electronics.id, tag="BIS_MARK", is_mandatory=True, legal_act_reference="BIS Act, 2016"),
    ])
    
    # Specific Additions: Cosmetics
    rules.extend([
        ComplianceRule(category_id=cat_cosmetics.id, tag="BATCH_CODE", is_mandatory=True, legal_act_reference="Drugs & Cosmetics Rules, 1945 - Rule 148"),
    ])

    db.add_all(rules)
    db.commit()

    # --- TIER 2: SECTORAL OVERRIDES ---
    overrides = []
    
    # Medical Devices Exemption from Rule 7 (Font Size)
    for rule in db.query(ComplianceRule).filter(ComplianceRule.category_id == cat_medical.id).all():
        overrides.append(
            SectoralOverride(
                rule_id=rule.id,
                override_condition="IS_MEDICAL_DEVICE",
                override_action="DISABLE_RULE_7_FONT_SIZE",
                statutory_reference="Medical Devices Rules, 2017 (Oct 2025 Amendment carve-out)"
            )
        )
    
    # FSSAI Supremacy over Best Before Date
    bb_rule = db.query(ComplianceRule).filter(ComplianceRule.tag == "BEST_BEFORE_DATE", ComplianceRule.category_id == cat_food.id).first()
    if bb_rule:
        overrides.append(
            SectoralOverride(
                rule_id=bb_rule.id,
                override_condition="IS_FOOD_PRODUCT",
                override_action="FSSAI_SUPERCEDES_METROLOGY_SHELF_LIFE",
                statutory_reference="FSSAI Regulations vs Legal Metrology Rule 6(1)"
            )
        )

    db.add_all(overrides)
    db.commit()

    # --- TIER 3: EXEMPTIONS (Rule 32 / Rule 33 / Institutional) ---
    exemptions = []
    
    # MRP Exemption for Institutional/Industrial Consumers (Rule 2(bb) & 2(bc))
    for mrp_rule in db.query(ComplianceRule).filter(ComplianceRule.tag == "MRP").all():
        exemptions.extend([
            ExemptionClause(
                rule_id=mrp_rule.id,
                exemption_condition="IS_INSTITUTIONAL_CONSUMER",
                alternative_requirement="NOT_FOR_RETAIL_SALE_TAG_REQUIRED",
                statutory_reference="Legal Metrology PCR, 2011 - Rule 2(bb) & 2(bc)"
            ),
            ExemptionClause(
                rule_id=mrp_rule.id,
                exemption_condition="WEIGHT_UNDER_10G_AND_NOT_TOBACCO",
                alternative_requirement="NONE",
                statutory_reference="Legal Metrology PCR, 2011 - Rule 32"
            ),
            ExemptionClause(
                rule_id=mrp_rule.id,
                exemption_condition="RULE_33_GST_EMERGENCY_ACTIVE",
                alternative_requirement="ALLOW_DUAL_MRP_STICKER",
                statutory_reference="Legal Metrology PCR, 2011 - Rule 33 (e.g. Sept 2025 GST rate revision)"
            )
        ])
    
    db.add_all(exemptions)
    db.commit()
