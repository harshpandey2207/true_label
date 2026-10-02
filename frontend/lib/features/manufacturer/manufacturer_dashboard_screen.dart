import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import 'package:sidebarx/sidebarx.dart';
import '../admin/mock_data.dart';
import 'dart:ui' as ui;
import 'package:flutter/rendering.dart';
import 'package:flutter/foundation.dart';
import '../../core/report_viewer.dart';
import 'package:image_picker/image_picker.dart';
import '../../core/api_service.dart';

class ManufacturerDashboard extends StatefulWidget {
  const ManufacturerDashboard({super.key});

  @override
  State<ManufacturerDashboard> createState() => _ManufacturerDashboardState();
}

class _ManufacturerDashboardState extends State<ManufacturerDashboard> {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  Widget _buildSidebar(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: Color(0xFF1E1E1E)),
        textStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
        selectedTextStyle: TextStyle(color: Colors.greenAccent),
        iconTheme: IconThemeData(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
        selectedIconTheme: IconThemeData(color: Colors.greenAccent),
      ),
      extendedTheme: SidebarXTheme(
        width: 260,
        decoration: BoxDecoration(color: Color(0xFF1E1E1E)),
      ),
      items: [
        SidebarXItem(icon: Icons.qr_code_scanner, label: 'Pre-Market Scan'),
        SidebarXItem(icon: Icons.dashboard_outlined, label: 'Workspace Overview'),
        SidebarXItem(icon: Icons.business_center, label: 'Enterprise Registry'),
        SidebarXItem(icon: Icons.folder_shared, label: 'Audit & Reports'),
        SidebarXItem(icon: Icons.receipt_long, label: 'Statutory Fines'),
        SidebarXItem(icon: Icons.mark_email_unread, label: 'Active Legal Notices'),
        SidebarXItem(icon: Icons.auto_awesome, label: 'AI Label Studio'),
        SidebarXItem(icon: Icons.person, label: 'Manufacturer Profile'),
        SidebarXItem(icon: Icons.logout, label: 'Secure Logout'),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final isMobile = MediaQuery.of(context).size.width < 600;

    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text('Manufacturer Portal', style: theme.textTheme.titleLarge?.copyWith(fontSize: 18) ?? TextStyle(fontSize: 18)),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: () {
              themeProvider.toggleTheme();
            },
          ),
        ],
      ),
      drawer: isMobile ? Drawer(child: _buildSidebar(context)) : null,
      body: Row(
        children: [
          if (!isMobile) _buildSidebar(context),
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(isMobile ? 16.0 : 24.0),
              child: _ManufacturerScreensRouter(controller: _controller),
            ),
          ),
        ],
      ),
    );
  }
}

class _ManufacturerScreensRouter extends StatefulWidget {
  const _ManufacturerScreensRouter({super.key, required this.controller});
  final SidebarXController controller;

  @override
  State<_ManufacturerScreensRouter> createState() => _ManufacturerScreensRouterState();
}

class _ManufacturerScreensRouterState extends State<_ManufacturerScreensRouter> {
  String _missingTagsForGenerator = "";

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, child) {
        switch (widget.controller.selectedIndex) {
          case 0: return _BusinessOwnerScannerScreen(
            onNavigateToGenerator: (missingTags) {
              setState(() {
                _missingTagsForGenerator = missingTags;
              });
              widget.controller.selectIndex(6); // Switch to AI Label Generator
            },
          );
          case 1: return _ManufacturerOverviewScreen();
          case 2: return _EnterpriseRegistryScreen();
          case 3: return _BusinessOwnerRepositoryScreen();
          case 4: return _StatutoryFinesScreen();
          case 5: return _LegalNoticesScreen();
          case 6: return _AILabelGeneratorScreen(initialMissingTags: _missingTagsForGenerator);
          case 7: return _ProfileScreen();
          case 8: return const _LogoutScreen();
          default: return Center(child: Text('Screen not found', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)));
        }
      },
    );
  }
}

// --- 1. PRE-MARKET SCANNER WITH CATEGORY SELECTOR ---
class _BusinessOwnerScannerScreen extends StatefulWidget {
  final Function(String missingTags)? onNavigateToGenerator;
  const _BusinessOwnerScannerScreen({super.key, this.onNavigateToGenerator});

