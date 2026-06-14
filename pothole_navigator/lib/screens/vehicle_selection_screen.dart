import 'package:flutter/material.dart';

import '../models/pothole.dart';
import 'map_screen.dart';

class VehicleSelectionScreen extends StatelessWidget {
  const VehicleSelectionScreen({super.key});

  static const _vehicles = [
    (VehicleType.car, Icons.directions_car, 'Standard pothole sensitivity'),
    (VehicleType.bike, Icons.two_wheeler, 'Most affected by potholes'),
    (VehicleType.truck, Icons.local_shipping, 'Least affected by potholes'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Spacer(),
              Icon(Icons.add_road,
                  size: 64, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 16),
              Text('Pothole Navigator',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 8),
              Text('Choose your vehicle to get pothole-aware routes',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodyMedium),
              const SizedBox(height: 32),
              for (final (type, icon, subtitle) in _vehicles)
                Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: Card(
                    child: ListTile(
                      contentPadding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 8),
                      leading: Icon(icon, size: 36),
                      title: Text(type.label,
                          style: const TextStyle(
                              fontSize: 18, fontWeight: FontWeight.w600)),
                      subtitle: Text(subtitle),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.of(context).push(
                        MaterialPageRoute(
                            builder: (_) => MapScreen(vehicle: type)),
                      ),
                    ),
                  ),
                ),
              const Spacer(flex: 2),
            ],
          ),
        ),
      ),
    );
  }
}
