import 'package:flutter/material.dart';
import 'package:unigather_frontend/widgets/bottom_nav_bar.dart';
import '../../models/event.dart';
import '../../mock_data/mock_events.dart';
import '../event_details/event_details_screen.dart';

class ExploreScreen extends StatefulWidget {
  const ExploreScreen({super.key});

  @override
  State<ExploreScreen> createState() => _ExploreScreenState();
}

class _ExploreScreenState extends State<ExploreScreen> {
  int currentIndex = 0;
  bool liked = false;

  @override
  Widget build(BuildContext context) {
    final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

    if (mockEvents.isEmpty) {
      return const Center(child: Text("No events available."));
    }

    final Event currentEvent = mockEvents[currentIndex];

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
              child: Card(
                elevation: 20,
                margin: const EdgeInsets.symmetric(horizontal: 20),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Column(
                  children: [
                    // Top image half (hardcoded for now)
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
                    // Bottom white content half
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
                          mainAxisAlignment:
                              MainAxisAlignment.center, // Vertically center
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.max,
                          children: [
                            Text(
                              currentEvent.title,
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              '📅 ${_formatDate(currentEvent.datetime)}',
                              style: const TextStyle(fontSize: 14),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              '📍 ${currentEvent.location}',
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
                                            (context) => EventDetailsScreen(
                                              event: currentEvent,
                                            ),
                                      ),
                                    );
                                  },
                                  child: const Text('See details'),
                                ),
                                TextButton.icon(
                                  onPressed: () {
                                    setState(() {
                                      liked = !liked;
                                    });
                                  },
                                  icon: Icon(
                                    liked
                                        ? Icons.favorite
                                        : Icons.favorite_border,
                                    color: liked ? Colors.red : Colors.grey,
                                  ),
                                  label: Text(
                                    liked ? 'Liked (21)' : 'Liked (20)',
                                    style: TextStyle(
                                      color: liked ? Colors.red : Colors.grey,
                                    ),
                                  ),
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
            ),
          ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildCircleButton('⏭️', size: 42, onTap: _skipEvent),
                _buildCircleButton('❌', size: 56, onTap: _skipEvent),
                _buildCircleButton(
                  '✅',
                  size: 56,
                  onTap: () {
                    // Optionally do something on "yes"
                    _skipEvent();
                  },
                ),
                _buildCircleButton(
                  '🌐',
                  size: 42,
                  onTap: () {
                    // TODO: Implement sharing
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 32),
        ],
      ),
      bottomNavigationBar: BottomNavBar(
        currentIndex: 1, // set this per screen (0=profile, 1=explore, etc.)
        onTap: (index) {
          // Replace this with proper navigation
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

  void _skipEvent() {
    setState(() {
      liked = false;
      num number = (currentIndex + 1) % mockEvents.length;
      currentIndex = number.toInt();
    });
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