  @override
  __BusinessOwnerScannerScreenState createState() => __BusinessOwnerScannerScreenState();
}

class __BusinessOwnerScannerScreenState extends State<_BusinessOwnerScannerScreen> {
  int _scanState = 0; 
  String _processingText = "Initializing AI Vision...";
  String _selectedCategory = 'General Packaged Commodity';
  
  final List<XFile> _capturedImages = []; 
  List<dynamic>? _analysisResults; 
  bool _overallCompliance = false;
  final ImagePicker _picker = ImagePicker();

  final List<String> _productCategories = [
    'General Packaged Commodity',
    'Food & Beverages',
    'Electronics & Appliances',
    'Cosmetics, Ointments & Pharma Goods',
    'Apparel & Textiles',
  ];

  Future<void> _pickCameraImage() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 70, 
      maxWidth: 1200,   
      maxHeight: 1200,
    );
    if (photo == null) return;
    setState(() {
      _capturedImages.add(photo);
    });
  }

  Future<void> _pickMultipleGalleryImages() async {
    final List<XFile> photos = await _picker.pickMultiImage(
      imageQuality: 70,
      maxWidth: 1200,
      maxHeight: 1200,
    );
    if (photos.isNotEmpty) {
      setState(() {
        _capturedImages.addAll(photos);
      });
    }
  }

  Future<void> _runScan() async {
    if (_capturedImages.isEmpty) return;
    
    setState(() {
      _scanState = 1;
      _processingText = "Analyzing ${_capturedImages.length} images...";
    });

    try {
      final result = await ApiService.analyzeArScan(
        imageFiles: _capturedImages,
        distanceMm: 300.0,
        focalLengthPx: 800.0,
        categoryId: _productCategories.indexOf(_selectedCategory) + 1,
      );

      if (result != null && result['status'] == 'SUCCESS') {
        setState(() {
          _analysisResults = result['results'];
          _overallCompliance = _analysisResults!.every((r) => r['analysis']['status'] == 'COMPLIANT');
          _scanState = 2;
        });
      } else {
        final errorMsg = result?['error'] ?? "Failed to get analysis from backend.";
        _showError(errorMsg);
      }
    } catch (e) {
      _showError("Connection error: $e");
    }
  }

  void _showError(String msg) {
    setState(() => _scanState = 0);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(msg), backgroundColor: Colors.redAccent),
    );
  }

  void _resetScanner() {
    setState(() {
      _scanState = 0;
      _analysisResults = null;
      _capturedImages.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Pre-Market Compliance Scanner', style: TextStyle(color: textColor, fontSize: 28, fontWeight: FontWeight.bold)),
            if (_scanState != 0)
              IconButton(
                icon: Icon(Icons.refresh, color: textMuted),
                onPressed: _resetScanner,
                tooltip: "New Scan",
              )
          ],
        ),
        SizedBox(height: 16),
        
        if (_scanState == 0) _buildConfigurationState(theme, textColor, textMuted),
        if (_scanState == 1) _buildProcessingState(theme, textColor),
        if (_scanState == 2) _buildResultState(theme, textColor, textMuted),
      ],
    );
  }

  Widget _buildConfigurationState(ThemeData theme, Color textColor, Color textMuted) {
    return Expanded(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
              decoration: BoxDecoration(
                color: theme.cardColor,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: textMuted),
              ),
              child: DropdownButtonHideUnderline(
                child: DropdownButton<String>(
                  isExpanded: true,
                  value: _selectedCategory,
                  dropdownColor: theme.cardColor,
                  style: TextStyle(color: textColor, fontSize: 14),
                  icon: Icon(Icons.arrow_drop_down, color: Colors.greenAccent),
                  items: _productCategories.map((String category) {
                    return DropdownMenuItem<String>(value: category, child: Text(category, overflow: TextOverflow.ellipsis));
                  }).toList(),
                  onChanged: (String? newValue) => setState(() => _selectedCategory = newValue!),
                ),
              ),
            ),
            SizedBox(height: 20),
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: theme.cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.3), width: 2),
              ),
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  Icon(Icons.camera_alt_outlined, size: 64, color: Colors.greenAccent),
                  SizedBox(height: 16),
                  Text('Capture all sides of the product packaging', style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Ensure high-resolution images of the Principal Display Panel (PDP) and back labels for OCR Rule 7 geometry analysis.', 
                    textAlign: TextAlign.center, style: TextStyle(color: textMuted, fontSize: 14)),
                  SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.brightness == Brightness.dark ? Colors.grey[800] : Colors.grey[200],
                          padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                        ),
                        onPressed: _pickCameraImage,
                        icon: Icon(Icons.camera, color: textColor),
                        label: Text('Camera', style: TextStyle(color: textColor)),
                      ),
                      SizedBox(width: 16),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.brightness == Brightness.dark ? Colors.grey[800] : Colors.grey[200],
                          padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                        ),
                        onPressed: _pickMultipleGalleryImages,
                        icon: Icon(Icons.photo_library, color: textColor),
                        label: Text('Gallery', style: TextStyle(color: textColor)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            SizedBox(height: 24),
            if (_capturedImages.isNotEmpty) ...[
              Text('Captured Images (${_capturedImages.length})', style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold)),
              SizedBox(height: 12),
              SizedBox(
                height: 100,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _capturedImages.length,
                  itemBuilder: (context, index) {
                    return Container(
                      margin: EdgeInsets.only(right: 12),
                      width: 100,
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.greenAccent),
                        image: DecorationImage(
                          image: NetworkImage(_capturedImages[index].path),
                          fit: BoxFit.cover,
                        ),
                      ),
                    );
                  },
                ),
              ),
              SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
                  onPressed: _runScan,
                  icon: Icon(Icons.document_scanner, color: Colors.black),
                  label: Text('RUN COMPLIANCE SCAN', style: TextStyle(color: Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
                ),
              )
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildProcessingState(ThemeData theme, Color textColor) {
    return Expanded(
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            SizedBox(
              width: 80, height: 80,
              child: CircularProgressIndicator(color: Colors.greenAccent, strokeWidth: 6),
            ),
            SizedBox(height: 32),
            Text(_processingText, style: TextStyle(color: textColor, fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            Text("Extracting spatial OCR geometries...", style: TextStyle(color: Colors.greenAccent, fontSize: 14)),
          ],
        ),
      ),
    );
  }

  Widget _buildResultState(ThemeData theme, Color textColor, Color textMuted) {
    if (_analysisResults == null || _analysisResults!.isEmpty) {
      return Center(child: Text("No results returned.", style: TextStyle(color: textColor)));
    }

    final allMissingTags = <String>{};
    for (var r in _analysisResults!) {
      if (r['analysis']['missing_tags'] != null) {
        allMissingTags.addAll(List<String>.from(r['analysis']['missing_tags']));
      }
    }
    final missingTagsString = allMissingTags.join(", ");

    return Expanded(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: _overallCompliance ? Colors.green.withValues(alpha: 0.1) : Colors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _overallCompliance ? Colors.green : Colors.redAccent, width: 2),
              ),
              child: Column(
                children: [
                  Icon(
                    _overallCompliance ? Icons.check_circle : Icons.warning_amber_rounded,
                    color: _overallCompliance ? Colors.green : Colors.redAccent,
                    size: 64,
                  ),
                  SizedBox(height: 12),
                  Text(
                    _overallCompliance ? 'Product is Fully Compliant!' : 'Product is Non-Compliant',
                    style: TextStyle(color: textColor, fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    _overallCompliance 
                        ? 'All mandatory declarations under the Legal Metrology Act, 2011 were detected.'
                        : 'Missing mandatory declarations or formatting errors detected. See report below.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: textMuted, fontSize: 14),
                  ),
                  if (!_overallCompliance) ...[
                    SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                        onPressed: () {
                          if (widget.onNavigateToGenerator != null) {
                            widget.onNavigateToGenerator!(missingTagsString);
                          }
                        },
                        icon: Icon(Icons.auto_awesome, color: Colors.white),
                        label: Text('REMEDIATE WITH AI LABEL GENERATOR', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      ),
                    )
                  ]
                ],
              ),
            ),
            SizedBox(height: 24),
            Text('Detailed Image Reports', style: TextStyle(color: textColor, fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 16),
            
            ListView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: _analysisResults!.length,
              itemBuilder: (context, index) {
                final result = _analysisResults![index];
                final analysis = result['analysis'];
                final bool isCompliant = analysis['status'] == 'COMPLIANT';
                
                return Card(
                  color: theme.cardColor,
                  margin: EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(color: isCompliant ? Colors.green.withValues(alpha: 0.5) : Colors.red.withValues(alpha: 0.5)),
                  ),
                  child: ExpansionTile(
                    title: Text('Image ${index + 1}: ${isCompliant ? "Passed" : "Failed"}', style: TextStyle(color: textColor, fontWeight: FontWeight.bold)),
                    subtitle: Text('${analysis['declarations']?.length ?? 0} declarations found', style: TextStyle(color: textMuted)),
                    leading: Icon(isCompliant ? Icons.check_circle : Icons.cancel, color: isCompliant ? Colors.green : Colors.red),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('As per rules applicable on this product:', style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 16)),
                              SizedBox(height: 12),
                              
                              // 1. Show Detected Mandatory Rules
                              if (analysis['declarations'] != null)
                                ...((analysis['declarations'] as List).where((d) => d['tag'] != 'GENERAL').map((d) {
                                  return ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: Icon(d['is_compliant'] ? Icons.check_circle_outline : Icons.error_outline, 
                                        color: d['is_compliant'] ? Colors.green : Colors.red),
                                    title: Text(d['tag'], style: TextStyle(color: d['is_compliant'] ? Colors.greenAccent : Colors.redAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                                    subtitle: Text("\
", style: TextStyle(color: textMuted, fontSize: 12)),
                                  );
                                }).toList()),
                                
                              // 2. Show Missing Mandatory Rules
                              if (analysis['missing_tags'] != null && analysis['missing_tags'].isNotEmpty)
                                ...((analysis['missing_tags'] as List).map((t) {
                                  return ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: Icon(Icons.cancel, color: Colors.red),
                                    title: Text(t.toString(), style: TextStyle(color: Colors.redAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                                    subtitle: Text("Missing mandatory declaration. Zero compliance.", style: TextStyle(color: textMuted, fontSize: 12)),
                                  );
                                }).toList()),
                          ],
                        ),
                      )
                    ],
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}

