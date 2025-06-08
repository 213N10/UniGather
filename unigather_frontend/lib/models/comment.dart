class Comment {
  final int id;
  final int userId;
  final int eventId;
  final String content;
  final String timestamp;

  Comment({
    required this.id,
    required this.userId,
    required this.eventId,
    required this.content,
    required this.timestamp,
  });

  factory Comment.fromJson(Map<String, dynamic> json) {
    return Comment(
      id: json['id'],
      userId: json['user_id'],
      eventId: json['event_id'],
      content: json['content'],
      timestamp: json['timestamp'],
    );
  }

  Map<String, dynamic> toJson() {
    return {'user_id': userId, 'event_id': eventId, 'content': content};
  }
}
