import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/comment.dart';
import '../config.dart';
import '../services/auth_service.dart';

class CommentsApi {
  static Future<List<Comment>> getCommentsForEvent(int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/comments/event/$eventId');
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Comment.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load comments for event');
    }
  }

  static Future<void> addComment(Comment comment) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/comments');
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(comment.toJson()),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception('Failed to add comment');
    }
  }

  static Future<void> deleteComment(int commentId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/comments/$commentId');
    final response = await http.delete(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete comment');
    }
  }
}
