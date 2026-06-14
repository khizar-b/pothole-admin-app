import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Runtime configuration loaded from the bundled .env asset.
class AppConfig {
  /// Google Maps Platform key used for Directions + Places REST calls.
  static String get googleApiKey => dotenv.env['GOOGLE_MAPS_API_KEY'] ?? '';

  /// Base URL of the pothole admin backend.
  /// 10.0.2.2 reaches the host machine from the Android emulator;
  /// use the PC's LAN IP (e.g. http://192.168.1.4:5000) on a physical device.
  static String get apiBaseUrl =>
      dotenv.env['API_BASE_URL'] ?? 'http://10.0.2.2:5000';
}
