import '../models/user.dart';

final User mockUser = User(
  id: 1,
  name: 'John Doe',
  email: 'john@example.com',
  password_hash: 'hashed_password_123', // just a placeholder
  role: 'student',
  createdAt: DateTime.parse('2024-10-01T12:34:56Z'),
);
