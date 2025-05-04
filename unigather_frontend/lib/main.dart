import 'package:flutter/material.dart';
import 'screens/main/main_screen.dart'; // or whatever your main screen is called

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
      theme: ThemeData(primarySwatch: Colors.red),
      home: const MainPage(), // <- This is your actual first screen
    );
  }
}
