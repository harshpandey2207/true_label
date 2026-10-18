import 'dart:io';

import 'package:flutter/material.dart';
import 'package:sidebarx/sidebarx.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';

import '../../core/theme_provider.dart';
import '../admin/mock_data.dart';
import '../../core/api_service.dart';
import '../../core/product_catalog.dart';

import 'package:flutter/foundation.dart' show kIsWeb;

import 'dart:typed_data';

import '../../core/report_viewer.dart';

bool _isConfirmedViolation(dynamic value) {
  if (value is! Map) return false;
  return value['finding_status']?.toString() == 'CONFIRMED_VIOLATION' ||
      value['is_compliant'] == false;
}

class InspectorDashboard extends StatelessWidget {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  InspectorDashboard({super.key});

  Widget _buildSidebar(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: theme.cardColor),
        textStyle: TextStyle(color: theme.textTheme.bodyMedium?.color),
        selectedTextStyle: TextStyle(color: Colors.orangeAccent),
        iconTheme: IconThemeData(
          color: theme.iconTheme.color?.withValues(alpha: 0.5),
        ),
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
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text(
          'Package Label Inspector',
          style: theme.textTheme.titleLarge,
        ),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(
              themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode,
            ),
            onPressed: () => themeProvider.toggleTheme(),
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
              child: Column(
                children: [
                  if (!isMobile)
                    Align(
                      alignment: Alignment.topRight,
                      child: IconButton(
                        icon: Icon(
                          themeProvider.isDarkMode
                              ? Icons.light_mode
                              : Icons.dark_mode,
                        ),
                        onPressed: () => themeProvider.toggleTheme(),
                      ),
                    ),
                  Expanded(
                    child: _InspectorScreensRouter(controller: _controller),
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

class _InspectorScreensRouter extends StatelessWidget {
  const _InspectorScreensRouter({super.key, required this.controller});
  final SidebarXController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0:
            return _ScannerScreen();
          case 1:
            return _InspectorReportsScreen();
          case 2:
            return _InspectorAnalyticsScreen();
          case 3:
            return _InspectionHistoryScreen();
          case 4:
            return _ProfileScreen();
          case 5:
            return _LogoutScreen();
          default:
            return Center(child: Text('Not found'));
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
  String _processingText = "Preparing local OCR...";
  String? _selectedCategory;

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
    final category = _selectedCategory;
    if (category == null || category.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Choose the closest product category before scanning.'),
        ),
      );
      return;
    }

    setState(() {
      _scanState = 1;
      _processingText = "Analyzing ${_capturedImages.length} images...";
    });

    try {
      final result = await ApiService.analyzeArScan(
        imageFiles: _capturedImages,
        distanceMm: 300.0,
        focalLengthPx: 800.0,
        categoryName: category,
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

  void _showClarificationError(String message) {
    setState(() => _scanState = 2);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.redAccent),
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
    final scanId = _scanId;
    final category = _selectedCategory;
    if (scanId == null || category == null || category.isEmpty) return;
    if (_capturedImages.length >= 9) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'This scan already has nine evidence images. Start a new scan for another package.',
          ),
        ),
      );
      return;
    }

