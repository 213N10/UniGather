import 'package:flutter/material.dart';
import 'package:unigather_frontend/widgets/bottom_nav_bar.dart';
import '../../api/likes_api.dart';
import '../../main.dart';
import '../../models/user.dart';
import '../../models/event.dart';
import '../../api/user_api.dart';
import '../../api/event_api.dart';
import '../../api/attendance_api.dart';
import '../../services/auth_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> with RouteAware {
  String selectedTab = 'upcoming';
  User? user;
  bool isLoading = true;
  Set<int> likedEventIds = {};

  List<Event> upcomingEvents = [];
  List<Event> finishedEvents = [];
  List<Event> createdEvents = [];

  @override
  void initState() {
    super.initState();
    _loadUserAndEvents();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final modalRoute = ModalRoute.of(context);
    if (modalRoute is PageRoute) {
      routeObserver.subscribe(this, modalRoute);
    }
  }

  @override
  void dispose() {
    routeObserver.unsubscribe(this);
    super.dispose();
  }

  @override
  void didPopNext() {
    // Called when coming back to this screen (from push)
    _loadUserAndEvents();
  }

  @override
  void didPush() {
    // Called when this screen is first pushed
    _loadUserAndEvents();
  }

  Future<void> _loadUserAndEvents() async {
    try {
      final userId = await AuthService.getCurrentUserId();
      if (userId == null) throw Exception("User ID not found.");

      final fetchedUser = await UserApi.getUser(userId);
      final allEvents = await EventApi.getEvents();
      final attendanceList = await AttendanceApi().getAttendanceByUser(userId);
      final likes = await LikesApi.getUserLikes(userId);
      final likedIds = likes.map((like) => like.eventId).toSet();

      final attendedEventIds =
          attendanceList
              .where((att) => att['status'] == 'going')
              .map((att) => att['event_id'] as int)
              .toSet();

      final now = DateTime.now();

      setState(() {
        user = fetchedUser;
        likedEventIds = likedIds;
        upcomingEvents =
            allEvents
                .where(
                  (e) =>
                      attendedEventIds.contains(e.id) &&
                      e.datetime.isAfter(now),
                )
                .toList();
        finishedEvents =
            allEvents
                .where(
                  (e) =>
                      attendedEventIds.contains(e.id) &&
                      e.datetime.isBefore(now),
                )
                .toList();
        createdEvents = allEvents.where((e) => e.createdBy == userId).toList();
        isLoading = false;
      });
    } catch (e) {
      print("Error loading user or events: $e");
      setState(() => isLoading = false);
    }
  }

  List<Event> getCurrentEvents() {
    switch (selectedTab) {
      case 'finished':
        return finishedEvents;
      case 'created':
        return createdEvents;
      default:
        return upcomingEvents;
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

    return Scaffold(
      backgroundColor: uniRed,
      appBar: AppBar(
        backgroundColor: Colors.white,
        iconTheme: IconThemeData(color: uniRed),
        title: const Text(
          'UniGather',
          style: TextStyle(
            color: Colors.black,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.group),
            onPressed: () => Navigator.pushNamed(context, '/friends'),
          ),
        ],
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : user == null
              ? const Center(child: Text('Failed to load user'))
              : Column(
                children: [
                  const SizedBox(height: 16),
                  CircleAvatar(
                    radius: 48,
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, size: 48, color: uniRed),
                  ),
                  const SizedBox(height: 12),
                  Text(
                    user!.name,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    user!.email,
                    style: const TextStyle(color: Colors.white70, fontSize: 14),
                  ),
                  const SizedBox(height: 24),
                  const Text(
                    'My Events',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 16.0),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildTabButton('upcoming', 'Upcoming'),
                        _buildTabButton('finished', 'Finished'),
                        _buildTabButton('created', 'Created by Me'),
                      ],
                    ),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: Container(
                      width: double.infinity,
                      decoration: const BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.vertical(
                          top: Radius.circular(24),
                        ),
                      ),
                      padding: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                      child: Padding(
                        padding: const EdgeInsets.only(bottom: 3),
                        child:
                            getCurrentEvents().isEmpty
                                ? const Center(
                                  child: Text(
                                    'No events in this section yet.',
                                    style: TextStyle(
                                      fontSize: 16,
                                      color: Colors.black54,
                                    ),
                                  ),
                                )
                                : ListView.builder(
                                  itemCount: getCurrentEvents().length,
                                  itemBuilder: (context, index) {
                                    final event = getCurrentEvents()[index];
                                    return _buildEventCard(event);
                                  },
                                ),
                      ),
                    ),
                  ),
                ],
              ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 0,
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

  Widget _buildTabButton(String key, String label) {
    final bool isSelected = selectedTab == key;
    return Expanded(
      child: GestureDetector(
        onTap: () {
          setState(() {
            selectedTab = key;
          });
        },
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 12),
          decoration: BoxDecoration(
            color: isSelected ? Colors.white : Colors.white24,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Center(
            child: Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.black : Colors.white,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEventCard(Event event) {
    final bool isAttending =
        event.id != null &&
        (upcomingEvents + finishedEvents).any((e) => e.id == event.id);

    final bool isLiked = event.id != null && likedEventIds.contains(event.id);

    return Card(
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        title: Text(
          event.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('📅 ${_formatDate(event.datetime)}'),
            Text('📍 ${event.location}'),
          ],
        ),
        trailing: FutureBuilder<List<Map<String, dynamic>>>(
          future: AttendanceApi().getAttendanceByEvent(event.id!),
          builder: (context, snapshot) {
            if (!snapshot.hasData) {
              return const SizedBox(
                width: 60,
                height: 24,
                child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
              );
            }

            final goingCount =
                snapshot.data!.where((a) => a['status'] == 'going').length;

            return Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.how_to_reg,
                  color: isAttending ? Colors.green : Colors.grey,
                  size: 20,
                ),
                const SizedBox(width: 4),
                Text('$goingCount'),
                const SizedBox(width: 12),
                Icon(
                  isLiked ? Icons.favorite : Icons.favorite_border,
                  color: isLiked ? Colors.red : Colors.grey,
                  size: 20,
                ),
              ],
            );
          },
        ),
        onTap: () {
          Navigator.pushNamed(context, '/event_details', arguments: event);
        },
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${dt.day}/${dt.month}/${dt.year} '
        '${dt.hour.toString().padLeft(2, '0')}:'
        '${dt.minute.toString().padLeft(2, '0')}';
  }
}
