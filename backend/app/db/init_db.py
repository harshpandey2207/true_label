from sqlalchemy import inspect
from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule

def init_db(db: Session):
    # Create missing tables without deleting scan history or existing records.
    Base.metadata.create_all(bind=engine)
    _add_sqlite_compatibility_columns()

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
            _prototype_rule(cat.id, "MANUFACTURER", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a)"),
            _prototype_rule(cat.id, "NET_QUANTITY", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(c)"),
            _prototype_rule(cat.id, "MANUFACTURING_DATE", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(d), subject to product-specific provisions and exceptions"),
            _prototype_rule(cat.id, "MRP", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(f)"),
            _prototype_rule(cat.id, "CONSUMER_CARE", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(2)"),
            # Applicability depends on package type and declared quantity; the
            # current prototype does not evaluate those conditions.
            _prototype_rule(cat.id, "UNIT_SALE_PRICE", False, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(11), check applicability"),
            _prototype_rule(cat.id, "LANGUAGE_CHECK", True, "Applicable declaration-language requirements; verify sector-specific rules"),
        ])

    # Specific Additions: Food & Beverages
    rules.extend([
        _prototype_rule(cat_food.id, "FSSAI_LICENSE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
        _prototype_rule(cat_food.id, "BEST_BEFORE_DATE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
        _prototype_rule(cat_food.id, "VEG_NON_VEG_LOGO", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
    ])

    # Specific Additions: Electronics
    rules.extend([
        _prototype_rule(cat_electronics.id, "BIS_MARK", False, "Applicable BIS / quality-control requirements, if the product is covered"),
    ])
    
    # Specific Additions: Cosmetics
    rules.extend([
        _prototype_rule(cat_cosmetics.id, "BATCH_CODE", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
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
            current.source_url = rule.source_url
            current.rule_version = rule.rule_version
            current.review_status = rule.review_status
            current.evidence_requirement = rule.evidence_requirement
    db.commit()


def _prototype_rule(category_id: int, tag: str, is_mandatory: bool, reference: str, food: bool = False) -> ComplianceRule:
    """Seed cautiously: source links aid review; they are not legal certification."""
    return ComplianceRule(
        category_id=category_id,
        tag=tag,
        is_mandatory=is_mandatory,
        legal_act_reference=reference,
        source_url=(
            "https://fssai.gov.in/food-law/regulations/amendments/labelling-display"
            if food
            else "https://consumeraffairs.gov.in/pages/legal-metrology-act"
        ),
        rule_version="prototype-2026-10",
        review_status="needs_legal_review",
        evidence_requirement="Readable declaration text or a manual confirmation",
    )


def _add_sqlite_compatibility_columns() -> None:
    """Add nullable columns only for existing local demo databases.

    `create_all` does not evolve existing tables. Render/PostgreSQL deployments
    should use an explicit migration process before rollout, so this helper is
    intentionally limited to SQLite and never drops or rewrites data.
    """
    if engine.dialect.name != "sqlite":
        return
    additions = {
        "compliance_rules": {
            "source_url": "VARCHAR",
            "rule_version": "VARCHAR",
            "effective_from": "VARCHAR",
            "review_status": "VARCHAR",
            "evidence_requirement": "VARCHAR",
        },
        "user_accounts": {"created_at": "DATETIME"},
        "audit_events": {"created_at": "DATETIME"},
        "scan_records": {
            "image_names": "JSON",
            "rule_engine_version": "VARCHAR",
            "updated_at": "DATETIME",
        },
        "label_draft_records": {"pdf_payload": "BLOB"},
    }
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, fields in additions.items():
            existing = {column["name"] for column in inspector.get_columns(table)}
            for name, sql_type in fields.items():
                if name not in existing:
                    connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}")
