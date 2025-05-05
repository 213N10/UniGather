class Event {
  final int id;
  final String title;
  final String description;
  final String location;
  final DateTime datetime;
  final String visibility;
  final int createdBy;
  final DateTime createdAt;

  Event({
    required this.id,
    required this.title,
    required this.description,
    required this.location,
    required this.datetime,
    required this.visibility,
    required this.createdBy,
    required this.createdAt,
  });
}
