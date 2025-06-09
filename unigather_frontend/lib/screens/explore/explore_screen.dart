import 'package:flutter/material.dart';

import '../../models/event.dart';
import '../../api/event_api.dart';
import '../../api/attendance_api.dart';
import '../../api/likes_api.dart';
import '../../services/auth_service.dart';
import '../../widgets/bottom_nav_bar.dart';
import '../event_details/event_details_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  List<Event> events = [];
  Set<int> likedEventIds = {};
  int currentIndex = 0;
  bool isLoading = true;
  int? userId;

  @override
  void initState() {
    super.initState();
    _loadUserAndEvents();
  }

  Future<void> _loadUserAndEvents() async {
    try {
      final fetchedUserId = await AuthService.getCurrentUserId();
      if (fetchedUserId == null) throw Exception('No user ID');

      final fetchedEvents = await EventApi.getEvents();
      final attendance = await AttendanceApi().getAttendanceByUser(fetchedUserId);
      final likes = await LikesApi.getUserLikes(fetchedUserId);

      likedEventIds = likes.map((l) => l.eventId).toSet();

      final attendingEventIds = attendance
          .where((a) => a['status'] == 'going')
          .map((e) => e['event_id'] as int)
          .toSet();

      final filteredEvents = fetchedEvents
          .where((e) => !attendingEventIds.contains(e.id))
          .toList();

      setState(() {
        userId = fetchedUserId;
        events = filteredEvents;
        isLoading = false;
      });
    } catch (e) {
      setState(() => isLoading = false);
      debugPrint('Error loading user/events: $e');
    }
  }

  Future<void> _toggleLike(Event event) async {
    if (userId == null) return;
    final eid = event.id!;
    try {
      if (likedEventIds.contains(eid)) {
        await LikesApi.removeLike(userId!, eid);
        setState(() => likedEventIds.remove(eid));
      } else {
        await LikesApi.addLike(userId!, eid);
        setState(() => likedEventIds.add(eid));
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error toggling like: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    const uniRed = Color.fromARGB(255, 124, 0, 0);

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
        actions: [
          IconButton(
            icon: const Icon(Icons.person, color: Colors.black),
            onPressed: () => Navigator.pushNamed(context, '/profile'),
          ),
        ],
      ),
      body: Column(
        children: [
          const SizedBox(height: 16),
          const Text(
            'Explore 🔍',
            style: TextStyle(
              fontSize: 28,
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: Center(
              child: isLoading
                  ? const CircularProgressIndicator()
                  : (events.isEmpty || currentIndex >= events.length)
                  ? const Padding(
                padding: EdgeInsets.symmetric(horizontal: 20.0),
                child: Text(
                  'No events available - check later!',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.w500,
                  ),
                  textAlign: TextAlign.center,
                ),
              )
                  : _buildEventCard(events[currentIndex]),
            ),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildCircleButton('❌', size: 56, onTap: _rejectEvent),
                _buildCircleButton('✅', size: 56, onTap: _attendEvent),
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 1, // Explore = index 1
        onTap: (index) {
          switch (index) {
            case 0: // Liked
              Navigator.pushNamed(context, '/liked');
              break;
            case 1: // Explore (you are already here)
              Navigator.pushNamed(context, '/explore');
              break;
            case 2: // Nearby
              Navigator.pushNamed(context, '/nearby');
              break;
            case 3: // Create
              Navigator.pushNamed(context, '/create');
              break;
          }
        },
      ),
    );
  }

  Widget _buildEventCard(Event event) {
    final isLiked = likedEventIds.contains(event.id);
    return Stack(
      children: [
        Card(
          elevation: 20,
          margin: const EdgeInsets.symmetric(horizontal: 20),
          shape:
          RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          child: Column(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                ),
                child: Image.asset(
                  'assets/images/header.png',
                  width: double.infinity,
                  height: 295,
                  fit: BoxFit.cover,
                ),
              ),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(16),
                  width: double.infinity,
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.vertical(
                      bottom: Radius.circular(20),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(event.title,
                          style: const TextStyle(
                              fontSize: 20, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Text('📅 ${_formatDate(event.datetime)}',
                          style: const TextStyle(fontSize: 14)),
                      const SizedBox(height: 4),
                      Text('📍 ${event.location}',
                          style: const TextStyle(fontSize: 14)),
                      const SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          ElevatedButton(
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) =>
                                    EventDetailsScreen(event: event),
                              ),
                            ),
                            child: const Text('See details'),
                          ),
                          FutureBuilder<List<Map<String, dynamic>>>(
                            future:
                            AttendanceApi().getAttendanceByEvent(event.id!),
                            builder: (ctx, snap) {
                              if (!snap.hasData) return const SizedBox();
                              final goingCount = snap.data!
                                  .where((a) => a['status'] == 'going')
                                  .length;
                              return Row(
                                children: [
                                  const Icon(Icons.people,
                                      color: Colors.grey),
                                  const SizedBox(width: 4),
                                  Text('$goingCount going'),
                                ],
                              );
                            },
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),

        // Heart toggle
        Positioned(
          top: 12,
          right: 32,
          child: GestureDetector(
            onTap: () => _toggleLike(event),
            child: Icon(
              isLiked ? Icons.favorite : Icons.favorite_border,
              size: 32,
              color: isLiked ? Colors.red : Colors.grey,
            ),
          ),
        ),
      ],
    );
  }

  void _attendEvent() async {
    if (userId == null || currentIndex >= events.length) return;
    final currentEvent = events[currentIndex];
    final success = await AttendanceApi()
        .addAttendance(userId: userId!, eventId: currentEvent.id!, status: "going");
    if (success) {
      setState(() {
        events.removeAt(currentIndex);
        if (currentIndex >= events.length) currentIndex = 0;
      });
    } else {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Failed to add attendance')));
    }
  }

  void _rejectEvent() {
    if (currentIndex < events.length) {
      setState(() {
        events.removeAt(currentIndex);
        if (currentIndex >= events.length) currentIndex = 0;
      });
    }
  }

  String _formatDate(DateTime dt) {
    const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const months = [
      'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'
    ];
    final w = weekdays[(dt.weekday - 1) % 7];
    final m = months[(dt.month - 1) % 12];
    final hh = dt.hour.toString().padLeft(2, '0');
    final mm = dt.minute.toString().padLeft(2, '0');
    return '$w, $m ${dt.day} · $hh:$mm';
  }

  Widget _buildCircleButton(String emoji,
      {double size = 48, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration:
        const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
        alignment: Alignment.center,
        child: Text(emoji, style: const TextStyle(fontSize: 24)),
      ),
    );
  }
}
