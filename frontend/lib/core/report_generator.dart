import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class ReportGenerator {
  static Future<Uint8List> generatePdfReport({
    required String reportId,
    required String product,
    required String findingsOrNotes,
    required bool noFlagsDetected,
    required String timestamp,
    List<Uint8List>? proofImages,
  }) async {
    final pdf = pw.Document(
      title: 'Automated Label Screening Summary - $reportId',
      author: 'True Label System',
    );

    final statusColor = noFlagsDetected ? PdfColors.green700 : PdfColors.red700;
    final statusText = noFlagsDetected ? 'NO FLAGS DETECTED' : 'POTENTIAL ISSUES FOUND';

    pdf.addPage(
      pw.Page(
        pageFormat: PdfPageFormat.a4,
        margin: const pw.EdgeInsets.all(40),
        build: (pw.Context context) {
          return pw.Column(
            crossAxisAlignment: pw.CrossAxisAlignment.start,
            children: [
              // HEADER
              pw.Container(
                alignment: pw.Alignment.center,
                padding: const pw.EdgeInsets.only(bottom: 20),
                decoration: const pw.BoxDecoration(
                  border: pw.Border(bottom: pw.BorderSide(color: PdfColors.grey400, width: 2)),
                ),
                child: pw.Column(
                  children: [
                    pw.Text('AUTOMATED LABEL SCREENING SUMMARY',
                      style: pw.TextStyle(fontSize: 22, fontWeight: pw.FontWeight.bold, color: PdfColors.blue900)
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text('Preliminary software output',
                      style: const pw.TextStyle(fontSize: 16, color: PdfColors.grey700)
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text('Not an official notice or legal determination',
                      style: pw.TextStyle(fontSize: 10, color: PdfColors.grey500, fontStyle: pw.FontStyle.italic)
                    ),
                  ],
                ),
              ),
              
              pw.SizedBox(height: 30),

              // META INFO
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.start,
                    children: [
                      pw.Text('Report ID:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text(reportId, style: const pw.TextStyle(fontSize: 12)),
                      pw.SizedBox(height: 10),
                      pw.Text('Target Product:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text(product, style: const pw.TextStyle(fontSize: 12)),
                    ]
                  ),
                  pw.Column(
                    crossAxisAlignment: pw.CrossAxisAlignment.end,
                    children: [
                      pw.Text('Report date:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text(timestamp, style: const pw.TextStyle(fontSize: 12)),
                      pw.SizedBox(height: 10),
                      pw.Text('Analysis method:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text('Automated OCR screening', style: const pw.TextStyle(fontSize: 12)),
                    ]
                  ),
                ]
              ),

              pw.SizedBox(height: 30),

              // FINDINGS
              pw.Container(
                padding: const pw.EdgeInsets.all(15),
                decoration: pw.BoxDecoration(
                  color: PdfColors.grey100,
                  borderRadius: const pw.BorderRadius.all(pw.Radius.circular(5)),
                  border: pw.Border.all(color: PdfColors.grey300),
                ),
                child: pw.Column(
                  crossAxisAlignment: pw.CrossAxisAlignment.start,
                  children: [
                    pw.Text('SCREENING SUMMARY:', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold)),
                    pw.SizedBox(height: 10),
                    pw.Text(
                      noFlagsDetected
                          ? 'The configured automated checks did not flag an issue in the images provided. This result does not establish legal compliance.'
                          : 'The configured automated checks found text or declarations that need human review. This result does not establish a legal violation.',
                      style: const pw.TextStyle(fontSize: 12, lineSpacing: 3),
                    ),
                    pw.SizedBox(height: 15),
                    pw.Text('Findings / notes:', style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold)),
                    pw.Text(findingsOrNotes, style: pw.TextStyle(fontSize: 12, color: PdfColors.grey900)),
                    pw.SizedBox(height: 15),
                    pw.Text(
                      'OCR can miss, misread or misclassify text. Confirm every declaration, applicable exemption, panel size and current rule with a qualified reviewer before acting.',
                      style: const pw.TextStyle(fontSize: 11, color: PdfColors.grey700, lineSpacing: 2),
                    ),
                  ],
                ),
              ),

              pw.SizedBox(height: 40),

              // FINAL STATUS
              pw.Container(
                width: double.infinity,
                padding: const pw.EdgeInsets.symmetric(vertical: 20),
                decoration: pw.BoxDecoration(
                  color: noFlagsDetected ? PdfColors.green50 : PdfColors.red50,
                  border: pw.Border.all(color: statusColor, width: 2),
                  borderRadius: const pw.BorderRadius.all(pw.Radius.circular(8)),
                ),
                child: pw.Center(
                  child: pw.Text(
                    'STATUS: $statusText',
                    style: pw.TextStyle(
                      color: statusColor,
                      fontSize: 16,
                      fontWeight: pw.FontWeight.bold,
                      letterSpacing: 1.5,
                    ),
                  ),
                ),
              ),

              pw.Spacer(),

              // FOOTER
              pw.Divider(color: PdfColors.grey400),
              pw.SizedBox(height: 5),
              pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text('True Label • automated screening', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                  pw.Text('Page ${context.pageNumber} of ${context.pagesCount}', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                ],
              )
            ],
          );
        },
      ),
    );

    // If proof images are provided, add a new MultiPage to display them
    if (proofImages != null && proofImages.isNotEmpty) {
      pdf.addPage(
        pw.MultiPage(
          pageFormat: PdfPageFormat.a4,
          margin: const pw.EdgeInsets.all(40),
          header: (pw.Context context) {
            return pw.Container(
              alignment: pw.Alignment.centerLeft,
              padding: const pw.EdgeInsets.only(bottom: 10),
              margin: const pw.EdgeInsets.only(bottom: 20),
              decoration: const pw.BoxDecoration(
                border: pw.Border(bottom: pw.BorderSide(color: PdfColors.grey400, width: 2)),
              ),
              child: pw.Text(
                'PROOF IMAGES', 
                style: pw.TextStyle(fontSize: 18, fontWeight: pw.FontWeight.bold, color: PdfColors.blue900)
              ),
            );
          },
          build: (pw.Context context) {
            return proofImages.map((imgBytes) {
              final image = pw.MemoryImage(imgBytes);
              return pw.Container(
                margin: const pw.EdgeInsets.only(bottom: 20),
                alignment: pw.Alignment.center,
                child: pw.Image(image, fit: pw.BoxFit.contain, height: 400),
              );
            }).toList();
          },
          footer: (pw.Context context) {
            return pw.Column(
              crossAxisAlignment: pw.CrossAxisAlignment.stretch,
              children: [
                pw.Divider(color: PdfColors.grey400),
                pw.SizedBox(height: 5),
                pw.Row(
                  mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                  children: [
                    pw.Text('True Label • automated screening', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                    pw.Text('Page ${context.pageNumber} of ${context.pagesCount}', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                  ],
                ),
              ],
            );
          },
        ),
      );
    }

    return pdf.save();
  }
}
