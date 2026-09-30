// frontend/lib/features/admin/mock_data.dart

final List<Map<String, dynamic>> regionalData = [
  {'name': 'Andaman and Nicobar', 'violations': 2, 'scans': 16, 'compliant': 14},
  {'name': 'Andhra Pradesh', 'violations': 10, 'scans': 41, 'compliant': 31},
  {'name': 'Arunachal Pradesh', 'violations': 0, 'scans': 9, 'compliant': 9},
  {'name': 'Assam', 'violations': 4, 'scans': 20, 'compliant': 16},
  {'name': 'Bihar', 'violations': 8, 'scans': 33, 'compliant': 25},
  {'name': 'Chandigarh', 'violations': 5, 'scans': 25, 'compliant': 20},
  {'name': 'Chhattisgarh', 'violations': 7, 'scans': 43, 'compliant': 36},
  {'name': 'Dadra and Nagar Haveli', 'violations': 4, 'scans': 46, 'compliant': 42},
  {'name': 'Daman and Diu', 'violations': 4, 'scans': 18, 'compliant': 14},
  {'name': 'Delhi', 'violations': 20, 'scans': 40, 'compliant': 20},
  {'name': 'Goa', 'violations': 3, 'scans': 16, 'compliant': 13},
  {'name': 'Gujarat', 'violations': 3, 'scans': 13, 'compliant': 10},
  {'name': 'Haryana', 'violations': 1, 'scans': 14, 'compliant': 13},
  {'name': 'Himachal Pradesh', 'violations': 2, 'scans': 28, 'compliant': 26},
  {'name': 'Jammu and Kashmir', 'violations': 13, 'scans': 46, 'compliant': 33},
  {'name': 'Jharkhand', 'violations': 1, 'scans': 21, 'compliant': 20},
  {'name': 'Karnataka', 'violations': 6, 'scans': 42, 'compliant': 36},
  {'name': 'Kerala', 'violations': 5, 'scans': 46, 'compliant': 41},
  {'name': 'Lakshadweep', 'violations': 0, 'scans': 8, 'compliant': 8},
  {'name': 'Madhya Pradesh', 'violations': 8, 'scans': 32, 'compliant': 24},
  {'name': 'Maharashtra', 'violations': 24, 'scans': 44, 'compliant': 20},
  {'name': 'Manipur', 'violations': 7, 'scans': 44, 'compliant': 37},
  {'name': 'Meghalaya', 'violations': 6, 'scans': 44, 'compliant': 38},
  {'name': 'Mizoram', 'violations': 4, 'scans': 36, 'compliant': 32},
  {'name': 'Nagaland', 'violations': 7, 'scans': 29, 'compliant': 22},
  {'name': 'Orissa', 'violations': 10, 'scans': 42, 'compliant': 32},
  {'name': 'Puducherry', 'violations': 6, 'scans': 28, 'compliant': 22},
  {'name': 'Punjab', 'violations': 2, 'scans': 29, 'compliant': 27},
  {'name': 'Rajasthan', 'violations': 0, 'scans': 7, 'compliant': 7},
  {'name': 'Sikkim', 'violations': 6, 'scans': 35, 'compliant': 29},
  {'name': 'Tamil Nadu', 'violations': 4, 'scans': 27, 'compliant': 23},
  {'name': 'Tripura', 'violations': 6, 'scans': 47, 'compliant': 41},
  {'name': 'Uttar Pradesh', 'violations': 22, 'scans': 28, 'compliant': 6},
  {'name': 'Uttaranchal', 'violations': 3, 'scans': 28, 'compliant': 25},
  {'name': 'West Bengal', 'violations': 5, 'scans': 40, 'compliant': 35},
];

final int totalScans = regionalData.fold(0, (sum, item) => sum + (item['scans'] as int));
final int totalViolations = regionalData.fold(0, (sum, item) => sum + (item['violations'] as int));
final int totalCompliant = regionalData.fold(0, (sum, item) => sum + (item['compliant'] as int));

// Diversified Legal Metrology (Packaged Commodities) Rules, 2011
final List<String> violationTypes = [
  "Rule 4: Missing Mandatory Declarations",
  "Rule 6: Missing MRP / Care Details",
  "Rule 7: Font Size < Minimum Threshold",
  "Rule 9: Illegible / Non-English Text",
  "Rule 12: Non-Standard Unit of Measure",
  "Rule 18: Wholesale Identity Missing"
];

// Generates exactly violations to match the heatmap data
final List<Map<String, dynamic>> mockViolations = List.generate(totalViolations, (index) {
  if (index == 0) {
    return {
      "id": "REP-2026-942", 
      "product": "AquaPure 1L", 
      "inspector": "Harsh P.", 
      "violation": violationTypes[1], // Rule 6
      "status": "Pending Review", 
      "date": "Oct 16, 2026"
    };
  }
  if (index == 1) {
    return {
      "id": "REP-2026-943", 
      "product": "GlowCream 50g", 
      "inspector": "Rohan M.", 
      "violation": violationTypes[2], // Rule 7
      "status": "Notice Sent", 
      "date": "Oct 16, 2026"
    };
  }
  
  return {
    "id": "REP-2026-${941 - index}",
    "product": index % 2 == 0 ? "Textile Goods Batch $index" : "Agri Seeds 5kg",
    "inspector": index % 3 == 0 ? "Harsh P." : "Rohan M.",
    "violation": violationTypes[index % violationTypes.length],
    "status": "Notice Sent",
    "date": "Oct 15, 2026"
  };
});

// Generates exactly audit logs to match the total scans
final List<Map<String, String>> auditLogs = List.generate(totalScans, (index) {
  if (index == 0) return {'action': 'Inspector Login: Harsh P. (ID: INS-402)', 'timestamp': 'Oct 16, 2026 - 09:14 AM', 'type': 'Authentication', 'status': 'Success'};
  if (index == 1) return {'action': 'Product Scan Performed: AquaPure 1L', 'timestamp': 'Oct 16, 2026 - 10:32 AM', 'type': 'Field Scan', 'status': 'Flagged'};
  if (index == 2) return {'action': 'Inspector Login: Rohan M. (ID: INS-405)', 'timestamp': 'Oct 16, 2026 - 11:05 AM', 'type': 'Authentication', 'status': 'Success'};
  
  bool isViolation = index < totalViolations + 3;
  return {
    'action': 'Product Scan Performed: SKU-${1000 + index}', 
    'timestamp': 'Oct 15, 2026', 
    'type': 'Field Scan', 
    'status': isViolation ? 'Flagged' : 'Success'
  };
});
