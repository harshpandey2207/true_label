import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';

import 'package:true_label/core/theme_provider.dart';
import 'package:true_label/main.dart';

void main() {
  testWidgets('demo entry screen exposes all three role workspaces', (tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => ThemeProvider(),
        child: const TrueLabelApp(),
      ),
    );
    await tester.pump();

    expect(find.text('True Label'), findsOneWidget);
    expect(find.text('Manufacturer'), findsOneWidget);
    expect(find.text('Inspector'), findsOneWidget);
    expect(find.text('Admin / Regulator'), findsOneWidget);
    expect(find.textContaining('Hackathon Demo Mode'), findsOneWidget);
  });
}
