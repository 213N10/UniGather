import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import '../config.dart';
import '../services/auth_service.dart';

class UserApi {
  // GET multiple users
  static Future<List<User>> getUsers({
    String? name,
    String? email,
    String? role,
  }) async {
    final token = await AuthService.getToken();

    final queryParams = {
      if (name != null) 'name': name,
      if (email != null) 'email': email,
      if (role != null) 'role': role,
    };

    final uri = Uri.parse(
      '$baseUrl/users',
    ).replace(queryParameters: queryParams);

    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> jsonUsers = jsonDecode(response.body)['users'];
      return jsonUsers.map((e) => User.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load users');
    }
  }

  // GET single user
  static Future<User?> getUser(int id) async {
    final token = await AuthService.getToken();
    final response = await http.get(
      Uri.parse('$baseUrl/users/$id'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final userJson = json['user'];
      return User.fromJson(userJson);
    } else {
      throw Exception('Failed to fetch user');
    }
  }

  // PUT update user
  static Future<bool> updateUser(int id, User user) async {
    final token = await AuthService.getToken();
    final response = await http.put(
      Uri.parse('$baseUrl/users/$id'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(user.toJson()),
    );

    return response.statusCode == 200;
  }

  // DELETE user
  static Future<bool> deleteUser(int id) async {
    final token = await AuthService.getToken();
    final response = await http.delete(
      Uri.parse('$baseUrl/users/$id'),
      headers: {'Authorization': 'Bearer $token'},
    );

    return response.statusCode == 200;
  }
}