    final image = await _picker.pickImage(
      source: ImageSource.gallery,
      imageQuality: 95,
      maxWidth: 3000,
      maxHeight: 3000,
    );
    if (!mounted || image == null) return;
    setState(() {
      _scanState = 1;
      _processingText = 'Adding this close-up to scan $scanId...';
    });
    try {
      final result = await ApiService.analyzeArScan(
        imageFiles: [image],
        distanceMm: 300,
        focalLengthPx: 800,
        categoryName: category,
        scanId: scanId,
      );
      if (!mounted) return;
      final rawResults = result?['results'];
      if (result == null ||
          result['status'] != 'SUCCESS' ||
          rawResults is! List ||
          rawResults.isEmpty) {
        _showClarificationError(
          result?['error']?.toString() ?? 'The close-up could not be attached to this scan. Please retry with a clearer image.',
        );
        return;
      }
      setState(() {
        _capturedImages.add(image);
        _analysisResults = rawResults;
        _overallStatus = result['overall_status']?.toString() ?? 'UNRESOLVED';
        _overallCompliance = _overallStatus == 'PASS';
        _scanId = int.tryParse(result['scan_id']?.toString() ?? '') ?? scanId;
        _scanState = 2;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text(
            'Close-up saved to this scan and checks were reanalysed.',
          ),
        ),
      );
    } catch (_) {
      if (mounted) {
        _showClarificationError(
          'The close-up could not be attached. Check the connection and retry.',
        );
      }
    }
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
        Text(
          'Package Label Scanner',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(height: 12),
        Container(
          padding: EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: Colors.blue.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: Colors.blue.withValues(alpha: 0.3)),
          ),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(Icons.info_outline, color: Colors.blue, size: 20),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Installed local RapidOCR starts automatically. Choose the closest product category, then add the front, back and every declaration-bearing side (up to six images). Text on an unsubmitted or unreadable side stays unresolved; a saved scan does not update when you add evidence later. Text-size values are estimates, not legal evidence.',
                  style: TextStyle(color: textMuted, fontSize: 12, height: 1.4),
                ),
              ),
            ],
          ),
        ),
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
              hint: Text(
                'Choose product category',
                style: theme.textTheme.bodyMedium,
              ),
              dropdownColor: theme.cardColor,
              style: theme.textTheme.bodyMedium,
              icon: Icon(Icons.arrow_drop_down, color: Colors.orangeAccent),
              items: _productCategories.map((String category) {
                return DropdownMenuItem<String>(
                  value: category,
                  child: Text(category, overflow: TextOverflow.ellipsis),
                );
              }).toList(),
              onChanged: (String? newValue) =>
                  setState(() => _selectedCategory = newValue),
            ),
          ),
        ),
        SizedBox(height: 20),
        Expanded(
          child: _scanState == 0
              ? _buildIdleState(theme)
              : _scanState == 1
              ? _buildScanningState(theme)
              : _buildResultState(context, theme),
        ),
      ],
    );
  }

  Widget _buildIdleState(ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
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
                Icon(
                  Icons.view_in_ar,
                  size: 100,
                  color: theme.iconTheme.color?.withValues(alpha: 0.1),
                ),
                if (_capturedImages.isEmpty)
                  Icon(
                    Icons.crop_free,
                    size: 150,
                    color: theme.iconTheme.color?.withValues(alpha: 0.2),
                  )
                else
                  Text(
                    '${_capturedImages.length} Image(s) Ready',
                    style: TextStyle(
                      color: Colors.orangeAccent,
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                    ),
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
                icon: Icon(
                  Icons.qr_code_scanner,
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                  size: 28,
                ),
                label: Text(
                  'SCAN IMAGES NOW',
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildScanningState(ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
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
                Icon(
                  Icons.view_in_ar,
                  size: 100,
                  color: theme.iconTheme.color?.withValues(alpha: 0.1),
                ),
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
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    final missingTags = <String>{
      for (final resultData in _analysisResults!)
        for (final tag
            in ((resultData['analysis']
                        as Map<String, dynamic>?)?['missing_tags']
                    as List? ??
                const []))
          tag.toString(),
    }.toList()..sort();
    final unresolvedTags = <String>{
      for (final resultData in _analysisResults!)
        for (final tag
            in ((resultData['analysis']
                        as Map<String, dynamic>?)?['unresolved_tags']
                    as List? ??
                const []))
          tag.toString(),
    }.toList()..sort();
    final localOcrUnavailable = _analysisResults!.any((resultData) {
      final analysis = resultData['analysis'] as Map<String, dynamic>? ?? {};
      return analysis['ocr_engine'] == 'unavailable';
    });

    if (missingTags.isNotEmpty) _overallCompliance = false;
    final isConfirmed = _overallStatus == 'CONFIRMED_VIOLATION';

    return SingleChildScrollView(
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            color: _overallCompliance
                ? Colors.green.withValues(alpha: 0.2)
                : isConfirmed
                ? Colors.red.withValues(alpha: 0.2)
                : Colors.amber.withValues(alpha: 0.18),
            width: double.infinity,
            child: Column(
              children: [
                Text(
                  _overallCompliance
                      ? 'SCREENING PASSED'
                      : isConfirmed
                      ? 'CONFIRMED LABEL ISSUES'
                      : 'UNRESOLVED — MORE EVIDENCE NEEDED',
                  style: TextStyle(
                    color: _overallCompliance
                        ? Colors.green
                        : isConfirmed
                        ? Colors.red
                        : Colors.amber.shade800,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    ElevatedButton(
                      onPressed: _resetScanner,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: theme.cardColor,
                      ),
                      child: Text(
                        'Clear & Start New Scan',
                        style: TextStyle(
                          color: theme.textTheme.bodyMedium?.color,
                        ),
                      ),
                    ),
                    SizedBox(width: 16),
                    ElevatedButton.icon(
                      onPressed: () async {
                        if (_scanId != null) {
                          final report =
                              await ApiService.createComplianceReport(_scanId!);
                          if (!context.mounted) return;
                          final downloadUrl = report['download_url']
                              ?.toString();
                          if (downloadUrl != null &&
                              report['status'] != 'ERROR') {
                            ReportViewer.showStoredPdfDialog(
                              context: context,
                              reportCode:
                                  report['report_code']?.toString() ??
                                  'TLR-$_scanId',
                              pdfBytes: ApiService.getBytes(downloadUrl),
                            );
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  report['error']?.toString() ?? 'The persisted report could not be created.',
                                ),
                              ),
                            );
                          }
                          return;
                        }
                        List<Uint8List> proofBytes = [];
                        for (var img in _capturedImages) {
                          proofBytes.add(await img.readAsBytes());
                        }
                        final reportNotes = <String>{...missingTags};
                        for (final resultData in _analysisResults!) {
                          final analysis =
                              resultData['analysis'] as Map<String, dynamic>? ??
                              {};
                          for (final rawDeclaration
                              in (analysis['declarations'] as List? ??
                                  const <dynamic>[])) {
                            final declaration = rawDeclaration as Map;
                            if (_isConfirmedViolation(declaration)) {
                              final tag =
                                  declaration['tag']?.toString() ??
                                  'Declaration';
                              final note =
                                  declaration['failure_reason']?.toString() ??
                                  declaration['message']?.toString() ??
                                  'Needs review';
                              reportNotes.add('$tag: $note');
                            }
                          }
                          for (final warning
                              in (analysis['warnings'] as List? ??
                                  const <dynamic>[])) {
                            reportNotes.add(warning.toString());
                          }
                        }
                        if (context.mounted) {
                          ReportViewer.showPdfDialog(
                            context: context,
                            reportId:
                                'RPT-${DateTime.now().millisecondsSinceEpoch.toString().substring(5)}',
                            product:
                                _selectedCategory ??
                                'Unselected product category',
                            findingsOrNotes: reportNotes.isEmpty
                                ? 'No flags in the selected prototype checks.'
                                : reportNotes.join('\n'),
                            noFlagsDetected: _overallCompliance,
                            proofImages: proofBytes,
                          );
                        }
                      },
                      icon: Icon(Icons.picture_as_pdf, color: Colors.white),
                      label: Text(
                        'Open Report PDF',
                        style: TextStyle(color: Colors.white),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.blueAccent,
                      ),
                    ),
                  ],
                ),
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
                  Text(
                    'Confirmed missing declarations:',
                    style: TextStyle(
                      color: Colors.red,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: missingTags
                        .map(
                          (t) => Chip(
                            label: Text(
                              t,
                              style: TextStyle(
                                color: theme.brightness == Brightness.dark
                                    ? Colors.white
                                    : Colors.black,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            backgroundColor: Colors.red.shade900,
                            side: BorderSide.none,
                          ),
                        )
                        .toList(),
                  ),
                ],
              ),
            ),

          if (unresolvedTags.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              margin: const EdgeInsets.only(top: 16),
              decoration: BoxDecoration(
                color: Colors.amber.withValues(alpha: 0.12),
                border: Border.all(color: Colors.amber.withValues(alpha: 0.65)),
                borderRadius: BorderRadius.circular(8),
              ),
              width: double.infinity,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Unable to verify from this evidence:',
                    style: TextStyle(
                      color: Colors.amber,
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    localOcrUnavailable
                        ? 'Text extraction was unavailable when this scan was created, so it could not verify the label. This saved result will not update by itself. Start a new scan after local OCR is available; no declaration is confirmed absent.'
                        : 'These declarations were not detected or could not be read in the submitted images. This is not confirmation that they are absent. Add the relevant package side or a clearer close-up, or manually confirm the value.',
                    style: TextStyle(color: textMuted, fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: unresolvedTags
                        .map(
                          (t) => Chip(
                            label: Text(
                              t,
                              style: TextStyle(
                                color: theme.brightness == Brightness.dark
                                    ? Colors.white
                                    : Colors.black,
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            backgroundColor: Colors.amber.shade800,
                            side: BorderSide.none,
                          ),
                        )
                        .toList(),
                  ),
                  if (_scanId != null) ...[
                    const SizedBox(height: 12),
                    OutlinedButton.icon(
                      onPressed: _submitClarification,
                      icon: const Icon(Icons.add_a_photo_outlined),
                      label: const Text('ADD A CLEAR DECLARATION CLOSE-UP'),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Attach the relevant side to this scan and recheck the complete evidence set.',
                      style: TextStyle(color: textMuted, fontSize: 11),
                    ),
                  ],
                ],
              ),
            ),

          // Keep clarification available for confirmed findings too: a new
          // readable side may establish that an apparent omission was only
          // outside the original camera coverage.
          if (_scanId != null &&
              missingTags.isNotEmpty &&
              unresolvedTags.isEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  OutlinedButton.icon(
                    onPressed: _submitClarification,
                    icon: const Icon(Icons.add_a_photo_outlined),
                    label: const Text('ADD A CLEAR DECLARATION CLOSE-UP'),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Attach the relevant side to this scan and recheck the complete evidence set.',
                    style: TextStyle(color: textMuted, fontSize: 11),
                  ),
                ],
              ),
            ),

          SizedBox(height: 16),

          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _analysisResults?.length ?? 0,
            itemBuilder: (context, index) {
              final resultData = _analysisResults![index];
              final analysis = resultData['analysis'];

              final List<dynamic> relevantDeclarations =
                  (analysis['declarations'] ?? [])
                      .where((d) => d['tag'] != 'GENERAL')
                      .toList();

              final XFile originalImage = _capturedImages.firstWhere(
                (img) => img.name == resultData['filename'],
              );

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
                          decoration: BoxDecoration(
                            border: Border.all(color: theme.dividerColor),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: LayoutBuilder(
                            builder: (context, constraints) {
                              double maxW = constraints.maxWidth > 500
                                  ? 500
                                  : constraints.maxWidth;
                              return ClipRRect(
                                borderRadius: BorderRadius.circular(8),
                                child: Stack(
                                  children: [
                                    kIsWeb
                                        ? Image.network(
                                            originalImage.path,
                                            width: maxW,
                                            fit: BoxFit.contain,
                                          )
                                        : Image.file(
                                            File(originalImage.path),
                                            width: maxW,
                                            fit: BoxFit.contain,
                                          ),
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
                            },
                          ),
                        ),
                      ),
                      SizedBox(height: 16),
                      Text(
                        'Image: ${originalImage.name}',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Divider(color: theme.dividerColor, height: 32),

                      ...relevantDeclarations.map((d) {
                        final bool passed = !_isConfirmedViolation(d);
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 16.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'As per rules applicable on this product:',
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
                                      return ListTile(
                                        contentPadding: EdgeInsets.zero,
                                        leading: Icon(
                                          passed
                                              ? Icons.check_circle_outline
                                              : Icons.error_outline,
                                          color: passed
                                              ? Colors.green
                                              : Colors.red,
                                        ),
                                        title: Text(
                                          d['tag'],
                                          style: TextStyle(
                                            color: passed
                                                ? Colors.greenAccent
                                                : Colors.redAccent,
                                            fontSize: 14,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                        subtitle: Text(
                                          "\n",
                                          style: TextStyle(
                                            color: textMuted,
                                            fontSize: 12,
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
                                      "Confirmed absent or incorrect from readable evidence. Verify against the package and applicable rules.",
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
                                      "Not verified in the submitted evidence; this is not a confirmed absence. Upload a clearer side or confirm manually.",
                                      style: TextStyle(
                                        color: textMuted,
                                        fontSize: 12,
                                      ),
                                    ),
                                  );
                                }).toList()),
                            ],
                          ),
                        );
                      }),

                      if (relevantDeclarations.isEmpty)
                        Text(
                          'No statutory declarations detected.',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                    ],
                  ),
                ),
              );
            },
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
                onPressed: () async {
                  if (_scanId == null) return;
                  final result = await ApiService.postJson(
                    '/workspace/escalations',
                    {
                      'scan_id': _scanId,
                      'note': 'Inspector requested review after evidence-backed screening.',
                    },
                  );
                  if (!context.mounted) return;
                  final message = result['status'] == 'ERROR'
                      ? (result['error']?.toString() ??
                            'Could not create the escalation case.')
                      : 'Escalation case #${result['id']} is ${result['status']}. It is visible to administrators.';
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(message),
                      backgroundColor: result['status'] == 'ERROR'
                          ? Colors.redAccent
                          : Colors.green,
                    ),
                  );
                },
                icon: Icon(
                  Icons.warning_amber_rounded,
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                  size: 24,
                ),
                label: Text(
                  'ESCALATE TO ADMIN',
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}

