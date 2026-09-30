import 'dart:typed_data';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;

class ReportGenerator {
  static Future<Uint8List> generatePdfReport({
    required String reportId,
    required String product,
    required String violation,
    required bool isCompliant,
    required String timestamp,
  }) async {
    final pdf = pw.Document(
      title: 'Legal Metrology Report - $reportId',
      author: 'True Label System',
    );

    final statusColor = isCompliant ? PdfColors.green700 : PdfColors.red700;
    final statusText = isCompliant ? 'COMPLIANT' : 'NON-COMPLIANT - E-NOTICE DISPATCHED';

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
                    pw.Text('DEPARTMENT OF LEGAL METROLOGY', 
                      style: pw.TextStyle(fontSize: 22, fontWeight: pw.FontWeight.bold, color: PdfColors.blue900)
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text('Official AI Compliance Inspection Report', 
                      style: const pw.TextStyle(fontSize: 16, color: PdfColors.grey700)
                    ),
                    pw.SizedBox(height: 5),
                    pw.Text('System Generated Document - True Label Engine', 
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
                      pw.Text('Date of Inspection:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text(timestamp, style: const pw.TextStyle(fontSize: 12)),
                      pw.SizedBox(height: 10),
                      pw.Text('Verification Authority:', style: pw.TextStyle(fontWeight: pw.FontWeight.bold, fontSize: 12)),
                      pw.Text('Automated CV Check', style: const pw.TextStyle(fontSize: 12)),
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
                    pw.Text('EXECUTIVE FINDINGS:', style: pw.TextStyle(fontSize: 14, fontWeight: pw.FontWeight.bold)),
                    pw.SizedBox(height: 10),
                    pw.Text(
                      isCompliant 
                          ? 'Computer Vision analysis confirms adherence to the Legal Metrology (Packaged Commodities) Rules, 2011.'
                          : 'Computer Vision analysis indicates a violation of the Legal Metrology (Packaged Commodities) Rules, 2011.',
                      style: const pw.TextStyle(fontSize: 12, lineSpacing: 3),
                    ),
                    pw.SizedBox(height: 15),
                    pw.Text('Identified Infraction:', style: pw.TextStyle(fontSize: 12, fontWeight: pw.FontWeight.bold)),
                    pw.Text(violation, style: pw.TextStyle(fontSize: 12, color: PdfColors.red900)),
                    pw.SizedBox(height: 15),
                    pw.Text(
                      'The mandatory declarations on the principal display panel were evaluated using automated bounds checking. '
                      'This report serves as a preliminary statutory log.',
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
                  color: isCompliant ? PdfColors.green50 : PdfColors.red50,
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
                  pw.Text('True Label Inspector App v2.4.0', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                  pw.Text('Page 1 of 1', style: const pw.TextStyle(fontSize: 9, color: PdfColors.grey500)),
                ],
              )
            ],
          );
        },
      ),
    );

    return pdf.save();
  }
}
