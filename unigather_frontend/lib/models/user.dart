class User {
  final int id;
  final String name;
  final String passwordHash;
  final DateTime createdAt;
  final String email;
  final String role;

  User({
    required this.id,
    required this.name,
    required this.passwordHash,
    required this.createdAt,
    required this.email,
    required this.role,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
    id: json['id'],
    name: json['name'],
    passwordHash: json['password_hash'],
    createdAt: DateTime.parse(json['created_at']),
    email: json['email'],
    role: json['role'],
  );

  Map<String, dynamic> toJson() => {
    'id': id,
    'name': name,
    'password_hash': passwordHash,
    'created_at': createdAt.toIso8601String(),
    'email': email,
    'role': role,
  };
}
