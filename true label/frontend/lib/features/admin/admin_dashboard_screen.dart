import 'package:flutter/material.dart';
import 'package:sidebarx/sidebarx.dart';

class AdminDashboard extends StatelessWidget {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF121212), // Dark theme background
      body: Row(
        children: [
          SidebarX(
            controller: _controller,
            theme: const SidebarXTheme(
              decoration: BoxDecoration(color: Color(0xFF1E1E1E)),
              textStyle: TextStyle(color: Colors.white),
              selectedTextStyle: TextStyle(color: Colors.blueAccent),
              iconTheme: IconThemeData(color: Colors.white54),
              selectedIconTheme: IconThemeData(color: Colors.blueAccent),
            ),
            items: const [
              SidebarXItem(icon: Icons.dashboard, label: 'Overview'),
              SidebarXItem(icon: Icons.warning_amber_rounded, label: 'Pending Violations'),
              SidebarXItem(icon: Icons.folder, label: 'Report Repository'),
              SidebarXItem(icon: Icons.list_alt, label: 'Audit Logs'),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: _ScreensExample(controller: _controller),
            ),
          ),
        ],
      ),
    );
  }
}

class _ScreensExample extends StatelessWidget {
  const _ScreensExample({Key? key, required this.controller}) : super(key: key);
  final SidebarXController controller;

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0:
            return Text('Overview Charts Go Here', style: TextStyle(color: Colors.white, fontSize: 24));
          case 1:
            return Text('Pending Action Cards Go Here', style: TextStyle(color: Colors.white, fontSize: 24));
          // Add other cases
          default:
            return const Center(child: Text('Not found'));
        }
      },
    );
  }
}