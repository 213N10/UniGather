import 'package:flutter/material.dart';

import '../../main.dart';
import '../../models/event.dart';
import '../../api/event_api.dart';
import '../../api/likes_api.dart';
import '../../services/auth_service.dart';
import '../../widgets/bottom_nav_bar.dart';
import '../event_details/event_details_screen.dart';

class LikedEventsScreen extends StatefulWidget {
  const LikedEventsScreen({Key? key}) : super(key: key);

  @override
  _LikedEventsScreenState createState() => _LikedEventsScreenState();
}

class _LikedEventsScreenState extends State<LikedEventsScreen> with RouteAware {
  late final int userId;
  List<Event> likedEvents = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadLikedEvents();
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
    _loadLikedEvents();
  }

  @override
  void didPush() {
    // Called when this screen is first pushed
    _loadLikedEvents();
  }

  Future<void> _loadLikedEvents() async {
    userId = (await AuthService.getCurrentUserId())!;
    final likes = await LikesApi.getUserLikes(userId);
    final allEvents = await EventApi.getEvents();
    final likedIds = likes.map((l) => l.eventId).toSet();

    setState(() {
      likedEvents = allEvents.where((e) => likedIds.contains(e.id)).toList();
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    const uniRed = Color.fromARGB(255, 124, 0, 0);
    return Scaffold(
      backgroundColor: uniRed, // white background
      appBar: AppBar(
        backgroundColor: Colors.white,
        title: const Text(
          'Liked Events',
          style: TextStyle(color: Colors.black),
        ),
        elevation: 1,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : likedEvents.isEmpty
              ? const Center(
                child: Text(
                  'No liked events yet.',
                  style: TextStyle(fontSize: 18, color: Colors.grey),
                ),
              )
              : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: likedEvents.length,
                itemBuilder: (ctx, i) {
                  final e = likedEvents[i];
                  return Card(
                    margin: const EdgeInsets.only(bottom: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 4,
                    child: InkWell(
                      onTap:
                          () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => EventDetailsScreen(event: e),
                            ),
                          ),
                      borderRadius: BorderRadius.circular(12),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Row(
                          children: [
                            // optional thumbnail placeholder
                            Container(
                              width: 60,
                              height: 60,
                              decoration: BoxDecoration(
                                color: Colors.grey.shade200,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Icon(
                                Icons.event,
                                size: 32,
                                color: Colors.grey,
                              ),
                            ),
                            const SizedBox(width: 16),
                            // event info
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    e.title,
                                    style: const TextStyle(
                                      fontSize: 16,
                                      fontWeight: FontWeight.bold,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    '📅 ${_formatDate(e.datetime)}',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    '📍 ${e.location}',
                                    style: const TextStyle(
                                      fontSize: 14,
                                      color: Colors.grey,
                                    ),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                              ),
                            ),
                            // remove like button
                            IconButton(
                              icon: const Icon(
                                Icons.favorite,
                                color: Colors.red,
                              ),
                              onPressed: () async {
                                await LikesApi.removeLike(userId, e.id!);
                                setState(() => likedEvents.removeAt(i));
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 0, // Liked tab
        onTap: (index) {
          switch (index) {
            case 0:
              // already here
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

  String _formatDate(DateTime dt) {
    const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
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
    final w = weekdays[(dt.weekday - 1) % 7];
    final m = months[(dt.month - 1) % 12];
    final hh = dt.hour.toString().padLeft(2, '0');
    final mm = dt.minute.toString().padLeft(2, '0');
    return '$w, $m ${dt.day} · $hh:$mm';
  }
}
