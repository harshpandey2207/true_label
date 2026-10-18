import 'dart:convert';
import 'dart:typed_data';

import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiService {
  // Production fallback for the existing Vercel deployment. Local developers
  // can still override this with API_BASE_URL in frontend/.env.
  static const String defaultUrl = 'https://true-label-backend.onrender.com';

  static String get baseUrl {
    return dotenv.env['API_BASE_URL'] ?? defaultUrl;
  }

  /// Fire-and-forget pre-warming ping to wake up backend if it was sleeping
  static void preWarmBackend() {
    try {
      http
          .get(Uri.parse('$baseUrl/'))
          .catchError((_) => http.Response('', 500));
    } catch (_) {}
  }

  static Future<Map<String, dynamic>?> analyzeArScan({
    required List<XFile> imageFiles, // <--- Accepts a list of images now
    required double distanceMm,
    required double focalLengthPx,
    required String categoryName,
    int? scanId,
  }) async {
    try {
      if (imageFiles.isEmpty) {
        return {
          'status': 'ERROR',
          'error': 'Select at least one package image before scanning.',
        };
      }
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/scan/analyze-ar'),
      );
      request.headers.addAll(_authHeaders);

      request.fields['distance_mm'] = distanceMm.toString();
      request.fields['focal_length_px'] = focalLengthPx.toString();
      request.fields['category_name'] = categoryName;
      if (scanId != null) request.fields['scan_id'] = scanId.toString();

      // Loop through all selected images and append them to the multipart request
      for (var imageFile in imageFiles) {
        var bytes = await imageFile.readAsBytes();
        var multipartFile = http.MultipartFile.fromBytes(
          'images', // <--- Must match FastAPI parameter name `images`
          bytes,
          filename: imageFile.name,
        );
        request.files.add(multipartFile);
      }

      var response = await request.send().timeout(const Duration(seconds: 120));

      if (response.statusCode == 200) {
        final respStr = await response.stream.bytesToString();
        final decoded = jsonDecode(respStr);
        if (decoded is! Map) {
          return {
            'status': 'ERROR',
            'error': 'The scanner returned an invalid response.',
          };
        }
        return Map<String, dynamic>.from(decoded);
      } else {
        final respStr = await response.stream.bytesToString();
        dynamic detail;
        try {
          detail = jsonDecode(respStr)['detail'];
        } catch (_) {}
        return {
          'status': 'ERROR',
          'error':
              detail?.toString() ?? 'Backend error (${response.statusCode}).',
        };
      }
    } catch (e) {
      return {'status': 'ERROR', 'error': 'Connection error: $e'};
    }
  }

  static Future<Map<String, dynamic>?> generateLabel({
    required List<XFile> imageFiles,
    required String productName,
    required String productCategory,
    required String shape,
    required String dimensions,
    required String customPrompt,
    required Map<String, String> missingTagValues,
    required String additionalDetails,
    required int sideCount,
    required bool useAiDesign,
    int? sourceScanId,
  }) async {
    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/label/generate'),
      );
      request.headers.addAll(_authHeaders);

      request.fields['product_name'] = productName;
      request.fields['product_category'] = productCategory;
      request.fields['shape'] = shape;
      request.fields['dimensions'] = dimensions;
      request.fields['custom_prompt'] = customPrompt;
      request.fields['missing_tag_values'] = jsonEncode(missingTagValues);
      request.fields['additional_details'] = additionalDetails;
      request.fields['side_count'] = sideCount.toString();
      request.fields['use_ai_design'] = useAiDesign.toString();
      if (sourceScanId != null)
        request.fields['source_scan_id'] = sourceScanId.toString();

      for (var imageFile in imageFiles) {
        var bytes = await imageFile.readAsBytes();
        request.files.add(
          http.MultipartFile.fromBytes(
            'images',
            bytes,
            filename: imageFile.name,
          ),
        );
      }

      var response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(respStr);
      } else {
        dynamic detail;
        try {
          detail = jsonDecode(respStr)['detail'];
        } catch (_) {}
        return {
          'success': false,
          'error': detail?.toString() ?? 'Backend error ${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }

  static Map<String, dynamic>? currentUser;

  static Future<Map<String, dynamic>> getLabelDesignStatus() =>
      getJson('/label/design-status');

  static Future<Map<String, dynamic>> getJson(String path) async {
    try {
      final response = await http
          .get(Uri.parse(baseUrl + path), headers: _authHeaders)
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200)
        return Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      dynamic detail;
      try {
        detail = jsonDecode(response.body)['detail'];
      } catch (_) {}
      return {
        'status': 'ERROR',
        'error':
            detail?.toString() ?? 'Backend error (${response.statusCode}).',
      };
    } catch (e) {
      return {'status': 'ERROR', 'error': 'Connection error: ' + e.toString()};
    }
  }

  static Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await http
          .post(
            Uri.parse(baseUrl + path),
            headers: {'Content-Type': 'application/json', ..._authHeaders},
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200 || response.statusCode == 201)
        return Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      dynamic detail;
      try {
        detail = jsonDecode(response.body)['detail'];
      } catch (_) {}
      return {
        'status': 'ERROR',
        'error':
            detail?.toString() ?? 'Backend error (${response.statusCode}).',
      };
    } catch (e) {
      return {'status': 'ERROR', 'error': 'Connection error: ' + e.toString()};
    }
  }

  static Future<Map<String, dynamic>> patchJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await http
          .patch(
            Uri.parse(baseUrl + path),
            headers: {'Content-Type': 'application/json', ..._authHeaders},
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200 || response.statusCode == 201)
        return Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      dynamic detail;
      try {
        detail = jsonDecode(response.body)['detail'];
      } catch (_) {}
      return {
        'status': 'ERROR',
        'error':
            detail?.toString() ?? 'Backend error (${response.statusCode}).',
      };
    } catch (e) {
      return {'status': 'ERROR', 'error': 'Connection error: ' + e.toString()};
    }
  }

  static Future<Map<String, dynamic>> createComplianceReport(int scanId) {
    return postJson('/reports/scans/$scanId', const <String, dynamic>{});
  }

  static Future<Uint8List?> getBytes(String path) async {
    try {
      final response = await http
          .get(Uri.parse(baseUrl + path), headers: _authHeaders)
          .timeout(const Duration(seconds: 30));
      return response.statusCode == 200 ? response.bodyBytes : null;
    } catch (_) {
      return null;
    }
  }

  static Future<Map<String, dynamic>> delete(String path) async {
    try {
      final response = await http
          .delete(Uri.parse(baseUrl + path), headers: _authHeaders)
          .timeout(const Duration(seconds: 15));
      if (response.statusCode == 200)
        return Map<String, dynamic>.from(jsonDecode(response.body) as Map);
      dynamic detail;
      try {
        detail = jsonDecode(response.body)['detail'];
      } catch (_) {}
      return {
        'status': 'ERROR',
        'error':
            detail?.toString() ?? 'Backend error (${response.statusCode}).',
      };
    } catch (e) {
      return {'status': 'ERROR', 'error': 'Connection error: ' + e.toString()};
    }
  }

  static Future<void> signOut() async {
    _sessionToken = null;
    currentUser = null;
  }

  static String? _sessionToken;

  static Map<String, String> get _authHeaders => _sessionToken == null
      ? const <String, String>{}
      : <String, String>{'Authorization': 'Bearer ' + _sessionToken!};

  static Future<Map<String, dynamic>> _authRequest(
    String endpoint,
    Map<String, dynamic> payload,
  ) async {
    final response = await http
        .post(
          Uri.parse(baseUrl + endpoint),
          headers: {'Content-Type': 'application/json'},
          body: jsonEncode(payload),
        )
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200 || response.statusCode == 201)
      return jsonDecode(response.body);

    dynamic detail;
    try {
      detail = jsonDecode(response.body)['detail'];
    } catch (_) {}
    throw Exception(detail ?? 'Authentication failed');
  }

  static Future<void> signIn({
    required String email,
    required String password,
  }) async {
    final session = await _authRequest('/auth/login', {
      'email': email,
      'password': password,
    });
    _sessionToken = session['access_token']?.toString();
    currentUser = Map<String, dynamic>.from(session['user'] as Map);
  }

  static Future<void> register({
    required String name,
    required String email,
    required String password,
    required String role,
    required String organizationName,
  }) async {
    await _authRequest('/auth/register', {
      'full_name': name,
      'email': email,
      'password': password,
      'role': role,
      'organization_name': organizationName,
    });
  }

  static Future<void> initialize() async {}
}
