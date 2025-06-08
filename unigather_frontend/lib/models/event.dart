class Event {
  final int? id;
  final String title;
  final String description;
  final String visibility;
  final int? createdBy;
  final DateTime datetime;
  final String location;
  final DateTime? createdAt;

  Event({
    this.id,
    required this.title,
    required this.description,
    required this.visibility,
    this.createdBy,
    required this.datetime,
    required this.location,
    this.createdAt,
  });

  factory Event.fromJson(Map<String, dynamic> json) => Event(
    id: json['id'],
    title: json['title'],
    description: json['description'],
    visibility: json['visibility'],
    createdBy: json['created_by'],
    datetime: DateTime.parse(json['datetime']),
    location: json['location'],
    createdAt:
        json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
  );

  Map<String, dynamic> toJson() => {
    if (id != null) 'id': id,
    'title': title,
    'description': description,
    'visibility': visibility,
    if (createdBy != null) 'created_by': createdBy,
    'event_datetime': datetime.toIso8601String(),
    'location': location,
    if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
  };
}