// --- 2. WORKSPACE OVERVIEW (Dashboard) ---
class _ManufacturerOverviewScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final manufacturerViolations = mockViolations.where((v) => v['product'].toString().contains('AquaPure')).toList();
    
    final int registeredSKUs = 124; 
    final int activeInfractions = manufacturerViolations.length; 
    final int compliantProducts = registeredSKUs - activeInfractions;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Manufacturer Operations Workspace', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
          SizedBox(height: 24),
          _buildStatCard('Registered SKUs', registeredSKUs.toString(), Colors.blueAccent, theme),
          SizedBox(height: 12),
          _buildStatCard('Compliant Products', compliantProducts.toString(), Colors.greenAccent, theme),
          SizedBox(height: 12),
          _buildStatCard('Active Infractions', activeInfractions.toString(), Colors.redAccent, theme),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, Color color, ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Card(
      color: theme.cardColor,
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: SizedBox(
          width: double.infinity,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 16)),
              SizedBox(height: 12),
              Text(value, style: TextStyle(color: color, fontSize: 32, fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }
}

// --- 3. ENTERPRISE REGISTRY (Profile) ---
class _EnterpriseRegistryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Enterprise & Compliance Registry', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 8),
        Text('Official business identity, GSTIN registration, packer licenses, and certified product ledger.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
        SizedBox(height: 24),
        Expanded(
          child: ListView(
            children: [
              Card(
                color: theme.cardColor,
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Business Credentials & Identifiers', style: TextStyle(color: Colors.greenAccent, fontSize: 20, fontWeight: FontWeight.bold)),
                      Divider(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, height: 24),
                      _buildRegistryRow('Legal Entity Name:', 'AquaPure Industries Ltd.', theme),
                      _buildRegistryRow('GSTIN Number:', '24AABCA1234F1Z5', theme),
                      _buildRegistryRow('Legal Metrology Packer License:', 'LMP-MH-2026-9921', theme),
                      _buildRegistryRow('Registered District Office:', 'Indore Sector-4, Madhya Pradesh', theme),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 16),
              Card(
                color: theme.cardColor,
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Registered Active Product SKUs', style: TextStyle(color: Colors.blueAccent, fontSize: 20, fontWeight: FontWeight.bold)),
                      Divider(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, height: 24),
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: Icon(Icons.inventory, color: Colors.greenAccent),
                        title: Text('AquaPure Packaged Drinking Water 1L', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        subtitle: Text('SKU ID: SKU-8841 | Rule 6 & 7 Certified', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                        trailing: Text('Active', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                      ),
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: Icon(Icons.inventory, color: Colors.greenAccent),
                        title: Text('AquaPure Mineral Water 500ml', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        subtitle: Text('SKU ID: SKU-8842 | Rule 6 & 7 Certified', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                        trailing: Text('Active', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildRegistryRow(String label, String value, ThemeData theme) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 16)),
          Text(value, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
        ],
      ),
    );
  }
}

// --- 4. AUDIT & REPORTS ---
class _BusinessOwnerRepositoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final manufacturerLogs = auditLogs.where((log) => 
      log['action']!.contains('AquaPure') || log['action']!.contains('SKU-100')
    ).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Internal Audit & Compliance Repository', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 24),
        Expanded(
          child: ListView.builder(
            itemCount: manufacturerLogs.length,
            itemBuilder: (context, index) {
              final log = manufacturerLogs[index];
              final isFlagged = log['status'] == 'Flagged';
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(isFlagged ? Icons.warning : Icons.check_circle, color: isFlagged ? Colors.redAccent : Colors.greenAccent),
                title: Text('Internal Audit Scan #${1024 + index}', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                subtitle: Text('Status: ${log['status']} Ledger Record', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                trailing: IconButton(
                  icon: Icon(Icons.picture_as_pdf, color: Colors.blueAccent),
                  tooltip: 'View Report PDF',
                  onPressed: () {
                    ReportViewer.showPdfDialog(context: context, reportId: 'AUDIT-${1024 + index}', product: 'AquaPure 1L Water Bottle', violation: isFlagged ? 'Missing MRP (Rule 6)' : 'None');
                  },
                ),
              );
            },
          ),
        )
      ],
    );
  }
}

// --- 5. STATUTORY FINES ---
class _StatutoryFinesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Statutory Fines & Penalty Management', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 24),
        Card(
          color: const Color(0xFF2A1616),
          shape: RoundedRectangleBorder(side: BorderSide(color: Colors.redAccent, width: 1), borderRadius: BorderRadius.circular(8)),
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(child: Text('INFRACTION: Rule 6 Violation - Missing MRP', style: TextStyle(color: Colors.redAccent, fontSize: 20, fontWeight: FontWeight.bold))),
                  ],
                ),
                SizedBox(height: 4),
                Text('Issued: Oct 16, 2026', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                SizedBox(height: 12),
                Text('Product: AquaPure 1L (ID: REP-2026-942)\nPenalty Amount: ₹ 2,000', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, height: 1.5)),
                SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.green, padding: const EdgeInsets.symmetric(vertical: 12)),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Payment Successful. Receipt stored in repository.'), backgroundColor: Colors.green));
                    },
                    icon: Icon(Icons.payment, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                    label: Text('Pay Fine ₹ 2,000', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
                  ),
                ),
                SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(side: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), padding: const EdgeInsets.symmetric(vertical: 12)),
                    onPressed: () {},
                    icon: Icon(Icons.download, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                    label: Text('Download Official PDF', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                  ),
                )
              ],
            ),
          ),
        )
      ],
    );
  }
}

