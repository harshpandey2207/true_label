import 'dart:html' as html;

Future<bool> saveSvgDraft(String filename, String svg) async {
  final blob = html.Blob([svg], 'image/svg+xml;charset=utf-8');
  final url = html.Url.createObjectUrlFromBlob(blob);
  final anchor = html.AnchorElement(href: url)
    ..download = filename
    ..style.display = 'none';
  html.document.body?.append(anchor);
  anchor.click();
  anchor.remove();
  html.Url.revokeObjectUrl(url);
  return true;
}
