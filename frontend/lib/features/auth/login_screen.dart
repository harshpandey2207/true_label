import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_service.dart';
import '../../core/theme_provider.dart';
import '../admin/admin_dashboard_screen.dart';
import '../inspector/inspector_dashboard_screen.dart';
import '../manufacturer/manufacturer_dashboard_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  Future<void> _enter(BuildContext context, String role) async {
    final demoEmail = 'demo_${role}@truelabel.ai';
    final demoPassword = 'demo_password123';
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(child: CircularProgressIndicator(color: Colors.greenAccent)),
    );

    try {
      try {
        await ApiService.signIn(email: demoEmail, password: demoPassword);
      } catch (e) {
        await ApiService.register(
          name: 'Demo $role',
          email: demoEmail,
          password: demoPassword,
          role: role,
          organizationName: 'Hackathon Demo',
        );
        await ApiService.signIn(email: demoEmail, password: demoPassword);
      }
      
      if (context.mounted) {
        Navigator.pop(context); // remove loading
        Widget screen;
        switch (role) {
          case 'manufacturer': screen = ManufacturerDashboard(); break;
          case 'inspector': screen = InspectorDashboard(); break;
          case 'admin': screen = AdminDashboard(); break;
          default: screen = ManufacturerDashboard();
        }
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => screen));
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to enter demo mode: $e')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = themeProvider.isDarkMode;
    final bg = isDark ? const Color(0xFF121212) : const Color(0xFFF5F5F5);
    final card = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final muted = isDark ? Colors.white60 : Colors.black54;

    return Scaffold(
      backgroundColor: bg,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.verified_outlined, size: 64, color: Colors.greenAccent),
              const SizedBox(height: 16),
              Text('True Label', style: TextStyle(color: textColor, fontSize: 36, fontWeight: FontWeight.bold, letterSpacing: 1)),
              const SizedBox(height: 8),
              Text('Legal Metrology Compliance Platform', style: TextStyle(color: muted, fontSize: 15)),
              const SizedBox(height: 4),
              Text('AI-Powered · Open Source · India-First', style: TextStyle(color: Colors.greenAccent.withValues(alpha: 0.85), fontSize: 13)),
              const SizedBox(height: 40),

              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                decoration: BoxDecoration(
                  color: Colors.greenAccent.withValues(alpha: 0.12),
                  border: Border.all(color: Colors.greenAccent.withValues(alpha: 0.4)),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.flash_on, color: Colors.greenAccent, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Hackathon Demo Mode — tap any role below to enter instantly. No account required.',
                        style: TextStyle(color: textColor, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              _RoleCard(
                icon: Icons.factory_outlined,
                title: 'Business Owner / Manufacturer',
                subtitle: 'Scan labels · Generate compliant SVG labels · View legal gaps',
                color: Colors.greenAccent,
                card: card, textColor: textColor, muted: muted,
                onTap: () => _enter(context, 'manufacturer'),
              ),
              const SizedBox(height: 16),
              _RoleCard(
                icon: Icons.search_outlined,
                title: 'Government Inspector',
                subtitle: 'Audit product labels · See violation scores · Issue notices',
                color: Colors.blueAccent,
                card: card, textColor: textColor, muted: muted,
                onTap: () => _enter(context, 'inspector'),
              ),
              const SizedBox(height: 16),
              _RoleCard(
                icon: Icons.admin_panel_settings_outlined,
                title: 'Admin / Regulator',
                subtitle: 'View district maps · Monitor compliance rates · Manage rules',
                color: Colors.orangeAccent,
                card: card, textColor: textColor, muted: muted,
                onTap: () => _enter(context, 'admin'),
              ),

              const SizedBox(height: 40),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.light_mode, size: 18, color: muted),
                  const SizedBox(width: 8),
                  Text('Theme', style: TextStyle(color: muted, fontSize: 13)),
                  const SizedBox(width: 8),
                  Switch(
                    value: isDark,
                    activeColor: Colors.greenAccent,
                    onChanged: (_) => themeProvider.toggleTheme(),
                  ),
                  const SizedBox(width: 4),
                  Icon(Icons.dark_mode, size: 18, color: muted),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RoleCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final Color card;
  final Color textColor;
  final Color muted;
  final VoidCallback onTap;

  const _RoleCard({
    required this.icon, required this.title, required this.subtitle,
    required this.color, required this.card, required this.textColor,
    required this.muted, required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: card,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 18),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.35)),
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: color.withValues(alpha: 0.12), shape: BoxShape.circle),
                child: Icon(icon, color: color, size: 28),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(title, style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 4),
                    Text(subtitle, style: TextStyle(color: muted, fontSize: 12)),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios_rounded, color: color, size: 16),
            ],
          ),
        ),
      ),
    );
  }
}
