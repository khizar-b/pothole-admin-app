import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/pothole.dart';

class PotholeApi {
  /// Fetch potholes from the admin backend, optionally limited to a
  /// bounding box (all four bounds must be provided to filter).
  static Future<List<Pothole>> fetchPotholes({
    double? minLat,
    double? maxLat,
    double? minLng,
    double? maxLng,
  }) async {
    var uri = Uri.parse('${AppConfig.apiBaseUrl}/api/public/potholes');
    if (minLat != null && maxLat != null && minLng != null && maxLng != null) {
      uri = uri.replace(queryParameters: {
        'min_lat': '$minLat',
        'max_lat': '$maxLat',
        'min_lng': '$minLng',
        'max_lng': '$maxLng',
      });
    }

    final response = await http.get(uri).timeout(const Duration(seconds: 15));
    if (response.statusCode != 200) {
      throw Exception('Pothole API error ${response.statusCode}');
    }

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    return (body['potholes'] as List)
        .map((p) => Pothole.fromJson(p as Map<String, dynamic>))
        .toList();
  }
}
