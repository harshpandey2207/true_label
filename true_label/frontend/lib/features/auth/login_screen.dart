import 'package:flutter/material.dart'; 
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import '../admin/admin_dashboard_screen.dart'; 
import '../inspector/inspector_dashboard_screen.dart'; 
import '../manufacturer/manufacturer_dashboard_screen.dart'; 

class LoginScreen extends StatelessWidget {   
  const LoginScreen({super.key});   
  
  @override   
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final isDark = themeProvider.isDarkMode;

    return Scaffold(       
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode, color: theme.iconTheme.color),
            onPressed: () {
              themeProvider.toggleTheme();
            },
          )
        ],
      ),
      body: Center(         
        child: SingleChildScrollView(           
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(             
              mainAxisAlignment: MainAxisAlignment.center,             
              children: [               
                Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: theme.cardColor,
                    border: Border.all(color: Colors.blueAccent, width: 3),
                    boxShadow: [
                      BoxShadow(color: Colors.blueAccent.withValues(alpha: 0.2), blurRadius: 20, spreadRadius: 5)
                    ],
                    image: const DecorationImage(
                      image: AssetImage('assets/images/logo.png'),
                      fit: BoxFit.cover,
                    ),
                  ),
                ),               
                SizedBox(height: 24),               
                Text(                 
                  'TRUE LABEL',                 
                  style: theme.textTheme.headlineLarge?.copyWith(fontWeight: FontWeight.bold, letterSpacing: 4.0),               
                ),               
                SizedBox(height: 8),               
                Text('Legal Metrology Compliance System', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey)),               
                SizedBox(height: 60),               
                Text('Login As', style: theme.textTheme.titleLarge),               
                SizedBox(height: 24),                              
                Wrap(                 
                  alignment: WrapAlignment.center,
                  spacing: 24,
                  runSpacing: 24,
                  children: [                   
                    _buildRoleCard(context, title: 'Admin', icon: Icons.admin_panel_settings, color: Colors.blueAccent, targetScreen: AdminDashboard()),                   
                    _buildRoleCard(context, title: 'Inspector', icon: Icons.qr_code_scanner, color: Colors.orangeAccent, targetScreen: InspectorDashboard()),                   
                    _buildRoleCard(context, title: 'Business Owner', icon: Icons.store, color: Colors.greenAccent, targetScreen: ManufacturerDashboard()),                 
                  ],               
                )             
              ],           
            ),
          ),         
        ),       
      ),     
    );
  }

  Widget _buildRoleCard(BuildContext context, {required String title, required IconData icon, required Color color, required Widget targetScreen}) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    
    return InkWell(       
      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => targetScreen)),       
      borderRadius: BorderRadius.circular(16),       
      child: Container(         
        width: 200,         
        height: 220,         
        decoration: BoxDecoration(           
          color: theme.cardColor,           
          borderRadius: BorderRadius.circular(16),           
          border: Border.all(color: color.withValues(alpha: 0.5), width: 2),           
          boxShadow: [BoxShadow(color: color.withValues(alpha: 0.1), blurRadius: 10, spreadRadius: 2)],         
        ),         
        child: Column(           
          mainAxisAlignment: MainAxisAlignment.center,           
          children: [             
            Icon(icon, size: 60, color: color),             
            SizedBox(height: 24),             
            Text(title, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),           
          ],         
        ),       
      ),     
    );
  }
}