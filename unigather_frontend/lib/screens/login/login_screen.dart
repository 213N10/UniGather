import 'package:flutter/material.dart';
import '../signup/signup_screen.dart';
import '../explore/explore_screen.dart';
import '../../api/auth_api.dart';
import '../../services/auth_service.dart';
import '../../models/user.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  bool isLoading = false;

  void _login() async {
    final email = emailController.text.trim();
    final password = passwordController.text.trim();

    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text("Please enter both email and password")),
      );
      return;
    }

    setState(() {
      isLoading = true;
    });

    try {
      final loginResponse = await AuthApi.login(email, password);
      if (loginResponse != null &&
          loginResponse['token'] != null &&
          loginResponse['user'] != null) {
        await AuthService.saveAuthData(
          loginResponse['token'] as String,
          loginResponse['user'] as User,
        );
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const ExploreScreen()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("Login failed: Invalid credentials or server error"),
          ),
        );
      }

      if (context.mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => const ExploreScreen()),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Login failed: $e")));
    } finally {
      if (mounted) {
        setState(() {
          isLoading = false;
        });
      }
    }
  }

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
            Navigator.of(context).pushReplacementNamed('/');
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
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            mainAxisSize: MainAxisSize.max,
            children: [
              const Text(
                'Welcome back!',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              const Text('Log in', style: TextStyle(fontSize: 16)),
              const SizedBox(height: 20),
              TextField(
                controller: emailController,
                decoration: const InputDecoration(labelText: 'Email'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: passwordController,
                decoration: const InputDecoration(labelText: 'Password'),
                obscureText: true,
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: 200,
                height: 45,
                child: ElevatedButton(
                  onPressed: isLoading ? null : _login,
                  child:
                      isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Log in'),
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
