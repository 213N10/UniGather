import 'package:flutter/material.dart';

class BottomNavBar extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const BottomNavBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      backgroundColor: Colors.white,
      selectedItemColor: Colors.black,
      unselectedItemColor: Colors.black54,
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.favorite_border),
          activeIcon: Icon(Icons.favorite, color: Colors.red),
          label: 'Liked',
        ),

        BottomNavigationBarItem(
          icon: Text('🔍', style: TextStyle(fontSize: 20)),
          label: 'Explore',
        ),
        BottomNavigationBarItem(
          icon: Text('📍', style: TextStyle(fontSize: 20)),
          label: 'Nearby',
        ),
        BottomNavigationBarItem(
          icon: Text('➕', style: TextStyle(fontSize: 20)),
          label: 'Create',
        ),
      ],
    );
  }


}
