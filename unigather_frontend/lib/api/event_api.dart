import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/event.dart';
import '../config.dart';
import '../services/auth_service.dart';

class EventApi {
  static Future<List<Event>> getEvents({
    int? createdBy,
    String? visibility,
  }) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/events').replace(
      queryParameters: {
        if (createdBy != null) 'created_by': createdBy.toString(),
        if (visibility != null) 'visibility': visibility,
      },
    );

    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((json) => Event.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load events');
    }
  }

  static Future<Event> getEvent(int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/events/$eventId');
    final response = await http.get(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return Event.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Event not found');
    }
  }

  static Future<void> createEvent(Event event) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/events');
    final response = await http.post(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(event.toJson()),
    );

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw Exception(
        'Failed to create event (status ${response.statusCode}): ${response.body}',
      );
    }
  }

  static Future<void> updateEvent(int eventId, Event event) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/events/$eventId');
    final response = await http.put(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode(event.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update event');
    }
  }

  static Future<void> deleteEvent(int eventId) async {
    final token = await AuthService.getToken();
    final uri = Uri.parse('$baseUrl/events/$eventId');
    final response = await http.delete(
      uri,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete event');
    }
  }
}
