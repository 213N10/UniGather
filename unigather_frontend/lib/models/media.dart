class Media {
  final int id;
  final int eventId;
  final String url;
  final String type; // e.g., "image", "video"

  Media({
    required this.id,
    required this.eventId,
    required this.url,
    required this.type,
  });

  factory Media.fromJson(Map<String, dynamic> json) {
    return Media(
      id: json['id'],
      eventId: json['event_id'],
      url: json['url'],
      type: json['type'],
    );
  }

  Map<String, dynamic> toJson() {
    return {'event_id': eventId, 'url': url, 'type': type};
  }
}