String _inspectorStatus(dynamic value) =>
    (value?.toString() ?? 'UNRESOLVED').replaceAll('_', ' ');

Color _inspectorStatusColor(BuildContext context, dynamic value) {
  final status = value?.toString();
  if (status == 'PASS' || status == 'NO_FLAGS') return Colors.green;
  if (status == 'CONFIRMED_VIOLATION' || status == 'POTENTIAL_ISSUES')
    return Colors.redAccent;
  return Colors.orange;
}

Widget _inspectorLiveError(
  BuildContext context,
  String message,
  VoidCallback retry,
) {
  return Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.cloud_off_outlined, size: 42),
        const SizedBox(height: 10),
        Text(message, textAlign: TextAlign.center),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: retry,
          icon: const Icon(Icons.refresh),
          label: const Text('Retry'),
        ),
      ],
    ),
  );
}

// --- 2. REPORTS SCREEN ---
class _InspectorReportsScreen extends StatefulWidget {
  @override
  State<_InspectorReportsScreen> createState() =>
      _InspectorReportsScreenState();
}

class _InspectorReportsScreenState extends State<_InspectorReportsScreen> {
  late Future<Map<String, dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _future = ApiService.getJson('/reports?limit=100');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final data = snapshot.data ?? const <String, dynamic>{};
        if (data['status'] == 'ERROR')
          return _inspectorLiveError(
            context,
            data['error']?.toString() ?? 'Reports could not be loaded.',
            () => setState(_load),
          );
        final rows = (data['items'] as List? ?? const [])
            .map((item) => Map<String, dynamic>.from(item as Map))
            .toList();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Persisted reports',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(_load),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh',
                ),
              ],
            ),
            Text(
              'Reports generated from your stored scan evidence.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Card(
                child: rows.isEmpty
                    ? const Center(
                        child: Text(
                          'No persisted reports yet. Generate one from a completed scan.',
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(8),
                        itemCount: rows.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (context, index) {
                          final report = rows[index];
                          return ListTile(
                            leading: Icon(
                              Icons.picture_as_pdf_outlined,
                              color: theme.colorScheme.primary,
                            ),
                            title: Text(
                              report['report_code']?.toString() ??
                                  'Compliance report',
                            ),
                            subtitle: Text(
                              'Scan ${report['scan_id'] ?? '-'} · ${report['created_at'] ?? 'Date unavailable'}',
                            ),
                            trailing: FilledButton.icon(
                              onPressed: () => ReportViewer.showStoredPdfDialog(
                                context: context,
                                reportCode:
                                    report['report_code']?.toString() ??
                                    'Report',
                                pdfBytes: ApiService.getBytes(
                                  report['download_url']?.toString() ?? '',
                                ),
                              ),
                              icon: const Icon(Icons.visibility_outlined),
                              label: const Text('Open'),
                            ),
                          );
                        },
                      ),
              ),
            ),
          ],
        );
      },
    );
  }
}

