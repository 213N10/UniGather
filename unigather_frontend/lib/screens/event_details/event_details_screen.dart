import 'package:flutter/material.dart';
import '../../models/event.dart';
import '../../models/media.dart';
import '../../api/media_api.dart';
import 'package:share_plus/share_plus.dart';
import '../../api/event_api.dart';

class EventDetailsScreen extends StatefulWidget {
  final Event event;

  const EventDetailsScreen({super.key, required this.event});

  @override
  State<EventDetailsScreen> createState() => _EventDetailsScreenState();
}

class _EventDetailsScreenState extends State<EventDetailsScreen> {
  List<Media> _mediaList = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchMedia();
    _fetchSimilarEvents(); // call it here
  }

  Future<void> _fetchMedia() async {
    try {
      final media = await MediaApi.getMediaForEvent(widget.event.id!);
      setState(() {
        _mediaList = media;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  List<Event> _similarEvents = [];
  bool _loadingSimilar = true;

  void _fetchSimilarEvents() async {
    try {
      final events = await EventApi.getEvents();
      setState(() {
        _similarEvents = events;
        _loadingSimilar = false;
      });
    } catch (e) {
      print('Error loading events: $e');
      setState(() => _loadingSimilar = false);
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
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
        centerTitle: true,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 12),
        child: Card(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          elevation: 8,
          clipBehavior: Clip.antiAlias,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Image.asset(
                'assets/images/header.png',
                width: double.infinity,
                height: 200,
                fit: BoxFit.cover,
              ),
              Container(
                color: Colors.white,
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.event.title,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      widget.event.description,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 20),
                    Row(
                      children: [
                        const Icon(Icons.calendar_today, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          _formatDate(widget.event.datetime),
                          style: const TextStyle(fontSize: 16),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.location_on, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          widget.event.location,
                          style: const TextStyle(fontSize: 16),
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Gallery section
                    const Text(
                      'Gallery',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 100,
                      child:
                          _isLoading
                              ? const Center(child: CircularProgressIndicator())
                              : _mediaList.isEmpty
                              ? const Center(child: Text('No media available.'))
                              : ListView.separated(
                                scrollDirection: Axis.horizontal,
                                itemCount: _mediaList.length,
                                separatorBuilder:
                                    (_, __) => const SizedBox(width: 8),
                                itemBuilder: (context, index) {
                                  final media = _mediaList[index];
                                  return ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child:
                                        media.type == 'image'
                                            ? Image.network(
                                              media.url,
                                              width: 100,
                                              height: 100,
                                              fit: BoxFit.cover,
                                            )
                                            : Stack(
                                              children: [
                                                Container(
                                                  width: 100,
                                                  height: 100,
                                                  color: Colors.black12,
                                                  child: const Icon(
                                                    Icons.videocam,
                                                    color: Colors.black45,
                                                    size: 40,
                                                  ),
                                                ),
                                                Positioned.fill(
                                                  child: Material(
                                                    color: Colors.transparent,
                                                    child: InkWell(
                                                      onTap: () {
                                                        // TODO: Open video URL in player/screen
                                                        print(
                                                          'Open video: ${media.url}',
                                                        );
                                                      },
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                  );
                                },
                              ),
                    ),

                    const SizedBox(height: 24),

                    // Similar events placeholder
                    const Text(
                      'Similar Events',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    SizedBox(
                      height: 120,
                      child:
                          _loadingSimilar
                              ? const Center(child: CircularProgressIndicator())
                              : ListView.builder(
                                scrollDirection: Axis.horizontal,
                                itemCount: _similarEvents.length,
                                itemBuilder: (context, index) {
                                  final e = _similarEvents[index];
                                  return GestureDetector(
                                    onTap: () {
                                      Navigator.push(
                                        context,
                                        MaterialPageRoute(
                                          builder:
                                              (_) =>
                                                  EventDetailsScreen(event: e),
                                        ),
                                      );
                                    },
                                    child: Container(
                                      width: 200,
                                      margin: const EdgeInsets.only(right: 12),
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.grey[200],
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            e.title,
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                            ),
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          const SizedBox(height: 4),
                                          Text(
                                            e.description,
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                          ),
                                          const Spacer(),
                                          Text(
                                            _formatDate(e.datetime),
                                            style: const TextStyle(
                                              fontSize: 12,
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  );
                                },
                              ),
                    ),

                    const SizedBox(height: 24),

                    Center(
                      child: ElevatedButton.icon(
                        onPressed: () {
                          final url =
                              'https://your-app-url.com/event/${widget.event.id}'; // TODO: Adjust link

                          SharePlus.instance.share(
                            ShareParams(
                              text:
                                  "Check out this event on UniGather!\n\n${widget.event.title}\n$url",
                            ),
                          );
                        },
                        icon: const Icon(Icons.share),
                        label: const Text(
                          "Let your friends know you're going!",
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: uniRed,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 14,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    return '${_weekday(dt.weekday)}, ${_month(dt.month)} ${dt.day}, ${dt.year} · ${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }

  String _weekday(int w) {
    const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return weekdays[(w - 1) % 7];
  }

  String _month(int m) {
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
    return months[(m - 1) % 12];
  }
}
