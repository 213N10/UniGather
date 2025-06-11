import 'package:flutter/material.dart';
import 'package:unigather_frontend/config.dart';
import '../../api/attendance_api.dart';
import '../../api/comments_api.dart';
import '../../api/likes_api.dart';
import '../../api/user_api.dart';
import '../../models/event.dart';
import '../../models/media.dart';
import '../../api/media_api.dart';
import 'package:share_plus/share_plus.dart';
import '../../api/event_api.dart';
import '../../services/auth_service.dart';
import '../../models/comment.dart';
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
  bool _isAttending = false;
  bool _isLiked = false;
  int _goingCount = 0;
  int? _userId; // Get current user ID
  List<Comment> _comments = [];
  List<CommentWithUser> commentsWithUsers = [];
  bool get _isCreator => widget.event.createdBy == _userId;

  bool _loadingComments = true;
  final TextEditingController _commentController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadUserData();
    _fetchMedia();
    _fetchSimilarEvents();
    loadCommentsWithUserNames();
  }

  Future<void> _loadUserData() async {
    _userId =
        await AuthService.getCurrentUserId(); // Assumes AuthService has this
    final attendanceList = await AttendanceApi().getAttendanceByEvent(
      widget.event.id!,
    );
    final userIsGoing = attendanceList.any(
      (a) => a['user_id'] == _userId && a['status'] == 'going',
    );
    final likeList = await LikesApi.getUserLikes(_userId!);
    final liked = likeList.any((like) => like.eventId == widget.event.id);

    setState(() {
      _isAttending = userIsGoing;
      _goingCount = attendanceList.where((a) => a['status'] == 'going').length;
      _isLiked = liked;
    });
  }

  Future<void> _toggleAttendance() async {
    if (_userId == null) return;
    if (_isAttending) {
      await AttendanceApi().deleteAttendance(
        userId: _userId!,
        eventId: widget.event.id!,
      );
      setState(() {
        _isAttending = false;
        _goingCount -= 1;
      });
    } else {
      await AttendanceApi().addAttendance(
        userId: _userId!,
        eventId: widget.event.id!,
        status: 'going',
      );
      setState(() {
        _isAttending = true;
        _goingCount += 1;
      });
    }
  }

  Future<void> _toggleLike() async {
    if (_userId == null) return;
    if (_isLiked) {
      await LikesApi.removeLike(_userId!, widget.event.id!);
      setState(() => _isLiked = false);
    } else {
      await LikesApi.addLike(_userId!, widget.event.id!);
      setState(() => _isLiked = true);
    }
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

  Future<void> loadCommentsWithUserNames() async {
    setState(() {
      _loadingComments = true;
    });

    try {
      final comments = await CommentsApi.getCommentsForEvent(widget.event.id!);

      final List<CommentWithUser> combined = [];

      for (final comment in comments) {
        try {
          final user = await UserApi.getUser(comment.userId);
          final userName = user?.name ?? 'Unknown User';
          combined.add(CommentWithUser(comment: comment, userName: userName));
        } catch (e) {
          combined.add(CommentWithUser(comment: comment, userName: 'Unknown'));
        }
      }

      setState(() {
        _comments = comments;
        commentsWithUsers = combined;
        _loadingComments = false;
      });
    } catch (e) {
      setState(() {
        _loadingComments = false;
      });
      debugPrint('Error loading comments with usernames: $e');
    }
  }

  Future<void> _submitComment() async {
    if (_commentController.text.trim().isEmpty || _userId == null) return;

    final newComment = Comment(
      id: 0,
      userId: _userId!,
      eventId: widget.event.id!,
      content: _commentController.text.trim(),
      timestamp: DateTime.now(),
    );

    try {
      await CommentsApi.addComment(newComment);
      _commentController.clear();
      await loadCommentsWithUserNames(); // Refresh
    } catch (e) {
      print('Failed to post comment: $e');
    }
  }

  Future<void> _confirmDeleteEvent() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Delete Event'),
            content: const Text('Are you sure you want to delete this event?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => Navigator.pop(context, true),
                child: const Text(
                  'Delete',
                  style: TextStyle(color: Colors.red),
                ),
              ),
            ],
          ),
    );

    if (confirmed == true) {
      try {
        await EventApi.deleteEvent(widget.event.id!);
        if (mounted) {
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Event deleted successfully')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Failed to delete event: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final Color uniRed = const Color.fromARGB(255, 124, 0, 0);

    return Scaffold(
      backgroundColor: uniRed,
      appBar: AppBar(
        actions: [
          if (_isCreator)
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.red),
              onPressed: _confirmDeleteEvent,
            ),
        ],
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
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      widget.event.title,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      widget.event.description,
                      textAlign: TextAlign.center,
                      style: const TextStyle(fontSize: 16),
                    ),
                    const SizedBox(height: 16),

                    // Attendance and Like icons row
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        IconButton(
                          icon: Icon(
                            Icons.how_to_reg,
                            color: _isAttending ? Colors.green : Colors.grey,
                          ),
                          onPressed: _toggleAttendance,
                          tooltip: 'Mark as attending',
                        ),
                        Text('$_goingCount'),
                        const SizedBox(width: 16),
                        IconButton(
                          icon: Icon(
                            _isLiked ? Icons.favorite : Icons.favorite_border,
                            color: _isLiked ? Colors.red : Colors.grey,
                          ),
                          onPressed: _toggleLike,
                          tooltip: 'Like event',
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Location
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.location_on, size: 20),
                        const SizedBox(width: 8),
                        Flexible(
                          child: Text(
                            widget.event.location,
                            style: const TextStyle(fontSize: 16),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),

                    // Date
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.calendar_today, size: 20),
                        const SizedBox(width: 8),
                        Text(
                          _formatDate(widget.event.datetime),
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
                              '$baseUrl/event/${widget.event.id}'; // TODO: Adjust link

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

                    const SizedBox(height: 24),
                    const Text(
                      'Comments',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),

                    _loadingComments
                        ? const Center(child: CircularProgressIndicator())
                        : Column(
                          children: [
                            if (commentsWithUsers.isNotEmpty)
                              SizedBox(
                                height:
                                    240, // Adjust based on your comment tile height
                                child: ListView.builder(
                                  itemCount: commentsWithUsers.length,
                                  itemBuilder: (context, index) {
                                    final item = commentsWithUsers[index];
                                    final comment = item.comment;
                                    return Container(
                                      margin: const EdgeInsets.symmetric(
                                        vertical: 4,
                                      ),
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.grey[100],
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            item.userName,
                                            style: const TextStyle(
                                              fontWeight: FontWeight.bold,
                                            ),
                                          ),
                                          const SizedBox(height: 4),
                                          Text(comment.content),
                                          const SizedBox(height: 4),
                                          Text(
                                            comment.timestamp
                                                .toLocal()
                                                .toString()
                                                .split('.')
                                                .first,
                                            style: const TextStyle(
                                              fontSize: 12,
                                              color: Colors.grey,
                                            ),
                                          ),
                                        ],
                                      ),
                                    );
                                  },
                                ),
                              )
                            else
                              const SizedBox(), // no comments yet – show nothing
                          ],
                        ),

                    const SizedBox(height: 12),
                    TextField(
                      controller: _commentController,
                      decoration: InputDecoration(
                        hintText: 'Write a comment...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        suffixIcon: IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: _submitComment,
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