// --- 6. ACTIVE LEGAL NOTICES ---
class _LegalNoticesScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Active Legal Notices & Directives', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 24),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView(
              padding: const EdgeInsets.all(20),
              children: [
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Icon(Icons.warning, color: Colors.orangeAccent),
                  title: Text('Notice #NOT-2026-112: Packaging Verification Directive', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
                  subtitle: Padding(
                    padding: EdgeInsets.only(top: 8.0),
                    child: Text('Administration requires immediate re-verification of Batch #401 font sizing parameters under Legal Metrology Rule 7.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

// --- 7. AI LABEL STUDIO (DYNAMIC GENERATION) ---
class _AILabelGeneratorScreen extends StatefulWidget {
  final String? initialMissingTags;
  const _AILabelGeneratorScreen({super.key, this.initialMissingTags});

  @override
  __AILabelGeneratorScreenState createState() => __AILabelGeneratorScreenState();
}

class __AILabelGeneratorScreenState extends State<_AILabelGeneratorScreen> {
  bool _isGenerating = false;
  bool _showLabel = false;
  bool _isExporting = false;
  bool _hasReferenceImage = false;
  final GlobalKey _labelKey = GlobalKey();

  final _productNameController = TextEditingController(text: 'My Custom Product');
  final _shapeController = TextEditingController(text: 'Cylindrical Bottle Wrap');
  final _dimensionController = TextEditingController(text: '12cm x 6cm');
  late TextEditingController _promptController;
  
  // Dynamic controllers for missing tags
  final Map<String, TextEditingController> _missingTagControllers = {};
  List<String> _missingTags = [];

  String _rule7RequiredHeight = '4.0mm';

  @override
  void initState() {
    super.initState();
    String defaultPrompt = 'Make it look organic and premium. Use dark green accents, preserve the original brand DNA, and ensure Legal Metrology rules are followed.';
    
    if (widget.initialMissingTags != null && widget.initialMissingTags!.isNotEmpty) {
      _missingTags = widget.initialMissingTags!.split(',').map((e) => e.trim()).toList();
      for (var tag in _missingTags) {
        _missingTagControllers[tag] = TextEditingController();
      }
    }
    
    _promptController = TextEditingController(text: defaultPrompt);
  }

  @override
  void dispose() {
    _productNameController.dispose();
    _shapeController.dispose();
    _dimensionController.dispose();
    _promptController.dispose();
    for (var controller in _missingTagControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  void _generateLabel() {
    // Basic validation
    for (var tag in _missingTags) {
      if (_missingTagControllers[tag]!.text.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please provide a value for missing tag: $tag'), backgroundColor: Colors.red),
        );
        return;
      }
    }

    setState(() => _isGenerating = true);
    // Simulate AI Vision analysis and Code generation
    Future.delayed(const Duration(milliseconds: 2500), () {
      if (mounted) {
        setState(() {
          _isGenerating = false;
          _showLabel = true;
          // Dynamically compute Rule 7 height (simulated logic)
          _rule7RequiredHeight = _dimensionController.text.contains('cm') ? '4.0mm' : '6.0mm';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Generative Vision-to-Code complete! Legal Metrology injected.'), 
            backgroundColor: Colors.green
          ),
        );
      }
    });
  }

  void _resetForm() {
    setState(() {
      _showLabel = false;
      _isGenerating = false;
      _hasReferenceImage = false;
    });
  }

  Future<void> _exportLabel() async {
    setState(() => _isExporting = true);
    await Future.delayed(const Duration(milliseconds: 800)); // Simulate render delay
    
    try {
      final RenderRepaintBoundary boundary = _labelKey.currentContext!.findRenderObject() as RenderRepaintBoundary;
      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      final Uint8List pngBytes = byteData!.buffer.asUint8List();
      
      setState(() => _isExporting = false);
      
      if (mounted) {
        _showExportDialog(pngBytes);
      }
    } catch (e) {
      setState(() => _isExporting = false);
    }
  }

  void _showExportDialog(Uint8List pngBytes) {
    final theme = Theme.of(context);
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: theme.cardColor,
        title: Text('Export Production Ready Label', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
        content: SizedBox(
          width: 320,
          height: 440,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: Image.memory(pngBytes, fit: BoxFit.contain),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
          ),
          ElevatedButton.icon(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Saved for production packaging print!'), backgroundColor: Colors.green),
              );
            },
            icon: Icon(Icons.check, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
            label: Text('Accept & Save', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  Widget _buildInputField(String label, TextEditingController controller, String hint, ThemeData theme, {int maxLines = 1}) {
    return TextFormField(
      controller: controller,
      style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 14),
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        hintStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white38 : Colors.black38),
        labelStyle: TextStyle(color: Colors.greenAccent, fontSize: 13),
        enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), borderRadius: BorderRadius.circular(8)),
        focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.greenAccent), borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Generative AI Label Remediation Studio', 
                    style: TextStyle(color: textColor, fontSize: 28, fontWeight: FontWeight.bold)),
                  SizedBox(height: 6),
                  Text('Upload your current brand label. Vision AI will extract your brand DNA and write code to dynamically inject strict Legal Metrology compliance.', 
                    style: TextStyle(color: textMuted, fontSize: 14)),
                ],
              ),
            ),
            if (_showLabel)
              IconButton(
                onPressed: _resetForm,
                icon: Icon(Icons.refresh, color: textMuted),
              )
          ],
        ),
        SizedBox(height: 20),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Input Parameters Card
                Card(
                  color: theme.cardColor,
                  child: Padding(
                    padding: const EdgeInsets.all(20.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Image Upload Area
                        Text('1. Reference Brand Image', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        GestureDetector(
                          onTap: () => setState(() => _hasReferenceImage = true),
                          child: Container(
                            width: double.infinity,
                            height: 120,
                            decoration: BoxDecoration(
                              border: Border.all(color: _hasReferenceImage ? Colors.greenAccent : textMuted, width: 2, style: BorderStyle.solid),
                              borderRadius: BorderRadius.circular(8),
                              color: _hasReferenceImage ? Colors.greenAccent.withValues(alpha: 0.1) : theme.cardColor,
                            ),
                            child: Center(
                              child: _hasReferenceImage 
                                ? Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.check_circle, color: Colors.greenAccent, size: 32),
                                      SizedBox(height: 8),
                                      Text('Brand Image Analyzed by Vision AI', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold))
                                    ],
                                  )
                                : Column(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.cloud_upload_outlined, color: textMuted, size: 32),
                                      SizedBox(height: 8),
                                      Text('Click to upload current label or packaging image', style: TextStyle(color: textMuted))
                                    ],
                                  ),
                            ),
                          ),
                        ),
                        SizedBox(height: 24),
                        
                        Text('2. Target Shape, Product & Dimensions', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        Row(
                          children: [
                            Expanded(child: _buildInputField('Product Name', _productNameController, 'e.g. Pure Honey', theme)),
                            SizedBox(width: 12),
                            Expanded(child: _buildInputField('Shape', _shapeController, 'e.g. Cylindrical', theme)),
                            SizedBox(width: 12),
                            Expanded(child: _buildInputField('Dimensions', _dimensionController, 'e.g. 10cm x 15cm', theme)),
                          ],
                        ),
                        SizedBox(height: 24),

                        if (_missingTags.isNotEmpty) ...[
                          Text('3. Fill Missing Mandatory Data', style: TextStyle(color: Colors.redAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          SizedBox(height: 8),
                          Wrap(
                            spacing: 12,
                            runSpacing: 12,
                            children: _missingTags.map((tag) {
                              return SizedBox(
                                width: (MediaQuery.of(context).size.width / 2) - 10,
                                child: _buildInputField('Missing: $tag', _missingTagControllers[tag]!, 'Provide value for $tag', theme),
                              );
                            }).toList(),
                          ),
                          SizedBox(height: 24),
                        ],

                        Text('${_missingTags.isNotEmpty ? "4" : "3"}. Custom AI Prompt', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        _buildInputField('AI Instructions', _promptController, 'e.g. Use organic colors, preserve logo...', theme, maxLines: 3),
                        
                        SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
                            onPressed: (_isGenerating || !_hasReferenceImage) ? null : _generateLabel,
                            icon: _isGenerating 
                                ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, strokeWidth: 2)) 
                                : Icon(Icons.auto_awesome, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                            label: Text(
                              _isGenerating ? 'Synthesizing Generative Layout...' : 'GENERATE COMPLIANT LAYOUT', 
                              style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 15, fontWeight: FontWeight.bold)
                            ),
                          ),
                        )
                      ],
                    ),
                  ),
                ),
                SizedBox(height: 24),

                // Generated Visual Label Preview
                if (_showLabel)
                  RepaintBoundary(
                    key: _labelKey,
                    child: Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: _shapeController.text.toLowerCase().contains('circle') ? BorderRadius.circular(150) : BorderRadius.circular(12),
                        border: Border.all(color: Colors.greenAccent, width: 2),
                        boxShadow: [
                          BoxShadow(color: Colors.black12, blurRadius: 10, spreadRadius: 2),
                        ]
                      ),
                      child: ClipRRect(
                        borderRadius: _shapeController.text.toLowerCase().contains('circle') ? BorderRadius.circular(150) : BorderRadius.circular(10),
                        child: Column(
                          children: [
                            // Branding Section (Dynamic Product Name)
                            Container(
                              padding: const EdgeInsets.symmetric(vertical: 30, horizontal: 20),
                              width: double.infinity,
                              color: const Color(0xFF1B4332), // Dark organic green (simulated extraction)
                              child: Column(
                                children: [
                                  Icon(Icons.auto_awesome, size: 48, color: Colors.greenAccent),
                                  SizedBox(height: 12),
                                  Text(
                                    _productNameController.text.toUpperCase(),
                                    style: TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold, letterSpacing: 2),
                                    textAlign: TextAlign.center,
                                  ),
                                  Text(
                                    'AI GENERATED LABEL',
                                    style: TextStyle(color: Colors.greenAccent, fontSize: 12, letterSpacing: 1),
                                  ),
                                ],
                              ),
                            ),
                            // Legal Metrology Section (Dynamic Injection)
                            Container(
                              padding: const EdgeInsets.all(24.0),
                              color: Colors.white,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('LEGAL METROLOGY DECLARATIONS', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w800, fontSize: 16)),
                                  SizedBox(height: 16),
                                  
                                  // Map over provided missing tags dynamically
                                  ..._missingTags.map((tag) {
                                    return Column(
                                      children: [
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: [
                                            Text('$tag:', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w600, fontSize: 12)),
                                            Text(_missingTagControllers[tag]!.text, style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 14)), // Required height 4mm dynamically applied
                                          ],
                                        ),
                                        Divider(color: Colors.grey.shade300),
                                      ],
                                    );
                                  }).toList(),

                                  // Simulated additional compliance lines to look complete if missing tags were few
                                  if (!_missingTags.contains('NET_QUANTITY')) ...[
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text('NET QUANTITY:', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w600, fontSize: 12)),
                                        Text('100g', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 14)),
                                      ],
                                    ),
                                    Divider(color: Colors.grey.shade300),
                                  ],
                                  if (!_missingTags.contains('MRP')) ...[
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text('MRP (Incl. taxes):', style: TextStyle(color: Colors.black87, fontWeight: FontWeight.w600, fontSize: 12)),
                                        Text('₹100.00', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 14)),
                                      ],
                                    ),
                                    Divider(color: Colors.grey.shade300),
                                  ],

                                  SizedBox(height: 16),
                                  // Rule 7 Simulation Badge
                                  Container(
                                    padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                    decoration: BoxDecoration(
                                      color: Colors.grey.shade100,
                                      border: Border.all(color: Colors.greenAccent),
                                      borderRadius: BorderRadius.circular(4)
                                    ),
                                    child: Row(
                                      children: [
                                        Icon(Icons.verified, color: Colors.green, size: 16),
                                        SizedBox(width: 8),
                                        Expanded(child: Text('Rule 7 Verified: Numerals formatted to ${_rule7RequiredHeight} minimum height for ${_dimensionController.text} ${_shapeController.text} area.', style: TextStyle(color: Colors.black87, fontSize: 11))),
                                      ],
                                    ),
                                  )
                                ],
                              ),
                            )
                          ],
                        ),
                      ),
                    ),
                  ),

                if (_showLabel) ...[
                  SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton.icon(
                        onPressed: () {},
                        icon: Icon(Icons.code, color: Colors.greenAccent),
                        label: Text('View Generated SVG Code', style: TextStyle(color: Colors.greenAccent)),
                      ),
                      SizedBox(width: 12),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                        onPressed: _isExporting ? null : _exportLabel,
                        icon: _isExporting 
                            ? SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : Icon(Icons.download, color: Colors.white),
                        label: Text('Export Label Ready for Print', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      )
                    ],
                  )
                ]
              ],
            ),
          ),
        ),
      ],
    );
  }
}
