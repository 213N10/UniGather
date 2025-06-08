class Like {
  final int userId;
  final int eventId;

  Like({required this.userId, required this.eventId});

  factory Like.fromJson(Map<String, dynamic> json) {
    return Like(userId: json['user_id'], eventId: json['event_id']);
  }

  Map<String, dynamic> toJson() {
    return {'user_id': userId, 'event_id': eventId};
  }
}
