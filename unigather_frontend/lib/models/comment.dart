class Comment {
  final int id;
  final String content;
  final int eventId;
  final int userId;
  final DateTime timestamp;

  Comment({
    required this.id,
    required this.content,
    required this.eventId,
    required this.userId,
    required this.timestamp,
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'],
      content: json['content'],
      eventId: json['event_id'],
      userId: json['user_id'],
      timestamp: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'event_id': eventId,
      'user_id': userId,
      'created_at': timestamp.toIso8601String(),
    };
  }
}

class CommentWithUser {
  final Comment comment;
  final String userName;

  CommentWithUser({required this.comment, required this.userName});
}
