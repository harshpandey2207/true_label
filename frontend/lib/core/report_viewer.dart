import 'package:flutter/material.dart';
import 'dart:typed_data';
import 'package:printing/printing.dart';
import 'report_generator.dart';

class ReportViewer {
  static void showPdfDialog({
    required BuildContext context,
    required String reportId,
    required String product,
    required String violation,
    List<Uint8List>? proofImages,
  }) {
    showDialog(
      context: context,
      builder: (context) {
        final screenWidth = MediaQuery.of(context).size.width;
        final theme = Theme.of(context);
        final screenHeight = MediaQuery.of(context).size.height;
        
        return Dialog(
          backgroundColor: Colors.transparent,
          child: Container(
            width: screenWidth > 800 ? 800 : screenWidth * 0.95,
            height: screenHeight > 900 ? 900 : screenHeight * 0.9,
            clipBehavior: Clip.antiAlias,
            decoration: BoxDecoration(
              color: theme.brightness == Brightness.dark ? const Color(0xFF1E1E1E) : Colors.white, 
              borderRadius: BorderRadius.circular(8)
            ),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  decoration: BoxDecoration(
                    color: theme.brightness == Brightness.dark ? Colors.black : const Color(0xFFE0E0E0), 
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(8))
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Official Legal Metrology Report - $reportId', 
                        style: TextStyle(
                          color: theme.brightness == Brightness.dark ? Colors.white : Colors.black87, 
                          fontWeight: FontWeight.bold, 
                          fontSize: 16
                        )
                      ),
                      InkWell(
                        onTap: () => Navigator.pop(context), 
                        child: Icon(Icons.close, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: FutureBuilder<Uint8List>(
                    future: ReportGenerator.generatePdfReport(
                      reportId: reportId,
                      product: product,
                      violation: violation,
                      isCompliant: violation == 'None' || violation.isEmpty,
                      timestamp: 'October 16, 2026',
                      proofImages: proofImages,
                    ),
                    builder: (context, snapshot) {
                      if (snapshot.connectionState == ConnectionState.waiting) {
                        return const Center(child: CircularProgressIndicator());
                      }
                      if (snapshot.hasData) {
                        return PdfPreview(
                          build: (format) => snapshot.data!,
                          canChangeOrientation: false,
                          canChangePageFormat: false,
                          canDebug: false,
                          pdfFileName: '$reportId-Compliance-Report.pdf',
                        );
                      }
                      return const Center(child: Text('Failed to generate PDF'));
                    },
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
