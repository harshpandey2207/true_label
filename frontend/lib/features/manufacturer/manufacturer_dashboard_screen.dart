import 'dart:math' as math;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:sidebarx/sidebarx.dart';
import 'package:image_picker/image_picker.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:pdf/pdf.dart';

import '../../core/api_service.dart';
import '../../core/product_catalog.dart';
import '../../core/report_viewer.dart';
import '../../core/theme_provider.dart';
import 'manufacturer_workspace_screens.dart';
import '../../core/svg_export.dart';

String _formatMillimetres(double value) => value == value.roundToDouble()
    ? value.toStringAsFixed(0)
    : value.toStringAsFixed(1);

class ManufacturerDashboard extends StatefulWidget {
  const ManufacturerDashboard({super.key});

  @override
  State<ManufacturerDashboard> createState() => _ManufacturerDashboardState();
}

class _ManufacturerDashboardState extends State<ManufacturerDashboard> {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  Widget _buildSidebar(BuildContext context) {
    final theme = Theme.of(context);
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: theme.cardColor),
        textStyle: TextStyle(
          color: theme.brightness == Brightness.dark
              ? Colors.white
              : Colors.black,
        ),
        selectedTextStyle: TextStyle(color: theme.colorScheme.primary),
        iconTheme: IconThemeData(
          color: theme.brightness == Brightness.dark
              ? Colors.white70
              : Colors.black87,
        ),
        selectedIconTheme: IconThemeData(color: theme.colorScheme.primary),
      ),
      extendedTheme: SidebarXTheme(
        width: 260,
        decoration: BoxDecoration(color: theme.cardColor),
      ),
      items: [
        SidebarXItem(icon: Icons.qr_code_scanner, label: 'Pre-Market Scan'),
        SidebarXItem(
          icon: Icons.dashboard_outlined,
          label: 'Workspace Overview',
        ),
        SidebarXItem(icon: Icons.business_center, label: 'Enterprise Registry'),
        SidebarXItem(icon: Icons.folder_shared, label: 'Audit & Reports'),
        SidebarXItem(icon: Icons.receipt_long, label: 'Billing & Payments'),
        SidebarXItem(icon: Icons.mark_email_unread, label: 'Review Notes'),
        SidebarXItem(icon: Icons.auto_awesome, label: 'Label Draft Studio'),
        SidebarXItem(icon: Icons.layers_outlined, label: 'Saved Label Drafts'),
        SidebarXItem(icon: Icons.person, label: 'Business Profile'),
        SidebarXItem(icon: Icons.logout, label: 'Log out'),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isMobile = MediaQuery.of(context).size.width < 600;

    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text(
          'Business Owner Workspace',
          style:
              theme.textTheme.titleLarge?.copyWith(fontSize: 18) ??
              TextStyle(fontSize: 18),
        ),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(
              themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode,
            ),
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
  const _ManufacturerScreensRouter({required this.controller});
  final SidebarXController controller;

  @override
  State<_ManufacturerScreensRouter> createState() =>
      _ManufacturerScreensRouterState();
}

class _ManufacturerScreensRouterState
    extends State<_ManufacturerScreensRouter> {
  String _missingTagsForGenerator = "";
  Map<String, String> _scannedTagValuesForGenerator = {};
  String _generatorCategory = 'General Packaged Commodity';
  List<XFile> _scannedImagesForGenerator = const [];
  int? _scanIdForGenerator;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AnimatedBuilder(
      animation: widget.controller,
      builder: (context, child) {
        switch (widget.controller.selectedIndex) {
          case 0:
            return _BusinessOwnerScannerScreen(
              onNavigateToGenerator:
                  (missingTags, tagValues, category, images, scanId) {
                    setState(() {
                      _missingTagsForGenerator = missingTags;
                      _scannedTagValuesForGenerator = tagValues;
                      _generatorCategory = category;
                      _scannedImagesForGenerator = List<XFile>.from(images);
                      _scanIdForGenerator = scanId;
                    });
                    widget.controller.selectIndex(
                      6,
                    ); // Switch to AI Label Generator
                  },
            );
          case 1:
            return WorkspaceOverviewScreen();
          case 2:
            return WorkspaceRegistryScreen();
          case 3:
            return WorkspaceReportsScreen();
          case 4:
            return WorkspaceBillingScreen();
          case 5:
            return WorkspaceNotesScreen();
          case 6:
            return _AILabelGeneratorScreen(
              initialMissingTags: _missingTagsForGenerator,
              initialTagValues: _scannedTagValuesForGenerator,
              initialCategory: _generatorCategory,
              initialReferenceImages: _scannedImagesForGenerator,
              sourceScanId: _scanIdForGenerator,
            );

          case 8:
            return WorkspaceProfileScreen();
          case 9:
            return WorkspaceLogoutScreen();
          default:
            return Center(
              child: Text(
                'Screen not found',
                style: TextStyle(
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                ),
              ),
            );
        }
      },
    );
  }
}

// --- 1. PRE-MARKET SCANNER WITH CATEGORY SELECTOR ---
class _BusinessOwnerScannerScreen extends StatefulWidget {
  final Function(
    String missingTags,
    Map<String, String> tagValues,
    String category,
    List<XFile> images,
    int? scanId,
  )?
  onNavigateToGenerator;
  const _BusinessOwnerScannerScreen({this.onNavigateToGenerator});

  @override
  __BusinessOwnerScannerScreenState createState() =>
      __BusinessOwnerScannerScreenState();
}

