import 'package:flutter/material.dart';
import '../signup/signup_screen.dart';
import '../explore/explore_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 124, 0, 0),
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 124, 0, 0),
        foregroundColor: Colors.white,
        title: const Text('Login'),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            Navigator.of(context).pushReplacementNamed(
              '/',
            ); // or pushNamed() if you prefer stacking
          },
        ),
      ),
      body: Center(
        child: Container(
          padding: const EdgeInsets.all(20),
          height: 500,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            mainAxisAlignment:
                MainAxisAlignment.center, // center items vertically
            crossAxisAlignment:
                CrossAxisAlignment.center, // center items horizontally
            mainAxisSize: MainAxisSize.max,
            children: [
              const Text(
                'Welcome back!',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              const Text('Log in', style: TextStyle(fontSize: 16)),
              const SizedBox(height: 20),
              const TextField(decoration: InputDecoration(labelText: 'Email')),
              const SizedBox(height: 10),
              const TextField(
                decoration: InputDecoration(labelText: 'Password'),
                obscureText: true,
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: 200,
                height: 45,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (context) => const ExploreScreen(),
                      ),
                    );
                  },
                  child: const Text('Log in'),
                ),
              ),
              const SizedBox(height: 15),
              GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const SignupScreen(),
                    ),
                  );
                },
                child: const Text(
                  "Don't have an account? Sign up.",
                  style: TextStyle(
                    decoration: TextDecoration.underline,
                    color: Colors.blue,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
