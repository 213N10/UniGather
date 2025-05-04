import 'package:flutter/material.dart';

void main() {
  runApp(const MainPage());
}

class MainPage extends StatelessWidget {
  const MainPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        backgroundColor: Color.fromARGB(255, 124, 0, 0),
        // No AppBar anymore
        body: Column(
          children: [
            Stack(
              children: [
                // Background image
                SizedBox(
                  height: 469, // or MediaQuery height * 0.4
                  width: double.infinity,
                  child: Image.asset(
                    'assets/images/header.png',
                    fit: BoxFit.cover,
                  ),
                ),
                // Overlay text
                Positioned.fill(
                  child: Center(
                    child: Text(
                      'UniGather. Stay connected.',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        shadows: [
                          Shadow(
                            blurRadius: 10,
                            color: Colors.black.withOpacity(0.6),
                            offset: Offset(2, 2),
                          ),
                        ],
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              ],
            ),
            // Add more widgets below as you build
          ],
        ),
      ),
    );
  }
}
