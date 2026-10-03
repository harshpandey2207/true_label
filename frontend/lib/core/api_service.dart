import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiService {
  static const String defaultUrl = 'https://true-label-backend.onrender.com';

  static String get baseUrl {
    return dotenv.env['API_BASE_URL'] ?? defaultUrl;
  }

  /// Fire-and-forget pre-warming ping to wake up backend if it was sleeping
  static void preWarmBackend() {
    try {
      http.get(Uri.parse('$baseUrl/')).catchError((_) => http.Response('', 500));
    } catch (_) {}
  }

  static Future<Map<String, dynamic>?> analyzeArScan({
    required List<XFile> imageFiles, // <--- Accepts a list of images now
    required double distanceMm,
    required double focalLengthPx,
    required int categoryId,
  }) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/scan/analyze-ar'));
      
      request.fields['distance_mm'] = distanceMm.toString();
      request.fields['focal_length_px'] = focalLengthPx.toString();
      request.fields['category_id'] = categoryId.toString();

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

      var response = await request.send();
      
      if (response.statusCode == 200) {
        final respStr = await response.stream.bytesToString();
        return jsonDecode(respStr);
      } else {
        return {
          'status': 'ERROR',
          'error': 'Backend error (${response.statusCode}). Backend may be waking up, please retry in 30 seconds.',
        };
      }
    } catch (e) {
      return {
        'status': 'ERROR',
        'error': 'Connection error: $e',
      };
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
  }) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/label/generate'));

      request.fields['product_name'] = productName;
      request.fields['product_category'] = productCategory;
      request.fields['shape'] = shape;
      request.fields['dimensions'] = dimensions;
      request.fields['custom_prompt'] = customPrompt;
      request.fields['missing_tag_values'] = jsonEncode(missingTagValues);

      for (var imageFile in imageFiles) {
        var bytes = await imageFile.readAsBytes();
        request.files.add(http.MultipartFile.fromBytes('images', bytes, filename: imageFile.name));
      }

      var response = await request.send();
      final respStr = await response.stream.bytesToString();

      if (response.statusCode == 200) {
        return jsonDecode(respStr);
      } else {
        return {'success': false, 'error': 'Backend error ${response.statusCode}: $respStr'};
      }
    } catch (e) {
      return {'success': false, 'error': 'Connection error: $e'};
    }
  }
}