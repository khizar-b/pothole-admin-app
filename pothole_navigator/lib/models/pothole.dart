import 'package:google_maps_flutter/google_maps_flutter.dart';

class Pothole {
  final int id;
  final double latitude;
  final double longitude;
  final double impactScore;
  final String bikeImpact;
  final String carImpact;
  final double confidenceScore;

  Pothole({
    required this.id,
    required this.latitude,
    required this.longitude,
    required this.impactScore,
    required this.bikeImpact,
    required this.carImpact,
    required this.confidenceScore,
  });

  factory Pothole.fromJson(Map<String, dynamic> json) => Pothole(
        id: json['id'] as int,
        latitude: (json['latitude'] as num).toDouble(),
        longitude: (json['longitude'] as num).toDouble(),
        impactScore: (json['impact_score'] as num).toDouble(),
        bikeImpact: json['bike_impact'] as String,
        carImpact: json['car_impact'] as String,
        confidenceScore: (json['confidence_score'] as num).toDouble(),
      );

  LatLng get position => LatLng(latitude, longitude);

  /// Impact level ('low'/'medium'/'high') as experienced by [vehicle].
  String impactFor(VehicleType vehicle) {
    switch (vehicle) {
      case VehicleType.bike:
        return bikeImpact;
      case VehicleType.car:
        return carImpact;
      case VehicleType.truck:
        // Trucks shrug off potholes one level better than cars.
        switch (carImpact) {
          case 'high':
            return 'medium';
          case 'medium':
            return 'low';
          default:
            return 'low';
        }
    }
  }
}

enum VehicleType { car, bike, truck }

extension VehicleTypeLabel on VehicleType {
  String get label {
    switch (this) {
      case VehicleType.car:
        return 'Car';
      case VehicleType.bike:
        return 'Bike';
      case VehicleType.truck:
        return 'Truck';
    }
  }
}
