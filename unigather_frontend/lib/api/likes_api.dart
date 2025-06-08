import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/like.dart';
import '../config.dart';
import '../services/auth_service.dart';

class LikesApi {
  static Future<void> addLike(int userId, int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/likes');
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'user_id': userId, 'event_id': eventId}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to add like');
    }
  }

  static Future<void> removeLike(int userId, int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/likes');
    final response = await http.delete(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'user_id': userId, 'event_id': eventId}),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to remove like');
    }
  }

  static Future<List<Like>> getUserLikes(int userId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/likes/$userId');
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> body = jsonDecode(response.body);
      final List<dynamic> likesJson = body['likes'];
      return likesJson.map((json) => Like.fromJson(json)).toList();
    } else {
      throw Exception('Failed to fetch user likes');
    }
  }
}
