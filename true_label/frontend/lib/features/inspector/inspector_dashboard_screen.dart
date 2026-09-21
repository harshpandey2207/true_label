import 'dart:io';
import 'package:flutter/material.dart';
import 'package:sidebarx/sidebarx.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import '../admin/mock_data.dart';
import '../../core/api_service.dart';
import 'package:flutter/foundation.dart' show kIsWeb;

class InspectorDashboard extends StatelessWidget {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  InspectorDashboard({super.key});

  Widget _buildSidebar(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: theme.cardColor),
        textStyle: TextStyle(color: theme.textTheme.bodyMedium?.color),
        selectedTextStyle: TextStyle(color: Colors.orangeAccent),
        iconTheme: IconThemeData(color: theme.iconTheme.color?.withValues(alpha: 0.5)),
        selectedIconTheme: IconThemeData(color: Colors.orangeAccent),
      ),
      extendedTheme: SidebarXTheme(
        width: 260,
        decoration: BoxDecoration(color: theme.cardColor),
      ),
      items: [
        SidebarXItem(icon: Icons.camera_alt, label: 'Scan'),
        SidebarXItem(icon: Icons.folder_open, label: 'Reports'),
        SidebarXItem(icon: Icons.analytics, label: 'My Inspection Analytics'),
        SidebarXItem(icon: Icons.history, label: 'Inspection History'),
        SidebarXItem(icon: Icons.person, label: 'Profile'),
        SidebarXItem(icon: Icons.logout, label: 'Logout'),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width < 600;
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text('AR Inspector', style: theme.textTheme.titleLarge),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode),
            onPressed: () => themeProvider.toggleTheme(),
          )
        ],
      ),
      drawer: isMobile ? Drawer(child: _buildSidebar(context)) : null,
      body: Row(
        children: [
          if (!isMobile) _buildSidebar(context),
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(isMobile ? 16.0 : 24.0),
              child: Column(
                children: [
                  if (!isMobile)
                    Align(
                      alignment: Alignment.topRight,
                      child: IconButton(
                        icon: Icon(themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode),
                        onPressed: () => themeProvider.toggleTheme(),
                      ),
                    ),
                  Expanded(child: _InspectorScreensRouter(controller: _controller)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _InspectorScreensRouter extends StatelessWidget {
  const _InspectorScreensRouter({super.key, required this.controller});
  final SidebarXController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0: return _ScannerScreen();
          case 1: return _InspectorReportsScreen();
          case 2: return _InspectorAnalyticsScreen();
          case 3: return _InspectionHistoryScreen();
          case 4: return _ProfileScreen();
          case 5: return _LogoutScreen();
          default: return Center(child: Text('Not found'));
        }
      },
    );
  }
}

// --- 1. LIVE AR SCAN SCREEN ---
class _ScannerScreen extends StatefulWidget {
  @override
  __ScannerScreenState createState() => __ScannerScreenState();
}

class __ScannerScreenState extends State<_ScannerScreen> {
  int _scanState = 0; 
  String _processingText = "Initializing AR Camera...";
  String _selectedCategory = 'Cosmetics & Pharma Goods';
  
  final List<XFile> _capturedImages = []; 
  List<dynamic>? _analysisResults; 
  bool _overallCompliance = false;
  final ImagePicker _picker = ImagePicker();
  
  final List<String> _productCategories = [
    'Packaged Drinking Water (Pre-packaged Commodities)',
    'Electronics & Household Appliances',
    'Cosmetics & Pharma Goods',
    'Textiles & Apparel Measure',
    'Agricultural Commodities & Seeds'
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
      );

      if (result != null && result['status'] == 'SUCCESS') {
        setState(() {
          _analysisResults = result['results'];
          _overallCompliance = _analysisResults!.every((r) => r['analysis']['status'] == 'COMPLIANT');
          _scanState = 2;
        });
      } else {
        _showError("Failed to get analysis from backend.");
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
        Text('AR Metrology Scanner', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
        SizedBox(height: 16),
        
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          decoration: BoxDecoration(
            color: theme.cardColor,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: theme.dividerColor),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: _selectedCategory,
              dropdownColor: theme.cardColor,
              style: theme.textTheme.bodyMedium,
              icon: Icon(Icons.arrow_drop_down, color: Colors.orangeAccent),
              items: _productCategories.map((String category) {
                return DropdownMenuItem<String>(
                  value: category,
                  child: Text(category, overflow: TextOverflow.ellipsis),
                );
              }).toList(),
              onChanged: (String? newValue) => setState(() => _selectedCategory = newValue!),
            ),
          ),
        ),
        SizedBox(height: 20),
        Expanded(
          child: _scanState == 0 ? _buildIdleState(theme) : _scanState == 1 ? _buildScanningState(theme) : _buildResultState(context, theme),
        ),
      ],
    );
  }

  Widget _buildIdleState(ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return SingleChildScrollView(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: double.infinity,
            height: 260,
            decoration: BoxDecoration(
              border: Border.all(color: theme.dividerColor, width: 2),
              borderRadius: BorderRadius.circular(16),
              color: theme.cardColor,
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Icon(Icons.view_in_ar, size: 100, color: theme.iconTheme.color?.withValues(alpha: 0.1)),
                if (_capturedImages.isEmpty)
                  Icon(Icons.crop_free, size: 150, color: theme.iconTheme.color?.withValues(alpha: 0.2))
                else
                  Text('${_capturedImages.length} Image(s) Ready', 
                    style: TextStyle(color: Colors.orangeAccent, fontSize: 24, fontWeight: FontWeight.bold)
                  ),
              ],
            ),
          ),
          SizedBox(height: 30),
          Column(
            children: [
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: theme.cardColor,
                    foregroundColor: theme.textTheme.bodyMedium?.color,
                    side: BorderSide(color: theme.dividerColor),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  onPressed: _pickCameraImage,
                  icon: Icon(Icons.camera_alt, color: theme.iconTheme.color),
                  label: Text('ADD FROM CAMERA'),
                ),
              ),
              SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    foregroundColor: theme.textTheme.bodyMedium?.color,
                    side: BorderSide(color: theme.dividerColor),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  onPressed: _pickMultipleGalleryImages,
                  icon: Icon(Icons.photo_library, color: theme.iconTheme.color),
                  label: Text('ADD FROM GALLERY'),
                ),
              ),
            ],
          ),
          SizedBox(height: 24),
          if (_capturedImages.isNotEmpty)
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orangeAccent,
                  padding: const EdgeInsets.symmetric(vertical: 20),
                ),
                onPressed: _runScan,
                icon: Icon(Icons.qr_code_scanner, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, size: 28),
                label: Text('SCAN IMAGES NOW', 
                  style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 18, fontWeight: FontWeight.bold)
                ),
              ),
            )
        ],
      ),
    );
  }

  Widget _buildScanningState(ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: double.infinity,
            height: 260,
            decoration: BoxDecoration(
              border: Border.all(color: Colors.orangeAccent, width: 2),
              borderRadius: BorderRadius.circular(16),
              color: theme.cardColor,
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                Icon(Icons.view_in_ar, size: 100, color: theme.iconTheme.color?.withValues(alpha: 0.1)),
                CircularProgressIndicator(color: Colors.orangeAccent),
              ],
            ),
          ),
          SizedBox(height: 30),
          Text(_processingText, style: theme.textTheme.titleMedium),
        ],
      ),
    );
  }

  Widget _buildResultState(BuildContext context, ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    Set<String> foundTags = {};
    for (var resultData in _analysisResults!) {
      final analysis = resultData['analysis'];
      final List<dynamic> declarations = analysis['declarations'] ?? [];
      for (var d in declarations) {
        if (d['tag'] != 'GENERAL') foundTags.add(d['tag'].toString().toUpperCase());
      }
    }

    final List<String> mandatoryTags = ['MRP', 'NET_QUANTITY', 'MANUFACTURER', 'MANUFACTURING_DATE', 'BATCH_CODE'];
    final List<String> missingTags = mandatoryTags.where((tag) => !foundTags.contains(tag)).toList();
    
    if (missingTags.isNotEmpty) _overallCompliance = false;

    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          color: _overallCompliance ? Colors.green.withValues(alpha: 0.2) : Colors.red.withValues(alpha: 0.2),
          width: double.infinity,
          child: Column(
            children: [
              Text(
                _overallCompliance ? 'FULLY COMPLIANT' : 'NON-COMPLIANT',
                style: TextStyle(
                  color: _overallCompliance ? Colors.green : Colors.red,
                  fontSize: 18, fontWeight: FontWeight.bold
                ),
              ),
              SizedBox(height: 8),
              ElevatedButton(
                onPressed: _resetScanner,
                style: ElevatedButton.styleFrom(backgroundColor: theme.cardColor),
                child: Text('Clear & Start New Scan', style: TextStyle(color: theme.textTheme.bodyMedium?.color)),
              )
            ],
          ),
        ),
        
        if (missingTags.isNotEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            margin: const EdgeInsets.only(top: 16),
            decoration: BoxDecoration(
              color: Colors.red.withValues(alpha: 0.1),
              border: Border.all(color: Colors.red.withValues(alpha: 0.5)),
              borderRadius: BorderRadius.circular(8),
            ),
            width: double.infinity,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Missing Declarations:', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 16)),
                SizedBox(height: 8),
                Wrap(
                  spacing: 8, runSpacing: 8,
                  children: missingTags.map((t) => Chip(
                    label: Text(t, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 12, fontWeight: FontWeight.bold)),
                    backgroundColor: Colors.red.shade900,
                    side: BorderSide.none,
                  )).toList(),
                )
              ],
            ),
          ),
          
        SizedBox(height: 16),
        
        Expanded(
          child: ListView.builder(
            itemCount: _analysisResults?.length ?? 0,
            itemBuilder: (context, index) {
              final resultData = _analysisResults![index];
              final analysis = resultData['analysis'];
              
              final List<dynamic> relevantDeclarations = (analysis['declarations'] ?? [])
                  .where((d) => d['tag'] != 'GENERAL').toList();

              final XFile originalImage = _capturedImages.firstWhere((img) => img.name == resultData['filename']);

              return Card(
                color: theme.cardColor,
                margin: const EdgeInsets.only(bottom: 24),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Center(
                        child: Container(
                          decoration: BoxDecoration(border: Border.all(color: theme.dividerColor), borderRadius: BorderRadius.circular(8)),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              double maxW = constraints.maxWidth > 500 ? 500 : constraints.maxWidth;
                              return ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Stack(
                                  children: [
                                    kIsWeb 
                                        ? Image.network(originalImage.path, width: maxW, fit: BoxFit.contain)
                                        : Image.file(File(originalImage.path), width: maxW, fit: BoxFit.contain),
                                    if (relevantDeclarations.isNotEmpty)
                                      Positioned.fill(
                                        child: CustomPaint(
                                          painter: BoundingBoxPainter(
                                            declarations: relevantDeclarations, 
                                            imageWidth: 250.0, 
                                            imageHeight: 350.0,
                                          ),
                                        ),
                                      ),
                                  ],
                                ),
                              );
                            }
                          ),
                        ),
                      ),
                      SizedBox(height: 16),
                      Text('Image: ${originalImage.name}', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
                      Divider(color: theme.dividerColor, height: 32),
                      
                      ...relevantDeclarations.map((d) {
                        final bool passed = d['is_compliant'] == true;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('${d['tag']}', style: TextStyle(color: passed ? Colors.green : Colors.red, fontWeight: FontWeight.bold)),
                              SizedBox(height: 4),
                              Text('Detected: "${d['text']}"', style: theme.textTheme.bodyMedium),
                              Text('Height: ${d['height_mm']}mm - ${passed ? 'Pass' : 'Fail'}', style: theme.textTheme.bodySmall),
                            ],
                          ),
                        );
                      }),

                      if (relevantDeclarations.isEmpty)
                        Text('No statutory declarations detected.', style: theme.textTheme.bodyMedium?.copyWith(fontStyle: FontStyle.italic)),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        
        if (!_overallCompliance)
          Padding(
            padding: const EdgeInsets.only(top: 16.0),
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red.shade900,
                padding: const EdgeInsets.symmetric(vertical: 16),
                minimumSize: const Size(double.infinity, 50), 
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Entire Product Report Escalated to Admin Queue.'), backgroundColor: Colors.redAccent)
                );
              },
              icon: Icon(Icons.warning_amber_rounded, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, size: 24),
              label: Text('ESCALATE TO ADMIN', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
            ),
          ),
      ],
    );
  }
}

