import 'package:flutter/material.dart';
import '../explore/explore_screen.dart';
import '../login/login_screen.dart';
import '../../api/auth_api.dart';
import '../../services/auth_service.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});

  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _nameController = TextEditingController();
  final _scaffoldKey = GlobalKey<ScaffoldState>();
  bool _isLoading = false;

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  Future<void> _signup() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text.trim();
    final name = _nameController.text.trim();

    if (email.isEmpty || password.isEmpty || name.isEmpty) {
      _showError("Please fill all fields");
      return;
    }

    setState(() => _isLoading = true);

    try {
      final user = await AuthApi.register(
        name: name,
        email: email,
        password: password,
        role: 'student',
      );

      if (user == null) {
        _showError("Email is already taken or registration failed");
        setState(() => _isLoading = false);
        return;
      }

      final loginResponse = await AuthApi.login(email, password);
      if (loginResponse != null) {
        await AuthService.saveAuthData(
          loginResponse['token'],
          loginResponse['user'],
        );
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const ExploreScreen()),
        );
      } else {
        _showError("Login after registration failed");
      }
    } catch (e) {
      _showError("Something went wrong");
    }

    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: const Color.fromARGB(255, 124, 0, 0),
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 124, 0, 0),
        foregroundColor: Colors.white,
        title: const Text('Sign up'),
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
          height: 520,
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'Welcome!',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              const Text('Sign up', style: TextStyle(fontSize: 16)),
              const SizedBox(height: 20),
              TextField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Name'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: 'Email'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Password'),
                obscureText: true,
              ),
              const SizedBox(height: 20),
              SizedBox(
                width: 200,
                height: 45,
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _signup,
                  child:
                      _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Sign up'),
                ),
              ),
              const SizedBox(height: 15),
              GestureDetector(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                },
                child: const Text(
                  "Have an account already? Log in.",
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
