import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geocoding/geocoding.dart';

import '../../models/event.dart';
import '../../api/event_api.dart';
import '../../widgets/bottom_nav_bar.dart';
import '../event_details/event_details_screen.dart';

class NearbyScreen extends StatefulWidget {
  const NearbyScreen({super.key});

  @override
  State<NearbyScreen> createState() => _NearbyScreenState();
}

class _NearbyScreenState extends State<NearbyScreen> {
  List<Event> events = [];
  Map<int, LatLng> _eventCoordinates = {};
  bool _isLoading = true;
  final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

  @override
  void initState() {
    super.initState();
    _loadEventsAndCoordinates();
  }

  Future<void> _loadEventsAndCoordinates() async {
    try {
      final fetchedEvents = await EventApi.getEvents();
      Map<int, LatLng> coordsMap = {};

      for (var event in fetchedEvents) {
        if (event.id == null) continue;

        try {
          List<Location> locations = await locationFromAddress(event.location);
          if (locations.isNotEmpty) {
            coordsMap[event.id!] = LatLng(
              locations[0].latitude,
              locations[0].longitude,
            );
          }
        } catch (e) {
          debugPrint('Geocoding failed for "${event.location}": $e');
        }
      }

      setState(() {
        events = fetchedEvents;
        _eventCoordinates = coordsMap;
        _isLoading = false;
      });
    } catch (e) {
      debugPrint('Error loading events: $e');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (events.isEmpty) {
      return const Scaffold(
        backgroundColor: Colors.white,
        body: Center(child: Text("No events available.")),
      );
    }

    return Scaffold(
      backgroundColor: uniRed,
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text(
          'UniGather',
          style: TextStyle(
            color: Colors.black,
            fontFamily: 'Roboto',
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(16),
            ),
            elevation: 6,
            child: SizedBox(
              width: double.infinity,
              height: 400,
              child: FlutterMap(
                options: MapOptions(
                  center: LatLng(51.1091, 17.0605), // Plac Grunwaldzki
                  zoom: 15.0,
                ),
                children: [
                  TileLayer(
                    urlTemplate:
                        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                    subdomains: ['a', 'b', 'c'],
                    userAgentPackageName:
                        'com.example.unigather', // ⚠️ Required in 4.x
                  ),
                  MarkerLayer(
                    markers:
                        events
                            .where(
                              (e) =>
                                  e.id != null &&
                                  _eventCoordinates.containsKey(e.id!),
                            )
                            .map((event) {
                              final coords = _eventCoordinates[event.id!]!;
                              return Marker(
                                width: 80,
                                height: 80,
                                point: coords,
                                builder:
                                    (ctx) => GestureDetector(
                                      onTap: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder:
                                                (_) => EventDetailsScreen(
                                                  event: event,
                                                ),
                                          ),
                                        );
                                      },
                                      child: const Icon(
                                        Icons.location_on,
                                        size: 40,
                                        color: Colors.red,
                                      ),
                                    ),
                              );
                            })
                            .toList(),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 2,
        onTap: (index) {
          switch (index) {
            case 0:
              Navigator.pushNamed(context, '/profile');
              break;
            case 1:
              Navigator.pushNamed(context, '/explore');
              break;
            case 2:
              Navigator.pushNamed(context, '/nearby');
              break;
            case 3:
              Navigator.pushNamed(context, '/create');
              break;
          }
        },
      ),
    );
  }
}
