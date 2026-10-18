from sqlalchemy import inspect
from sqlalchemy.orm import Session
from backend.app.db.database import engine, Base
from backend.app.db.models import ProductCategory, ComplianceRule

def init_db(db: Session):
    # Create missing tables without deleting scan history or existing records.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Base.metadata.create_all notice: {e}")

    _add_compatibility_columns()

    try:
        category_descriptions = {
            "General Packaged Commodity": "Standard consumer goods",
            "Food & Beverages": "Food and beverages",
            "Packaged Drinking Water": "Packaged drinking and mineral water",
            "Electronics & Appliances": "Electronic devices and appliances",
            "Electrical Cables & Accessories": "Cables, chargers, plugs and electrical accessories",
            "Cosmetics, Ointments & Pharma Goods": "Cosmetics and pharmaceutical goods",
            "Personal Care Products": "Soaps, shampoos, oral care and personal care products",
            "Household Cleaning Products": "Detergents, cleaners and household chemicals",
            "Apparel & Textiles": "Clothing and textile products",
            "Footwear & Leather Goods": "Footwear, bags and leather goods",
            "Toys & Childcare Products": "Toys, games and childcare products",
            "Medical Devices": "Medical devices",
            "Automotive Components & Lubricants": "Automotive parts, fluids and lubricants",
            "Tobacco & Nicotine Products": "Tobacco and nicotine products",
            "Stationery & School Supplies": "Stationery, writing and school supplies",
            "Agricultural Inputs": "Seeds, fertilisers and agricultural inputs",
            "Other / Custom Packaged Product": "Fallback profile for a packaged product not covered by a named category",
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
        cat_water = categories["Packaged Drinking Water"]
        cat_electronics = categories["Electronics & Appliances"]
        cat_electrical = categories["Electrical Cables & Accessories"]
        cat_cosmetics = categories["Cosmetics, Ointments & Pharma Goods"]
        cat_personal_care = categories["Personal Care Products"]
        cat_cleaning = categories["Household Cleaning Products"]
        cat_textiles = categories["Apparel & Textiles"]
        cat_footwear = categories["Footwear & Leather Goods"]
        cat_toys = categories["Toys & Childcare Products"]
        cat_medical = categories["Medical Devices"]
        cat_automotive = categories["Automotive Components & Lubricants"]
        cat_tobacco = categories["Tobacco & Nicotine Products"]
        cat_stationery = categories["Stationery & School Supplies"]
        cat_agri = categories["Agricultural Inputs"]

        rules = []
        
        # Rule 6(1) Common Rules for ALL categories
        for cat in categories.values():
            rules.extend([
                _prototype_rule(cat.id, "COMMODITY_NAME", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(b)"),
                _prototype_rule(cat.id, "MANUFACTURER", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(a)"),
                _prototype_rule(cat.id, "NET_QUANTITY", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(c)"),
                _prototype_rule(cat.id, "MANUFACTURING_DATE", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(d), subject to product-specific provisions and exceptions"),
                _prototype_rule(cat.id, "MRP", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(1)(f)"),
                _prototype_rule(cat.id, "CONSUMER_CARE", True, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(2)"),
                _prototype_rule(cat.id, "UNIT_SALE_PRICE", False, "Legal Metrology (Packaged Commodities) Rules, 2011 - Rule 6(11), check applicability"),
                _prototype_rule(cat.id, "LANGUAGE_CHECK", True, "Applicable declaration-language requirements; verify sector-specific rules"),
            ])

        # Specific Additions: Food & Beverages
        rules.extend([
            _prototype_rule(cat_food.id, "FSSAI_LICENSE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_food.id, "BEST_BEFORE_DATE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_food.id, "VEG_NON_VEG_LOGO", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_food.id, "INGREDIENTS", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_water.id, "FSSAI_LICENSE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_water.id, "BEST_BEFORE_DATE", True, "Food Safety and Standards (Labelling and Display) Regulations, 2020, as amended", food=True),
            _prototype_rule(cat_water.id, "SOURCE_NAME", True, "Food Safety and Standards (Food Products Standards and Food Additives) Regulations, as amended", food=True),
        ])

        # Specific Additions: Electronics
        rules.extend([
            _prototype_rule(cat_electronics.id, "BIS_MARK", False, "Applicable BIS / quality-control requirements, if the product is covered"),
            _prototype_rule(cat_electronics.id, "MODEL", True, "Consumer product identification and applicable quality-control requirements"),
            _prototype_rule(cat_electronics.id, "COUNTRY_OF_ORIGIN", False, "Legal Metrology (Packaged Commodities) Rules, 2011 - importer/origin declarations where applicable"),
            _prototype_rule(cat_electronics.id, "E_WASTE_INFO", False, "E-Waste (Management) Rules, as amended, where applicable"),
            _prototype_rule(cat_electrical.id, "BIS_MARK", False, "Applicable BIS / quality-control requirements, if the product is covered"),
            _prototype_rule(cat_electrical.id, "MODEL", True, "Consumer product identification and applicable quality-control requirements"),
        ])
        
        # Specific Additions: Cosmetics
        rules.extend([
            _prototype_rule(cat_cosmetics.id, "BATCH_CODE", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_cosmetics.id, "EXPIRY_DATE", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_cosmetics.id, "INGREDIENTS", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_personal_care.id, "BATCH_CODE", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_personal_care.id, "EXPIRY_DATE", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_personal_care.id, "INGREDIENTS", True, "Drugs and Cosmetics Rules, 1945, and product-specific requirements"),
            _prototype_rule(cat_cleaning.id, "BATCH_CODE", True, "Applicable product-safety and packaged-commodity requirements"),
            _prototype_rule(cat_cleaning.id, "HAZARD_WARNING", True, "Applicable product-safety and chemical labelling requirements"),
            _prototype_rule(cat_cleaning.id, "INGREDIENTS", False, "Applicable product-safety and chemical labelling requirements"),
        ])

        rules.extend([
            _prototype_rule(cat_textiles.id, "SIZE", True, "Legal Metrology and textile labelling requirements, where applicable"),
            _prototype_rule(cat_textiles.id, "FIBRE_CONTENT", True, "Textile labelling requirements, subject to product and sector applicability"),
            _prototype_rule(cat_textiles.id, "COUNTRY_OF_ORIGIN", False, "Legal Metrology (Packaged Commodities) Rules, 2011 - importer/origin declarations where applicable"),
            _prototype_rule(cat_footwear.id, "SIZE", True, "Footwear labelling requirements, subject to product and sector applicability"),
            _prototype_rule(cat_footwear.id, "MATERIAL", False, "Footwear and leather product labelling requirements, where applicable"),
            _prototype_rule(cat_toys.id, "AGE_GROUP", True, "Toy safety and labelling requirements, subject to product and age group"),
            _prototype_rule(cat_toys.id, "HAZARD_WARNING", True, "Toy safety and labelling requirements, subject to product and age group"),
            _prototype_rule(cat_medical.id, "MODEL", True, "Medical Devices Rules, 2017, as amended"),
            _prototype_rule(cat_medical.id, "SERIAL_NUMBER", False, "Medical Devices Rules, 2017, as amended, where applicable"),
            _prototype_rule(cat_medical.id, "LICENSE_NO", True, "Medical Devices Rules, 2017, as amended"),
            _prototype_rule(cat_medical.id, "STERILE_STATUS", False, "Medical Devices Rules, 2017, as amended, where applicable"),
            _prototype_rule(cat_automotive.id, "MODEL", True, "Applicable automotive product and packaged-commodity requirements"),
            _prototype_rule(cat_automotive.id, "BATCH_CODE", False, "Applicable automotive product and safety requirements"),
            _prototype_rule(cat_tobacco.id, "HEALTH_WARNING", True, "Cigarettes and Other Tobacco Products (Packaging and Labelling) Rules, as amended"),
            _prototype_rule(cat_tobacco.id, "BATCH_CODE", True, "Applicable tobacco packaging and traceability requirements"),
            _prototype_rule(cat_stationery.id, "COUNTRY_OF_ORIGIN", False, "Legal Metrology (Packaged Commodities) Rules, 2011 - importer/origin declarations where applicable"),
            _prototype_rule(cat_agri.id, "BATCH_CODE", True, "Applicable agricultural-input labelling requirements"),
            _prototype_rule(cat_agri.id, "LICENSE_NO", True, "Applicable fertiliser, seed or pesticide licensing requirements"),
            _prototype_rule(cat_agri.id, "EXPIRY_DATE", False, "Applicable agricultural-input labelling requirements, where applicable"),
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
    except Exception as e:
        db.rollback()
        print(f"Warning during rule/category seeding: {e}")


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


def _add_compatibility_columns() -> None:
    """Add nullable columns safely for existing demo databases across SQLite and PostgreSQL."""
    try:
        is_pg = engine.dialect.name == "postgresql"
        varchar_type = "VARCHAR(1024)" if is_pg else "VARCHAR"
        datetime_type = "TIMESTAMP" if is_pg else "DATETIME"
        json_type = "JSON" if is_pg else "JSON"
        blob_type = "BYTEA" if is_pg else "BLOB"

        additions = {
            "compliance_rules": {
                "source_url": varchar_type,
                "rule_version": varchar_type,
                "effective_from": varchar_type,
                "review_status": varchar_type,
                "evidence_requirement": varchar_type,
            },
            "user_accounts": {"created_at": datetime_type},
            "audit_events": {"created_at": datetime_type},
            "scan_records": {
                "image_names": json_type,
                "rule_engine_version": varchar_type,
                "updated_at": datetime_type,
            },
            "label_draft_records": {"pdf_payload": blob_type},
        }
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        with engine.begin() as connection:
            for table, fields in additions.items():
                if table not in existing_tables:
                    continue
                try:
                    existing = {column["name"] for column in inspector.get_columns(table)}
                except Exception:
                    existing = set()
                for name, sql_type in fields.items():
                    if name not in existing:
                        try:
                            connection.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}")
                        except Exception as col_err:
                            print(f"Column addition note for {table}.{name}: {col_err}")
    except Exception as e:
        print(f"Compatibility column migration note: {e}")