// --- 2. REPORTS SCREEN ---
class _InspectorReportsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final myReports = mockViolations.where((v) => v['inspector'] == 'Harsh P.').toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Reports', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
        SizedBox(height: 16),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.builder(
              itemCount: myReports.length,
              itemBuilder: (context, index) {
                final violation = myReports[index];
                return ListTile(
                  leading: Icon(Icons.picture_as_pdf, color: Colors.orangeAccent),
                  title: Text('${violation['id']}.pdf', style: theme.textTheme.titleMedium),
                  subtitle: Text('${violation['status']}', style: theme.textTheme.bodySmall),
                  trailing: Icon(Icons.download, color: theme.iconTheme.color),
                );
              },
            ),
          ),
        )
      ],
    );
  }
}

// --- 3. MY INSPECTION ANALYTICS SCREEN ---
class _InspectorAnalyticsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Analytics', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
          SizedBox(height: 16),
          Card(
            color: theme.cardColor,
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Text('Weekly Scan Volume', style: theme.textTheme.titleMedium),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200, 
                    child: BarChart(
                      BarChartData(
                        gridData: const FlGridData(show: false),
                        borderData: FlBorderData(show: false),
                        barGroups: [
                          BarChartGroupData(x: 0, barRods: [BarChartRodData(toY: 8, color: Colors.orangeAccent)]),
                          BarChartGroupData(x: 1, barRods: [BarChartRodData(toY: 10, color: Colors.orangeAccent)]),
                          BarChartGroupData(x: 2, barRods: [BarChartRodData(toY: 14, color: Colors.orangeAccent)]),
                          BarChartGroupData(x: 3, barRods: [BarChartRodData(toY: 15, color: Colors.orangeAccent)]),
                          BarChartGroupData(x: 4, barRods: [BarChartRodData(toY: 13, color: Colors.orangeAccent)]),
                        ],
                      ),
                    ),
                  ),
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
                children: [
                  Text('Violation Discoveries', style: theme.textTheme.titleMedium),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: PieChart(
                      PieChartData(
                        sectionsSpace: 4,
                        centerSpaceRadius: 40,
                        sections: [
                          PieChartSectionData(color: Colors.orange, value: 40, title: 'MRP', radius: 40, titleStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold, fontSize: 10)),
                          PieChartSectionData(color: Colors.redAccent, value: 30, title: 'Font', radius: 40, titleStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold, fontSize: 10)),
                          PieChartSectionData(color: Colors.blueAccent, value: 30, title: 'Qty', radius: 40, titleStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold, fontSize: 10)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// --- 4. INSPECTION HISTORY SCREEN ---
class _InspectionHistoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final myHistory = auditLogs.where((log) => 
      log['action']!.contains('Harsh P.') || 
      (log['type'] == 'Field Scan' && log.hashCode % 2 == 0)
    ).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('History', style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
        SizedBox(height: 16),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.builder(
              itemCount: myHistory.length,
              itemBuilder: (context, index) {
                final log = myHistory[index];
                return ListTile(
                  leading: Icon(Icons.history_edu, color: Colors.orangeAccent),
                  title: Text(log['action'] ?? 'Inspection', style: theme.textTheme.bodyMedium),
                  subtitle: Text('${log['timestamp']}', style: theme.textTheme.bodySmall),
                  trailing: Text(
                    log['status']!, 
                    style: TextStyle(color: log['status'] == 'Flagged' ? Colors.red : Colors.green, fontSize: 12)
                  ),
                );
              },
            ),
          ),
        )
      ],
    );
  }
}

