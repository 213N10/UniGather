import '../models/event.dart';

List<Event> mockEvents = [
  Event(
    id: 1,
    title: 'AI Study Group',
    description: 'Join us for a fun and productive AI study session!',
    location: 'Building D20, Room 105',
    datetime: DateTime.parse('2025-05-10 18:00:00'),
    visibility: 'public',
    createdBy: 1,
    createdAt: DateTime.now(),
  ),
  Event(
    id: 2,
    title: 'End of Semester Party',
    description: 'Celebrate the end of exams with your classmates!',
    location: 'Wyspa Słodowa',
    datetime: DateTime.parse('2025-05-15 20:00:00'),
    visibility: 'public',
    createdBy: 2,
    createdAt: DateTime.now(),
  ),
];
