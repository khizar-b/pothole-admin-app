import 'dart:convert';

import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;

import '../config.dart';

class PlaceSuggestion {
  final String placeId;
  final String description;

  PlaceSuggestion({required this.placeId, required this.description});
}

/// Destination search using Places API (New).
class PlacesService {
  /// Autocomplete suggestions for [input], biased around [near] if given.
  static Future<List<PlaceSuggestion>> autocomplete(String input,
      {LatLng? near}) async {
    final response = await http
        .post(
          Uri.parse('https://places.googleapis.com/v1/places:autocomplete'),
          headers: {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': AppConfig.googleApiKey,
          },
          body: jsonEncode({
            'input': input,
            if (near != null)
              'locationBias': {
                'circle': {
                  'center': {
                    'latitude': near.latitude,
                    'longitude': near.longitude,
                  },
                  'radius': 50000.0,
                }
              },
          }),
        )
        .timeout(const Duration(seconds: 15));

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode != 200) {
      final message = (body['error'] as Map<String, dynamic>?)?['message'];
      throw Exception('Places API: ${message ?? 'HTTP ${response.statusCode}'}');
    }

    return ((body['suggestions'] as List?) ?? [])
        .map((s) => (s as Map<String, dynamic>)['placePrediction'])
        .whereType<Map<String, dynamic>>()
        .map((pred) => PlaceSuggestion(
              placeId: pred['placeId'] as String,
              description:
                  ((pred['text'] as Map<String, dynamic>?)?['text'] as String?) ??
                      '',
            ))
        .toList();
  }

  /// Resolve a place id to coordinates.
  static Future<LatLng> placeLocation(String placeId) async {
    final response = await http.get(
      Uri.parse('https://places.googleapis.com/v1/places/$placeId'),
      headers: {
        'X-Goog-Api-Key': AppConfig.googleApiKey,
        'X-Goog-FieldMask': 'location',
      },
    ).timeout(const Duration(seconds: 15));

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode != 200) {
      final message = (body['error'] as Map<String, dynamic>?)?['message'];
      throw Exception(
          'Place details API: ${message ?? 'HTTP ${response.statusCode}'}');
    }

    final loc = body['location'] as Map<String, dynamic>;
    return LatLng(
        (loc['latitude'] as num).toDouble(), (loc['longitude'] as num).toDouble());
  }
}
