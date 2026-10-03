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
import 'package:flutter_svg/flutter_svg.dart';
import '../../core/api_service.dart';
import '../../core/svg_export.dart';

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
        SidebarXItem(icon: Icons.receipt_long, label: 'Penalty Demo'),
        SidebarXItem(icon: Icons.mark_email_unread, label: 'Notice Workflow Demo'),
        SidebarXItem(icon: Icons.auto_awesome, label: 'Label Draft Studio'),
        SidebarXItem(icon: Icons.person, label: 'Manufacturer Profile'),
        SidebarXItem(icon: Icons.logout, label: 'Back to role selection'),
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
  Map<String, String> _scannedTagValuesForGenerator = {};
  String _generatorCategory = 'General Packaged Commodity';

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, child) {
        switch (widget.controller.selectedIndex) {
          case 0: return _BusinessOwnerScannerScreen(
            onNavigateToGenerator: (missingTags, tagValues, category) {
              setState(() {
                _missingTagsForGenerator = missingTags;
                _scannedTagValuesForGenerator = tagValues;
                _generatorCategory = category;
              });
              widget.controller.selectIndex(6); // Switch to AI Label Generator
            },
          );
          case 1: return _ManufacturerOverviewScreen();
          case 2: return _EnterpriseRegistryScreen();
          case 3: return _BusinessOwnerRepositoryScreen();
          case 4: return _StatutoryFinesScreen();
          case 5: return _LegalNoticesScreen();
          case 6: return _AILabelGeneratorScreen(
            initialMissingTags: _missingTagsForGenerator,
            initialTagValues: _scannedTagValuesForGenerator,
            initialCategory: _generatorCategory,
          );
          case 7: return Center(child: Text('Manufacturer Profile'));
          case 8: return Center(child: Text('Logout'));
          default: return Center(child: Text('Screen not found', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)));
        }
      },
    );
  }
}

// --- 1. PRE-MARKET SCANNER WITH CATEGORY SELECTOR ---
class _BusinessOwnerScannerScreen extends StatefulWidget {
  final Function(String missingTags, Map<String, String> tagValues, String category)? onNavigateToGenerator;
  const _BusinessOwnerScannerScreen({super.key, this.onNavigateToGenerator});

  @override
  __BusinessOwnerScannerScreenState createState() => __BusinessOwnerScannerScreenState();
}

