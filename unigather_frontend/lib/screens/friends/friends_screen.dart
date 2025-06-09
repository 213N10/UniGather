import 'package:flutter/material.dart';
import '../../models/friend.dart';
import '../../api/friends_api.dart';
import '../../services/auth_service.dart';

class FriendsScreen extends StatefulWidget {
  const FriendsScreen({Key? key}) : super(key: key);

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen> {
  late final int userId;
  List<Friend> friends = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadFriends();
  }

  Future<void> _loadFriends() async {
    userId = (await AuthService.getCurrentUserId())!;
    final list = await FriendsApi.getFriends(userId);
    setState(() {
      friends = list;
      isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Your Friends'),
        centerTitle: true,
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : friends.isEmpty
          ? const Center(child: Text('No friends yet.'))
          : ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: friends.length,
        itemBuilder: (ctx, i) {
          final f = friends[i];
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              title: Text('User #${f.friendId}'),
              subtitle: Text('Status: ${f.status}'),
              trailing: IconButton(
                icon: const Icon(Icons.person_remove, color: Colors.red),
                onPressed: () async {
                  final ok = await FriendsApi.deleteFriend(userId, f.friendId);
                  if (ok) setState(() => friends.removeAt(i));
                },
              ),
            ),
          );
        },
      ),
    );
  }
}
