import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:pothole_navigator/screens/vehicle_selection_screen.dart';

void main() {
  testWidgets('Vehicle selection shows all three vehicle types',
      (WidgetTester tester) async {
    await tester
        .pumpWidget(const MaterialApp(home: VehicleSelectionScreen()));

    expect(find.text('Car'), findsOneWidget);
    expect(find.text('Bike'), findsOneWidget);
    expect(find.text('Truck'), findsOneWidget);
  });
}
