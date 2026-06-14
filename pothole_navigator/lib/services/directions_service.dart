import 'dart:convert';

import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:http/http.dart' as http;

import '../config.dart';
import '../models/route_option.dart';

/// Fetches routes from the Google Routes API (computeRoutes).
class DirectionsService {
  /// Fetch the main route plus alternatives between [origin] and [destination].
  static Future<List<RouteOption>> getRoutes(
      LatLng origin, LatLng destination) async {
    final response = await http
        .post(
          Uri.parse('https://routes.googleapis.com/directions/v2:computeRoutes'),
          headers: {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': AppConfig.googleApiKey,
            'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,'
                'routes.polyline.encodedPolyline,routes.description',
          },
          body: jsonEncode({
            'origin': {
              'location': {
                'latLng': {
                  'latitude': origin.latitude,
                  'longitude': origin.longitude,
                }
              }
            },
            'destination': {
              'location': {
                'latLng': {
                  'latitude': destination.latitude,
                  'longitude': destination.longitude,
                }
              }
            },
            'travelMode': 'DRIVE',
            'computeAlternativeRoutes': true,
          }),
        )
        .timeout(const Duration(seconds: 20));

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode != 200) {
      final message = (body['error'] as Map<String, dynamic>?)?['message'];
      throw Exception('Routes API: ${message ?? 'HTTP ${response.statusCode}'}');
    }

    final routes = (body['routes'] as List?) ?? [];
    if (routes.isEmpty) throw Exception('Routes API returned no routes');

    return routes.map((r) {
      final route = r as Map<String, dynamic>;
      final distanceMeters = (route['distanceMeters'] as num?)?.toInt() ?? 0;
      // duration arrives as e.g. "845s"
      final durationSeconds = int.tryParse(
              (route['duration'] as String? ?? '0s').replaceAll('s', '')) ??
          0;
      return RouteOption(
        summary: (route['description'] as String?) ?? '',
        points: decodePolyline(
            (route['polyline'] as Map<String, dynamic>)['encodedPolyline']
                as String),
        distanceText: _formatDistance(distanceMeters),
        distanceMeters: distanceMeters,
        durationText: _formatDuration(durationSeconds),
        durationSeconds: durationSeconds,
      );
    }).toList();
  }

  static String _formatDistance(int meters) => meters < 1000
      ? '$meters m'
      : '${(meters / 1000).toStringAsFixed(1)} km';

  static String _formatDuration(int seconds) {
    final minutes = (seconds / 60).round();
    if (minutes < 60) return '$minutes min';
    return '${minutes ~/ 60} hr ${minutes % 60} min';
  }

  /// Decode a Google encoded polyline string into LatLng points.
  static List<LatLng> decodePolyline(String encoded) {
    final points = <LatLng>[];
    int index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
      int shift = 0, result = 0, byte;
      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1f) << shift;
        shift += 5;
      } while (byte >= 0x20);
      lat += (result & 1) != 0 ? ~(result >> 1) : (result >> 1);

      shift = 0;
      result = 0;
      do {
        byte = encoded.codeUnitAt(index++) - 63;
        result |= (byte & 0x1f) << shift;
        shift += 5;
      } while (byte >= 0x20);
      lng += (result & 1) != 0 ? ~(result >> 1) : (result >> 1);

      points.add(LatLng(lat / 1e5, lng / 1e5));
    }
    return points;
  }
}
