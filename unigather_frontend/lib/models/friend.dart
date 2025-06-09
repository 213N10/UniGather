class Friend {
  final int userId;
  final int friendId;
  final String status;
  final DateTime createdAt;

  Friend({
    required this.userId,
    required this.friendId,
    required this.status,
    required this.createdAt,
  });

  factory Friend.fromJson(Map<String, dynamic> json) => Friend(
    userId: json['user_id'] as int,
    friendId: json['friend_id'] as int,
    status: json['status'] as String,
    createdAt: DateTime.parse(json['created_at'] as String),
  );

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'friend_id': friendId,
    'status': status,
    'created_at': createdAt.toIso8601String(),
  };
}