// --- 3. MY INSPECTION ANALYTICS SCREEN ---
class _InspectorAnalyticsScreen extends StatefulWidget {
  @override
  State<_InspectorAnalyticsScreen> createState() =>
      _InspectorAnalyticsScreenState();
}

class _InspectorAnalyticsScreenState extends State<_InspectorAnalyticsScreen> {
  late Future<Map<String, dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _future = ApiService.getJson('/workspace/scans?limit=200');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final data = snapshot.data ?? const <String, dynamic>{};
        if (data['status'] == 'ERROR')
          return _inspectorLiveError(
            context,
            data['error']?.toString() ?? 'Analytics could not be loaded.',
            () => setState(_load),
          );
        final rows = (data['items'] as List? ?? const [])
            .map((item) => Map<String, dynamic>.from(item as Map))
            .toList();
        final counts = <String, int>{};
        final categories = <String, int>{};
        for (final row in rows) {
          final result = Map<String, dynamic>.from(
            (row['result'] as Map?) ?? const {},
          );
          final outcome = result['overall_status']?.toString() ??
              (row['status']?.toString() == 'NO_FLAGS' ? 'PASS' : 'UNRESOLVED');
          counts[outcome] = (counts[outcome] ?? 0) + 1;
          final category = row['category']?.toString() ?? 'Unknown category';
          categories[category] = (categories[category] ?? 0) + 1;
        }
        final demoPreview = rows.isEmpty;
        final chartCounts = demoPreview
            ? const <String, int>{
                'PASS': 8,
                'UNRESOLVED': 3,
                'CONFIRMED_VIOLATION': 1,
                'NOT_APPLICABLE': 0,
              }
            : counts;
        final chartCategories = demoPreview
            ? const <String, int>{
                'Food & Beverages': 4,
                'General Packaged Commodity': 3,
                'Cosmetics, Ointments & Pharma Goods': 2,
                'Electronics & Appliances': 2,
                'Medical Devices': 1,
              }
            : categories;
        return RefreshIndicator(
          onRefresh: () async {
            setState(_load);
            await _future;
          },
          child: ListView(
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      demoPreview
                          ? 'My inspection analysis'
                          : 'Live inspection analytics',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => setState(_load),
                    icon: const Icon(Icons.refresh),
                  ),
                ],
              ),
              Text(
                demoPreview
                    ? 'No live inspections are recorded for this account. Charts below show an illustrative demo preview.'
                    : 'Derived from persisted scans visible to this inspector account.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _InspectorMetric(
                    label: 'Total scans',
                    value: '${rows.length}',
                    icon: Icons.document_scanner_outlined,
                    color: Colors.teal,
                  ),
                  _InspectorMetric(
                    label: 'Passed',
                    value: '${counts['PASS'] ?? 0}',
                    icon: Icons.verified_outlined,
                    color: Colors.green,
                  ),
                  _InspectorMetric(
                    label: 'Unresolved',
                    value: '${counts['UNRESOLVED'] ?? 0}',
                    icon: Icons.help_outline,
                    color: Colors.orange,
                  ),
                  _InspectorMetric(
                    label: 'Confirmed issues',
                    value: '${counts['CONFIRMED_VIOLATION'] ?? 0}',
                    icon: Icons.warning_amber_rounded,
                    color: Colors.red,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              LayoutBuilder(
                builder: (context, constraints) {
                  final cardWidth = constraints.maxWidth >= 860
                      ? (constraints.maxWidth - 16) / 2
                      : constraints.maxWidth;
                  final outcomes = [
                    ('Passed', chartCounts['PASS'] ?? 0, Colors.teal),
                    ('Needs review', chartCounts['UNRESOLVED'] ?? 0, Colors.orange),
                    ('Confirmed issue', chartCounts['CONFIRMED_VIOLATION'] ?? 0, Colors.deepOrange),
                    ('Not applicable', chartCounts['NOT_APPLICABLE'] ?? 0, Colors.blueGrey),
                  ];
                  final rankedCategories = chartCategories.entries.toList()
                    ..sort((a, b) => b.value.compareTo(a.value));
                  final shownCategories = rankedCategories.take(5).toList();
                  final maxCategoryCount = shownCategories.isEmpty
                      ? 1.0
                      : shownCategories.map((entry) => entry.value).reduce((a, b) => a > b ? a : b).toDouble() + 1;
                  return Wrap(
                    spacing: 16,
                    runSpacing: 16,
                    children: [
                      SizedBox(
                        width: cardWidth,
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(18),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(demoPreview ? 'Outcome mix · demo preview' : 'Inspection outcome mix', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                                const SizedBox(height: 8),
                                SizedBox(
                                  height: 190,
                                  child: PieChart(PieChartData(
                                    centerSpaceRadius: 42,
                                    sectionsSpace: 3,
                                    sections: [
                                      for (final outcome in outcomes)
                                        PieChartSectionData(
                                          value: outcome.$2 == 0 ? 0.001 : outcome.$2.toDouble(),
                                          color: outcome.$3,
                                          title: outcome.$2 == 0 ? '' : '${outcome.$2}',
                                          radius: 48,
                                          titleStyle: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                                        ),
                                    ],
                                  )),
                                ),
                                for (final outcome in outcomes)
                                  Padding(
                                    padding: const EdgeInsets.only(top: 6),
                                    child: Row(children: [
                                      Container(width: 10, height: 10, decoration: BoxDecoration(color: outcome.$3, shape: BoxShape.circle)),
                                      const SizedBox(width: 8),
                                      Expanded(child: Text(outcome.$1)),
                                      Text('${outcome.$2}', style: const TextStyle(fontWeight: FontWeight.w700)),
                                    ]),
                                  ),
                              ],
                            ),
                          ),
                        ),
                      ),
                      SizedBox(
                        width: cardWidth,
                        child: Card(
                          child: Padding(
                            padding: const EdgeInsets.all(18),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(demoPreview ? 'Product profiles · demo preview' : 'Scans by product profile', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
                                const SizedBox(height: 12),
                                SizedBox(
                                  height: 255,
                                  child: BarChart(BarChartData(
                                    maxY: maxCategoryCount,
                                    gridData: const FlGridData(show: true, drawVerticalLine: false),
                                    borderData: FlBorderData(show: false),
                                    titlesData: FlTitlesData(
                                      rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                                      leftTitles: const AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 28)),
                                      bottomTitles: AxisTitles(sideTitles: SideTitles(
                                        showTitles: true,
                                        reservedSize: 46,
                                        getTitlesWidget: (value, meta) {
                                          final index = value.toInt();
                                          if (index < 0 || index >= shownCategories.length) return const SizedBox.shrink();
                                          final name = shownCategories[index].key;
                                          final shortName = name.length > 11 ? '${name.substring(0, 9)}…' : name;
                                          return Padding(padding: const EdgeInsets.only(top: 7), child: Text(shortName, style: theme.textTheme.labelSmall, textAlign: TextAlign.center));
                                        },
                                      )),
                                    ),
                                    barGroups: [
                                      for (var index = 0; index < shownCategories.length; index++)
                                        BarChartGroupData(x: index, barRods: [BarChartRodData(toY: shownCategories[index].value.toDouble(), width: 22, borderRadius: BorderRadius.circular(4), color: theme.colorScheme.primary)]),
                                    ],
                                  )),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ],
          ),
        );
      },
    );
  }
}

