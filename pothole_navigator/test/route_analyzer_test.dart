import 'package:flutter_test/flutter_test.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import 'package:pothole_navigator/models/pothole.dart';
import 'package:pothole_navigator/models/route_option.dart';
import 'package:pothole_navigator/services/route_analyzer.dart';

Pothole pothole(int id, double lat, double lng,
        {String bike = 'high', String car = 'medium'}) =>
    Pothole(
      id: id,
      latitude: lat,
      longitude: lng,
      impactScore: 50,
      bikeImpact: bike,
      carImpact: car,
      confidenceScore: 0.9,
    );

RouteOption route(String name, List<LatLng> points,
        {int durationSeconds = 600}) =>
    RouteOption(
      summary: name,
      points: points,
      distanceText: '5 km',
      distanceMeters: 5000,
      durationText: '10 min',
      durationSeconds: durationSeconds,
    );

void main() {
  // Murree Road segment used in sample_data_rawalpindi.csv
  final murreeRoad = [
    const LatLng(33.6614, 73.0782),
    const LatLng(33.6565, 73.0745),
    const LatLng(33.6520, 73.0712),
    const LatLng(33.6478, 73.0680),
    const LatLng(33.6300, 73.0680),
  ];

  test('counts potholes on the route and ignores distant ones', () {
    final onRoute = pothole(1, 33.6565, 73.0745); // exactly on a vertex
    final nearRoute = pothole(2, 33.65201, 73.07121); // ~1.5 m off
    final farAway = pothole(3, 33.7000, 73.2000); // ~12 km away

    final r = route('Murree Rd', murreeRoad);
    RouteAnalyzer.analyze([r], [onRoute, nearRoute, farAway], VehicleType.car);

    expect(r.potholes.map((p) => p.id), containsAll([1, 2]));
    expect(r.potholes.map((p) => p.id), isNot(contains(3)));
  });

  test('risk score weights severity per vehicle', () {
    final p = pothole(1, 33.6565, 73.0745, bike: 'high', car: 'medium');
    final r1 = route('A', murreeRoad);
    RouteAnalyzer.analyze([r1], [p], VehicleType.bike);
    expect(r1.riskScore, 3); // high = 3

    final r2 = route('A', murreeRoad);
    RouteAnalyzer.analyze([r2], [p], VehicleType.car);
    expect(r2.riskScore, 2); // medium = 2

    final r3 = route('A', murreeRoad);
    RouteAnalyzer.analyze([r3], [p], VehicleType.truck);
    expect(r3.riskScore, 1); // truck: one level below car -> low = 1
  });

  test('best() prefers fewer potholes, then shorter time', () {
    final potholes = [
      pothole(1, 33.6565, 73.0745),
      pothole(2, 33.6520, 73.0712),
    ];
    final risky = route('Murree Rd', murreeRoad, durationSeconds: 500);
    final clean = route('IJP Rd', [
      const LatLng(33.6655, 73.0710),
      const LatLng(33.6700, 73.0500),
      const LatLng(33.6300, 73.0400),
    ], durationSeconds: 900);

    RouteAnalyzer.analyze([risky, clean], potholes, VehicleType.car);
    expect(RouteAnalyzer.best([risky, clean]).summary, 'IJP Rd');

    // With no potholes anywhere, the faster route wins.
    RouteAnalyzer.analyze([risky, clean], [], VehicleType.car);
    expect(RouteAnalyzer.best([risky, clean]).summary, 'Murree Rd');
  });
}
