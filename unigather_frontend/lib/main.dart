import 'package:flutter/material.dart';
import 'screens/main/main_screen.dart';
import 'screens/login/login_screen.dart';
import 'screens/signup/signup_screen.dart';
import 'screens/explore/explore_screen.dart';
import 'screens/nearby/nearby_screen.dart';
import 'screens/create_event/create_event_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'package:unigather_frontend/mock_data/mock_users.dart'; // contains mockUser

const MaterialColor uniRed = MaterialColor(_uniRedPrimaryValue, <int, Color>{
  50: Color(0xFFF3CCCC),
  100: Color(0xFFE6A8A8),
  200: Color(0xFFD98080),
  300: Color(0xFFCC5959),
  400: Color(0xFFC03939),
  500: Color(_uniRedPrimaryValue),
  600: Color(0xFFA60000),
  700: Color(0xFF8F0000),
  800: Color(0xFF780000),
  900: Color(0xFF5C0000),
});
const int _uniRedPrimaryValue = 0xFFE00000;

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'UniGather',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primarySwatch: uniRed, scaffoldBackgroundColor: uniRed),
      initialRoute: '/main',
      routes: {
        '/main': (context) => const MainPage(),
        '/login': (context) => const LoginScreen(),
        '/signup': (context) => const SignupScreen(),
        '/explore': (context) => const ExploreScreen(),
        '/nearby': (context) => const NearbyScreen(),
        '/create': (context) => const CreateEventScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/profile') {
          return MaterialPageRoute(
            builder: (context) => ProfileScreen(user: mockUser),
          );
        }
        return null; // fallback for undefined routes
      },
    );
  }
}
