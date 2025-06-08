import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';

class FriendsApi {
  // Add friend
  static Future<bool> addFriend(int userId, int friendId) async {
    final url = Uri.parse('$baseUrl/friends');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'friend_id': friendId}),
    );

    if (response.statusCode == 200) {
      final message = jsonDecode(response.body)['message'];
      return message == 'Friend added';
    }
    return false;
  }

  // Get friends of a user
  static Future<List<Map<String, dynamic>>> getFriends(int userId) async {
    final url = Uri.parse('$baseUrl/friends/$userId');
    final response = await http.get(url);

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(response.body);
      return jsonList.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load friends list');
    }
  }

  // Remove friend
  static Future<bool> deleteFriend(int userId, int friendId) async {
    final url = Uri.parse(
      '$baseUrl/friends?user_id=$userId&friend_id=$friendId',
    );
    final response = await http.delete(url);

    if (response.statusCode == 200) {
      final message = jsonDecode(response.body)['message'];
      return message == 'Friend removed';
    }
    return false;
  }
}
