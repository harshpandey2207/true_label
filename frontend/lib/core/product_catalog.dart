/// Product categories shared by scanner, registry and Label Draft Studio.
///
/// These are broad prototype screening profiles. They do not replace a legal
/// determination for a specific product, material, sale channel or exemption.
const productCategories = <String>[
  'General Packaged Commodity',
  'Food & Beverages',
  'Packaged Drinking Water',
  'Electronics & Appliances',
  'Electrical Cables & Accessories',
  'Cosmetics, Ointments & Pharma Goods',
  'Personal Care Products',
  'Household Cleaning Products',
  'Apparel & Textiles',
  'Footwear & Leather Goods',
  'Toys & Childcare Products',
  'Medical Devices',
  'Automotive Components & Lubricants',
  'Tobacco & Nicotine Products',
  'Stationery & School Supplies',
  'Agricultural Inputs',
  'Other / Custom Packaged Product',
];

const productCategoryFields = <String, List<String>>{
  'Food & Beverages': [
    'batch_code',
    'best_before_date',
    'fssai_license',
    'veg_non_veg_logo',
    'ingredients',
  ],
  'Packaged Drinking Water': [
    'batch_code',
    'best_before_date',
    'fssai_license',
    'source_name',
  ],
  'Electronics & Appliances': [
    'model',
    'bis_mark',
    'country_of_origin',
    'e_waste_info',
  ],
  'Electrical Cables & Accessories': ['model', 'bis_mark', 'country_of_origin'],
  'Cosmetics, Ointments & Pharma Goods': [
    'batch_code',
    'expiry_date',
    'manufacturing_license',
    'ingredients',
  ],
  'Personal Care Products': ['batch_code', 'expiry_date', 'ingredients'],
  'Household Cleaning Products': [
    'batch_code',
    'hazard_warning',
    'ingredients',
  ],
  'Apparel & Textiles': ['size', 'fibre_content', 'country_of_origin'],
  'Footwear & Leather Goods': ['size', 'material', 'country_of_origin'],
  'Toys & Childcare Products': [
    'age_group',
    'hazard_warning',
    'country_of_origin',
  ],
  'Medical Devices': [
    'model',
    'batch_code',
    'serial_number',
    'license_no',
    'sterile_status',
  ],
  'Automotive Components & Lubricants': [
    'model',
    'batch_code',
    'country_of_origin',
  ],
  'Tobacco & Nicotine Products': [
    'batch_code',
    'health_warning',
    'country_of_origin',
  ],
  'Stationery & School Supplies': ['country_of_origin'],
  'Agricultural Inputs': ['batch_code', 'expiry_date', 'license_no'],
};

List<String> fieldsForProductCategory(String category) => [
  'manufacturer',
  'commodity_name',
  'net_quantity',
  'manufacturing_date',
  'mrp',
  'unit_sale_price',
  'consumer_care',
  ...(productCategoryFields[category] ?? const <String>[]),
];
