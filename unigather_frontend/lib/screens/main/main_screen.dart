import 'package:flutter/material.dart';
import 'package:unigather_frontend/screens/login/login_screen.dart';
import 'package:unigather_frontend/screens/signup/signup_screen.dart';

void main() {
  runApp(const MainPage());
}

class MainPage extends StatelessWidget {
  const MainPage({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: const Color.fromARGB(255, 124, 0, 0),
        body: SingleChildScrollView(
          child: Column(
            children: [
              // Hero image section with overlay
              Stack(
                children: [
                  // Background image
                  SizedBox(
                    height: 400,
                    width: double.infinity,
                    child: Image.asset(
                      'assets/images/header.png',
                      fit: BoxFit.cover,
                    ),
                  ),
                  // Overlay text and buttons
                  Positioned.fill(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 96),
                        const Text(
                          'UniGather. Stay connected.',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            shadows: [
                              Shadow(
                                blurRadius: 10,
                                color: Colors.black54,
                                offset: Offset(2, 2),
                              ),
                            ],
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 48),
                        SizedBox(
                          width: 200,
                          height: 45,
                          child: ElevatedButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => const LoginScreen(),
                                ),
                              );
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Color.fromARGB(
                                255,
                                224,
                                145,
                                110,
                              ),
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('Log In'),
                          ),
                        ),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: 100,
                          height: 45,
                          child: OutlinedButton(
                            onPressed: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(
                                  builder: (context) => const SignUpScreen(),
                                ),
                              );
                            },
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: Colors.white),
                              foregroundColor: Colors.white,
                            ),
                            child: const Text('Sign up'),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              // Descriptive text section
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: const Text(
                  '''UniGather is the ultimate event hub for students at Wrocław University of Science and Technology. Stay up to date with university events, student council activities, and scientific circles - or create your own events, from study groups to house parties!

🎉 Discover exciting events happening on campus and beyond.
📅 Create and share your own gatherings with the people you choose.
🔑 Connect with students who share your interests.

Whether it’s an official university event or a last-minute meetup, UniGather makes it easy to bring people together. Log in now and start exploring! 🚀''',
                  style: TextStyle(fontSize: 15, color: Colors.white),
                  textAlign: TextAlign.justify,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
