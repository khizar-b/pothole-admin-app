# Pothole Navigator (Mobile App)

An Android app that finds **pothole-aware routes**. Pick a vehicle
(car / bike / truck), choose a destination, and the app compares
alternative routes by distance, time, and the number & severity of
potholes on each — then highlights the smoothest one as **BEST**.

Pothole data comes from the admin portal (`../`, a Flask + PostgreSQL app)
through its public endpoint `GET /api/public/potholes`.

| | |
|---|---|
| Framework | Flutter (Android) |
| Maps | Google Maps SDK for Android |
| Routing | Google Routes API (with alternatives) |
| Search | Google Places API (New) |
| Backend | `../` Flask admin portal |

---

## Prerequisites

- [Flutter SDK](https://docs.flutter.dev/get-started/install) installed (`flutter doctor` passes)
- An Android device (USB debugging on) or emulator
- The admin backend running — see [`../README.md`](../README.md)
- A **Google Maps Platform API key** (steps below)

## 1. Get a Google Maps API key

In the [Google Cloud Console](https://console.cloud.google.com):

1. Create a project and **enable billing** (required — there is a free
   monthly usage allowance, but a card must be on file).
2. **APIs & Services → Library**, enable all three:
   - **Maps SDK for Android**
   - **Routes API**
   - **Places API (New)**
3. **APIs & Services → Credentials → Create credentials → API key**, copy it.

## 2. Configure the app

The key goes in **two** files (both are git-ignored, so your key stays private):

**a) `.env`** — copy the template and paste your key:

```bash
cp .env.example .env
```
```env
GOOGLE_MAPS_API_KEY=PASTE_YOUR_KEY_HERE
API_BASE_URL=http://10.0.2.2:5000
```

**b) `android/local.properties`** — add one line:

```properties
MAPS_API_KEY=PASTE_YOUR_KEY_HERE
```

### Set `API_BASE_URL` to match how you run

| How you run | `API_BASE_URL` | Note |
|---|---|---|
| Android emulator | `http://10.0.2.2:5000` | `10.0.2.2` = your PC from the emulator |
| Physical phone via USB | `http://127.0.0.1:5000` | run `adb reverse tcp:5000 tcp:5000` first |
| Physical phone on same WiFi | `http://<your-pc-ip>:5000` | allow port 5000 through the PC firewall |

## 3. Run

```bash
flutter pub get
flutter run
```

Or build an installable APK:

```bash
flutter build apk --debug
# output: build/app/outputs/flutter-apk/app-debug.apk
```

---

## How it works

1. **Pick a vehicle** → opens the map on your current location.
2. **Search a destination** → Places (New) autocomplete suggestions.
3. The app asks the **Routes API** for the main route + alternatives.
4. For each route it fetches nearby potholes from the backend and counts
   the ones **within 30 m of the route line**, weighting each by severity
   for the chosen vehicle (bikes feel potholes most, trucks least).
5. The lowest-risk route (ties broken by time) is badged **BEST**;
   potholes show as markers — red = high, orange = medium, yellow = low.

## Project layout

```
lib/
  main.dart                     app entry, loads .env
  config.dart                   reads API key + backend URL
  models/                       Pothole, RouteOption, VehicleType
  services/
    places_service.dart         destination autocomplete + details
    directions_service.dart     Routes API + polyline decoding
    pothole_api.dart            fetches potholes from the backend
    route_analyzer.dart         pothole-to-route matching + risk scoring
  screens/
    vehicle_selection_screen.dart
    map_screen.dart             map, search, route comparison UI
test/                           widget + route-analyzer unit tests
```

Run the tests with `flutter test`.

## Troubleshooting

- **`REQUEST_DENIED` / no routes or suggestions** — an API isn't enabled or
  billing is off. Re-check step 1.
- **Map is blank/grey** — `MAPS_API_KEY` missing from `android/local.properties`,
  or Maps SDK for Android not enabled.
- **Potholes never appear** — the app couldn't reach the backend. Confirm
  `API_BASE_URL` and that the Flask app is running (open it in the phone's browser).