class __BusinessOwnerScannerScreenState extends State<_BusinessOwnerScannerScreen> {
  int _scanState = 0; 
  String _processingText = "Preparing local text recognition...";
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
    'Medical Devices',
  ];

  Future<void> _pickCameraImage() async {
    if (_capturedImages.length >= 6) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('A scan can include up to six package-side images.')));
      return;
    }
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 70, 
      maxWidth: 1200,   
      maxHeight: 1200,
    );
    if (!mounted || photo == null) return;
    setState(() {
      _capturedImages.add(photo);
    });
  }

  Future<void> _pickMultipleGalleryImages() async {
    final remaining = 6 - _capturedImages.length;
    if (remaining <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('A scan can include up to six package-side images.')));
      return;
    }
    final List<XFile> photos = await _picker.pickMultiImage(
      imageQuality: 70,
      maxWidth: 1200,
      maxHeight: 1200,
    );
    if (mounted && photos.isNotEmpty) {
      setState(() {
        _capturedImages.addAll(photos.take(remaining));
      });
      if (photos.length > remaining) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('This scan supports six images. Extra selections were skipped.')));
      }
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
        categoryName: _selectedCategory,
      );

      if (result != null && result['status'] == 'SUCCESS') {
        setState(() {
          _analysisResults = result['results'];
          _overallCompliance = _analysisResults!.every((r) => r['analysis']['status'] == 'NO_FLAGS');
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
                  Text('Upload clear, straight-on photos of the front, back and other package sides. Text-size values are rough estimates and are not used to determine scan status.',
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
                        _overallCompliance ? 'No issues detected in this scan' : 'Potential label issues detected',
                    style: TextStyle(color: textColor, fontSize: 24, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    _overallCompliance 
                        ? 'The prototype screening found no flags in its selected checks. Text-size values are rough estimates and are not used to determine status. Review current requirements before relying on this result.'
                        : 'Some declarations were not found or need review. Text-size values are rough estimates; check the source images, current requirements and findings below.',
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
                            final tagValues = <String, String>{};
                            for (final result in _analysisResults ?? const []) {
                              final analysis = result['analysis'] as Map<String, dynamic>? ?? {};
                              for (final declaration in (analysis['declarations'] as List? ?? const [])) {
                                final tag = declaration['tag']?.toString() ?? '';
                                final value = declaration['text']?.toString() ?? '';
                                if (tag.isNotEmpty && tag.toUpperCase() != 'GENERAL' && value.isNotEmpty) {
                                  tagValues.putIfAbsent(tag, () => value);
                                }
                              }
                            }
                            widget.onNavigateToGenerator!(missingTagsString, tagValues, _selectedCategory);
                          }
                        },
                        icon: Icon(Icons.auto_awesome, color: Colors.white),
                        label: Text('CREATE A LABEL DRAFT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
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
                final bool noFlags = analysis['status'] == 'NO_FLAGS';
                
                return Card(
                  color: theme.cardColor,
                  margin: EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(color: noFlags ? Colors.green.withValues(alpha: 0.5) : Colors.red.withValues(alpha: 0.5)),
                  ),
                  child: ExpansionTile(
                    title: Text('Image ${index + 1}: ${noFlags ? "No flags" : "Potential flags"}', style: TextStyle(color: textColor, fontWeight: FontWeight.bold)),
                    subtitle: Text('${analysis['declarations']?.length ?? 0} declarations found', style: TextStyle(color: textMuted)),
                    leading: Icon(noFlags ? Icons.check_circle : Icons.cancel, color: noFlags ? Colors.green : Colors.red),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Prototype screening findings — verify rule applicability:', style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 16)),
                              SizedBox(height: 12),
                              
                              // 1. Show Detected Mandatory Rules
                              if (analysis['declarations'] != null)
                                ...((analysis['declarations'] as List).where((d) => d['tag'] != 'GENERAL').map((d) {
                                  return ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: Icon(d['is_compliant'] ? Icons.check_circle_outline : Icons.error_outline, 
                                        color: d['is_compliant'] ? Colors.green : Colors.red),
                                    title: Text(d['tag'], style: TextStyle(color: d['is_compliant'] ? Colors.greenAccent : Colors.redAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                                    subtitle: Text("\n", style: TextStyle(color: textMuted, fontSize: 12)),
                                  );
                                }).toList()),
                                
                              // 2. Show Missing Mandatory Rules
                              if (analysis['missing_tags'] != null && analysis['missing_tags'].isNotEmpty)
                                ...((analysis['missing_tags'] as List).map((t) {
                                  return ListTile(
                                    contentPadding: EdgeInsets.zero,
                                    leading: Icon(Icons.cancel, color: Colors.red),
                                    title: Text(t.toString(), style: TextStyle(color: Colors.redAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                                    subtitle: Text("Not detected in the selected prototype rule set. Verify against the package and applicable rules.", style: TextStyle(color: textMuted, fontSize: 12)),
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
          Text('Manufacturer Operations Workspace (Sample)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text('Static demonstration numbers; product registry and audit records are not connected.', style: TextStyle(color: textMuted)),
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
        Text('Enterprise & Compliance Registry (Sample)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 8),
        Text('Demo profile data only. No business identity, licence or product registry is connected.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
                        subtitle: Text('Sample SKU ID: SKU-8841 | No certification is connected', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                        trailing: Text('Active', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                      ),
                      ListTile(
                        contentPadding: EdgeInsets.zero,
                        leading: Icon(Icons.inventory, color: Colors.greenAccent),
                        title: Text('AquaPure Mineral Water 500ml', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        subtitle: Text('Sample SKU ID: SKU-8842 | No certification is connected', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
        Text('Sample Audit & Reports', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text('Static sample records. A report preview is an automated screening summary, not an official document.', style: TextStyle(color: textMuted)),
        SizedBox(height: 24),
        Expanded(
          child: ListView.builder(
            itemCount: manufacturerLogs.length,
            itemBuilder: (context, index) {
              final log = manufacturerLogs[index];
              final isFlagged = log['status'].toString().toLowerCase().contains('flag');
              return ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(isFlagged ? Icons.warning : Icons.check_circle, color: isFlagged ? Colors.redAccent : Colors.greenAccent),
                title: Text('Internal Audit Scan #${1024 + index}', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                subtitle: Text('Status: ${log['status']} Ledger Record', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                trailing: IconButton(
                  icon: Icon(Icons.picture_as_pdf, color: Colors.blueAccent),
                  tooltip: 'View Report PDF',
                  onPressed: () {
                    ReportViewer.showPdfDialog(context: context, reportId: 'AUDIT-${1024 + index}', product: 'AquaPure 1L Water Bottle', findingsOrNotes: isFlagged ? 'Sample: MRP field needs review.' : 'Sample: no flags in the configured checks.', noFlagsDetected: !isFlagged);
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
        Text('Penalty Workflow Demo', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 24),
        Text('The example record below is sample data. This screen is not connected to a regulator, payment service or official notice system.', style: TextStyle(color: textMuted)),
        SizedBox(height: 12),
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
                    Expanded(child: Text('SAMPLE: Potential missing MRP field', style: TextStyle(color: Colors.redAccent, fontSize: 20, fontWeight: FontWeight.bold))),
                  ],
                ),
                SizedBox(height: 4),
                Text('Sample record', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                SizedBox(height: 12),
                Text('Example product: AquaPure 1L\nExample amount: ₹ 2,000', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, height: 1.5)),
                SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.green, padding: const EdgeInsets.symmetric(vertical: 12)),
                    onPressed: null,
                    icon: Icon(Icons.payment, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                    label: Text('Payment service not connected', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
                  ),
                ),
                SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    style: OutlinedButton.styleFrom(side: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), padding: const EdgeInsets.symmetric(vertical: 12)),
                    onPressed: null,
                    icon: Icon(Icons.download, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                    label: Text('Official PDF unavailable', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
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
        Text('Notice Workflow Demo', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text('The example below is not an issued notice and is not connected to a regulator.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
                  title: Text('Sample notice: Packaging verification', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
                  subtitle: Padding(
                    padding: EdgeInsets.only(top: 8.0),
                    child: Text('This example shows where a manual review reminder could appear. No case or batch record is connected.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
  final Map<String, String> initialTagValues;
  final String initialCategory;
  const _AILabelGeneratorScreen({
    super.key,
    this.initialMissingTags,
    this.initialTagValues = const {},
    this.initialCategory = 'General Packaged Commodity',
  });

  @override
  __AILabelGeneratorScreenState createState() => __AILabelGeneratorScreenState();
}

class __AILabelGeneratorScreenState extends State<_AILabelGeneratorScreen> with TickerProviderStateMixin {
  bool _isGenerating = false;
  Map<String, dynamic>? _labelData;
  String? _errorMessage;
  String? _engineInfo;
  List<String> _warnings = [];
  int _selectedSideIndex = 0;
  TabController? _sideTabController;
  String _selectedCategory = 'General Packaged Commodity';
  int _sideCount = 2;

  final _productNameController = TextEditingController(text: 'My Product');
  final _shapeController = TextEditingController();
  final _dimensionController = TextEditingController();
  final _promptController = TextEditingController();
  final _additionalDetailsController = TextEditingController();
  
  final Map<String, TextEditingController> _labelValueControllers = {};
  List<String> _missingTags = [];
  
  final List<XFile> _referenceImages = [];
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    _selectedCategory = widget.initialCategory;
    if (widget.initialMissingTags != null && widget.initialMissingTags!.isNotEmpty) {
      _missingTags = widget.initialMissingTags!.split(',').map((e) => e.trim()).where((t) => t.isNotEmpty).toList();
    }
    _ensureValueControllers();
  }

  @override
  void dispose() {
    _productNameController.dispose();
    _shapeController.dispose();
    _dimensionController.dispose();
    _promptController.dispose();
    _additionalDetailsController.dispose();
    _sideTabController?.dispose();
    for (var c in _labelValueControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _pickImages() async {
    final List<XFile> photos = await _picker.pickMultiImage(imageQuality: 80);
    if (photos.isNotEmpty) {
      setState(() {
        _referenceImages.clear();
        _referenceImages.addAll(photos.take(6));
      });
      if (photos.length > 6 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Use up to six package-side images. The first six were selected.')),
        );
      }
    }
  }

  List<String> _categoryFields(String category) {
    const categoryFields = <String, List<String>>{
      'Food & Beverages': ['batch_code', 'best_before_date', 'fssai_license', 'veg_non_veg_logo', 'ingredients'],
      'Electronics & Appliances': ['model', 'bis_mark', 'country_of_origin', 'e_waste_info'],
      'Cosmetics, Ointments & Pharma Goods': ['batch_code', 'expiry_date', 'manufacturing_license', 'ingredients'],
      'Apparel & Textiles': ['size', 'fibre_content', 'country_of_origin'],
      'Medical Devices': ['batch_code', 'serial_number', 'license_no', 'sterile_status'],
    };
    return [
      'manufacturer', 'commodity_name', 'net_quantity', 'manufacturing_date', 'mrp', 'unit_sale_price', 'consumer_care',
      ...(categoryFields[category] ?? const <String>[]),
    ];
  }

  String _fieldTitle(String tag) {
    const labels = <String, String>{
      'manufacturer': 'Manufacturer / packer / importer details',
      'commodity_name': 'Common / generic commodity name',
      'net_quantity': 'Net quantity',
      'manufacturing_date': 'Manufacturing / packing date',
      'mrp': 'MRP (inclusive of taxes)',
      'consumer_care': 'Consumer care details',
      'unit_sale_price': 'Unit sale price (if applicable)',
      'batch_code': 'Batch / lot number',
      'best_before_date': 'Best before / expiry',
      'fssai_license': 'FSSAI licence / registration',
      'veg_non_veg_logo': 'Food symbol / declaration',
      'ingredients': 'Ingredients / allergen information',
      'bis_mark': 'BIS registration / mark (if applicable)',
      'model': 'Model / product ID',
      'country_of_origin': 'Country of origin',
      'e_waste_info': 'E-waste information (if applicable)',
      'manufacturing_license': 'Manufacturing licence',
      'expiry_date': 'Expiry date',
      'size': 'Size',
      'fibre_content': 'Fibre content',
      'serial_number': 'Serial number',
      'license_no': 'Licence number',
      'sterile_status': 'Sterile status',
      'language_check': 'Language / declaration text',
    };
    final key = tag.toLowerCase().replaceAll(' ', '_').replaceAll('-', '_');
    return labels[key] ?? tag.replaceAll('_', ' ').toLowerCase().split(' ').map((w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}').join(' ');
  }

  void _ensureValueControllers() {
    final keys = <String>{
      ..._categoryFields(_selectedCategory),
      ..._missingTags.map((tag) => tag.toLowerCase()),
      ...widget.initialTagValues.keys.map((tag) => tag.toLowerCase()),
    };
    for (final tag in keys) {
      _labelValueControllers.putIfAbsent(
        tag,
        () {
          final entry = widget.initialTagValues.entries.firstWhere(
            (entry) => entry.key.toLowerCase() == tag,
            orElse: () => const MapEntry('', ''),
          );
          return TextEditingController(text: entry.value);
        },
      );
    }
  }

  Future<void> _generateLabel() async {
    // Validate required fields
    for (var tag in _missingTags) {
      if (_labelValueControllers[tag.toLowerCase()]?.text.trim().isEmpty ?? true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Please provide a value for: $tag'), backgroundColor: Colors.red),
        );
        return;
      }
    }

    setState(() {
      _isGenerating = true;
      _errorMessage = null;
      _labelData = null;
    });

    final Map<String, String> tagValues = {};
    for (final entry in _labelValueControllers.entries) {
      if (entry.value.text.trim().isNotEmpty) {
        tagValues[entry.key] = entry.value.text.trim();
      }
    }

    final result = await ApiService.generateLabel(
      imageFiles: _referenceImages,
      productName: _productNameController.text.trim(),
      productCategory: _selectedCategory,
      shape: _shapeController.text.trim(),
      dimensions: _dimensionController.text.trim(),
      customPrompt: _promptController.text.trim(),
      missingTagValues: tagValues,
      additionalDetails: _additionalDetailsController.text.trim(),
      sideCount: _sideCount,
    );

    if (!mounted) return;

    if (result != null && result['success'] == true) {
      final sides = (result['label_data']['sides'] as List?) ?? [];
      _sideTabController?.dispose();
      _sideTabController = sides.isEmpty ? null : TabController(length: sides.length, vsync: this);
      setState(() {
        _isGenerating = false;
        _labelData = result['label_data'];
        _engineInfo = result['engine_used']?.toString();
        _warnings = (result['warnings'] as List? ?? const []).map((value) => value.toString()).toList();
        _selectedSideIndex = 0;
      });
    } else {
      setState(() {
        _isGenerating = false;
        _errorMessage = result?['error'] ?? 'Could not generate this label draft.';
      });
    }
  }

  void _resetForm() {
    setState(() {
      _labelData = null;
      _errorMessage = null;
      _engineInfo = null;
      _warnings = [];
      _referenceImages.clear();
    });
  }

  Color _parseColor(String hex) {
    try {
      final h = hex.replaceAll('#', '');
      return Color(int.parse('FF$h', radix: 16));
    } catch (_) {
      return const Color(0xFF1B4332);
    }
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
        labelStyle: const TextStyle(color: Colors.greenAccent, fontSize: 13),
        enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white54 : Colors.black54), borderRadius: BorderRadius.circular(8)),
        focusedBorder: OutlineInputBorder(borderSide: const BorderSide(color: Colors.greenAccent), borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  Widget _buildGeneratedLabelCard(Map<String, dynamic> side, Map<String, dynamic> brandDna, ThemeData theme) {
    final svgCode = side['svg_code'] as String? ?? '';
    final sideName = side['side_name'] ?? 'Generated Label';
    
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.greenAccent, width: 2),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 10, spreadRadius: 2)],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
            decoration: const BoxDecoration(
              color: Colors.black87,
              borderRadius: BorderRadius.only(topLeft: Radius.circular(10), topRight: Radius.circular(10)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(sideName.toUpperCase(), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, letterSpacing: 1)),
                const Icon(Icons.code, color: Colors.greenAccent, size: 20),
              ],
            ),
          ),
          if (svgCode.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              // The API returns locally-rendered SVG using escaped user copy.
              child: SvgPicture.string(
                svgCode,
                fit: BoxFit.contain,
                width: double.infinity,
                placeholderBuilder: (BuildContext context) => Container(
                    padding: const EdgeInsets.all(30.0),
                    child: const CircularProgressIndicator()),
              ),
            )
          else
            const Padding(
              padding: EdgeInsets.all(32.0),
              child: Center(child: Text("No artwork was returned for this side.", style: TextStyle(color: Colors.red))),
            ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;

    final sides = (_labelData?['sides'] as List?) ?? [];
    final brandDna = (_labelData?['brand_dna'] as Map?) ?? {};
    final selectedSide = sides.isNotEmpty
        ? sides[_selectedSideIndex] as Map<String, dynamic>
        : <String, dynamic>{};

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
                  Text('Label Draft Studio', style: TextStyle(color: textColor, fontSize: 26, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text('Create side-by-side editable SVG drafts from package photos or a written brief. Review every declaration before printing.', style: TextStyle(color: textMuted, fontSize: 13)),
                ],
              ),
            ),
            if (_labelData != null)
              IconButton(onPressed: _resetForm, icon: Icon(Icons.refresh, color: textMuted), tooltip: 'Start Over'),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_labelData == null) ...[
                  // === INPUT FORM ===
                  Card(
                    color: theme.cardColor,
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Reference images are optional: prompt-only label drafts are supported.
                          Text('1. Reference package photos (optional)', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          GestureDetector(
                            onTap: _pickImages,
                            child: Container(
                              width: double.infinity,
                              height: 120,
                              decoration: BoxDecoration(
                                border: Border.all(color: _referenceImages.isNotEmpty ? Colors.greenAccent : textMuted, width: 2),
                                borderRadius: BorderRadius.circular(8),
                                color: _referenceImages.isNotEmpty ? Colors.greenAccent.withValues(alpha: 0.05) : theme.cardColor,
                              ),
                              child: Center(
                                child: _referenceImages.isNotEmpty
                                  ? Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                                      const Icon(Icons.check_circle, color: Colors.greenAccent, size: 32),
                                      const SizedBox(height: 8),
                                      Text('${_referenceImages.length} image(s) selected — one draft will be made per image', style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                                      const SizedBox(height: 4),
                                      Text(_referenceImages.map((image) => image.name).join('  •  '), maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(color: textMuted, fontSize: 11)),
                                    ])
                                  : Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                                      Icon(Icons.cloud_upload_outlined, color: textMuted, size: 32),
                                      const SizedBox(height: 8),
                                      Text('Tap to upload front, back or other side photos', style: TextStyle(color: textMuted)),
                                      Text('Files named Front, Back, Left, Right, Top or Bottom keep those side names.', style: TextStyle(color: textMuted, fontSize: 12)),
                                    ]),
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          Text('2. Product and package details', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          DropdownButtonFormField<String>(
                            value: _selectedCategory,
                            decoration: const InputDecoration(labelText: 'Product category'),
                            items: const [
                              'General Packaged Commodity', 'Food & Beverages', 'Electronics & Appliances',
                              'Cosmetics, Ointments & Pharma Goods', 'Apparel & Textiles', 'Medical Devices',
                            ].map((category) => DropdownMenuItem(value: category, child: Text(category))).toList(),
                            onChanged: (category) {
                              if (category == null) return;
                              setState(() {
                                _selectedCategory = category;
                                _ensureValueControllers();
                              });
                            },
                          ),
                          const SizedBox(height: 12),
                          Wrap(spacing: 12, runSpacing: 12, children: [
                            SizedBox(width: (MediaQuery.of(context).size.width / 2) - 48, child: _buildInputField('Product name', _productNameController, 'e.g. Pure Honey', theme)),
                            SizedBox(width: (MediaQuery.of(context).size.width / 2) - 48, child: _buildInputField('Package shape', _shapeController, 'e.g. carton, bottle, pouch', theme)),
                            SizedBox(width: (MediaQuery.of(context).size.width / 2) - 48, child: _buildInputField('Finished label size', _dimensionController, 'e.g. 10 cm x 15 cm', theme)),
                          ]),
                          const SizedBox(height: 24),

                          Text('3. Declarations and product copy', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          Text('Scanner values are prefilled where detected. Missing fields are highlighted; enter the exact approved wording.', style: TextStyle(color: textMuted, fontSize: 12)),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 12,
                            runSpacing: 12,
                            children: (_categoryFields(_selectedCategory).toSet()
                                  ..addAll(_missingTags.map((tag) => tag.toLowerCase()))
                                  ..addAll(widget.initialTagValues.keys.map((tag) => tag.toLowerCase())))
                                .map((tag) => SizedBox(
                                  width: (MediaQuery.of(context).size.width / 2) - 48,
                                  child: _buildInputField(
                                    _missingTags.any((missing) => missing.toLowerCase() == tag) ? 'Missing in scan: ${_fieldTitle(tag)}' : _fieldTitle(tag),
                                    _labelValueControllers[tag]!,
                                    'Enter label text',
                                    theme,
                                  ),
                                )).toList(),
                          ),
                          const SizedBox(height: 24),

                          Text('4. Extra declarations or product features', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          _buildInputField('Additional label text (one item per line)', _additionalDetailsController, 'e.g. Storage: Keep in a cool, dry place', theme, maxLines: 3),
                          const SizedBox(height: 20),
                          Text('5. Design brief', style: TextStyle(color: Colors.greenAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 8),
                          _buildInputField('Describe style and features to retain', _promptController, 'e.g. earthy green, minimal, reserve a logo/artwork space', theme, maxLines: 3),
                          const SizedBox(height: 8),
                          Text('The local renderer uses the brief for simple style choices and can reserve an artwork box. It does not reproduce logos, photos or barcodes from the reference.', style: TextStyle(color: textMuted, fontSize: 12)),
                          const SizedBox(height: 24),

                          if (_referenceImages.isEmpty) ...[
                            DropdownButtonFormField<int>(
                              value: _sideCount,
                              decoration: const InputDecoration(labelText: 'Package sides to draft'),
                              items: const [2, 4, 6].map((count) => DropdownMenuItem(value: count, child: Text('$count sides'))).toList(),
                              onChanged: (count) => setState(() => _sideCount = count ?? 2),
                            ),
                            const SizedBox(height: 20),
                          ],

                          SizedBox(
                            width: double.infinity,
                            height: 52,
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
                              onPressed: _isGenerating ? null : _generateLabel,
                              icon: _isGenerating
                                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.black, strokeWidth: 2))
                                  : const Icon(Icons.auto_awesome, color: Colors.black),
                              label: Text(
                                _isGenerating ? 'Building label drafts...' : 'GENERATE LABEL DRAFTS',
                                style: const TextStyle(color: Colors.black, fontSize: 14, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ),

                          if (_isGenerating) ...[
                            const SizedBox(height: 16),
                            Center(child: Text('Applying local templates to ${_referenceImages.isEmpty ? _sideCount : _referenceImages.length} package side(s)...', style: TextStyle(color: textMuted, fontSize: 12), textAlign: TextAlign.center)),
                          ],

                          if (_errorMessage != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(color: Colors.red.shade50, border: Border.all(color: Colors.red), borderRadius: BorderRadius.circular(8)),
                              child: Row(children: [
                                const Icon(Icons.error, color: Colors.red),
                                const SizedBox(width: 8),
                                Expanded(child: Text(_errorMessage!, style: const TextStyle(color: Colors.red))),
                              ]),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ),
                ] else ...[
                  // === GENERATED DRAFT OUTPUT ===
                  Card(
                    color: theme.cardColor,
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Local style sample', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold, fontSize: 14)),
                          const SizedBox(height: 12),
                          Wrap(spacing: 12, runSpacing: 8, children: [
                            _colorChip(selectedSide['sampled_primary_color'] ?? brandDna['primary_color'] ?? '#1B4332', 'Primary'),
                            _colorChip(selectedSide['sampled_secondary_color'] ?? brandDna['secondary_color'] ?? '#FFFFFF', 'Secondary'),
                            _colorChip(selectedSide['sampled_accent_color'] ?? brandDna['accent_color'] ?? '#52B788', 'Accent'),
                          ]),
                          if ((brandDna['font_style'] ?? '').isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text('Font: ${brandDna['font_style']}', style: TextStyle(color: textMuted, fontSize: 13)),
                          ],
                          if ((brandDna['design_aesthetic'] ?? '').isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text('Design: ${brandDna['design_aesthetic']}', style: TextStyle(color: textMuted, fontSize: 13)),
                          ],
                          if (_engineInfo != null) ...[
                            const SizedBox(height: 8),
                            Text(_engineInfo!, style: TextStyle(color: textMuted, fontSize: 12)),
                          ],
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),

                  if (_warnings.isNotEmpty)
                    Card(
                      color: Colors.amber.withValues(alpha: 0.12),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: _warnings.map((warning) => Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Text('• $warning', style: TextStyle(color: textColor, fontSize: 12)),
                          )).toList(),
                        ),
                      ),
                    ),

                  // Side tabs
                  if (sides.length > 1 && _sideTabController != null) ...[
                    TabBar(
                      controller: _sideTabController,
                      isScrollable: true,
                      labelColor: Colors.greenAccent,
                      unselectedLabelColor: textMuted,
                      indicatorColor: Colors.greenAccent,
                      onTap: (i) => setState(() => _selectedSideIndex = i),
                      tabs: sides.asMap().entries.map((e) => Tab(text: e.value['side_name'] ?? 'Side ${e.key + 1}')).toList(),
                    ),
                    const SizedBox(height: 16),
                  ],

                  // Selected side label
                  if (sides.isNotEmpty)
                    _buildGeneratedLabelCard(
                      selectedSide,
                      brandDna as Map<String, dynamic>,
                      theme,
                    ),

                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () async {
                          final svg = selectedSide['svg_code']?.toString() ?? '';
                          final productSlug = _productNameController.text.trim().replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '-');
                          final sideSlug = (selectedSide['side_name']?.toString() ?? 'side').replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '-');
                          final saved = await saveSvgDraft('${productSlug}_$sideSlug.svg', svg);
                          if (!context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                            content: Text(saved ? 'SVG draft downloaded.' : 'SVG download is available in the web app.'),
                          ));
                        },
                        icon: const Icon(Icons.download),
                        label: const Text('Download SVG'),
                      ),
                      const SizedBox(width: 8),
                      TextButton.icon(
                        onPressed: _resetForm,
                        icon: Icon(Icons.refresh, color: textMuted),
                        label: Text('Regenerate', style: TextStyle(color: textMuted)),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _colorChip(String hex, String label) {
    Color color;
    try {
      final h = hex.replaceAll('#', '');
      color = Color(int.parse('FF$h', radix: 16));
    } catch (_) {
      color = Colors.grey;
    }
    return Row(children: [
      Container(width: 20, height: 20, decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(4), border: Border.all(color: Colors.black12))),
      const SizedBox(width: 6),
      Text('$label ($hex)', style: const TextStyle(fontSize: 12)),
    ]);
  }
}

class _ProfileScreen extends StatelessWidget {
  const _ProfileScreen();
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    return Center(child: Text('Manufacturer Profile', style: TextStyle(color: textColor, fontSize: 24)));
  }
}

class _LogoutScreen extends StatelessWidget {
  const _LogoutScreen();
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Terminate Manufacturer Session?', style: TextStyle(color: textColor, fontSize: 22)),
          const SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16)),
            onPressed: () => Navigator.pop(context),
            child: Text('Confirm Logout', style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}
