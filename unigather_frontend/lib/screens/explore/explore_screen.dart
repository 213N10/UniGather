import 'package:flutter/material.dart';
import '../../models/event.dart';
import '../../api/event_api.dart';
import '../../api/attendance_api.dart';
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
      final attendance = await AttendanceApi().getAttendanceByUser(
        fetchedUserId,
      );

      final attendingEventIds =
          attendance
              .where((a) => a['status'] == 'going')
              .map((e) => e['event_id'] as int)
              .toSet();

      final filteredEvents =
          fetchedEvents
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

  @override
  Widget build(BuildContext context) {
    final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

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
              child:
                  isLoading
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
        currentIndex: 1,
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

  Widget _buildEventCard(Event event) {
    return Card(
      elevation: 20,
      margin: const EdgeInsets.symmetric(horizontal: 20),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
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
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.max,
                children: [
                  Text(
                    event.title,
                    style: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '📅 ${_formatDate(event.datetime)}',
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '📍 ${event.location}',
                    style: const TextStyle(fontSize: 14),
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      ElevatedButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder:
                                  (context) => EventDetailsScreen(event: event),
                            ),
                          );
                        },
                        child: const Text('See details'),
                      ),
                      FutureBuilder<List<Map<String, dynamic>>>(
                        future: AttendanceApi().getAttendanceByEvent(event.id!),
                        builder: (context, snapshot) {
                          if (!snapshot.hasData) return const SizedBox();
                          final goingCount =
                              snapshot.data!
                                  .where((a) => a['status'] == 'going')
                                  .length;
                          return Row(
                            children: [
                              const Icon(Icons.people, color: Colors.grey),
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
    );
  }

  void _attendEvent() async {
    if (userId == null || currentIndex >= events.length) return;

    final currentEvent = events[currentIndex];
    final success = await AttendanceApi().addAttendance(
      userId: userId!,
      eventId: currentEvent.id!,
      status: "going",
    );

    if (success) {
      setState(() {
        events.removeAt(currentIndex);
        if (currentIndex >= events.length) currentIndex = 0;
      });
    } else {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Failed to add attendance')));
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
    return "${_weekday(dt.weekday)}, ${_month(dt.month)} ${dt.day} · ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}";
  }

  String _weekday(int weekday) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days[(weekday - 1) % 7];
  }

  String _month(int month) {
    const months = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];
    return months[(month - 1) % 12];
  }

  Widget _buildCircleButton(
    String emoji, {
    double size = 48,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: size,
        height: size,
        decoration: const BoxDecoration(
          color: Colors.white,
          shape: BoxShape.circle,
        ),
        alignment: Alignment.center,
        child: Text(emoji, style: const TextStyle(fontSize: 24)),
      ),
    );
  }
}
