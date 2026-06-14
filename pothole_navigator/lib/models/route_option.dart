import 'package:google_maps_flutter/google_maps_flutter.dart';

import 'pothole.dart';

/// One candidate route returned by the Directions API, plus its
/// pothole analysis for the selected vehicle.
class RouteOption {
  final String summary;
  final List<LatLng> points;
  final String distanceText;
  final int distanceMeters;
  final String durationText;
  final int durationSeconds;

  /// Potholes within the proximity threshold of this route.
  List<Pothole> potholes = [];

  /// Severity-weighted risk for the selected vehicle (lower is better).
  int riskScore = 0;

  RouteOption({
    required this.summary,
    required this.points,
    required this.distanceText,
    required this.distanceMeters,
    required this.durationText,
    required this.durationSeconds,
  });
}
