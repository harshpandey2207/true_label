import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import 'package:sidebarx/sidebarx.dart';
import '../admin/mock_data.dart';
import 'dart:ui' as ui;
import 'package:flutter/rendering.dart';
import 'package:flutter/foundation.dart'; // for Uint8List // REQUIRED IMPORT

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

class _ManufacturerScreensRouter extends StatelessWidget {
  const _ManufacturerScreensRouter({super.key, required this.controller});
  final SidebarXController controller;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0: return const _BusinessOwnerScannerScreen();
          case 1: return _ManufacturerOverviewScreen();
          case 2: return _EnterpriseRegistryScreen();
          case 3: return _BusinessOwnerRepositoryScreen();
          case 4: return _StatutoryFinesScreen();
          case 5: return _LegalNoticesScreen();
          case 6: return const _AILabelGeneratorScreen();
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
  const _BusinessOwnerScannerScreen({super.key});

  @override
  __BusinessOwnerScannerScreenState createState() => __BusinessOwnerScannerScreenState();
}

class __BusinessOwnerScannerScreenState extends State<_BusinessOwnerScannerScreen> {
  bool _isScanning = false;
  String _selectedCategory = 'Packaged Drinking Water (Pre-packaged Commodities)';

  final List<String> _productCategories = [
    'Packaged Drinking Water (Pre-packaged Commodities)',
    'Electronics & Household Appliances',
    'Cosmetics & Pharma Goods',
    'Textiles & Apparel Measure',
    'Agricultural Commodities & Seeds'
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Pre-Market AI Compliance Scanner', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 16),
        
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
          decoration: BoxDecoration(
            color: theme.cardColor,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              isExpanded: true,
              value: _selectedCategory,
              dropdownColor: theme.cardColor,
              style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 14),
              icon: Icon(Icons.arrow_drop_down, color: Colors.greenAccent),
              items: _productCategories.map((String category) {
                return DropdownMenuItem<String>(
                  value: category,
                  child: Text(category, overflow: TextOverflow.ellipsis),
                );
              }).toList(),
              onChanged: (String? newValue) {
                setState(() {
                  _selectedCategory = newValue!;
                });
              },
            ),
          ),
        ),
        SizedBox(height: 20),

        Expanded(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Container(
                  width: double.infinity,
                  height: 280,
                  decoration: BoxDecoration(
                    border: Border.all(color: _isScanning ? Colors.greenAccent : Colors.white24, width: 2),
                    borderRadius: BorderRadius.circular(16),
                    color: theme.cardColor,
                  ),
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      Icon(Icons.document_scanner_outlined, size: 100, color: Colors.white12),
                      if (_isScanning) CircularProgressIndicator(color: Colors.greenAccent),
                      if (!_isScanning) Icon(Icons.crop_free, size: 150, color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
                    ],
                  ),
                ),
                SizedBox(height: 30),
                SizedBox(
                  width: double.infinity,
                  height: 60,
                  child: ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
                    onPressed: () {
                      setState(() => _isScanning = true);
                      Future.delayed(const Duration(seconds: 2), () {
                        if (mounted) {
                          setState(() => _isScanning = false);
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Scan complete. Report saved to Audit Repository.'), backgroundColor: Colors.green),
                          );
                        }
                      });
                    },
                    icon: Icon(Icons.camera, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, size: 28),
                    label: Text('RUN PRE-MARKET SCAN', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
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
                trailing: Icon(Icons.download, color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, size: 20),
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
  const _AILabelGeneratorScreen({super.key});

  @override
  __AILabelGeneratorScreenState createState() => __AILabelGeneratorScreenState();
}

class __AILabelGeneratorScreenState extends State<_AILabelGeneratorScreen> {
  bool _isGenerating = false;
  bool _showLabel = false;
  bool _isExporting = false;
  final GlobalKey _labelKey = GlobalKey();

  String _selectedCategory = 'Food Product (FSSAI/LM)';
  final List<String> _categories = [
    'Food Product (FSSAI/LM)',
    'Cosmetics & Pharma Goods',
    'Electronics & Appliances',
  ];

