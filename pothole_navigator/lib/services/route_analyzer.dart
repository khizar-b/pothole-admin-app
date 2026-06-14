import 'dart:math';

import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../models/pothole.dart';
import '../models/route_option.dart';

class RouteAnalyzer {
  /// A pothole closer than this to the route polyline counts as "on" it.
  static const double proximityMeters = 30;

  static const _severityWeight = {'low': 1, 'medium': 2, 'high': 3};

  /// Attach nearby potholes and a vehicle-specific risk score to each route.
  static void analyze(
      List<RouteOption> routes, List<Pothole> potholes, VehicleType vehicle) {
    for (final route in routes) {
      route.potholes = potholes
          .where((p) =>
              _distanceToPolyline(p.position, route.points) <= proximityMeters)
          .toList();
      route.riskScore = route.potholes.fold(
          0, (sum, p) => sum + (_severityWeight[p.impactFor(vehicle)] ?? 1));
    }
  }

  /// The route with the lowest risk; ties broken by travel time.
  static RouteOption best(List<RouteOption> routes) {
    final sorted = [...routes]..sort((a, b) {
        final byRisk = a.riskScore.compareTo(b.riskScore);
        return byRisk != 0
            ? byRisk
            : a.durationSeconds.compareTo(b.durationSeconds);
      });
    return sorted.first;
  }

  /// Bounding box around all route points, padded by ~[proximityMeters].
  static Map<String, double> boundingBox(List<RouteOption> routes) {
    var minLat = double.infinity, maxLat = -double.infinity;
    var minLng = double.infinity, maxLng = -double.infinity;
    for (final route in routes) {
      for (final p in route.points) {
        minLat = min(minLat, p.latitude);
        maxLat = max(maxLat, p.latitude);
        minLng = min(minLng, p.longitude);
        maxLng = max(maxLng, p.longitude);
      }
    }
    const latPad = proximityMeters / 111320; // meters -> degrees latitude
    final lngPad =
        latPad / cos((minLat + maxLat) / 2 * pi / 180).abs().clamp(0.1, 1.0);
    return {
      'min_lat': minLat - latPad,
      'max_lat': maxLat + latPad,
      'min_lng': minLng - lngPad,
      'max_lng': maxLng + lngPad,
    };
  }

  static double _distanceToPolyline(LatLng point, List<LatLng> polyline) {
    var best = double.infinity;
    for (var i = 0; i < polyline.length - 1; i++) {
      best = min(best, _distanceToSegment(point, polyline[i], polyline[i + 1]));
      if (best == 0) break;
    }
    return best;
  }

  /// Point-to-segment distance in meters using a local equirectangular
  /// projection (accurate at street scale).
  static double _distanceToSegment(LatLng p, LatLng a, LatLng b) {
    const metersPerDegLat = 111320.0;
    final metersPerDegLng = metersPerDegLat * cos(p.latitude * pi / 180);

    final ax = (a.longitude - p.longitude) * metersPerDegLng;
    final ay = (a.latitude - p.latitude) * metersPerDegLat;
    final bx = (b.longitude - p.longitude) * metersPerDegLng;
    final by = (b.latitude - p.latitude) * metersPerDegLat;

    final dx = bx - ax, dy = by - ay;
    final lenSq = dx * dx + dy * dy;
    if (lenSq == 0) return sqrt(ax * ax + ay * ay);

    final t = (-(ax * dx + ay * dy) / lenSq).clamp(0.0, 1.0);
    final cx = ax + t * dx, cy = ay + t * dy;
    return sqrt(cx * cx + cy * cy);
  }
}