class __BusinessOwnerScannerScreenState
    extends State<_BusinessOwnerScannerScreen> {
  int _scanState = 0;
  String _processingText = "Preparing text recognition...";
  String _selectedCategory = 'General Packaged Commodity';

  final List<XFile> _capturedImages = [];
  List<dynamic>? _analysisResults;
  bool _overallCompliance = false;
  String _overallStatus = 'UNRESOLVED';
  int? _scanId;
  final ImagePicker _picker = ImagePicker();

  final List<String> _productCategories = productCategories;

  Future<void> _pickCameraImage() async {
    if (_capturedImages.length >= 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('A scan can include up to six package-side images.'),
        ),
      );
      return;
    }
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      imageQuality: 95,
      maxWidth: 3000,
      maxHeight: 3000,
    );
    if (!mounted || photo == null) return;
    setState(() {
      _capturedImages.add(photo);
    });
  }

  Future<void> _pickMultipleGalleryImages() async {
    final remaining = 6 - _capturedImages.length;
    if (remaining <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('A scan can include up to six package-side images.'),
        ),
      );
      return;
    }
    final List<XFile> photos = await _picker.pickMultiImage(
      imageQuality: 95,
      maxWidth: 3000,
      maxHeight: 3000,
    );
    if (mounted && photos.isNotEmpty) {
      setState(() {
        _capturedImages.addAll(photos.take(remaining));
      });
      if (photos.length > remaining) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'This scan supports six images. Extra selections were skipped.',
            ),
          ),
        );
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
        final rawResults = result['results'];
        if (rawResults is! List || rawResults.isEmpty) {
          _showError(
            'The scanner returned no image analysis. Please retry with a readable package photo.',
          );
          return;
        }
        if (!mounted) return;
        setState(() {
          _analysisResults = rawResults;
          _overallStatus = result['overall_status']?.toString() ?? 'UNRESOLVED';
          _overallCompliance = _overallStatus == 'PASS';
          _scanId = int.tryParse(result['scan_id']?.toString() ?? '');
          _scanState = 2;
        });
      } else {
        final errorMsg =
            result?['error'] ?? "Failed to get analysis from backend.";
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
      _scanId = null;
      _overallStatus = 'UNRESOLVED';
      _capturedImages.clear();
    });
  }

  Future<void> _submitClarification() async {
    if (_scanId == null) return;
    final image = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 95,
      maxWidth: 3000,
      maxHeight: 3000,
    );
    if (!mounted || image == null) return;
    setState(() {
      _scanState = 1;
      _processingText = 'Adding the clarification image to scan $_scanId...';
    });
    final result = await ApiService.analyzeArScan(
      imageFiles: [image],
      distanceMm: 300.0,
      focalLengthPx: 800.0,
      categoryName: _selectedCategory,
      scanId: _scanId,
    );
    if (!mounted) return;
    if (result != null && result['status'] == 'SUCCESS') {
      final rawResults = result['results'];
      if (rawResults is! List || rawResults.isEmpty) {
        _showError(
          'The clarification response contained no image analysis. Please retry with a clearer image.',
        );
        return;
      }
      if (!mounted) return;
      setState(() {
        _capturedImages.add(image);
        _analysisResults = rawResults;
        _overallStatus = result['overall_status']?.toString() ?? 'UNRESOLVED';
        _overallCompliance = _overallStatus == 'PASS';
        _scanState = 2;
      });
    } else {
      _showError(
        result?['error']?.toString() ??
            'The clarification image could not be analysed.',
      );
    }
  }

  Future<void> _showCurrentScanReport() async {
    if (_analysisResults == null) return;
    if (_scanId != null) {
      final report = await ApiService.createComplianceReport(_scanId!);
      if (!mounted) return;
      final downloadUrl = report['download_url']?.toString();
      if (downloadUrl != null && report['status'] != 'ERROR') {
        ReportViewer.showStoredPdfDialog(
          context: context,
          reportCode: report['report_code']?.toString() ?? 'TLR-$_scanId',
          pdfBytes: ApiService.getBytes(downloadUrl),
        );
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            report['error']?.toString() ??
                'The persisted report could not be created.',
          ),
        ),
      );
      return;
    }
    final notes = StringBuffer('Category: $_selectedCategory\n\n');
    for (var index = 0; index < _analysisResults!.length; index++) {
      final result = Map<String, dynamic>.from(_analysisResults![index] as Map);
      final analysis = Map<String, dynamic>.from(
        (result['analysis'] as Map?) ?? const {},
      );
      notes.writeln('${result['filename'] ?? 'Package side ${index + 1}'}');
      for (final raw in (analysis['declarations'] as List? ?? const [])) {
        final declaration = Map<String, dynamic>.from(raw as Map);
        final tag = declaration['tag']?.toString() ?? 'Declaration';
        if (tag.toUpperCase() == 'GENERAL') continue;
        final text = declaration['text']?.toString() ?? '';
        final confidence = declaration['confidence'] as num?;
        final confidenceText = confidence == null
            ? 'OCR confidence unavailable'
            : '${(confidence.toDouble() * 100).toStringAsFixed(0)}% OCR confidence';
        final status =
            declaration['finding_status'] == 'FLAGGED' ||
                declaration['is_compliant'] == false
            ? 'flagged for review'
            : 'detected; not fully validated';
        notes.writeln('• $tag: $text — $status ($confidenceText)');
        final message = declaration['message']?.toString();
        if (message != null && message.isNotEmpty) notes.writeln('  $message');
      }
      final missing = (analysis['missing_tags'] as List? ?? const [])
          .map((value) => value.toString())
          .toList();
      if (missing.isNotEmpty)
        notes.writeln('Confirmed missing or incorrect: ${missing.join(', ')}');
      final unresolved = (analysis['unresolved_tags'] as List? ?? const [])
          .map((value) => value.toString())
          .toList();
      if (unresolved.isNotEmpty)
        notes.writeln(
          'Unable to verify (not confirmed absent): ${unresolved.join(', ')}',
        );
      for (final warning in (analysis['warnings'] as List? ?? const [])) {
        notes.writeln('Review note: $warning');
      }
      notes.writeln();
    }
    final evidence = await Future.wait(
      _capturedImages.map((image) => image.readAsBytes()),
    );
    final firstAnalysis = _analysisResults!.isEmpty
        ? const <String, dynamic>{}
        : Map<String, dynamic>.from(
            (_analysisResults!.first as Map)['analysis'] as Map,
          );
    if (!mounted) return;
    ReportViewer.showPdfDialog(
      context: context,
      reportId: _scanId == null
          ? 'SCAN-${DateTime.now().millisecondsSinceEpoch}'
          : 'SCAN-$_scanId',
      product: '$_selectedCategory package',
      findingsOrNotes: notes.toString(),
      noFlagsDetected: _overallCompliance,
      proofImages: evidence,
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Pre-Market Compliance Scanner',
              style: TextStyle(
                color: textColor,
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            if (_scanState != 0)
              IconButton(
                icon: Icon(Icons.refresh, color: textMuted),
                onPressed: _resetScanner,
                tooltip: "Clear and start a new scan",
              ),
          ],
        ),
        SizedBox(height: 16),

        if (_scanState == 0)
          _buildConfigurationState(theme, textColor, textMuted),
        if (_scanState == 1) _buildProcessingState(theme, textColor),
        if (_scanState == 2) _buildResultState(theme, textColor, textMuted),
      ],
    );
  }

  Widget _buildConfigurationState(
    ThemeData theme,
    Color textColor,
    Color textMuted,
  ) {
    return Expanded(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: EdgeInsets.all(12),
              margin: EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.1),
                border: Border.all(color: Colors.orange.withValues(alpha: 0.5)),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.orange),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'Demo mode uses local, deterministic processing. If optional local OCR is not configured, the scan remains unresolved and asks for a clear close-up or manual confirmation.',
                      style: TextStyle(
                        color: Colors.orange.shade800,
                        fontSize: 12,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
            ),

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
                    return DropdownMenuItem<String>(
                      value: category,
                      child: Text(category, overflow: TextOverflow.ellipsis),
                    );
                  }).toList(),
                  onChanged: (String? newValue) =>
                      setState(() => _selectedCategory = newValue!),
                ),
              ),
            ),
            SizedBox(height: 20),
            Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: theme.cardColor,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: Colors.greenAccent.withValues(alpha: 0.3),
                  width: 2,
                ),
              ),
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  Icon(
                    Icons.camera_alt_outlined,
                    size: 64,
                    color: Colors.greenAccent,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'Capture all sides of the product packaging',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Upload clear, straight-on photos of the front, back and other package sides. Text-size values are rough estimates and are not used to determine scan status.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: textMuted, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Package photos stay within this deployment. Optional local RapidOCR is preferred (PaddleOCR can also be configured); without local OCR, uploaded images are retained as evidence and the scan asks for a clear crop or manual confirmation.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: textMuted, fontSize: 12),
                  ),
                  SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.brightness == Brightness.dark
                              ? Colors.grey[800]
                              : Colors.grey[200],
                          padding: EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 16,
                          ),
                        ),
                        onPressed: _pickCameraImage,
                        icon: Icon(Icons.camera, color: textColor),
                        label: Text(
                          'Camera',
                          style: TextStyle(color: textColor),
                        ),
                      ),
                      SizedBox(width: 16),
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: theme.brightness == Brightness.dark
                              ? Colors.grey[800]
                              : Colors.grey[200],
                          padding: EdgeInsets.symmetric(
                            horizontal: 20,
                            vertical: 16,
                          ),
                        ),
                        onPressed: _pickMultipleGalleryImages,
                        icon: Icon(Icons.photo_library, color: textColor),
                        label: Text(
                          'Gallery',
                          style: TextStyle(color: textColor),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            SizedBox(height: 24),
            if (_capturedImages.isNotEmpty) ...[
              Text(
                'Captured Images (${_capturedImages.length})',
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 12),
              SizedBox(
                height: 100,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _capturedImages.length,
                  itemBuilder: (context, index) {
                    return FutureBuilder<Uint8List>(
                      future: _capturedImages[index].readAsBytes(),
                      builder: (context, snapshot) => Container(
                        margin: const EdgeInsets.only(right: 12),
                        width: 100,
                        decoration: BoxDecoration(
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.greenAccent),
                        ),
                        clipBehavior: Clip.antiAlias,
                        child: snapshot.hasData
                            ? Image.memory(snapshot.data!, fit: BoxFit.cover)
                            : const Center(
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                ),
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
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.greenAccent,
                  ),
                  onPressed: _runScan,
                  icon: Icon(Icons.document_scanner, color: Colors.black),
                  label: Text(
                    'RUN COMPLIANCE SCAN',
                    style: TextStyle(
                      color: Colors.black,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
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
              width: 80,
              height: 80,
              child: CircularProgressIndicator(
                color: Colors.greenAccent,
                strokeWidth: 6,
              ),
            ),
            SizedBox(height: 32),
            Text(
              _processingText,
              style: TextStyle(
                color: textColor,
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 16),
            Text(
              "Assessing image quality and reading package declarations when local OCR is available.",
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.greenAccent, fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultState(ThemeData theme, Color textColor, Color textMuted) {
    if (_analysisResults == null || _analysisResults!.isEmpty) {
      return Center(
        child: Text("No results returned.", style: TextStyle(color: textColor)),
      );
    }

    final allMissingTags = <String>{};
    final allUnresolvedTags = <String>{};
    for (var r in _analysisResults!) {
      if (r['analysis']['missing_tags'] != null) {
        allMissingTags.addAll(List<String>.from(r['analysis']['missing_tags']));
      }
      if (r['analysis']['unresolved_tags'] != null) {
        allUnresolvedTags.addAll(
          List<String>.from(r['analysis']['unresolved_tags']),
        );
      }
    }
    final missingTagsString = allMissingTags.join(", ");

    return Expanded(
      child: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: EdgeInsets.all(12),
              margin: EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.1),
                border: Border.all(color: Colors.orange.withValues(alpha: 0.5)),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.orange),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'This is evidence-backed screening, not a legal certificate. Unread or uncertain declarations stay unresolved instead of being marked as violations.',
                      style: TextStyle(
                        color: Colors.orange.shade800,
                        fontSize: 12,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            Container(
              width: double.infinity,
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: _overallCompliance
                    ? Colors.green.withValues(alpha: 0.1)
                    : _overallStatus == 'CONFIRMED_VIOLATION'
                    ? Colors.red.withValues(alpha: 0.1)
                    : Colors.amber.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _overallCompliance
                      ? Colors.green
                      : _overallStatus == 'CONFIRMED_VIOLATION'
                      ? Colors.redAccent
                      : Colors.amber.shade800,
                  width: 2,
                ),
              ),
              child: Column(
                children: [
                  Icon(
                    _overallCompliance
                        ? Icons.check_circle
                        : Icons.warning_amber_rounded,
                    color: _overallCompliance
                        ? Colors.green
                        : _overallStatus == 'CONFIRMED_VIOLATION'
                        ? Colors.redAccent
                        : Colors.amber.shade800,
                    size: 64,
                  ),
                  SizedBox(height: 12),
                  Text(
                    _overallCompliance
                        ? 'Screening passed'
                        : _overallStatus == 'CONFIRMED_VIOLATION'
                        ? 'Confirmed label issues'
                        : 'Unresolved — more evidence needed',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    _overallCompliance
                        ? 'The selected automated checks did not flag an issue in the submitted images. This screening is not a legal determination; review declarations and applicable requirements before relying on it.'
                        : _overallStatus == 'CONFIRMED_VIOLATION'
                        ? 'Readable evidence supports one or more confirmed findings. Review the evidence and applicable requirement before acting.'
                        : 'Some declarations could not be verified from the submitted evidence. This is not confirmation that they are absent; add a clearer side or confirm manually.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: textMuted, fontSize: 14),
                  ),
                  if (!_overallCompliance) ...[
                    SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      height: 52,
                      child: ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blueAccent,
                        ),
                        onPressed: () {
                          if (widget.onNavigateToGenerator != null) {
                            final tagValues = <String, String>{};
                            for (final result in _analysisResults ?? const []) {
                              final analysis =
                                  result['analysis'] as Map<String, dynamic>? ??
                                  {};
                              for (final declaration
                                  in (analysis['declarations'] as List? ??
                                      const [])) {
                                final tag =
                                    declaration['tag']?.toString() ?? '';
                                final value =
                                    declaration['text']?.toString() ?? '';
                                if (tag.isNotEmpty &&
                                    tag.toUpperCase() != 'GENERAL' &&
                                    value.isNotEmpty) {
                                  tagValues.putIfAbsent(tag, () => value);
                                }
                              }
                            }
                            widget.onNavigateToGenerator!(
                              missingTagsString,
                              tagValues,
                              _selectedCategory,
                              List<XFile>.from(_capturedImages),
                              _scanId,
                            );
                          }
                        },
                        icon: Icon(Icons.auto_awesome, color: Colors.white),
                        label: Text(
                          'CREATE A LABEL DRAFT',
                          style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    if (_scanId != null) ...[
                      SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed: _submitClarification,
                        icon: const Icon(Icons.add_a_photo_outlined),
                        label: const Text('ADD A CLEAR DECLARATION CLOSE-UP'),
                      ),
                    ],
                  ],
                ],
              ),
            ),
            SizedBox(height: 24),
            if (allMissingTags.isNotEmpty)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.1),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.5)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Confirmed missing or incorrect declarations',
                      style: TextStyle(
                        color: Colors.red,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: allMissingTags
                          .map(
                            (tag) => Chip(
                              label: Text(tag),
                              backgroundColor: Colors.red.shade900,
                            ),
                          )
                          .toList(),
                    ),
                  ],
                ),
              ),
            if (allUnresolvedTags.isNotEmpty)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.amber.withValues(alpha: 0.12),
                  border: Border.all(
                    color: Colors.amber.withValues(alpha: 0.65),
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Unable to verify from this evidence',
                      style: TextStyle(
                        color: Colors.amber,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Not detected or not readable is not the same as confirmed absent. Upload a clearer relevant side or confirm these declarations manually.',
                      style: TextStyle(color: textMuted, fontSize: 12),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: allUnresolvedTags
                          .map(
                            (tag) => Chip(
                              label: Text(tag),
                              backgroundColor: Colors.amber.shade800,
                            ),
                          )
                          .toList(),
                    ),
                  ],
                ),
              ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    'Screening report',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: _showCurrentScanReport,
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('Export report'),
                ),
              ],
            ),
            SizedBox(height: 16),

            ListView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemCount: _analysisResults!.length,
              itemBuilder: (context, index) {
                final result = _analysisResults![index];
                final analysis = result['analysis'];
                final bool noFlags = _overallStatus == 'PASS';

                return Card(
                  color: theme.cardColor,
                  margin: EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(
                      color: noFlags
                          ? Colors.green.withValues(alpha: 0.5)
                          : Colors.red.withValues(alpha: 0.5),
                    ),
                  ),
                  child: ExpansionTile(
                    title: Text(
                      'Image ${index + 1}: ${noFlags ? "No flags" : "Potential flags"}',
                      style: TextStyle(
                        color: textColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text(
                      '${analysis['declarations']?.length ?? 0} declarations found',
                      style: TextStyle(color: textMuted),
                    ),
                    leading: Icon(
                      noFlags ? Icons.check_circle : Icons.cancel,
                      color: noFlags ? Colors.green : Colors.red,
                    ),
                    children: [
                      Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Automated screening findings — verify rule applicability:',
                              style: TextStyle(
                                color: textColor,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                            SizedBox(height: 12),

                            // 1. Show Detected Mandatory Rules
                            if (analysis['declarations'] != null)
                              ...((analysis['declarations'] as List)
                                  .where((d) => d['tag'] != 'GENERAL')
                                  .map((d) {
                                    final flagged =
                                        d['finding_status'] ==
                                            'CONFIRMED_VIOLATION' ||
                                        d['is_compliant'] == false;
                                    final accent = flagged
                                        ? Colors.deepOrange
                                        : theme.colorScheme.primary;
                                    return ListTile(
                                      contentPadding: EdgeInsets.zero,
                                      leading: Icon(
                                        flagged
                                            ? Icons.warning_amber_outlined
                                            : Icons.subject,
                                        color: accent,
                                      ),
                                      title: Text(
                                        d['tag']?.toString() ?? 'Declaration',
                                        style: TextStyle(
                                          color: accent,
                                          fontSize: 14,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      subtitle: Padding(
                                        padding: const EdgeInsets.only(top: 6),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Text(
                                              d['text']?.toString() ??
                                                  'Text detected',
                                              style: TextStyle(
                                                color: textColor,
                                                fontSize: 13,
                                              ),
                                            ),
                                            Text(
                                              flagged
                                                  ? 'Automated check flagged this text'
                                                  : 'Detected; full rule applicability and content were not evaluated',
                                              style: TextStyle(
                                                color: flagged
                                                    ? accent
                                                    : textMuted,
                                                fontSize: 11,
                                              ),
                                            ),
                                            if ((d['message']?.toString() ?? '')
                                                .isNotEmpty)
                                              Padding(
                                                padding: const EdgeInsets.only(
                                                  top: 4,
                                                ),
                                                child: Text(
                                                  d['message'].toString(),
                                                  style: TextStyle(
                                                    color: textMuted,
                                                    fontSize: 12,
                                                  ),
                                                ),
                                              ),
                                            Text(
                                              d['confidence'] is num
                                                  ? 'OCR confidence: ${(((d['confidence'] as num).toDouble()) * 100).toStringAsFixed(0)}%'
                                                  : 'OCR confidence not supplied by this engine',
                                              style: TextStyle(
                                                color: textMuted,
                                                fontSize: 11,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    );
                                  })
                                  .toList()),

                            // 2. Show Missing Mandatory Rules
                            if (analysis['missing_tags'] != null &&
                                analysis['missing_tags'].isNotEmpty)
                              ...((analysis['missing_tags'] as List).map((t) {
                                return ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: Icon(
                                    Icons.cancel,
                                    color: Colors.red,
                                  ),
                                  title: Text(
                                    t.toString(),
                                    style: TextStyle(
                                      color: Colors.redAccent,
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text(
                                    "Confirmed absent or incorrect from readable evidence. Check the package directly and confirm whether this declaration applies.",
                                    style: TextStyle(
                                      color: textMuted,
                                      fontSize: 12,
                                    ),
                                  ),
                                );
                              }).toList()),
                            if (analysis['unresolved_tags'] != null &&
                                analysis['unresolved_tags'].isNotEmpty)
                              ...((analysis['unresolved_tags'] as List).map((
                                t,
                              ) {
                                return ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: Icon(
                                    Icons.help_outline,
                                    color: Colors.amber,
                                  ),
                                  title: Text(
                                    t.toString(),
                                    style: TextStyle(
                                      color: Colors.amber,
                                      fontSize: 14,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  subtitle: Text(
                                    'Not verified in the submitted evidence; this is not a confirmed absence. Upload a clearer side or confirm manually.',
                                    style: TextStyle(
                                      color: textMuted,
                                      fontSize: 12,
                                    ),
                                  ),
                                );
                              }).toList()),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
            const SizedBox(height: 8),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: _resetScanner,
                icon: const Icon(Icons.restart_alt),
                label: const Text('Clear results and start a new scan'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// --- 7. AI LABEL STUDIO (DYNAMIC GENERATION) ---
class _AILabelGeneratorScreen extends StatefulWidget {
  final String? initialMissingTags;
  final Map<String, String> initialTagValues;
  final String initialCategory;
  final List<XFile> initialReferenceImages;
  final int? sourceScanId;
  const _AILabelGeneratorScreen({
    this.initialMissingTags,
    this.initialTagValues = const {},
    this.initialCategory = 'General Packaged Commodity',
    this.initialReferenceImages = const [],
    this.sourceScanId,
  });

  @override
  __AILabelGeneratorScreenState createState() =>
      __AILabelGeneratorScreenState();
}

class __AILabelGeneratorScreenState extends State<_AILabelGeneratorScreen> {
  bool _isGenerating = false;
  bool _aiDesignStatusLoading = true;
  bool _aiDesignConfigured = false;
  bool _useAiDesign = false;
  Map<String, dynamic>? _labelData;
  String? _errorMessage;
  String? _engineInfo;
  String? _pdfDownloadUrl;
  String? _draftId;
  List<String> _warnings = [];
  int _selectedSideIndex = 0;
  String _selectedCategory = 'General Packaged Commodity';
  int _sideCount = 2;

  // Product identity is always supplied by the manufacturer or scan evidence;
  // never start with a fabricated name.
  final _productNameController = TextEditingController();
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
    _referenceImages.addAll(widget.initialReferenceImages.take(6));
    if (widget.initialMissingTags != null &&
        widget.initialMissingTags!.isNotEmpty) {
      _missingTags = widget.initialMissingTags!
          .split(',')
          .map((e) => e.trim())
          .where((t) => t.isNotEmpty)
          .toList();
    }
    _ensureValueControllers();
    _loadLabelDesignStatus();
  }

  Future<void> _loadLabelDesignStatus() async {
    final status = await ApiService.getLabelDesignStatus();
    if (!mounted) return;
    setState(() {
      _aiDesignConfigured = status['configured'] == true;
      _aiDesignStatusLoading = false;
    });
  }

  @override
  void dispose() {
    _productNameController.dispose();
    _shapeController.dispose();
    _dimensionController.dispose();
    _promptController.dispose();
    _additionalDetailsController.dispose();
    for (var c in _labelValueControllers.values) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _pickImages() async {
    final List<XFile> photos = await _picker.pickMultiImage(
      imageQuality: 78,
      maxWidth: 1600,
      maxHeight: 1600,
    );
    if (mounted && photos.isNotEmpty) {
      setState(() {
        _referenceImages.clear();
        _referenceImages.addAll(photos.take(6));
      });
      if (photos.length > 6 && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'Use up to six package-side images. The first six were selected.',
            ),
          ),
        );
      }
    }
  }

  List<String> _categoryFields(String category) {
    return fieldsForProductCategory(category);
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
    return labels[key] ??
        tag
            .replaceAll('_', ' ')
            .toLowerCase()
            .split(' ')
            .map(
              (w) => w.isEmpty ? w : '${w[0].toUpperCase()}${w.substring(1)}',
            )
            .join(' ');
  }

  void _ensureValueControllers() {
    final keys = <String>{
      ..._categoryFields(_selectedCategory),
      ..._missingTags.map((tag) => tag.toLowerCase()),
      ...widget.initialTagValues.keys.map((tag) => tag.toLowerCase()),
    };
    for (final tag in keys) {
      _labelValueControllers.putIfAbsent(tag, () {
        final entry = widget.initialTagValues.entries.firstWhere(
          (entry) => entry.key.toLowerCase() == tag,
          orElse: () => const MapEntry('', ''),
        );
        return TextEditingController(text: entry.value);
      });
    }
  }

  Future<void> _generateLabel() async {
    // Validate required fields
    if (_productNameController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Enter the approved product name before generating a label.',
          ),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }
    if (_dimensionController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Enter the finished label size (for example, 100 mm x 150 mm).',
          ),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }
    for (var tag in _missingTags) {
      if (_labelValueControllers[tag.toLowerCase()]?.text.trim().isEmpty ??
          true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Please provide a value for: $tag'),
            backgroundColor: Colors.red,
          ),
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
      useAiDesign: _useAiDesign,
      sourceScanId: widget.sourceScanId,
    );

    if (!mounted) return;

    if (result != null && result['success'] == true) {
      final sides = (result['label_data']['sides'] as List?) ?? [];
      setState(() {
        _isGenerating = false;
        _labelData = result['label_data'];
        _engineInfo = result['engine_used']?.toString();
        _pdfDownloadUrl = result['pdf_download_url']?.toString();
        _draftId = result['draft_id']?.toString();
        _warnings = (result['warnings'] as List? ?? const [])
            .map((value) => value.toString())
            .toList();
        _selectedSideIndex = 0;
      });
    } else {
      setState(() {
        _isGenerating = false;
        _errorMessage =
            result?['error'] ?? 'Could not generate this label draft.';
      });
    }
  }

  void _resetForm() {
    setState(() {
      _labelData = null;
      _errorMessage = null;
      _engineInfo = null;
      _pdfDownloadUrl = null;
      _draftId = null;
      _warnings = [];
    });
  }

  Widget _buildInputField(
    String label,
    TextEditingController controller,
    String hint,
    ThemeData theme, {
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      style: TextStyle(
        color: theme.brightness == Brightness.dark
            ? Colors.white
            : Colors.black,
        fontSize: 14,
      ),
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        hintStyle: TextStyle(
          color: theme.brightness == Brightness.dark
              ? Colors.white38
              : Colors.black38,
        ),
        labelStyle: TextStyle(color: theme.colorScheme.primary, fontSize: 13),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(
            color: theme.brightness == Brightness.dark
                ? Colors.white54
                : Colors.black54,
          ),
          borderRadius: BorderRadius.circular(8),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(color: theme.colorScheme.primary),
          borderRadius: BorderRadius.circular(8),
        ),
      ),
    );
  }

  Widget _buildGeneratedLabelCard(
    Map<String, dynamic> side,
    ThemeData theme,
    double width,
    bool selected,
    VoidCallback onTap,
  ) {
    final svgCode = side['svg_code'] as String? ?? '';
    final sideName = side['side_name']?.toString() ?? 'Generated Label';
    final dimensions = side['physical_dimensions_mm'] as Map? ?? const {};
    final widthMm = (dimensions['width'] as num?)?.toDouble() ?? 100;
    final heightMm = (dimensions['height'] as num?)?.toDouble() ?? 150;
    final dimensionLabel =
        '${_formatMillimetres(widthMm)} × ${_formatMillimetres(heightMm)} mm';

    return SizedBox(
      width: width,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(14),
        child: Container(
          decoration: BoxDecoration(
            color: theme.cardColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: selected ? theme.colorScheme.primary : theme.dividerColor,
              width: selected ? 2.5 : 1,
            ),
            boxShadow: const [
              BoxShadow(color: Colors.black12, blurRadius: 8, spreadRadius: 1),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  vertical: 10,
                  horizontal: 12,
                ),
                decoration: BoxDecoration(
                  color: selected
                      ? theme.colorScheme.primaryContainer
                      : theme.colorScheme.surfaceContainerHighest,
                  borderRadius: const BorderRadius.only(
                    topLeft: Radius.circular(12),
                    topRight: Radius.circular(12),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Text(
                        sideName.toUpperCase(),
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: theme.colorScheme.onSurface,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.8,
                        ),
                      ),
                    ),
                    if (selected) ...[
                      const SizedBox(width: 8),
                      Icon(
                        Icons.check_circle,
                        size: 16,
                        color: theme.colorScheme.primary,
                      ),
                    ],
                  ],
                ),
              ),
              if (svgCode.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      const maxPreviewHeight = 320.0;
                      final scale = math
                          .min(
                            constraints.maxWidth / widthMm,
                            maxPreviewHeight / heightMm,
                          )
                          .toDouble();
                      final previewWidth = widthMm * scale;
                      final previewHeight = heightMm * scale;
                      return SizedBox(
                        height: maxPreviewHeight,
                        child: Stack(
                          children: [
                            const Positioned.fill(
                              child: ColoredBox(color: Color(0xFFEAF1EC)),
                            ),
                            Center(
                              child: DecoratedBox(
                                decoration: const BoxDecoration(
                                  color: Color(0xFFFFFDF8),
                                  boxShadow: [
                                    BoxShadow(
                                      color: Colors.black26,
                                      blurRadius: 8,
                                      offset: Offset(0, 3),
                                    ),
                                  ],
                                ),
                                child: SizedBox(
                                  width: previewWidth,
                                  height: previewHeight,
                                  child: SvgPicture.string(
                                    svgCode,
                                    fit: BoxFit.fill,
                                    placeholderBuilder:
                                        (BuildContext context) => const Center(
                                          child: CircularProgressIndicator(),
                                        ),
                                  ),
                                ),
                              ),
                            ),
                            Positioned(
                              top: 8,
                              right: 8,
                              child: DecoratedBox(
                                decoration: BoxDecoration(
                                  color: theme.colorScheme.primaryContainer,
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(
                                    color: theme.colorScheme.primary,
                                  ),
                                ),
                                child: Padding(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 10,
                                    vertical: 6,
                                  ),
                                  child: Text(
                                    dimensionLabel,
                                    style: TextStyle(
                                      color:
                                          theme.colorScheme.onPrimaryContainer,
                                      fontSize: 11,
                                      fontWeight: FontWeight.w800,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                )
              else
                const Padding(
                  padding: EdgeInsets.all(32.0),
                  child: Center(
                    child: Text(
                      "No artwork was returned for this side.",
                      style: TextStyle(color: Colors.red),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final accent = theme.colorScheme.primary;
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;

    final sides = (_labelData?['sides'] as List?) ?? [];
    final brandDna = (_labelData?['brand_dna'] as Map?) ?? {};
    final selectedSide = sides.isNotEmpty
        ? sides[_selectedSideIndex] as Map<String, dynamic>
        : <String, dynamic>{};
    final physicalDimensions =
        selectedSide['physical_dimensions_mm'] as Map? ?? const {};
    final labelWidthMm =
        (physicalDimensions['width'] as num?)?.toDouble() ?? 100;
    final labelHeightMm =
        (physicalDimensions['height'] as num?)?.toDouble() ?? 150;
    final labelPageFormat = PdfPageFormat(
      labelWidthMm * PdfPageFormat.mm,
      labelHeightMm * PdfPageFormat.mm,
      marginAll: 0,
    );
    final pageLooksLikeA4 =
        ((labelWidthMm - 210).abs() < 25 && (labelHeightMm - 297).abs() < 25) ||
        ((labelHeightMm - 210).abs() < 25 && (labelWidthMm - 297).abs() < 25);

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
                  Text(
                    'Label Draft Studio',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Create side-by-side editable SVG drafts from package photos or a written brief. Review every declaration before printing.',
                    style: TextStyle(color: textMuted, fontSize: 13),
                  ),
                ],
              ),
            ),
            if (_labelData != null)
              IconButton(
                onPressed: _resetForm,
                icon: Icon(Icons.refresh, color: textMuted),
                tooltip: 'Start Over',
              ),
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
                          Text(
                            '1. Reference package photos (optional)',
                            style: TextStyle(
                              color: accent,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          GestureDetector(
                            onTap: _pickImages,
                            child: Container(
                              width: double.infinity,
                              height: 120,
                              decoration: BoxDecoration(
                                border: Border.all(
                                  color: _referenceImages.isNotEmpty
                                      ? accent
                                      : textMuted,
                                  width: 2,
                                ),
                                borderRadius: BorderRadius.circular(8),
                                color: _referenceImages.isNotEmpty
                                    ? accent.withValues(alpha: 0.05)
                                    : theme.cardColor,
                              ),
                              child: Center(
                                child: _referenceImages.isNotEmpty
                                    ? Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.check_circle,
                                            color: accent,
                                            size: 32,
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            '${_referenceImages.length} reference image(s) — one draft will be made per side',
                                            style: TextStyle(
                                              color: accent,
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            _referenceImages
                                                .map((image) => image.name)
                                                .join('  •  '),
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                            style: TextStyle(
                                              color: textMuted,
                                              fontSize: 11,
                                            ),
                                          ),
                                        ],
                                      )
                                    : Column(
                                        mainAxisAlignment:
                                            MainAxisAlignment.center,
                                        children: [
                                          Icon(
                                            Icons.cloud_upload_outlined,
                                            color: textMuted,
                                            size: 32,
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            'Add optional front, back or other side photos',
                                            style: TextStyle(color: textMuted),
                                          ),
                                          Text(
                                            'Files named Front, Back, Left, Right, Top or Bottom keep those side names.',
                                            style: TextStyle(
                                              color: textMuted,
                                              fontSize: 12,
                                            ),
                                          ),
                                        ],
                                      ),
                              ),
                            ),
                          ),
                          if (_referenceImages.isNotEmpty)
                            Align(
                              alignment: Alignment.centerRight,
                              child: TextButton.icon(
                                onPressed: () =>
                                    setState(_referenceImages.clear),
                                icon: const Icon(Icons.close),
                                label: const Text('Remove reference photos'),
                              ),
                            ),
                          const SizedBox(height: 24),

                          Text(
                            '2. Product and package details',
                            style: TextStyle(
                              color: accent,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          DropdownButtonFormField<String>(
                            initialValue: _selectedCategory,
                            decoration: const InputDecoration(
                              labelText: 'Product category',
                            ),
                            items: productCategories
                                .map(
                                  (category) => DropdownMenuItem(
                                    value: category,
                                    child: Text(category),
                                  ),
                                )
                                .toList(),
                            onChanged: (category) {
                              if (category == null) return;
                              setState(() {
                                _selectedCategory = category;
                                _ensureValueControllers();
                              });
                            },
                          ),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 12,
                            runSpacing: 12,
                            children: [
                              SizedBox(
                                width:
                                    (MediaQuery.of(context).size.width / 2) -
                                    48,
                                child: _buildInputField(
                                  'Product name',
                                  _productNameController,
                                  'e.g. Pure Honey',
                                  theme,
                                ),
                              ),
                              SizedBox(
                                width:
                                    (MediaQuery.of(context).size.width / 2) -
                                    48,
                                child: _buildInputField(
                                  'Package shape',
                                  _shapeController,
                                  'e.g. carton, bottle, pouch',
                                  theme,
                                ),
                              ),
                              SizedBox(
                                width:
                                    (MediaQuery.of(context).size.width / 2) -
                                    48,
                                child: _buildInputField(
                                  'Finished label size',
                                  _dimensionController,
                                  'e.g. 10 cm x 15 cm',
                                  theme,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 24),

                          Text(
                            '3. Declarations and product copy',
                            style: TextStyle(
                              color: accent,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'Scanner values are prefilled where detected. Fields not detected by OCR are highlighted for review; enter the exact approved wording.',
                            style: TextStyle(color: textMuted, fontSize: 12),
                          ),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 12,
                            runSpacing: 12,
                            children:
                                (_categoryFields(_selectedCategory).toSet()
                                      ..addAll(
                                        _missingTags.map(
                                          (tag) => tag.toLowerCase(),
                                        ),
                                      )
                                      ..addAll(
                                        widget.initialTagValues.keys.map(
                                          (tag) => tag.toLowerCase(),
                                        ),
                                      ))
                                    .map(
                                      (tag) => SizedBox(
                                        width:
                                            (MediaQuery.of(context).size.width /
                                                2) -
                                            48,
                                        child: _buildInputField(
                                          _missingTags.any(
                                                (missing) =>
                                                    missing.toLowerCase() ==
                                                    tag,
                                              )
                                              ? 'Confirmed issue: ${_fieldTitle(tag)}'
                                              : _fieldTitle(tag),
                                          _labelValueControllers[tag]!,
                                          'Enter label text',
                                          theme,
                                        ),
                                      ),
                                    )
                                    .toList(),
                          ),
                          const SizedBox(height: 24),

                          Text(
                            '4. Extra declarations or product features',
                            style: TextStyle(
                              color: accent,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildInputField(
                            'Additional label text (one item per line)',
                            _additionalDetailsController,
                            'e.g. Storage: Keep in a cool, dry place',
                            theme,
                            maxLines: 3,
                          ),
                          const SizedBox(height: 20),
                          Text(
                            '5. Design brief',
                            style: TextStyle(
                              color: accent,
                              fontSize: 14,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 8),
                          _buildInputField(
                            'Describe style and features to retain',
                            _promptController,
                            'e.g. earthy green, minimal, reserve a logo/artwork space',
                            theme,
                            maxLines: 3,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _referenceImages.isEmpty
                                ? 'The local vector renderer uses only supplied product identity and approved declaration values. It does not invent copy.'
                                : 'Reference photos are analysed locally for colour and side names. They are not sent to the optional AI design provider.',
                            style: TextStyle(color: textMuted, fontSize: 12),
                          ),
                          const SizedBox(height: 12),
                          Card(
                            color: theme.colorScheme.surfaceContainerHighest,
                            child: SwitchListTile.adaptive(
                              value: _useAiDesign && _aiDesignConfigured,
                              onChanged:
                                  !_aiDesignConfigured || _aiDesignStatusLoading
                                  ? null
                                  : (enabled) =>
                                        setState(() => _useAiDesign = enabled),
                              secondary: Icon(
                                Icons.auto_awesome,
                                color: _aiDesignConfigured
                                    ? theme.colorScheme.primary
                                    : textMuted,
                              ),
                              title: const Text('AI-assisted visual direction'),
                              subtitle: Text(
                                _aiDesignStatusLoading
                                    ? 'Checking local backend configuration…'
                                    : _aiDesignConfigured
                                    ? 'Optional Gemini styling. Only your category, shape, size, design brief and locally sampled colour palette are sent. No package photos, product name, declaration text or compliance result is shared.'
                                    : 'Not configured on this computer. The label remains editable with local category-aware vector styling; no AI provider is currently being used.',
                                style: TextStyle(
                                  color: textMuted,
                                  fontSize: 12,
                                ),
                              ),
                              contentPadding: const EdgeInsets.symmetric(
                                horizontal: 14,
                                vertical: 4,
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),

                          if (_referenceImages.isEmpty) ...[
                            DropdownButtonFormField<int>(
                              initialValue: _sideCount,
                              decoration: const InputDecoration(
                                labelText: 'Package sides to draft',
                              ),
                              items: const [2, 4, 6]
                                  .map(
                                    (count) => DropdownMenuItem(
                                      value: count,
                                      child: Text('$count sides'),
                                    ),
                                  )
                                  .toList(),
                              onChanged: (count) =>
                                  setState(() => _sideCount = count ?? 2),
                            ),
                            const SizedBox(height: 20),
                          ],

                          SizedBox(
                            width: double.infinity,
                            height: 52,
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: accent,
                              ),
                              onPressed: _isGenerating ? null : _generateLabel,
                              icon: _isGenerating
                                  ? const SizedBox(
                                      width: 20,
                                      height: 20,
                                      child: CircularProgressIndicator(
                                        color: Colors.black,
                                        strokeWidth: 2,
                                      ),
                                    )
                                  : const Icon(
                                      Icons.auto_awesome,
                                      color: Colors.black,
                                    ),
                              label: Text(
                                _isGenerating
                                    ? 'Building label drafts...'
                                    : 'GENERATE LABEL DRAFTS',
                                style: const TextStyle(
                                  color: Colors.black,
                                  fontSize: 14,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ),

                          if (_isGenerating) ...[
                            const SizedBox(height: 16),
                            Center(
                              child: Text(
                                '${_useAiDesign ? 'Generating a validated design direction for' : 'Building editable vector artwork for'} ${_referenceImages.isEmpty ? _sideCount : _referenceImages.length} package side(s)...',
                                style: TextStyle(
                                  color: textMuted,
                                  fontSize: 12,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ],

                          if (_errorMessage != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.red.shade50,
                                border: Border.all(color: Colors.red),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.error, color: Colors.red),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _errorMessage!,
                                      style: const TextStyle(color: Colors.red),
                                    ),
                                  ),
                                ],
                              ),
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
                          Text(
                            'Reference-image colour cues',
                            style: TextStyle(
                              color: Colors.greenAccent,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Wrap(
                            spacing: 12,
                            runSpacing: 8,
                            children: [
                              _colorChip(
                                selectedSide['sampled_primary_color'] ??
                                    brandDna['primary_color'] ??
                                    '#1B4332',
                                'Primary',
                              ),
                              _colorChip(
                                selectedSide['sampled_secondary_color'] ??
                                    brandDna['secondary_color'] ??
                                    '#FFFFFF',
                                'Secondary',
                              ),
                              _colorChip(
                                selectedSide['sampled_accent_color'] ??
                                    brandDna['accent_color'] ??
                                    '#52B788',
                                'Accent',
                              ),
                            ],
                          ),
                          if ((brandDna['font_style'] ?? '').isNotEmpty) ...[
                            const SizedBox(height: 8),
                            Text(
                              'Font: ${brandDna['font_style']}',
                              style: TextStyle(color: textMuted, fontSize: 13),
                            ),
                          ],
                          if ((brandDna['design_aesthetic'] ?? '')
                              .isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text(
                              'Design: ${brandDna['design_aesthetic']}',
                              style: TextStyle(color: textMuted, fontSize: 13),
                            ),
                          ],
                          if (_engineInfo != null) ...[
                            const SizedBox(height: 8),
                            Text(
                              _engineInfo!,
                              style: TextStyle(color: textMuted, fontSize: 12),
                            ),
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
                          children: _warnings
                              .map(
                                (warning) => Padding(
                                  padding: const EdgeInsets.only(bottom: 6),
                                  child: Text(
                                    '• $warning',
                                    style: TextStyle(
                                      color: textColor,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              )
                              .toList(),
                        ),
                      ),
                    ),

                  // Show all editable panels together; tapping selects export.
                  if (sides.isNotEmpty) ...[
                    Text(
                      'All ${sides.length} package sides appear together. Each artwork header carries its physical dimensions; tap a panel to choose its editable SVG export.',
                      style: TextStyle(color: textMuted, fontSize: 12),
                    ),
                    const SizedBox(height: 10),
                    LayoutBuilder(
                      builder: (context, constraints) {
                        final columns =
                            sides.length == 4 && constraints.maxWidth >= 880
                            ? 4
                            : constraints.maxWidth >= 930
                            ? 3
                            : constraints.maxWidth >= 600
                            ? 2
                            : 1;
                        const gap = 12.0;
                        final tileWidth =
                            (constraints.maxWidth - gap * (columns - 1)) /
                            columns;
                        return Wrap(
                          spacing: gap,
                          runSpacing: gap,
                          children: sides.asMap().entries.map((entry) {
                            final index = entry.key;
                            final side = Map<String, dynamic>.from(
                              entry.value as Map,
                            );
                            return _buildGeneratedLabelCard(
                              side,
                              theme,
                              tileWidth,
                              index == _selectedSideIndex,
                              () => setState(() => _selectedSideIndex = index),
                            );
                          }).toList(),
                        );
                      },
                    ),
                    const SizedBox(height: 16),
                  ],

                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: theme.colorScheme.primaryContainer.withValues(
                        alpha: 0.32,
                      ),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: theme.colorScheme.primary.withValues(
                          alpha: 0.35,
                        ),
                      ),
                    ),
                    child: Text(
                      'PDF page per side: exact ${_formatMillimetres(labelWidthMm)} × ${_formatMillimetres(labelHeightMm)} mm.${pageLooksLikeA4 ? ' These dimensions look close to A4 on screen, but the PDF page remains the exact label size.' : ''} When printing, select Actual size / 100% (not Fit to page); ask the printer to confirm bleed, trim and material.',
                      style: TextStyle(
                        color: textMuted,
                        fontSize: 12,
                        height: 1.4,
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () async {
                          final svg =
                              selectedSide['svg_code']?.toString() ?? '';
                          final productSlug = _productNameController.text
                              .trim()
                              .replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '-');
                          final sideSlug =
                              (selectedSide['side_name']?.toString() ?? 'side')
                                  .replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '-');
                          final saved = await saveSvgDraft(
                            '${productSlug}_$sideSlug.svg',
                            svg,
                          );
                          if (!context.mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(
                                saved ? 'SVG draft downloaded.' : 'SVG download is available in the web app.',
                              ),
                            ),
                          );
                        },
                        icon: const Icon(Icons.download),
                        label: const Text('Download SVG'),
                      ),
                      const SizedBox(width: 8),
                      if (_pdfDownloadUrl != null) ...[
                        OutlinedButton.icon(
                          onPressed: () => ReportViewer.showStoredPdfDialog(
                            context: context,
                            reportCode: 'label-${_draftId ?? 'draft'}',
                            pdfBytes: ApiService.getBytes(_pdfDownloadUrl!),
                            dialogTitle:
                                'Label print proof - ${_formatMillimetres(labelWidthMm)} x ${_formatMillimetres(labelHeightMm)} mm per side',
                            initialPageFormat: labelPageFormat,
                          ),
                          icon: const Icon(Icons.picture_as_pdf_outlined),
                          label: const Text('Preview / download PDF'),
                        ),
                        const SizedBox(width: 8),
                      ],
                      TextButton.icon(
                        onPressed: _resetForm,
                        icon: Icon(Icons.refresh, color: textMuted),
                        label: Text(
                          'Edit draft',
                          style: TextStyle(color: textMuted),
                        ),
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
    return Row(
      children: [
        Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: Colors.black12),
          ),
        ),
        const SizedBox(width: 6),
        Text('$label ($hex)', style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
