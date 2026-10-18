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
    final textColor = isDark ? Colors.white : Colors.black87;
    final muted = isDark ? Colors.white60 : Colors.black54;
    final accent = isDark ? const Color(0xFF6EE7B7) : const Color(0xFF0F766E);
    final accentBlue = isDark ? const Color(0xFF93C5FD) : const Color(0xFF2563EB);
    final surface = isDark ? const Color(0xFF18232B) : Colors.white;

    return Scaffold(
      backgroundColor: bg,
      body: DecoratedBox(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: isDark
                ? const [Color(0xFF0B1720), Color(0xFF122B32), Color(0xFF111827)]
                : const [Color(0xFFEFFAF7), Color(0xFFF8FAFC), Color(0xFFEFF6FF)],
          ),
        ),
        child: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 28, 20, 28),
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 980),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Image.asset(
                          'assets/images/logo.png',
                          width: 104,
                          height: 104,
                          fit: BoxFit.contain,
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Evidence-led label screening for India', style: TextStyle(color: textColor, fontSize: 18, fontWeight: FontWeight.w700)),
                              const SizedBox(height: 6),
                              Text('Scan · Understand · Consume safely', style: TextStyle(color: muted, fontSize: 14)),
                            ],
                          ),
                        ),
                        IconButton(
                          tooltip: isDark ? 'Use light theme' : 'Use dark theme',
                          icon: Icon(isDark ? Icons.light_mode_rounded : Icons.dark_mode_rounded, color: muted),
                          onPressed: themeProvider.toggleTheme,
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Container(
                      padding: const EdgeInsets.all(22),
                      decoration: BoxDecoration(
                        color: surface.withValues(alpha: isDark ? .82 : .92),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: accent.withValues(alpha: .22)),
                        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: isDark ? .18 : .06), blurRadius: 28, offset: const Offset(0, 12))],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Move from package photo to review-ready evidence', style: TextStyle(color: textColor, fontSize: 24, fontWeight: FontWeight.w700, height: 1.15)),
                          const SizedBox(height: 8),
                          Text('Read package declarations locally, keep every image attached to its scan, and generate editable label drafts without inventing missing values.', style: TextStyle(color: muted, fontSize: 14, height: 1.45)),
                          const SizedBox(height: 16),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: const [
                              _FeaturePill(icon: Icons.document_scanner_outlined, label: 'Local OCR'),
                              _FeaturePill(icon: Icons.fact_check_outlined, label: 'Evidence-aware checks'),
                              _FeaturePill(icon: Icons.picture_as_pdf_outlined, label: 'Reports & labels'),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 26),
                    Row(
                      children: [
                        Text('Choose your workspace', style: TextStyle(color: textColor, fontSize: 18, fontWeight: FontWeight.w700)),
                        const SizedBox(width: 10),
                        Expanded(child: Divider(color: muted.withValues(alpha: .25))),
                      ],
                    ),
                    const SizedBox(height: 12),
                    LayoutBuilder(
                      builder: (context, constraints) {
                        final columns = constraints.maxWidth >= 760 ? 3 : 1;
                        final width = columns == 3 ? (constraints.maxWidth - 32) / 3 : constraints.maxWidth;
                        return Wrap(
                          spacing: 16,
                          runSpacing: 16,
                          children: [
                            SizedBox(width: width, child: _RoleCard(icon: Icons.factory_outlined, title: 'Manufacturer', subtitle: 'Scan packages, review gaps and generate editable drafts.', color: accent, card: surface, textColor: textColor, muted: muted, onTap: () => _enter(context, 'manufacturer'))),
                            SizedBox(width: width, child: _RoleCard(icon: Icons.search_rounded, title: 'Inspector', subtitle: 'Capture evidence, review verdicts and escalate cases.', color: accentBlue, card: surface, textColor: textColor, muted: muted, onTap: () => _enter(context, 'inspector'))),
                            SizedBox(width: width, child: _RoleCard(icon: Icons.admin_panel_settings_outlined, title: 'Admin / Regulator', subtitle: 'Monitor rules, reports, audit trails and escalations.', color: const Color(0xFFF59E0B), card: surface, textColor: textColor, muted: muted, onTap: () => _enter(context, 'admin'))),
                          ],
                        );
                      },
                    ),
                    const SizedBox(height: 18),
                    Row(
                      children: [
                        Icon(Icons.flash_on_rounded, color: accent, size: 18),
                        const SizedBox(width: 8),
                        Expanded(child: Text('Hackathon Demo Mode — use any role to enter instantly. No account setup required.', style: TextStyle(color: muted, fontSize: 12))),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text('Automated results are screening evidence, not legal certification. Review unclear or unresolved declarations before acting.', textAlign: TextAlign.center, style: TextStyle(color: muted.withValues(alpha: .82), fontSize: 11)),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FeaturePill extends StatelessWidget {
  final IconData icon;
  final String label;

  const _FeaturePill({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 8),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withValues(alpha: .08),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: theme.colorScheme.primary.withValues(alpha: .15)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [Icon(icon, size: 16, color: theme.colorScheme.primary), const SizedBox(width: 6), Text(label, style: TextStyle(color: theme.colorScheme.onSurface, fontSize: 12, fontWeight: FontWeight.w600))]),
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
      elevation: 2,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          width: double.infinity,
          constraints: const BoxConstraints(minHeight: 152),
          padding: const EdgeInsets.fromLTRB(18, 18, 14, 18),
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
                    Text(title, style: TextStyle(color: textColor, fontWeight: FontWeight.w700, fontSize: 16)),
                    const SizedBox(height: 4),
                    Text(subtitle, style: TextStyle(color: muted, fontSize: 12, height: 1.35)),
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