class _InspectorMetric extends StatelessWidget {
  const _InspectorMetric({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 180,
    child: Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: color.withValues(alpha: .12),
              child: Icon(icon, color: color),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    value,
                    style: Theme.of(context).textTheme.titleLarge
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Text(label, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

// --- 4. INSPECTION HISTORY SCREEN ---
class _InspectionHistoryScreen extends StatefulWidget {
  @override
  State<_InspectionHistoryScreen> createState() =>
      _InspectionHistoryScreenState();
}

class _InspectionHistoryScreenState extends State<_InspectionHistoryScreen> {
  late Future<Map<String, dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _future = ApiService.getJson('/workspace/scans?limit=100');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final data = snapshot.data ?? const <String, dynamic>{};
        if (data['status'] == 'ERROR')
          return _inspectorLiveError(
            context,
            data['error']?.toString() ?? 'History could not be loaded.',
            () => setState(_load),
          );
        final rows = (data['items'] as List? ?? const [])
            .map((item) => Map<String, dynamic>.from(item as Map))
            .toList();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Inspection history',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(_load),
                  icon: const Icon(Icons.refresh),
                ),
              ],
            ),
            Text(
              'Stable scan records, evidence status and category are preserved here.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: Card(
                child: rows.isEmpty
                    ? const Center(
                        child: Text('No scans have been recorded yet.'),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(8),
                        itemCount: rows.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (context, index) {
                          final row = rows[index];
                          final status =
                              row['status']?.toString() ?? 'POTENTIAL_ISSUES';
                          return ListTile(
                            leading: Icon(
                              Icons.history_outlined,
                              color: _inspectorStatusColor(context, status),
                            ),
                            title: Text(
                              'Scan #${row['id'] ?? '-'} · ${row['category'] ?? 'Unknown category'}',
                            ),
                            subtitle: Text(
                              row['created_at']?.toString() ??
                                  'Date unavailable',
                            ),
                            trailing: Chip(
                              label: Text(_inspectorStatus(status)),
                              backgroundColor: _inspectorStatusColor(
                                context,
                                status,
                              ).withValues(alpha: .12),
                            ),
                          );
                        },
                      ),
              ),
            ),
          ],
        );
      },
    );
  }
}

