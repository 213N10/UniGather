class User {
  final int id;
  final String name;
  final String email;
  final String password_hash;
  final String role;
  final DateTime createdAt;

  User({
    required this.id,
    required this.name,
    required this.email,
    required this.password_hash,
    required this.role,
    required this.createdAt,
  });
}
