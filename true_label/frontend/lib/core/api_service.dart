import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiService {
  static const String defaultUrl = 'https://true-label-backend.onrender.com';

  static String get baseUrl {
    return dotenv.env['API_BASE_URL'] ?? defaultUrl;
  }

  static Future<Map<String, dynamic>?> analyzeArScan({
    required List<XFile> imageFiles, // <--- Accepts a list of images now
    required double distanceMm,
    required double focalLengthPx,
  }) async {
    try {
      var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/scan/analyze-ar'));
      
      request.fields['distance_mm'] = distanceMm.toString();
      request.fields['focal_length_px'] = focalLengthPx.toString();

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
}