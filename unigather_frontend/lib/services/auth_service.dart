import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';

class AuthService {
  static const _tokenKey = 'access_token';
  static const _userKey = 'user_data';

  static Future<void> saveAuthData(String token, User user) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_userKey, jsonEncode(user.toJson()));
  }

  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey) != null;
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<User?> getUser() async {
    final prefs = await SharedPreferences.getInstance();
    final userData = prefs.getString(_userKey);
    if (userData != null) {
      return User.fromJson(jsonDecode(userData));
    }
    return null;
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userKey);
  }

  static Future<int?> getCurrentUserId() async {
    final token = await getToken();
    if (token == null) return null;

    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;

      final payload = utf8.decode(
        base64Url.decode(base64Url.normalize(parts[1])),
      );
      final Map<String, dynamic> data = jsonDecode(payload);

      final sub = data['sub'];
      if (sub is int) return sub;
      if (sub is String) return int.tryParse(sub);

      return null;
    } catch (e) {
      print('Failed to decode token: $e');
      return null;
    }
  }
}