// --- 5. LOGOUT SCREEN ---
class _ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Center(
      child: SingleChildScrollView(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 600),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            CircleAvatar(
              radius: 60,
              backgroundColor: theme.brightness == Brightness.dark ? Colors.orangeAccent.withValues(alpha: 0.2) : Colors.orange.shade100,
              child: Icon(Icons.badge, size: 60, color: theme.brightness == Brightness.dark ? Colors.orangeAccent : Colors.orange.shade800),
            ),
            SizedBox(height: 24),
            Text('Harsh Pandey', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Senior Field Inspector', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey)),
            SizedBox(height: 32),
            Card(
              color: theme.cardColor,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    _buildProfileItem(Icons.email, 'Email', 'harsh.pandey@inspector.gov.in', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.phone, 'Phone', '+91 99988 77766', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.badge, 'Inspector ID', 'INS-402', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.verified_user, 'Clearance', 'Level 2 - Regional Auditor', theme),
                  ],
                ),
              ),
            ),
            SizedBox(height: 32),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orangeAccent,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              onPressed: () {},
              icon: Icon(Icons.edit, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Update Credentials', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16)),
            ),
          ],
        ),
      ),
      ),
    );
  }

  Widget _buildProfileItem(IconData icon, String title, String value, ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Row(
      children: [
        Icon(icon, color: Colors.orangeAccent, size: 28),
        SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey)),
              SizedBox(height: 4),
              Text(value, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ],
    );
  }
}

