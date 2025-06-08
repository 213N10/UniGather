import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config.dart';
import '../services/auth_service.dart';

class AttendanceApi {
  Future<Map<String, String>> _authHeaders() async {
    final token = await AuthService.getToken();
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  Future<bool> addAttendance({
    required int userId,
    required int eventId,
    required String status,
  }) async {
    final url = Uri.parse('$baseUrl/attendance');
    final headers = await _authHeaders();
    final response = await http.post(
      url,
      headers: headers,
      body: jsonEncode({
        'user_id': userId,
        'event_id': eventId,
        'status': status,
      }),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['message'] == 'Attendance added';
    }
    return false;
  }

  Future<List<Map<String, dynamic>>> getAttendanceByEvent(int eventId) async {
    final url = Uri.parse('$baseUrl/attendance/event/$eventId');
    final headers = await _authHeaders();
    final response = await http.get(url, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(response.body);
      return jsonList.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load event attendance');
    }
  }

  Future<List<Map<String, dynamic>>> getAttendanceByUser(int userId) async {
    final url = Uri.parse('$baseUrl/attendance/user/$userId');
    final headers = await _authHeaders();
    final response = await http.get(url, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(response.body);
      return jsonList.cast<Map<String, dynamic>>();
    } else {
      throw Exception('Failed to load user attendance');
    }
  }

  Future<bool> deleteAttendance({
    required int userId,
    required int eventId,
  }) async {
    final url = Uri.parse(
      '$baseUrl/attendance?user_id=$userId&event_id=$eventId',
    );
    final headers = await _authHeaders();
    final response = await http.delete(url, headers: headers);

    if (response.statusCode == 200) {
      return jsonDecode(response.body)['message'] == 'Attendance removed';
    }
    return false;
  }
}
