import 'dart:async';

import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../models/pothole.dart';
import '../models/route_option.dart';
import '../services/directions_service.dart';
import '../services/places_service.dart';
import '../services/pothole_api.dart';
import '../services/route_analyzer.dart';

class MapScreen extends StatefulWidget {
  final VehicleType vehicle;

  const MapScreen({super.key, required this.vehicle});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  static const _fallbackCenter = LatLng(33.6602, 73.0756); // Faizabad, RWP

  GoogleMapController? _mapController;
  final _searchController = TextEditingController();
  Timer? _debounce;

  LatLng? _currentLocation;
  List<PlaceSuggestion> _suggestions = [];
  List<RouteOption> _routes = [];
  int _selectedRoute = 0;
  bool _loadingRoutes = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _initLocation();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _initLocation() async {
    try {
      if (!await Geolocator.isLocationServiceEnabled()) {
        throw Exception('Location services are disabled');
      }
      var permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }
      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw Exception('Location permission denied');
      }
      final pos = await Geolocator.getCurrentPosition();
      setState(() => _currentLocation = LatLng(pos.latitude, pos.longitude));
      _mapController?.animateCamera(
          CameraUpdate.newLatLngZoom(_currentLocation!, 15));
    } catch (e) {
      setState(() => _error = e.toString());
    }
  }

  void _onSearchChanged(String input) {
    _debounce?.cancel();
    if (input.trim().length < 3) {
      setState(() => _suggestions = []);
      return;
    }
    _debounce = Timer(const Duration(milliseconds: 400), () async {
      try {
        final results =
            await PlacesService.autocomplete(input, near: _currentLocation);
        if (mounted) setState(() => _suggestions = results);
      } catch (e) {
        if (mounted) setState(() => _error = e.toString());
      }
    });
  }

  Future<void> _onDestinationPicked(PlaceSuggestion suggestion) async {
    FocusScope.of(context).unfocus();
    setState(() {
      _searchController.text = suggestion.description;
      _suggestions = [];
      _loadingRoutes = true;
      _error = null;
      _routes = [];
    });

    try {
      final origin = _currentLocation ?? _fallbackCenter;
      final destination = await PlacesService.placeLocation(suggestion.placeId);

      final routes = await DirectionsService.getRoutes(origin, destination);
      if (routes.isEmpty) throw Exception('No routes found');

      final box = RouteAnalyzer.boundingBox(routes);
      final potholes = await PotholeApi.fetchPotholes(
        minLat: box['min_lat'],
        maxLat: box['max_lat'],
        minLng: box['min_lng'],
        maxLng: box['max_lng'],
      );
      RouteAnalyzer.analyze(routes, potholes, widget.vehicle);

      final best = RouteAnalyzer.best(routes);
      setState(() {
        _routes = routes;
        _selectedRoute = routes.indexOf(best);
        _loadingRoutes = false;
      });
      _fitCamera(routes);
    } catch (e) {
      setState(() {
        _loadingRoutes = false;
        _error = e.toString();
      });
    }
  }

  void _fitCamera(List<RouteOption> routes) {
    final box = RouteAnalyzer.boundingBox(routes);
    _mapController?.animateCamera(CameraUpdate.newLatLngBounds(
      LatLngBounds(
        southwest: LatLng(box['min_lat']!, box['min_lng']!),
        northeast: LatLng(box['max_lat']!, box['max_lng']!),
      ),
      60,
    ));
  }

  Set<Polyline> get _polylines => {
        for (var i = 0; i < _routes.length; i++)
          Polyline(
            polylineId: PolylineId('route_$i'),
            points: _routes[i].points,
            width: i == _selectedRoute ? 6 : 4,
            color: i == _selectedRoute
                ? Colors.blue
                : Colors.blueGrey.withValues(alpha: 0.6),
            onTap: () => setState(() => _selectedRoute = i),
            consumeTapEvents: true,
          ),
      };

  Set<Marker> get _markers {
    if (_routes.isEmpty) return {};
    final markers = <Marker>{};
    for (final pothole in _routes[_selectedRoute].potholes) {
      final impact = pothole.impactFor(widget.vehicle);
      markers.add(Marker(
        markerId: MarkerId('pothole_${pothole.id}'),
        position: pothole.position,
        icon: BitmapDescriptor.defaultMarkerWithHue(switch (impact) {
          'high' => BitmapDescriptor.hueRed,
          'medium' => BitmapDescriptor.hueOrange,
          _ => BitmapDescriptor.hueYellow,
        }),
        infoWindow: InfoWindow(
          title: 'Pothole — $impact impact',
          snippet:
              'Impact score: ${pothole.impactScore.toStringAsFixed(1)} / 100',
        ),
      ));
    }
    return markers;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Route — ${widget.vehicle.label}'),
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: const CameraPosition(
                target: _fallbackCenter, zoom: 13),
            myLocationEnabled: true,
            myLocationButtonEnabled: true,
            polylines: _polylines,
            markers: _markers,
            onMapCreated: (c) {
              _mapController = c;
              if (_currentLocation != null) {
                c.animateCamera(
                    CameraUpdate.newLatLngZoom(_currentLocation!, 15));
              }
            },
          ),
          // Destination search box + suggestions
          Positioned(
            top: 12,
            left: 12,
            right: 12,
            child: Column(
              children: [
                Material(
                  elevation: 4,
                  borderRadius: BorderRadius.circular(12),
                  child: TextField(
                    controller: _searchController,
                    onChanged: _onSearchChanged,
                    decoration: InputDecoration(
                      hintText: 'Where do you want to go?',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () => setState(() {
                                _searchController.clear();
                                _suggestions = [];
                                _routes = [];
                              }),
                            )
                          : null,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      filled: true,
                      fillColor: Colors.white,
                    ),
                  ),
                ),
                if (_suggestions.isNotEmpty)
                  Material(
                    elevation: 4,
                    borderRadius: BorderRadius.circular(12),
                    child: ListView.separated(
                      shrinkWrap: true,
                      padding: EdgeInsets.zero,
                      itemCount: _suggestions.length,
                      separatorBuilder: (_, _) => const Divider(height: 1),
                      itemBuilder: (_, i) => ListTile(
                        dense: true,
                        leading: const Icon(Icons.place_outlined),
                        title: Text(_suggestions[i].description,
                            maxLines: 2, overflow: TextOverflow.ellipsis),
                        onTap: () => _onDestinationPicked(_suggestions[i]),
                      ),
                    ),
                  ),
              ],
            ),
          ),
          if (_loadingRoutes)
            const Center(child: CircularProgressIndicator()),
          if (_error != null)
            Positioned(
              bottom: _routes.isEmpty ? 24 : 220,
              left: 12,
              right: 12,
              child: Card(
                color: Theme.of(context).colorScheme.errorContainer,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text(_error!,
                      style: TextStyle(
                          color:
                              Theme.of(context).colorScheme.onErrorContainer)),
                ),
              ),
            ),
          // Route comparison cards
          if (_routes.isNotEmpty)
            Positioned(
              bottom: 16,
              left: 0,
              right: 0,
              child: SizedBox(
                height: 150,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  itemCount: _routes.length,
                  itemBuilder: (_, i) => _routeCard(i),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _routeCard(int index) {
    final route = _routes[index];
    final selected = index == _selectedRoute;
    final isBest = route == RouteAnalyzer.best(_routes);

    return GestureDetector(
      onTap: () => setState(() => _selectedRoute = index),
      child: Container(
        width: 250,
        margin: const EdgeInsets.only(right: 10),
        child: Card(
          elevation: selected ? 6 : 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
            side: selected
                ? const BorderSide(color: Colors.blue, width: 2)
                : BorderSide.none,
          ),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        route.summary.isEmpty
                            ? 'Route ${index + 1}'
                            : 'Via ${route.summary}',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    if (isBest)
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 2),
                        decoration: BoxDecoration(
                          color: Colors.green.shade100,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text('BEST',
                            style: TextStyle(
                                color: Colors.green.shade800,
                                fontSize: 11,
                                fontWeight: FontWeight.bold)),
                      ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.schedule, size: 16),
                    const SizedBox(width: 4),
                    Text(route.durationText),
                    const SizedBox(width: 12),
                    const Icon(Icons.straighten, size: 16),
                    const SizedBox(width: 4),
                    Text(route.distanceText),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.warning_amber,
                        size: 16,
                        color: route.potholes.isEmpty
                            ? Colors.green
                            : Colors.orange),
                    const SizedBox(width: 4),
                    Text(
                      route.potholes.isEmpty
                          ? 'No known potholes'
                          : '${route.potholes.length} pothole(s) · risk ${route.riskScore}',
                      style: const TextStyle(fontSize: 13),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
