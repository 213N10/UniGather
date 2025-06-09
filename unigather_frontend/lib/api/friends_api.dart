import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../models/friend.dart';

class FriendsApi {
  // Send a friend request
  static Future<bool> addFriend(int userId, int friendId) async {
    final url = Uri.parse('$baseUrl/friends');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'user_id': userId, 'friend_id': friendId}),
    );
    if (response.statusCode == 200) {
      final msg = jsonDecode(response.body)['message'];
      return msg == 'Friend request sent';
    }
    return false;
  }

  // Get all friendships for a user
  static Future<List<Friend>> getFriends(int userId) async {
    final url = Uri.parse('$baseUrl/friends/$userId');
    final response = await http.get(url);
    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(response.body);
      return jsonList
          .map((j) => Friend.fromJson(j as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception('Failed to load friends list');
    }
  }

  // Remove a friendship
  static Future<bool> deleteFriend(int userId, int friendId) async {
    final url = Uri.parse('$baseUrl/friends/$userId/$friendId');
    final response = await http.delete(
      url,
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode == 200) {
      final msg = jsonDecode(response.body)['message'];
      return msg == 'Friend removed';
    }
    return false;
  }
}
