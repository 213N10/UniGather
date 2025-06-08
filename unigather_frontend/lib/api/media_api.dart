import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/media.dart';
import '../config.dart';
import '../services/auth_service.dart';

class MediaApi {
  static Future<List<Media>> getMediaForEvent(int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/media/event/$eventId');
    final response = await http.get(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Media.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load media for event');
    }
  }

  static Future<void> addMedia(Media media) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/media');
    final response = await http.post(
      uri,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode(media.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to add media');
    }
  }

  static Future<void> deleteMedia(int mediaId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/media/$mediaId');
    final response = await http.delete(
      uri,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete media');
    }
  }
}
