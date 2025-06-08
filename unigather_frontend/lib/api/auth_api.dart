import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../models/user.dart';

class AuthApi {
  // LOGIN
  static Future<Map<String, dynamic>?> login(
    String email,
    String password,
  ) async {
    final url = Uri.parse('$baseUrl/login');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['access_token'] != null && data['user'] != null) {
        return {
          'token': data['access_token'],
          'user': User.fromJson(data['user']),
        };
      }
    }
    return null;
  }

  // REGISTER
  static Future<User?> register({
    required String name,
    required String email,
    required String password,
    String? role, // optional, in case you want to set a role
  }) async {
    final url = Uri.parse('$baseUrl/register');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'email': email,
        'password': password,
        if (role != null) 'role': role,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      if (data['user'] != null) {
        return User.fromJson(data['user']);
      }
    }
    return null;
  }
}
