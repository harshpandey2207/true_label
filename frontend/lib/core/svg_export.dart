import 'svg_export_stub.dart'
    if (dart.library.html) 'svg_export_web.dart' as platform;

Future<bool> saveSvgDraft(String filename, String svg) =>
    platform.saveSvgDraft(filename, svg);
