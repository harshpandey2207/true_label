import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'core/theme_provider.dart';
import 'core/api_service.dart';
import 'features/auth/login_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  try {
    await dotenv.load(fileName: ".env");
  } catch (e) {
    debugPrint("Could not load .env file: $e");
  }
  
  // Asynchronously wake up or ping backend container immediately upon app open
  ApiService.preWarmBackend();
  
  runApp(
    ChangeNotifierProvider(
      create: (_) => ThemeProvider(),
      child: const TrueLabelApp(),
    ),
  );
}

class TrueLabelApp extends StatelessWidget {
  const TrueLabelApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);
    
    return MaterialApp(
      title: 'True Label',
      debugShowCheckedModeBanner: false,
      themeMode: themeProvider.isDarkMode ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0F766E), brightness: Brightness.light),
        scaffoldBackgroundColor: const Color(0xFFF4F8F7),
        textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme),
        cardTheme: CardThemeData(color: Colors.white, elevation: 1, margin: EdgeInsets.zero, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
        inputDecorationTheme: InputDecorationTheme(border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)), filled: true, fillColor: Colors.white),
      ),
      darkTheme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF2DD4BF), brightness: Brightness.dark),
        scaffoldBackgroundColor: const Color(0xFF0E171D),
        textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme),
        cardTheme: CardThemeData(color: const Color(0xFF16232B), elevation: 1, margin: EdgeInsets.zero, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18))),
        inputDecorationTheme: InputDecorationTheme(border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)), filled: true, fillColor: const Color(0xFF16232B)),
      ),
      home: const LoginScreen(),
      routes: {
        '/login': (_) => const LoginScreen(),
      },
    );
  }
}
