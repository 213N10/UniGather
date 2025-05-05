import 'package:flutter/material.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 124, 0, 0),
      appBar: AppBar(
        title: const Text('Log In'),
        backgroundColor: const Color.fromARGB(255, 124, 0, 0),
      ),
      body: const Center(
        child: Text(
          'Login Screen',
          style: TextStyle(color: Colors.white, fontSize: 24),
        ),
      ),
    );
  }
}