class _LogoutScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Log out?', style: theme.textTheme.titleLarge),
          SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent, padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16)),
            onPressed: () => Navigator.pop(context),
            child: Text('Confirm Logout', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }
}

// --- 6. BOUNDING BOX PAINTER ---
class BoundingBoxPainter extends CustomPainter {
  final List<dynamic> declarations;
  final double imageWidth;
  final double imageHeight;

  BoundingBoxPainter({
    required this.declarations,
    required this.imageWidth,
    required this.imageHeight,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final double scaleX = size.width / imageWidth;
    final double scaleY = size.height / imageHeight;

    for (var item in declarations) {
      final bool isCompliant = item['is_compliant'];
      final List<dynamic> box = item['box'];
      
      final paint = Paint()
        ..color = isCompliant ? Colors.greenAccent : Colors.redAccent
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0;

      final fillPaint = Paint()
        ..color = (isCompliant ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.2)
        ..style = PaintingStyle.fill;

      final path = Path();
      path.moveTo(box[0][0] * scaleX, box[0][1] * scaleY);
      path.lineTo(box[1][0] * scaleX, box[1][1] * scaleY);
      path.lineTo(box[2][0] * scaleX, box[2][1] * scaleY);
      path.lineTo(box[3][0] * scaleX, box[3][1] * scaleY);
      path.close();

      canvas.drawPath(path, fillPaint);
      canvas.drawPath(path, paint);

      String detectedText = item['text'] ?? '';
      if (detectedText.length > 20) {
        detectedText = '${detectedText.substring(0, 17)}...';
      }

      final textSpan = TextSpan(
        text: '${item['tag']}\n$detectedText',
        style: TextStyle(
          color: isCompliant ? Colors.greenAccent : Colors.redAccent,
          fontSize: 10,
          fontWeight: FontWeight.bold,
          backgroundColor: Colors.black87,
        ),
      );

      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(canvas, Offset(box[0][0] * scaleX, (box[0][1] * scaleY) - 32));
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}