// --- 5. PROFILE SCREEN ---
class _ProfileScreen extends StatefulWidget {
  @override
  State<_ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<_ProfileScreen> {
  late Future<Map<String, dynamic>> _future;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _future = ApiService.getJson('/auth/me');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _future,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        final payload = snapshot.data ?? const <String, dynamic>{};
        if (payload['status'] == 'ERROR')
          return _inspectorLiveError(
            context,
            payload['error']?.toString() ?? 'Profile could not be loaded.',
            () => setState(_load),
          );
        final data = Map<String, dynamic>.from(
          (payload['user'] as Map?) ?? payload,
        );
        return Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 620),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: theme.colorScheme.primaryContainer,
                      child: Icon(
                        Icons.badge_outlined,
                        size: 38,
                        color: theme.colorScheme.primary,
                      ),
                    ),
                    const SizedBox(height: 14),
                    Text(
                      data['full_name']?.toString() ?? 'Inspector',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      data['email']?.toString() ?? '',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                    const Divider(height: 28),
                    _profileLine(
                      'Organization',
                      data['organization_name']?.toString() ?? 'Not provided',
                      theme,
                    ),
                    _profileLine(
                      'Role',
                      data['role']?.toString() ?? 'inspector',
                      theme,
                    ),
                    _profileLine(
                      'Account status',
                      data['is_active'] == false ? 'Inactive' : 'Active',
                      theme,
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}

Widget _profileLine(String label, String value, ThemeData theme) => Padding(
  padding: const EdgeInsets.symmetric(vertical: 8),
  child: Row(
    children: [
      SizedBox(
        width: 150,
        child: Text(
          label,
          style: theme.textTheme.bodyMedium?.copyWith(
            color: theme.colorScheme.onSurfaceVariant,
          ),
        ),
      ),
      Expanded(
        child: Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    ],
  ),
);

// --- legacy demo widgets retained for comparison only ---
class _LegacyInspectorReportsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    final myReports = mockViolations
        .where((v) => v['inspector'] == 'Harsh P.')
        .toList();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Sample Reports',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          'These example rows are static demo data. PDF previews are preliminary screening summaries.',
          style: TextStyle(color: textMuted),
        ),
        SizedBox(height: 16),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.builder(
              itemCount: myReports.length,
              itemBuilder: (context, index) {
                final violation = myReports[index];
                return ListTile(
                  leading: Icon(
                    Icons.picture_as_pdf,
                    color: Colors.orangeAccent,
                  ),
                  title: Text(
                    '${violation['id']}.pdf',
                    style: theme.textTheme.titleMedium,
                  ),
                  subtitle: Text(
                    '${violation['status']}',
                    style: theme.textTheme.bodySmall,
                  ),
                  trailing: IconButton(
                    icon: Icon(Icons.picture_as_pdf, color: Colors.blueAccent),
                    tooltip: 'View Report PDF',
                    onPressed: () {
                      ReportViewer.showPdfDialog(
                        context: context,
                        reportId: violation['id'],
                        product: violation['product'],
                        findingsOrNotes: 'Sample: ${violation["violation"]}',
                        noFlagsDetected: false,
                      );
                    },
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

// --- 3. MY INSPECTION ANALYTICS SCREEN ---
class _LegacyInspectorAnalyticsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Analytics',
            style: theme.textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Static demo charts; no inspection history is connected.',
            style: TextStyle(color: textMuted),
          ),
          SizedBox(height: 16),
          Card(
            color: theme.cardColor,
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Text(
                    'Weekly Scan Volume',
                    style: theme.textTheme.titleMedium,
                  ),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: BarChart(
                      BarChartData(
                        gridData: const FlGridData(show: false),
                        borderData: FlBorderData(show: false),
                        barGroups: [
                          BarChartGroupData(
                            x: 0,
                            barRods: [
                              BarChartRodData(
                                toY: 8,
                                color: Colors.orangeAccent,
                              ),
                            ],
                          ),
                          BarChartGroupData(
                            x: 1,
                            barRods: [
                              BarChartRodData(
                                toY: 10,
                                color: Colors.orangeAccent,
                              ),
                            ],
                          ),
                          BarChartGroupData(
                            x: 2,
                            barRods: [
                              BarChartRodData(
                                toY: 14,
                                color: Colors.orangeAccent,
                              ),
                            ],
                          ),
                          BarChartGroupData(
                            x: 3,
                            barRods: [
                              BarChartRodData(
                                toY: 15,
                                color: Colors.orangeAccent,
                              ),
                            ],
                          ),
                          BarChartGroupData(
                            x: 4,
                            barRods: [
                              BarChartRodData(
                                toY: 13,
                                color: Colors.orangeAccent,
                              ),
                            ],
                          ),
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
                  Text(
                    'Violation Discoveries',
                    style: theme.textTheme.titleMedium,
                  ),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: PieChart(
                      PieChartData(
                        sectionsSpace: 4,
                        centerSpaceRadius: 40,
                        sections: [
                          PieChartSectionData(
                            color: Colors.orange,
                            value: 40,
                            title: 'MRP',
                            radius: 40,
                            titleStyle: TextStyle(
                              color: theme.brightness == Brightness.dark
                                  ? Colors.white
                                  : Colors.black,
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                          PieChartSectionData(
                            color: Colors.redAccent,
                            value: 30,
                            title: 'Font',
                            radius: 40,
                            titleStyle: TextStyle(
                              color: theme.brightness == Brightness.dark
                                  ? Colors.white
                                  : Colors.black,
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
                          PieChartSectionData(
                            color: Colors.blueAccent,
                            value: 30,
                            title: 'Qty',
                            radius: 40,
                            titleStyle: TextStyle(
                              color: theme.brightness == Brightness.dark
                                  ? Colors.white
                                  : Colors.black,
                              fontWeight: FontWeight.bold,
                              fontSize: 10,
                            ),
                          ),
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
class _LegacyInspectionHistoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    final myHistory = auditLogs;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Sample History',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(height: 16),
        Text(
          'Static example records; the app is not connected to an authentication or audit service.',
          style: TextStyle(color: textMuted),
        ),
        SizedBox(height: 12),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.builder(
              itemCount: myHistory.length,
              itemBuilder: (context, index) {
                final log = myHistory[index];
                return ListTile(
                  leading: Icon(Icons.history_edu, color: Colors.orangeAccent),
                  title: Text(
                    log['action'] ?? 'Inspection',
                    style: theme.textTheme.bodyMedium,
                  ),
                  subtitle: Text(
                    '${log['timestamp']}',
                    style: theme.textTheme.bodySmall,
                  ),
                  trailing: Text(
                    log['status']!,
                    style: TextStyle(
                      color: log['status'] == 'Flagged'
                          ? Colors.red
                          : Colors.green,
                      fontSize: 12,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

// --- 5. LOGOUT SCREEN ---
class _LegacyProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
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
                backgroundColor: theme.brightness == Brightness.dark
                    ? Colors.orangeAccent.withValues(alpha: 0.2)
                    : Colors.orange.shade100,
                child: Icon(
                  Icons.badge,
                  size: 60,
                  color: theme.brightness == Brightness.dark
                      ? Colors.orangeAccent
                      : Colors.orange.shade800,
                ),
              ),
              SizedBox(height: 24),
              Text(
                'Sample Inspector Profile',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Demo only • no authentication is connected',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: Colors.grey,
                ),
              ),
              SizedBox(height: 32),
              Card(
                color: theme.cardColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      _buildProfileItem(
                        Icons.email,
                        'Email',
                        'Sample profile — not a real account',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.phone,
                        'Phone',
                        'Not connected',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.badge,
                        'Inspector ID',
                        'Sample only',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.verified_user,
                        'Clearance',
                        'Not verified',
                        theme,
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 32),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orangeAccent,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                ),
                onPressed: null,
                icon: Icon(
                  Icons.edit,
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                ),
                label: Text(
                  'Profile editing not connected',
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                    fontSize: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileItem(
    IconData icon,
    String title,
    String value,
    ThemeData theme,
  ) {
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Row(
      children: [
        Icon(icon, color: Colors.orangeAccent, size: 28),
        SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey),
              ),
              SizedBox(height: 4),
              Text(
                value,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
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
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text('Log out?', style: theme.textTheme.titleLarge),
          SizedBox(height: 24),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.redAccent,
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
            ),
            onPressed: () async {
              await ApiService.signOut();
              if (context.mounted) {
                Navigator.of(context)
                    .pushNamedAndRemoveUntil('/login', (route) => false);
              }
            },
            child: Text(
              'Confirm Logout',
              style: TextStyle(
                color: theme.brightness == Brightness.dark
                    ? Colors.white
                    : Colors.black,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
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
    for (var item in declarations) {
      final bool isCompliant = !_isConfirmedViolation(item);
      final rawBox = item['box'];
      if (rawBox is! List || rawBox.length < 2) continue;
      final List<dynamic> box = rawBox;
      final flattened = box
          .expand((point) => point is List ? point : const <dynamic>[])
          .toList();
      final normalized =
          flattened.isNotEmpty &&
          flattened.every((value) => (value as num).abs() <= 1.2);
      final double scaleX = normalized ? size.width : size.width / imageWidth;
      final double scaleY = normalized
          ? size.height
          : size.height / imageHeight;

      final paint = Paint()
        ..color = isCompliant ? Colors.greenAccent : Colors.redAccent
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0;

      final fillPaint = Paint()
        ..color = (isCompliant ? Colors.greenAccent : Colors.redAccent)
            .withValues(alpha: 0.2)
        ..style = PaintingStyle.fill;

      final path = Path();
      if (box.length >= 4) {
        path.moveTo(box[0][0] * scaleX, box[0][1] * scaleY);
        for (final point in box.skip(1)) {
          path.lineTo(point[0] * scaleX, point[1] * scaleY);
        }
        path.close();
      } else {
        final left = box[0][0] * scaleX;
        final top = box[0][1] * scaleY;
        final right = box[1][0] * scaleX;
        final bottom = box[1][1] * scaleY;
        path.addRect(Rect.fromLTRB(left, top, right, bottom));
      }

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
      textPainter.paint(
        canvas,
        Offset(box[0][0] * scaleX, (box[0][1] * scaleY) - 32),
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