  final _productNameController = TextEditingController(text: 'Organic Almond Milk');
  final _netQuantityController = TextEditingController(text: '1 L');
  final _mrpController = TextEditingController(text: '75.00');
  final _consumerCareController = TextEditingController(text: 'support@almondorganics.in');
  final _manufacturerController = TextEditingController(text: 'Almond Organics Pvt Ltd, Plot 18, MIDC, Indore, MP - 452001');
  final _mfgDateController = TextEditingController(text: '10/2026');
  final _batchCodeController = TextEditingController(text: 'BAT-2026-901');

  String _rule7RequiredHeight = '4.0mm';

  @override
  void dispose() {
    _productNameController.dispose();
    _netQuantityController.dispose();
    _mrpController.dispose();
    _consumerCareController.dispose();
    _manufacturerController.dispose();
    _mfgDateController.dispose();
    _batchCodeController.dispose();
    super.dispose();
  }

  String _calculateRule7FontHeight(String qtyText) {
    final lower = qtyText.toLowerCase();
    final numMatch = RegExp(r'(\d+(?:\.\d+)?)').firstMatch(lower);
    if (numMatch == null) return '2.0mm';

    final double val = double.tryParse(numMatch.group(1)!) ?? 1.0;
    if (lower.contains('kg') || lower.contains('l') || lower.contains('litre')) {
      return val > 1.0 ? '6.0mm' : '4.0mm';
    } else if (lower.contains('g') || lower.contains('ml') || lower.contains('gm')) {
      if (val <= 50) return '1.0mm';
      if (val <= 200) return '2.0mm';
      if (val <= 1000) return '4.0mm';
      return '6.0mm';
    }
    return '4.0mm';
  }

