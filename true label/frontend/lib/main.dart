import 'package:flutter/material.dart';
// This imports the file you just created!
import 'features/admin/admin_dashboard_screen.dart';

void main() {
  runApp(const TrueLabelApp());
}

class TrueLabelApp extends StatelessWidget {
  const TrueLabelApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'True Label Admin',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF121212),
      ),
      // This tells the app to load your dashboard first
      home: AdminDashboard(),
    );
  }
}