  void _generateLabel() {
    setState(() => _isGenerating = true);
    final computedHeight = _calculateRule7FontHeight(_netQuantityController.text);

    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        setState(() {
          _isGenerating = false;
          _showLabel = true;
          _rule7RequiredHeight = computedHeight;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Compliant packaging layout synthesized under Rule 6 & 7!'), 
            backgroundColor: Colors.green
          ),
        );
      }
    });
  }

  void _resetForm() {
    setState(() {
      _showLabel = false;
      _productNameController.clear();
      _netQuantityController.clear();
      _mrpController.clear();
      _consumerCareController.clear();
      _manufacturerController.clear();
      _mfgDateController.clear();
      _batchCodeController.clear();
    });
  }

  Future<void> _exportPng() async {
    setState(() => _isExporting = true);
    try {
      await Future.delayed(const Duration(milliseconds: 100));
      final boundary = _labelKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) return;

      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final ByteData? byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      
      if (byteData != null) {
        final Uint8List pngBytes = byteData.buffer.asUint8List();
        _showPngPreviewDialog(pngBytes);
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to generate PNG: $e'), backgroundColor: Colors.redAccent),
      );
    } finally {
      if (mounted) setState(() => _isExporting = false);
    }
  }

  void _showPngPreviewDialog(Uint8List pngBytes) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: theme.cardColor,
        title: Text('Generated Label PNG (High Res)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
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
                const SnackBar(content: Text('PNG ready for production packaging print!'), backgroundColor: Colors.green),
              );
            },
            icon: Icon(Icons.check, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
            label: Text('Accept & Save', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
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
                    style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
                  SizedBox(height: 6),
                  Text('Input commodity parameters to auto-generate statutory Rule 6 declarations and Rule 7 dimensions.', 
                    style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                ],
              ),
            ),
            if (_showLabel)
              IconButton(
                onPressed: _resetForm,
                icon: Icon(Icons.refresh, color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
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
                      children: [
                        DropdownButtonFormField<String>(
                          initialValue: _selectedCategory,
                          dropdownColor: theme.cardColor,
                          isExpanded: true,
                          style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 14),
                          decoration: InputDecoration(
                            labelText: 'Product Category',
                            labelStyle: TextStyle(color: Colors.greenAccent, fontSize: 13),
                            enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), borderRadius: BorderRadius.circular(8)),
                            focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.greenAccent), borderRadius: BorderRadius.circular(8)),
                          ),
                          items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                          onChanged: (val) => setState(() => _selectedCategory = val!),
                        ),
                        SizedBox(height: 14),
                        
                        _buildInputField('Generic Name of Commodity', _productNameController, 'e.g. Organic Almond Milk', theme),
                        SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(child: _buildInputField('Net Quantity', _netQuantityController, 'e.g. 1 L or 500 g', theme)),
                            SizedBox(width: 12),
                            Expanded(child: _buildInputField('MRP (₹)', _mrpController, 'e.g. 75.00', theme)),
                          ],
                        ),
                        SizedBox(height: 14),
                        Row(
                          children: [
                            Expanded(child: _buildInputField('Mfg. Date', _mfgDateController, 'e.g. 10/2026', theme)),
                            SizedBox(width: 12),
                            Expanded(child: _buildInputField('Batch / Lot No.', _batchCodeController, 'e.g. BAT-2026-901', theme)),
                          ],
                        ),
                        SizedBox(height: 14),
                        _buildInputField('Full Manufacturer & Packer Details', _manufacturerController, 'Name, premise, address, pin code', theme, maxLines: 2),
                        SizedBox(height: 14),
                        _buildInputField('Consumer Care Contact (Email / Phone)', _consumerCareController, 'care@company.com / 1800-XXX-XXXX', theme),
                        SizedBox(height: 24),
                        SizedBox(
                          width: double.infinity,
                          height: 52,
                          child: ElevatedButton.icon(
                            style: ElevatedButton.styleFrom(backgroundColor: Colors.greenAccent),
                            onPressed: _isGenerating ? null : _generateLabel,
                            icon: _isGenerating 
                                ? SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, strokeWidth: 2)) 
                                : Icon(Icons.auto_awesome, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                            label: Text(
                              _isGenerating ? 'Synthesizing Compliant Spec...' : 'GENERATE COMPLIANT LAYOUT', 
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
                  _buildCompliantLabelMockup()
                else
                  Container(
                    width: double.infinity,
                    height: 250,
                    decoration: BoxDecoration(
                      color: const Color(0xFF181818),
                      border: Border.all(color: Colors.white12),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.style_outlined, size: 70, color: Colors.white12),
                          SizedBox(height: 16),
                          Text('Synthesized Packaging Spec Preview', 
                            style: TextStyle(color: Colors.white38, fontSize: 16, fontWeight: FontWeight.bold)),
                          SizedBox(height: 6),
                          Text('Enter product values above and click Generate', 
                            style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 13)),
                        ],
                      ),
                    ),
                  )
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInputField(String label, TextEditingController controller, String hint, ThemeData theme, {int maxLines = 1}) {
    return TextField(
      controller: controller,
      maxLines: maxLines,
      style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 14),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: Colors.greenAccent, fontSize: 13),
        hintText: hint,
        hintStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 13),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        enabledBorder: OutlineInputBorder(borderSide: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), borderRadius: BorderRadius.circular(8)),
        focusedBorder: OutlineInputBorder(borderSide: BorderSide(color: Colors.greenAccent), borderRadius: BorderRadius.circular(8)),
      ),
    );
  }

  Widget _buildCompliantLabelMockup() {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final name = _productNameController.text.trim().isEmpty ? 'COMMODITY NAME' : _productNameController.text.toUpperCase();
    final qty = _netQuantityController.text.trim().isEmpty ? '1 N' : _netQuantityController.text;
    final mrp = _mrpController.text.trim().isEmpty ? '0.00' : _mrpController.text;
    final mfgDate = _mfgDateController.text.trim().isEmpty ? 'MM/YYYY' : _mfgDateController.text;
    final batch = _batchCodeController.text.trim().isEmpty ? 'N/A' : _batchCodeController.text;
    final mfg = _manufacturerController.text.trim().isEmpty ? 'Registered Manufacturer Details' : _manufacturerController.text;
    final care = _consumerCareController.text.trim().isEmpty ? 'care@enterprise.com' : _consumerCareController.text;

    return Column(
      children: [
        RepaintBoundary(
          key: _labelKey,
          child: Card(
              color: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(28.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Center(
                    child: Text(
                      name, 
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.black, fontSize: 22, fontWeight: FontWeight.bold, letterSpacing: 1.2)
                    ),
                  ),
                  SizedBox(height: 20),
                  Divider(color: Colors.black26),
                  _buildLabelRow('Net Quantity:', qty, theme, highlight: true),
                  Divider(color: Colors.black12),
                  _buildLabelRow('Maximum Retail Price (MRP):', '₹ $mrp (Incl. of all taxes)', theme, highlight: false),
                  Divider(color: Colors.black12),
                  _buildLabelRow('Month & Year of Mfg:', mfgDate, theme, highlight: false),
                  Divider(color: Colors.black12),
                  _buildLabelRow('Batch / Lot Number:', batch, theme, highlight: false),
                  Divider(color: Colors.black26),
                  SizedBox(height: 8),
                  Text('Manufactured & Packed By: $mfg', 
                    style: TextStyle(color: Colors.black87, fontSize: 11, height: 1.4)),
                  SizedBox(height: 6),
                  Text('Consumer Complaints: Contact Executive at above address or $care', 
                    style: TextStyle(color: Colors.black87, fontSize: 11, height: 1.4)),
                  SizedBox(height: 20),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: Colors.green.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.green.shade400),
                    ),
                    child: Row(
                      children: [
                        Icon(Icons.verified, color: Colors.green.shade700, size: 26),
                        SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('STATUTORY VERIFICATION: 100% COMPLIANT', 
                                style: TextStyle(color: Colors.green.shade800, fontWeight: FontWeight.bold, fontSize: 12)),
                              SizedBox(height: 2),
                              Text('Rule 6 declarations present • Rule 7 font height: $_rule7RequiredHeight', 
                                style: TextStyle(color: Colors.green.shade700, fontSize: 11)),
                            ],
                          ),
                        ),
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
        ),
        SizedBox(height: 16),
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton.icon(
            style: ElevatedButton.styleFrom(
              backgroundColor: theme.cardColor,
              side: BorderSide(color: Colors.greenAccent),
            ),
            onPressed: _isExporting ? null : _exportPng,
            icon: _isExporting 
                ? SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.greenAccent, strokeWidth: 2))
                : Icon(Icons.download, color: Colors.greenAccent),
            label: Text('EXPORT HIGH-RES PNG', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
          ),
        )
      ],
    );
  }

    Widget _buildLabelRow(String title, String value, ThemeData theme, {bool highlight = false}) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 4.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: TextStyle(color: Colors.black87, fontSize: 14, fontWeight: FontWeight.w500)),
            Text(value, style: TextStyle(color: Colors.black, fontSize: highlight ? 18 : 14, fontWeight: FontWeight.bold)),
          ],
        ),
      );
    }
}

// --- 8. PROFILE SCREEN ---
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
              backgroundColor: theme.brightness == Brightness.dark ? Colors.purpleAccent.withValues(alpha: 0.2) : Colors.purple.shade100,
              child: Icon(Icons.person, size: 60, color: theme.brightness == Brightness.dark ? Colors.purpleAccent : Colors.purple.shade800),
            ),
            SizedBox(height: 24),
            Text('Harsh Pandey', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Business Owner', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey)),
            SizedBox(height: 32),
            Card(
              color: theme.cardColor,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    _buildProfileItem(Icons.email, 'Email', 'harsh.pandey@aquapure.com', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.phone, 'Phone', '+91 99988 77755', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.business, 'Enterprise', 'AquaPure Industries Ltd.', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.verified_user, 'Account Status', 'Active - Corporate verified', theme),
                  ],
                ),
              ),
            ),
            SizedBox(height: 32),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.purpleAccent,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              onPressed: () {},
              icon: Icon(Icons.edit, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Update Profile', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16)),
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
        Icon(icon, color: Colors.purpleAccent, size: 28),
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

// --- 9. SECURE LOGOUT SCREEN ---
class _LogoutScreen extends StatelessWidget {
  const _LogoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Terminate Manufacturer Session?', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 22)),
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