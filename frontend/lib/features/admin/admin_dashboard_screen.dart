import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import 'dart:convert';

import 'package:provider/provider.dart';

import '../../core/theme_provider.dart';

import 'package:sidebarx/sidebarx.dart';
import 'package:fl_chart/fl_chart.dart';

import '../../core/report_viewer.dart';
import '../../core/api_service.dart';
import '../../core/product_catalog.dart';
import 'mock_data.dart';

class AdminDashboard extends StatefulWidget {
  const AdminDashboard({super.key});

  @override
  State<AdminDashboard> createState() => _AdminDashboardState();
}

class _AdminDashboardState extends State<AdminDashboard> {
  final _controller = SidebarXController(selectedIndex: 0, extended: true);

  Widget _buildSidebar(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: theme.cardColor),
        textStyle: TextStyle(
          color: theme.brightness == Brightness.dark
              ? Colors.white
              : Colors.black,
        ),
        selectedTextStyle: TextStyle(color: theme.colorScheme.primary),
        iconTheme: IconThemeData(
          color: theme.iconTheme.color?.withValues(alpha: 0.65),
        ),
        selectedIconTheme: IconThemeData(color: theme.colorScheme.primary),
      ),
      extendedTheme: SidebarXTheme(
        width: 260,
        decoration: BoxDecoration(color: theme.cardColor),
      ),
      items: [
        SidebarXItem(icon: Icons.dashboard, label: 'Dashboard'),
        SidebarXItem(icon: Icons.warning_amber_rounded, label: 'Violations'),
        SidebarXItem(icon: Icons.rule, label: 'Rules'),
        SidebarXItem(icon: Icons.folder, label: 'Reports'),
        SidebarXItem(icon: Icons.list_alt, label: 'Audit Logs'),
        SidebarXItem(icon: Icons.person, label: 'Profile'),
        SidebarXItem(icon: Icons.logout, label: 'Logout'),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    final isMobile = MediaQuery.of(context).size.width < 600;

    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text(
          'Admin Portal',
          style:
              theme.textTheme.titleLarge?.copyWith(fontSize: 18) ??
              TextStyle(fontSize: 18),
        ),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(
              themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode,
            ),
            onPressed: () {
              themeProvider.toggleTheme();
            },
          ),
        ],
      ),
      drawer: isMobile ? Drawer(child: _buildSidebar(context)) : null,
      body: Row(
        children: [
          if (!isMobile) _buildSidebar(context),
          Expanded(
            child: Padding(
              padding: EdgeInsets.all(isMobile ? 16.0 : 24.0),
              child: _ScreensRouter(controller: _controller),
            ),
          ),
        ],
      ),
    );
  }
}

class _ScreensRouter extends StatelessWidget {
  const _ScreensRouter({super.key, required this.controller});
  final SidebarXController controller;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0:
            return _OverviewScreen();
          case 1:
            return _PendingViolationsScreen();
          case 2:
            return _RulesScreen();
          case 3:
            return _ReportRepositoryScreen();
          case 4:
            return _AuditLogsScreen();
          case 5:
            return _ProfileScreen();
          case 6:
            return _LogoutScreen();
          default:
            return Center(
              child: Text(
                'Not found',
                style: TextStyle(
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                ),
              ),
            );
        }
      },
    );
  }
}

class _OverviewScreen extends StatefulWidget {
  @override
  State<_OverviewScreen> createState() => _OverviewScreenState();
}

class _OverviewScreenState extends State<_OverviewScreen> {
  late Future<Map<String, dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _data = ApiService.getJson('/workspace/admin/overview');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(
            child: FilledButton.icon(
              onPressed: () => setState(_load),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry live overview'),
            ),
          );
        }
        final data = snapshot.data ?? const <String, dynamic>{};
        final total = (data['scan_count'] as num?)?.toInt() ?? 0;
        final pass = (data['pass_scan_count'] as num?)?.toInt() ?? 0;
        final unresolved =
            (data['unresolved_scan_count'] as num?)?.toInt() ?? 0;
        final violations =
            (data['confirmed_violation_count'] as num?)?.toInt() ?? 0;
        final categories = (data['by_category'] as List?) ?? const [];
        return RefreshIndicator(
          onRefresh: () async => setState(_load),
          child: ListView(
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Live compliance overview',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => setState(_load),
                    icon: const Icon(Icons.refresh),
                    tooltip: 'Refresh',
                  ),
                ],
              ),
              Text(
                'Operational counts from persisted scans, reports and review cases.',
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 18),
              LayoutBuilder(
                builder: (context, constraints) {
                  final columns = constraints.maxWidth >= 880
                      ? 4
                      : constraints.maxWidth >= 560
                      ? 2
                      : 1;
                  final width =
                      (constraints.maxWidth - (columns - 1) * 12) / columns;
                  final metrics = <(String, String, IconData, Color)>[
                    (
                      'Scans',
                      '$total',
                      Icons.document_scanner_outlined,
                      Colors.teal,
                    ),
                    (
                      'Passed checks',
                      '$pass',
                      Icons.verified_outlined,
                      Colors.green,
                    ),
                    (
                      'Unresolved',
                      '$unresolved',
                      Icons.help_outline_rounded,
                      Colors.orange,
                    ),
                    (
                      'Confirmed issues',
                      '$violations',
                      Icons.warning_amber_rounded,
                      Colors.red,
                    ),
                  ];
                  return Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: metrics
                        .map(
                          (item) => SizedBox(
                            width: width,
                            child: Card(
                              child: Padding(
                                padding: const EdgeInsets.all(18),
                                child: Row(
                                  children: [
                                    CircleAvatar(
                                      backgroundColor: item.$4.withValues(
                                        alpha: .12,
                                      ),
                                      child: Icon(item.$3, color: item.$4),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          Text(
                                            item.$2,
                                            style: theme.textTheme.headlineSmall
                                                ?.copyWith(
                                                  fontWeight: FontWeight.w800,
                                                ),
                                          ),
                                          Text(
                                            item.$1,
                                            style: theme.textTheme.bodySmall
                                                ?.copyWith(
                                                  color: theme
                                                      .colorScheme
                                                      .onSurfaceVariant,
                                                ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ),
                        )
                        .toList(),
                  );
                },
              ),
              const SizedBox(height: 18),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Workspace coverage',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Wrap(
                        spacing: 20,
                        runSpacing: 10,
                        children: [
                          _AdminCount(
                            label: 'Users',
                            value: '${data['user_count'] ?? 0}',
                            icon: Icons.people_outline,
                          ),
                          _AdminCount(
                            label: 'Categories',
                            value: '${data['category_count'] ?? 0}',
                            icon: Icons.category_outlined,
                          ),
                          _AdminCount(
                            label: 'Rules',
                            value: '${data['rule_count'] ?? 0}',
                            icon: Icons.rule_outlined,
                          ),
                          _AdminCount(
                            label: 'Reports',
                            value: '${data['report_count'] ?? 0}',
                            icon: Icons.picture_as_pdf_outlined,
                          ),
                          _AdminCount(
                            label: 'Escalations',
                            value: '${data['escalation_count'] ?? 0}',
                            icon: Icons.escalator_warning_outlined,
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Scans by product profile',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      if (categories.isEmpty)
                        Text(
                          'No scans have been recorded yet.',
                          style: theme.textTheme.bodyMedium?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant,
                          ),
                        )
                      else
                        ...categories.map((raw) {
                          final item = Map<String, dynamic>.from(raw as Map);
                          return ListTile(
                            contentPadding: EdgeInsets.zero,
                            leading: const Icon(Icons.label_outline),
                            title: Text(
                              item['category']?.toString() ??
                                  'Unknown category',
                            ),
                            trailing: Text(
                              '${item['count'] ?? 0}',
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          );
                        }),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 18),
              const _AdminSampleAnalyticsPanel(),
              const SizedBox(height: 12),
              Text(
                'Automated screening is evidence support, not a legal certificate. Review unresolved and category-specific checks before acting.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _AdminCount extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _AdminCount({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, size: 18, color: theme.colorScheme.primary),
        const SizedBox(width: 7),
        Text('$label  ', style: theme.textTheme.bodyMedium),
        Text(
          value,
          style: theme.textTheme.bodyMedium?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
      ],
    );
  }
}

/// Keeps the jury/demo analytics useful even when a fresh local database has
/// no scans yet. It is explicitly labelled sample data and never replaces the
/// live counters above.
class _AdminSampleAnalyticsPanel extends StatelessWidget {
  const _AdminSampleAnalyticsPanel();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final sampleScans = [44.0, 36.0, 31.0, 27.0, 24.0, 20.0];
    final sampleLabels = ['Maha.', 'UP', 'Delhi', 'J&K', 'AP', 'Karn.'];
    final sampleViolations = regionalData.fold<int>(
      0,
      (sum, item) => sum + (item['violations'] as int),
    );
    final sampleCompliant = regionalData.fold<int>(
      0,
      (sum, item) => sum + (item['compliant'] as int),
    );
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Regional analytics',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Illustrative demo distribution — not government enforcement data.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            SizedBox(
              height: 230,
              child: BarChart(
                BarChartData(
                  maxY: 50,
                  gridData: const FlGridData(
                    show: true,
                    drawVerticalLine: false,
                  ),
                  borderData: FlBorderData(show: false),
                  titlesData: FlTitlesData(
                    rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false),
                    ),
                    leftTitles: const AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 30,
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          return index >= 0 && index < sampleLabels.length
                              ? Padding(
                                  padding: const EdgeInsets.only(top: 6),
                                  child: Text(
                                    sampleLabels[index],
                                    style: theme.textTheme.labelSmall,
                                  ),
                                )
                              : const SizedBox.shrink();
                        },
                      ),
                    ),
                  ),
                  barGroups: [
                    for (var i = 0; i < sampleScans.length; i++)
                      BarChartGroupData(
                        x: i,
                        barRods: [
                          BarChartRodData(
                            toY: sampleScans[i],
                            width: 18,
                            borderRadius: BorderRadius.circular(4),
                            color: theme.colorScheme.primary,
                          ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Sample scan volume by selected state',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: SizedBox(
                    height: 170,
                    child: PieChart(
                      PieChartData(
                        centerSpaceRadius: 38,
                        sectionsSpace: 2,
                        sections: [
                          PieChartSectionData(
                            value: sampleCompliant.toDouble(),
                            color: Colors.teal,
                            title: '$sampleCompliant',
                            radius: 44,
                            titleStyle: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          PieChartSectionData(
                            value: sampleViolations.toDouble(),
                            color: Colors.deepOrange,
                            title: '$sampleViolations',
                            radius: 44,
                            titleStyle: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Sample outcome mix',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const _LegendDot(
                        color: Colors.teal,
                        label: 'Screened without sample flags',
                      ),
                      const SizedBox(height: 6),
                      const _LegendDot(
                        color: Colors.deepOrange,
                        label: 'Illustrative review flags',
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Use live persisted scans above for operational decisions.',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text(
              'India state-wise heatmap',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Hover or tap a region for the illustrative scan/flag distribution.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            SizedBox(
              height: 390,
              child: InteractiveGeographicHeatmap(sharedData: regionalData),
            ),
          ],
        ),
      ),
    );
  }
}

class _LegendDot extends StatelessWidget {
  const _LegendDot({required this.color, required this.label});
  final Color color;
  final String label;
  @override
  Widget build(BuildContext context) => Row(
    children: [
      Container(
        width: 10,
        height: 10,
        decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      ),
      const SizedBox(width: 8),
      Expanded(
        child: Text(label, style: Theme.of(context).textTheme.bodySmall),
      ),
    ],
  );
}

class _LegacyOverviewScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    double compliancePercentage = (totalCompliant / totalScans) * 100;
    double violationPercentage = 100 - compliancePercentage;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Sample Metrics & Heatmap',
            style: TextStyle(
              color: theme.brightness == Brightness.dark
                  ? Colors.white
                  : Colors.black,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Static demonstration data; not live government records or enforcement metrics.',
            style: TextStyle(color: textMuted),
          ),
          SizedBox(height: 20),

          _buildStatCard(
            title: 'Total Scans Recorded',
            value: totalScans.toString(),
            subtitle: 'Static sample value',
            icon: Icons.qr_code_scanner,
            color: Colors.blueAccent,
            theme: theme,
          ),
          SizedBox(height: 12),

          Card(
            color: theme.cardColor,
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        'Sample screening counts',
                        style: TextStyle(
                          color: theme.brightness == Brightness.dark
                              ? Colors.white70
                              : Colors.black87,
                          fontSize: 14,
                        ),
                      ),
                      SizedBox(height: 6),
                      Text(
                        '$totalCompliant Compliant',
                        style: TextStyle(
                          color: Colors.greenAccent,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        '$totalViolations Non-Compliant',
                        style: TextStyle(
                          color: Colors.redAccent,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  SizedBox(
                    width: 70,
                    height: 70,
                    child: Stack(
                      alignment: Alignment.center,
                      children: [
                        PieChart(
                          PieChartData(
                            sectionsSpace: 2,
                            centerSpaceRadius: 22,
                            sections: [
                              PieChartSectionData(
                                color: Colors.greenAccent,
                                value: compliancePercentage,
                                title: '',
                                radius: 8,
                              ),
                              PieChartSectionData(
                                color: Colors.redAccent,
                                value: violationPercentage,
                                title: '',
                                radius: 8,
                              ),
                            ],
                          ),
                        ),
                        Text(
                          '${compliancePercentage.toStringAsFixed(0)}%',
                          style: TextStyle(
                            color: theme.brightness == Brightness.dark
                                ? Colors.white
                                : Colors.black,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 12),

          _buildStatCard(
            title: 'Penalty estimate',
            value: 'Not calculated',
            subtitle:
                'The prototype has no penalty calculation or payment service',
            icon: Icons.account_balance_wallet,
            color: Colors.orangeAccent,
            theme: theme,
          ),
          SizedBox(height: 24),

          Card(
            color: theme.cardColor,
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Text(
                    'Violations Over Time (Last 7 Days)',
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white70
                          : Colors.black87,
                      fontSize: 18,
                    ),
                  ),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: LineChart(
                      LineChartData(
                        gridData: FlGridData(
                          show: true,
                          drawVerticalLine: false,
                          getDrawingHorizontalLine: (value) =>
                              FlLine(color: Colors.white12, strokeWidth: 1),
                        ),
                        titlesData: FlTitlesData(
                          show: true,
                          rightTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                          topTitles: const AxisTitles(
                            sideTitles: SideTitles(showTitles: false),
                          ),
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 22,
                              interval: 1,
                              getTitlesWidget: (value, meta) {
                                final style = TextStyle(
                                  color: theme.brightness == Brightness.dark
                                      ? Colors.white70
                                      : Colors.black87,
                                  fontSize: 12,
                                );
                                Widget text;
                                switch (value.toInt()) {
                                  case 0:
                                    text = Text('Mon', style: style);
                                    break;
                                  case 2:
                                    text = Text('Wed', style: style);
                                    break;
                                  case 4:
                                    text = Text('Fri', style: style);
                                    break;
                                  case 6:
                                    text = Text('Sun', style: style);
                                    break;
                                  default:
                                    text = Text('', style: style);
                                    break;
                                }
                                return SideTitleWidget(
                                  axisSide: meta.axisSide,
                                  child: text,
                                );
                              },
                            ),
                          ),
                          leftTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 28,
                              interval: 1,
                              getTitlesWidget: (value, meta) {
                                return Text(
                                  value.toInt().toString(),
                                  style: TextStyle(
                                    color: theme.brightness == Brightness.dark
                                        ? Colors.white70
                                        : Colors.black87,
                                    fontSize: 12,
                                  ),
                                );
                              },
                            ),
                          ),
                        ),
                        borderData: FlBorderData(
                          show: true,
                          border: Border(
                            bottom: BorderSide(
                              color: theme.brightness == Brightness.dark
                                  ? Colors.white70
                                  : Colors.black87,
                              width: 1,
                            ),
                            left: BorderSide(
                              color: theme.brightness == Brightness.dark
                                  ? Colors.white70
                                  : Colors.black87,
                              width: 1,
                            ),
                            right: BorderSide.none,
                            top: BorderSide.none,
                          ),
                        ),
                        minY: 0,
                        maxY: 6,
                        lineBarsData: [
                          LineChartBarData(
                            spots: [
                              FlSpot(0, 3),
                              FlSpot(1, 1),
                              FlSpot(2, 4),
                              FlSpot(3, 2),
                              FlSpot(4, 5),
                              FlSpot(5, 3),
                              FlSpot(6, 4),
                            ],
                            isCurved: true,
                            color: Colors.blueAccent,
                            barWidth: 4,
                            isStrokeCapRound: true,
                            belowBarData: BarAreaData(
                              show: true,
                              color: Colors.blueAccent.withValues(alpha: 0.3),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 16),
          Card(
            color: theme.cardColor,
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  Text(
                    'India State-wise Violation Heatmap',
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white70
                          : Colors.black87,
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  Text(
                    'Hover over any state to see scan & violation details',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                  SizedBox(height: 16),
                  SizedBox(
                    height: 480,
                    child: InteractiveGeographicHeatmap(
                      sharedData: regionalData,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
    required ThemeData theme,
  }) {
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Card(
      color: theme.cardColor,
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white70
                          : Colors.black87,
                      fontSize: 12,
                    ),
                  ),
                  SizedBox(height: 4),
                  Text(
                    value,
                    style: TextStyle(
                      color: color,
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    subtitle,
                    style: TextStyle(color: Colors.white38, fontSize: 11),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// INDIA CHOROPLETH HEATMAP — Pure Flutter CustomPainter
// Performance model: ValueNotifier drives hover; zero setState on mouse move.
// CustomPainter.repaint is wired to the notifier so only the canvas repaints.
// ─────────────────────────────────────────────────────────────────────────────

typedef _HoverState = ({int? idx, Offset pos});

class InteractiveGeographicHeatmap extends StatefulWidget {
  final List<Map<String, dynamic>> sharedData;
  const InteractiveGeographicHeatmap({super.key, required this.sharedData});

  @override
  State<InteractiveGeographicHeatmap> createState() =>
      _InteractiveGeographicHeatmapState();
}

class _InteractiveGeographicHeatmapState
    extends State<InteractiveGeographicHeatmap> {
  List<_StateShape> _shapes = [];
  bool _loading = true;

  // Notifier replaces setState for hover — no widget rebuild on every mouse move
  final _hover = ValueNotifier<_HoverState>((idx: null, pos: Offset.zero));

  @override
  void initState() {
    super.initState();
    _loadGeoJson();
  }

  @override
  void dispose() {
    _hover.dispose();
    super.dispose();
  }

  Future<void> _loadGeoJson() async {
    try {
      final raw = await rootBundle.loadString(
        'assets/maps/india_states.geojson',
      );
      final geo = json.decode(raw) as Map<String, dynamic>;
      final features = geo['features'] as List;

      final lookup = <String, Map<String, dynamic>>{};
      for (final row in widget.sharedData) {
        lookup[(row['name'] as String).toLowerCase()] = row;
      }

      double minLon = 999, maxLon = -999, minLat = 999, maxLat = -999;
      for (final feat in features) {
        _iterCoords(feat['geometry'], (lon, lat) {
          if (lon < minLon) minLon = lon;
          if (lon > maxLon) maxLon = lon;
          if (lat < minLat) minLat = lat;
          if (lat > maxLat) maxLat = lat;
        });
      }

      final shapes = <_StateShape>[];
      for (final feat in features) {
        final name = feat['properties']?['NAME_1'] as String? ?? '';
        final data = lookup[name.toLowerCase()];
        shapes.add(
          _StateShape(
            name: name,
            polygons: _extractPolygons(feat['geometry']),
            violations: (data?['violations'] as int?) ?? 0,
            scans: (data?['scans'] as int?) ?? 0,
            compliant: (data?['compliant'] as int?) ?? 0,
            minLon: minLon,
            maxLon: maxLon,
            minLat: minLat,
            maxLat: maxLat,
          ),
        );
      }
      // Pre-bake paths at a common size so first hover is instant
      // (actual sizing happens in paint, this just warms the cache structure)
      setState(() {
        _shapes = shapes;
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  void _iterCoords(
    Map<String, dynamic> geom,
    void Function(double, double) fn,
  ) {
    final type = geom['type'] as String;
    final coords = geom['coordinates'];
    if (type == 'Polygon') {
      for (final ring in coords as List) {
        for (final pt in ring as List) {
          fn((pt[0] as num).toDouble(), (pt[1] as num).toDouble());
        }
      }
    } else if (type == 'MultiPolygon') {
      for (final poly in coords as List) {
        for (final ring in poly as List) {
          for (final pt in ring as List) {
            fn((pt[0] as num).toDouble(), (pt[1] as num).toDouble());
          }
        }
      }
    }
  }

  List<List<List<double>>> _extractPolygons(Map<String, dynamic> geom) {
    final type = geom['type'] as String;
    final coords = geom['coordinates'];
    final result = <List<List<double>>>[];
    if (type == 'Polygon') {
      final outer = coords[0] as List;
      result.add(
        outer
            .map((p) => [(p[0] as num).toDouble(), (p[1] as num).toDouble()])
            .toList(),
      );
    } else if (type == 'MultiPolygon') {
      for (final poly in coords as List) {
        final outer = poly[0] as List;
        result.add(
          outer
              .map((p) => [(p[0] as num).toDouble(), (p[1] as num).toDouble()])
              .toList(),
        );
      }
    }
    return result;
  }

  void _onHover(PointerEvent e, Size size) {
    final pos = e.localPosition;
    int? found;
    final current = _hover.value;

    // Fast-path: 99% of the time, mouse is in the SAME state.
    // Checking current first skips 34 complex polygon ray-casts!
    if (current.idx != null && _shapes[current.idx!].hitTest(pos, size)) {
      found = current.idx;
    } else {
      for (int i = 0; i < _shapes.length; i++) {
        if (_shapes[i].hitTest(pos, size)) {
          found = i;
          break;
        }
      }
    }

    // Only trigger heavy DOM/Canvas layout rebuilding if the state CHANGED,
    // or if the mouse moved more than 20 pixels (debounces 60fps tooltips).
    if (current.idx != found) {
      _hover.value = (idx: found, pos: pos);
    } else if (found != null) {
      final dx = (pos.dx - current.pos.dx).abs();
      final dy = (pos.dy - current.pos.dy).abs();
      if (dx > 20 || dy > 20) {
        _hover.value = (idx: found, pos: pos);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    if (_loading) return const Center(child: CircularProgressIndicator());

    return LayoutBuilder(
      builder: (ctx, constraints) {
        final size = Size(constraints.maxWidth, constraints.maxHeight);
        return RepaintBoundary(
          // isolate this subtree from parent repaints
          child: MouseRegion(
            onExit: (_) => _hover.value = (idx: null, pos: Offset.zero),
            child: Listener(
              behavior: HitTestBehavior.opaque,
              onPointerHover: (e) => _onHover(e, size),
              child: Stack(
                children: [
                  // ── Static Canvas layer — NEVER repaints, caches map ──────
                  RepaintBoundary(
                    child: CustomPaint(
                      size: size,
                      painter: _IndiaStaticPainter(
                        shapes: _shapes,
                        isDark: isDark,
                      ),
                    ),
                  ),
                  // ── Hover Canvas layer — incredibly fast, draws 1 state ──────
                  CustomPaint(
                    size: size,
                    painter: _IndiaHoverPainter(
                      shapes: _shapes,
                      hoverNotifier: _hover,
                      isDark: isDark,
                    ),
                  ),
                  // ── Legend — static, never repaints ──────────────────────
                  Positioned(bottom: 8, left: 8, child: _buildLegend(isDark)),
                  // ── Tooltip — rebuilds only when notifier changes ─────────
                  ValueListenableBuilder<_HoverState>(
                    valueListenable: _hover,
                    builder: (_, hover, __) {
                      if (hover.idx == null) return const SizedBox.shrink();
                      final shape = _shapes[hover.idx!];
                      return Positioned(
                        left: (hover.pos.dx + 14).clamp(0.0, size.width - 180),
                        top: (hover.pos.dy - 100).clamp(0.0, size.height - 130),
                        child: _buildTooltip(shape, isDark),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildLegend(bool isDark) {
    final items = [
      (_StateShape._colorForViolations(0), '0 violations'),
      (_StateShape._colorForViolations(5), '1–8'),
      (_StateShape._colorForViolations(12), '9–15'),
      (_StateShape._colorForViolations(20), '16–22'),
      (_StateShape._colorForViolations(30), '23+'),
    ];
    final bg = isDark ? Colors.black54 : Colors.white70;
    final fg = isDark ? Colors.white : Colors.black87;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            'Violations',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              color: fg,
            ),
          ),
          const SizedBox(height: 4),
          ...items.map(
            (e) => Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(width: 14, height: 10, color: e.$1),
                const SizedBox(width: 4),
                Text(e.$2, style: TextStyle(fontSize: 9, color: fg)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTooltip(_StateShape shape, bool isDark) {
    final bg = isDark ? const Color(0xFF1E1E2E) : Colors.white;
    final fg = isDark ? Colors.white : Colors.black87;
    final rate = shape.scans > 0
        ? (shape.violations / shape.scans * 100).toStringAsFixed(1)
        : '0.0';
    return Material(
      color: Colors.transparent,
      child: Container(
        width: 170,
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: _StateShape._colorForViolations(shape.violations),
            width: 1.5,
          ),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              shape.name,
              style: TextStyle(
                color: fg,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const Divider(height: 10),
            _ttRow('📦 Scans', '${shape.scans}', fg),
            _ttRow('⚠️ Violations', '${shape.violations}', Colors.orangeAccent),
            _ttRow('✅ Compliant', '${shape.compliant}', Colors.greenAccent),
            _ttRow('📊 Violation Rate', '$rate%', fg),
          ],
        ),
      ),
    );
  }

  Widget _ttRow(String label, String val, Color valColor) => Padding(
    padding: const EdgeInsets.symmetric(vertical: 1),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(fontSize: 10, color: Colors.grey)),
        Text(
          val,
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: valColor,
          ),
        ),
      ],
    ),
  );
}

// ─── Data model ───────────────────────────────────────────────────────────────
class _StateShape {
  final String name;
  final List<List<List<double>>> polygons;
  final int violations, scans, compliant;
  final double minLon, maxLon, minLat, maxLat;

  // Pre-baked projected Offsets, keyed by size
  final Map<Size, List<List<Offset>>> _cache = {};
  // Pre-baked Path to eliminate CPU lag on mouse hover
  final Map<Size, Path> _pathCache = {};

  _StateShape({
    required this.name,
    required this.polygons,
    required this.violations,
    required this.scans,
    required this.compliant,
    required this.minLon,
    required this.maxLon,
    required this.minLat,
    required this.maxLat,
  });

  List<List<Offset>> project(Size size) => _cache.putIfAbsent(
    size,
    () => polygons
        .map((ring) => ring.map((pt) => _proj(pt[0], pt[1], size)).toList())
        .toList(),
  );

  Path getPath(Size size) {
    if (_pathCache.containsKey(size)) return _pathCache[size]!;
    final path = Path();
    for (final ring in project(size)) {
      if (ring.isEmpty) continue;
      path.moveTo(ring[0].dx, ring[0].dy);
      for (int p = 1; p < ring.length; p++) path.lineTo(ring[p].dx, ring[p].dy);
      path.close();
    }
    _pathCache[size] = path;
    return path;
  }

  Offset _proj(double lon, double lat, Size size) {
    const pad = 0.05;
    final lonSpan = maxLon - minLon;
    final latSpan = maxLat - minLat;
    final x =
        ((lon - minLon + lonSpan * pad) / (lonSpan * (1 + pad * 2))) *
        size.width;
    final y =
        (1 - (lat - minLat + latSpan * pad) / (latSpan * (1 + pad * 2))) *
        size.height;
    return Offset(x, y);
  }

  bool hitTest(Offset pos, Size size) {
    final path = getPath(size);
    // 1. Lightning fast bounding box check
    if (!path.getBounds().contains(pos)) return false;
    // 2. Native C++ Skia path containment check
    return path.contains(pos);
  }

  static Color _colorForViolations(int v) {
    if (v == 0) return const Color(0xFF1a9850);
    if (v <= 8) return const Color(0xFF66bd63);
    if (v <= 15) return const Color(0xFFfee08b);
    if (v <= 22) return const Color(0xFFf46d43);
    return const Color(0xFFd73027);
  }

  Color get fillColor => _colorForViolations(violations);
}

// ─── CustomPainter — repaint driven by ValueNotifier, not setState ────────────
class _IndiaStaticPainter extends CustomPainter {
  final List<_StateShape> shapes;
  final bool isDark;

  _IndiaStaticPainter({required this.shapes, required this.isDark});

  @override
  void paint(Canvas canvas, Size size) {
    final strokeNormal = isDark ? Colors.white24 : Colors.black26;

    for (int i = 0; i < shapes.length; i++) {
      final shape = shapes[i];
      final path = shape.getPath(size);

      canvas.drawPath(
        path,
        Paint()
          ..color = shape.fillColor.withAlpha(175)
          ..style = PaintingStyle.fill,
      );

      canvas.drawPath(
        path,
        Paint()
          ..color = strokeNormal
          ..style = PaintingStyle.stroke
          ..strokeWidth = 0.5,
      );
    }
  }

  @override
  bool shouldRepaint(covariant _IndiaStaticPainter oldDelegate) =>
      oldDelegate.isDark != isDark;
}

class _IndiaHoverPainter extends CustomPainter {
  final List<_StateShape> shapes;
  final ValueNotifier<_HoverState> hoverNotifier;
  final bool isDark;

  _IndiaHoverPainter({
    required this.shapes,
    required this.hoverNotifier,
    required this.isDark,
  }) : super(repaint: hoverNotifier);

  @override
  void paint(Canvas canvas, Size size) {
    final hovered = hoverNotifier.value.idx;
    if (hovered == null || hovered < 0 || hovered >= shapes.length) return;

    final shape = shapes[hovered];
    final path = shape.getPath(size);
    final strokeHover = isDark ? Colors.white : Colors.black87;

    canvas.drawPath(
      path,
      Paint()
        ..color = shape.fillColor.withAlpha(230)
        ..style = PaintingStyle.fill,
    );

    canvas.drawPath(
      path,
      Paint()
        ..color = strokeHover
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.8,
    );
  }

  @override
  bool shouldRepaint(covariant _IndiaHoverPainter oldDelegate) =>
      oldDelegate.isDark != isDark;
}

class _PendingViolationsScreen extends StatefulWidget {
  @override
  State<_PendingViolationsScreen> createState() =>
      _PendingViolationsScreenState();
}

class _PendingViolationsScreenState extends State<_PendingViolationsScreen> {
  late Future<Map<String, dynamic>> _cases;
  String _query = '';
  String _statusFilter = 'All';
  final Set<String> _demoNotices = {};

  @override
  void initState() {
    super.initState();
    _cases = ApiService.getJson('/workspace/escalations?limit=100');
  }

  Future<void> _setStatus(int caseId, String status) async {
    final response = await ApiService.patchJson(
      '/workspace/escalations/$caseId',
      {'status': status},
    );
    if (!mounted) return;
    if (response['status'] == 'ERROR') {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            response['error']?.toString() ?? 'Could not update the case.',
          ),
        ),
      );
      return;
    }
    setState(
      () => _cases = ApiService.getJson('/workspace/escalations?limit=100'),
    );
  }

  Future<void> _openReport(Map<String, dynamic> item) async {
    final rawId = item['scan_id'];
    final scanId = rawId is int ? rawId : int.tryParse(rawId?.toString() ?? '');
    if (item['sample'] == true || scanId == null) {
      ReportViewer.showPdfDialog(
        context: context,
        reportId: item['id']?.toString() ?? 'DEMO-REPORT',
        product: item['product']?.toString() ?? 'Sample product',
        findingsOrNotes:
            '${item['violation'] ?? 'Potential label issue'}\n\nIllustrative screening report for demonstration only. This is not an official finding or enforcement document.',
        noFlagsDetected: false,
      );
      return;
    }
    final report = await ApiService.createComplianceReport(scanId);
    if (!mounted) return;
    final downloadUrl = report['download_url']?.toString();
    if (report['status'] == 'ERROR' || downloadUrl == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            report['error']?.toString() ?? 'Could not open the PDF report.',
          ),
        ),
      );
      return;
    }
    ReportViewer.showStoredPdfDialog(
      context: context,
      reportCode: report['report_code']?.toString() ?? 'TLR-$scanId',
      pdfBytes: ApiService.getBytes(downloadUrl),
    );
  }

  Future<void> _issueDemoNotice(Map<String, dynamic> item) async {
    final noticeKey =
        item['id']?.toString() ?? item['scan_id']?.toString() ?? 'case';
    final owner = TextEditingController(
      text: item['business_owner']?.toString() ?? 'Business owner',
    );
    final details = TextEditingController(
      text:
          item['violation']?.toString() ??
          'Potential non-compliance identified during screening',
    );
    final issued = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Issue demo notice'),
        content: SizedBox(
          width: 460,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Preview a notice for the listed business owner. This demo does not send an official or external notice.',
              ),
              const SizedBox(height: 14),
              TextField(
                controller: owner,
                decoration: const InputDecoration(
                  labelText: 'Business owner / manufacturer',
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: details,
                minLines: 2,
                maxLines: 4,
                decoration: const InputDecoration(labelText: 'Finding'),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(dialogContext, true),
            child: const Text('Issue demo notice'),
          ),
        ],
      ),
    );
    owner.dispose();
    details.dispose();
    if (issued == true && mounted) setState(() => _demoNotices.add(noticeKey));
  }

  List<Map<String, dynamic>> _demoCases() => mockViolations
      .take(10)
      .map(
        (item) => {
          ...item,
          'sample': true,
          'category': item['product'] == 'AquaPure 1L'
              ? 'Food & Beverages'
              : 'General Packaged Commodity',
          'scan_id': 'DEMO-${item['id']}',
          'note': 'Illustrative sample case only. No government notice, penalty or enforcement record.',
          'evidence': [
            'Package-side photo (sample)',
            'Rule reference: ${item['violation']}',
          ],
        },
      )
      .toList();

  bool _matches(Map<String, dynamic> item) {
    final needle = _query.trim().toLowerCase();
    final status = item['status']?.toString() ?? '';
    if (_statusFilter != 'All' &&
        !status.toLowerCase().contains(_statusFilter.toLowerCase()))
      return false;
    if (needle.isEmpty) return true;
    return [
          item['id'],
          item['product'],
          item['category'],
          item['violation'],
          item['inspector'],
        ]
        .map((value) => value?.toString().toLowerCase() ?? '')
        .any((value) => value.contains(needle));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Violation reports',
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.w800,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          'Live inspector escalations plus clearly marked illustrative cases for the local demo. No government notice, fine, or external message is sent.',
          style: TextStyle(color: textMuted),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextField(
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search),
                  labelText: 'Search cases, products or rules',
                ),
                onChanged: (value) => setState(() => _query = value),
              ),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: 150,
              child: DropdownButtonFormField<String>(
                value: _statusFilter,
                decoration: const InputDecoration(labelText: 'Status'),
                items: const ['All', 'Pending', 'Review', 'Resolved']
                    .map(
                      (value) =>
                          DropdownMenuItem(value: value, child: Text(value)),
                    )
                    .toList(),
                onChanged: (value) =>
                    setState(() => _statusFilter = value ?? 'All'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: FutureBuilder<Map<String, dynamic>>(
            future: _cases,
            builder: (context, snapshot) {
              final liveItems = (snapshot.data?['items'] as List? ?? const [])
                  .map((raw) => Map<String, dynamic>.from(raw as Map))
                  .toList();
              final allItems = [
                ..._demoCases(),
                ...liveItems,
              ].where(_matches).toList();
              return ListView(
                children: [
                  if (snapshot.connectionState == ConnectionState.waiting)
                    const LinearProgressIndicator(),
                  if (snapshot.data?['status'] == 'ERROR')
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Text(
                        snapshot.data?['error']?.toString() ?? 'Live cases could not be loaded; sample cases remain available.',
                        style: TextStyle(color: theme.colorScheme.error),
                      ),
                    ),
                  if (allItems.isEmpty)
                    const Padding(
                      padding: EdgeInsets.all(24),
                      child: Center(child: Text('No cases match this filter.')),
                    ),
                  ...allItems.map(
                    (violation) =>
                        _buildCaseCard(context, violation, theme, textMuted),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildCaseCard(
    BuildContext context,
    Map<String, dynamic> violation,
    ThemeData theme,
    Color textMuted,
  ) {
    final sample = violation['sample'] == true;
    final evidence =
        (violation['evidence'] as List?)
            ?.map((item) => item.toString())
            .toList() ??
        const <String>[];
    return Card(
      color: theme.cardColor,
      margin: const EdgeInsets.only(bottom: 14),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Text(
                    '${violation['product'] ?? violation['category'] ?? 'Product'}',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                Chip(
                  label: Text(sample ? 'DEMO SAMPLE' : 'LIVE CASE'),
                  backgroundColor: sample
                      ? Colors.blue.withValues(alpha: .12)
                      : Colors.orange.withValues(alpha: .14),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${violation['category'] ?? 'Uncategorised'} · scan ${violation['scan_id'] ?? 'n/a'} · case ${violation['id'] ?? 'n/a'}',
              style: theme.textTheme.bodySmall?.copyWith(color: textMuted),
            ),
            const SizedBox(height: 12),
            Text(
              violation['violation']?.toString() ?? 'Review finding',
              style: theme.textTheme.titleMedium?.copyWith(
                color: Colors.deepOrange,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Status: ${violation['status'] ?? 'pending'}',
              style: theme.textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            if (violation['inspector'] != null)
              Text(
                'Reported by: ${violation['inspector']}',
                style: theme.textTheme.bodySmall?.copyWith(color: textMuted),
              ),
            if (violation['note'] != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  violation['note'].toString(),
                  style: theme.textTheme.bodySmall?.copyWith(color: textMuted),
                ),
              ),
            if (evidence.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text('Evidence attached', style: theme.textTheme.labelLarge),
              Wrap(
                spacing: 6,
                runSpacing: 6,
                children: evidence
                    .map(
                      (item) => Chip(
                        avatar: const Icon(Icons.attachment, size: 15),
                        label: Text(item),
                      ),
                    )
                    .toList(),
              ),
            ],
            const SizedBox(height: 12),
            Wrap(
              spacing: 10,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: () => _openReport(violation),
                  icon: const Icon(Icons.picture_as_pdf_outlined),
                  label: const Text('Open PDF report'),
                ),
                if (violation['status']?.toString().toLowerCase().contains(
                          'compliant',
                        ) !=
                        true &&
                    violation['status']?.toString().toLowerCase() != 'resolved')
                  FilledButton.icon(
                    onPressed:
                        _demoNotices.contains(violation['id']?.toString())
                        ? null
                        : () => _issueDemoNotice(violation),
                    icon: const Icon(Icons.forward_to_inbox_outlined),
                    label: Text(
                      _demoNotices.contains(violation['id']?.toString())
                          ? 'Demo notice issued'
                          : 'Issue notice to owner',
                    ),
                  ),
                if (!sample && violation['id'] is int) ...[
                  OutlinedButton.icon(
                    onPressed: () =>
                        _setStatus(violation['id'] as int, 'in_review'),
                    icon: const Icon(Icons.rate_review),
                    label: const Text('Mark in review'),
                  ),
                  OutlinedButton.icon(
                    onPressed: () =>
                        _setStatus(violation['id'] as int, 'resolved'),
                    icon: const Icon(Icons.check),
                    label: const Text('Mark resolved'),
                  ),
                ],
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _RulesScreen extends StatefulWidget {
  @override
  State<_RulesScreen> createState() => _RulesScreenState();
}

class _RulesScreenState extends State<_RulesScreen> {
  late Future<Map<String, dynamic>> _data;
  String _category = 'All categories';

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _data = ApiService.getJson('/workspace/admin/rules');

  Future<void> _toggle(Map<String, dynamic> rule, bool value) async {
    try {
      await ApiService.patchJson('/workspace/admin/rules/${rule['id']}', {
        'is_mandatory': value,
      });
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted)
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Rule update failed: $error')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError)
          return Center(
            child: FilledButton.icon(
              onPressed: () => setState(_load),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry rules'),
            ),
          );
        final apiRules = (snapshot.data?['items'] as List? ?? const [])
            .map((raw) => Map<String, dynamic>.from(raw as Map))
            .toList();
        final rules = apiRules.isNotEmpty ? apiRules : _categoryRuleFallback();
        final categories = <String>{
          'All categories',
          ...rules.map(
            (rule) => rule['category']?.toString() ?? 'Uncategorised',
          ),
        }.toList()..sort();
        final visible = _category == 'All categories'
            ? rules
            : rules.where((rule) => rule['category'] == _category).toList();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Live rule catalogue',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(_load),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh rules',
                ),
              ],
            ),
            Text(
              '${rules.length} checks across ${categories.length - 1} product profiles. ${apiRules.isEmpty ? 'Showing the built-in demo catalogue while live rules are unavailable.' : 'Changes are recorded for review.'}',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: categories.contains(_category)
                  ? _category
                  : 'All categories',
              decoration: const InputDecoration(
                labelText: 'Filter by product profile',
              ),
              items: categories
                  .map(
                    (category) => DropdownMenuItem(
                      value: category,
                      child: Text(category),
                    ),
                  )
                  .toList(),
              onChanged: (value) =>
                  setState(() => _category = value ?? 'All categories'),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: visible.isEmpty
                  ? const Center(child: Text('No rules match this profile.'))
                  : ListView.separated(
                      itemCount: visible.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final rule = visible[index];
                        final mandatory = rule['is_mandatory'] == true;
                        return Card(
                          child: ListTile(
                            isThreeLine: true,
                            leading: CircleAvatar(
                              backgroundColor:
                                  (mandatory ? Colors.orange : Colors.blue)
                                      .withValues(alpha: .12),
                              child: Icon(
                                mandatory ? Icons.priority_high : Icons.tune,
                                color: mandatory ? Colors.orange : Colors.blue,
                              ),
                            ),
                            title: Text(
                              '${rule['tag']} · ${rule['category']}',
                              style: const TextStyle(
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                            subtitle: Text(
                              '${rule['legal_act_reference'] ?? 'Reference pending'}\n${rule['automated_scope'] ?? 'Evidence-aware presence check'}',
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            trailing: rule['id'] is int
                                ? Switch(
                                    value: mandatory,
                                    onChanged: (value) => _toggle(rule, value),
                                  )
                                : const Tooltip(
                                    message: 'Demo catalogue entry',
                                    child: Icon(Icons.info_outline),
                                  ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        );
      },
    );
  }

  List<Map<String, dynamic>> _categoryRuleFallback() {
    final extraFields = <String, List<String>>{
      'Food & Beverages': [
        'FSSAI_LICENSE',
        'BEST_BEFORE_DATE',
        'VEG_NON_VEG_LOGO',
        'INGREDIENTS',
      ],
      'Packaged Drinking Water': [
        'FSSAI_LICENSE',
        'BEST_BEFORE_DATE',
        'SOURCE_NAME',
      ],
      'Electronics & Appliances': [
        'BIS_MARK',
        'MODEL',
        'COUNTRY_OF_ORIGIN',
        'E_WASTE_INFO',
      ],
      'Electrical Cables & Accessories': ['BIS_MARK', 'MODEL'],
      'Cosmetics, Ointments & Pharma Goods': [
        'BATCH_CODE',
        'EXPIRY_DATE',
        'INGREDIENTS',
      ],
      'Personal Care Products': ['BATCH_CODE', 'EXPIRY_DATE', 'INGREDIENTS'],
      'Household Cleaning Products': [
        'BATCH_CODE',
        'HAZARD_WARNING',
        'INGREDIENTS',
      ],
      'Apparel & Textiles': ['SIZE', 'FIBRE_CONTENT', 'COUNTRY_OF_ORIGIN'],
      'Footwear & Leather Goods': ['SIZE', 'MATERIAL'],
      'Toys & Childcare Products': ['AGE_GROUP', 'HAZARD_WARNING'],
      'Medical Devices': [
        'MODEL',
        'SERIAL_NUMBER',
        'LICENSE_NO',
        'STERILE_STATUS',
      ],
      'Automotive Components & Lubricants': ['MODEL', 'BATCH_CODE'],
      'Tobacco & Nicotine Products': ['HEALTH_WARNING', 'BATCH_CODE'],
      'Stationery & School Supplies': ['COUNTRY_OF_ORIGIN'],
      'Agricultural Inputs': ['BATCH_CODE', 'LICENSE_NO', 'EXPIRY_DATE'],
    };
    return productCategories.expand((category) {
      final fields = {
        ...fieldsForProductCategory(category)
            .map((field) => field.toUpperCase()),
        ...(extraFields[category] ?? const <String>[]),
      };
      return fields.map(
        (tag) => <String, dynamic>{
          'category': category,
          'tag': tag,
          'is_mandatory': !{
            'UNIT_SALE_PRICE',
            'BIS_MARK',
            'COUNTRY_OF_ORIGIN',
            'E_WASTE_INFO',
            'SOURCE_NAME',
            'MATERIAL',
            'SERIAL_NUMBER',
            'STERILE_STATUS',
            'EXPIRY_DATE',
          }.contains(tag),
          'legal_act_reference': tag.startsWith('FSSAI')
              ? 'Food labelling and display requirements (verify current applicability)'
              : 'Legal Metrology and applicable sector-specific requirements (verify current applicability)',
          'automated_scope': 'Demo screening check: confirms declaration evidence only. Applicability and exemptions require review.',
        },
      );
    }).toList();
  }
}

class _LegacyRulesScreen extends StatefulWidget {
  @override
  __RulesScreenState createState() => __RulesScreenState();
}

class __RulesScreenState extends State<_RulesScreen> {
  final List<Map<String, String>> _rulesList = [
    {
      'code': 'Example 1',
      'title': 'Package identity',
      'description': 'Prototype OCR check for manufacturer, packer or importer details and the product name. Exact wording and applicability need current rule review.',
      'penalty': 'Not evaluated',
    },
    {
      'code': 'Example 2',
      'title': 'Quantity and price declarations',
      'description': 'Prototype OCR looks for a net quantity and retail price. Unit sale price and exemptions depend on package details that this demo does not evaluate.',
      'penalty': 'Not evaluated',
    },
    {
      'code': 'Example 3',
      'title': 'Dates and batch information',
      'description': 'Prototype OCR looks for date and batch text. Which declarations apply varies by product and sector-specific requirements.',
      'penalty': 'Not evaluated',
    },
    {
      'code': 'Example 4',
      'title': 'Consumer contact details',
      'description': 'Prototype OCR looks for consumer-care contact text. OCR output does not confirm that the details are complete or usable.',
      'penalty': 'Not evaluated',
    },
    {
      'code': 'Example 5',
      'title': 'Category-specific information',
      'description': 'Food, cosmetics, medical devices and other products may have separate declarations. This small prototype catalogue is not a complete ruleset.',
      'penalty': 'Not evaluated',
    },
  ];

  void _showAddRuleDialog(BuildContext context) {
    final TextEditingController codeController = TextEditingController();
    final TextEditingController titleController = TextEditingController();
    final TextEditingController descController = TextEditingController();
    final TextEditingController penaltyController = TextEditingController();
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: theme.dialogBackgroundColor,
          title: Text(
            'Add Demo Catalogue Entry',
            style: TextStyle(
              color: theme.brightness == Brightness.dark
                  ? Colors.white
                  : Colors.black,
            ),
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: codeController,
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Example ID',
                    labelStyle: TextStyle(color: Colors.blueAccent),
                  ),
                ),
                SizedBox(height: 12),
                TextField(
                  controller: titleController,
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Example title',
                    labelStyle: TextStyle(color: Colors.blueAccent),
                  ),
                ),
                SizedBox(height: 12),
                TextField(
                  controller: descController,
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Description',
                    labelStyle: TextStyle(color: Colors.blueAccent),
                  ),
                ),
                SizedBox(height: 12),
                TextField(
                  controller: penaltyController,
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Example note (not a verified penalty)',
                    labelStyle: TextStyle(color: Colors.blueAccent),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(
                'Cancel',
                style: TextStyle(
                  color: theme.brightness == Brightness.dark
                      ? Colors.white70
                      : Colors.black87,
                ),
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
              ),
              onPressed: () {
                if (codeController.text.isNotEmpty &&
                    titleController.text.isNotEmpty) {
                  setState(() {
                    _rulesList.add({
                      'code': codeController.text,
                      'title': titleController.text,
                      'description': descController.text,
                      'penalty': penaltyController.text.isEmpty
                          ? 'Not specified'
                          : penaltyController.text,
                    });
                  });
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Added to this screen only. It was not saved to the backend.',
                      ),
                      backgroundColor: Colors.blueGrey,
                    ),
                  );
                }
              },
              child: Text(
                'Add demo entry',
                style: TextStyle(
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 12,
          runSpacing: 12,
          children: [
            Text(
              'Prototype Rule Catalogue',
              style: TextStyle(
                color: theme.brightness == Brightness.dark
                    ? Colors.white
                    : Colors.black,
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 12,
                ),
              ),
              onPressed: () => _showAddRuleDialog(context),
              icon: Icon(
                Icons.add,
                color: theme.brightness == Brightness.dark
                    ? Colors.white
                    : Colors.black,
              ),
              label: Text(
                'Add Demo Entry',
                style: TextStyle(
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'Example data only. Entries are not verified against current law and changes are not saved to the backend.',
          style: TextStyle(color: textMuted),
        ),
        SizedBox(height: 20),
        Expanded(
          child: ListView.builder(
            itemCount: _rulesList.length,
            itemBuilder: (context, index) {
              final rule = _rulesList[index];
              return Card(
                color: theme.cardColor,
                margin: const EdgeInsets.only(bottom: 16),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Wrap(
                        alignment: WrapAlignment.spaceBetween,
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          Text(
                            rule['code']!,
                            style: TextStyle(
                              color: Colors.blueAccent,
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            'Demo note: ${rule['penalty']}',
                            style: TextStyle(
                              color: Colors.orangeAccent,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 8),
                      Text(
                        rule['title']!,
                        style: TextStyle(
                          color: theme.brightness == Brightness.dark
                              ? Colors.white
                              : Colors.black,
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      SizedBox(height: 8),
                      Text(
                        rule['description']!,
                        style: TextStyle(
                          color: theme.brightness == Brightness.dark
                              ? Colors.white70
                              : Colors.black87,
                          fontSize: 14,
                          height: 1.4,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

class _ReportRepositoryScreen extends StatefulWidget {
  @override
  State<_ReportRepositoryScreen> createState() =>
      _ReportRepositoryScreenState();
}

class _ReportRepositoryScreenState extends State<_ReportRepositoryScreen> {
  late Future<Map<String, dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _data = ApiService.getJson('/reports?limit=100');

  Future<void> _open(Map<String, dynamic> report) async {
    final bytes = await ApiService.getBytes(
      report['download_url']?.toString() ?? '',
    );
    if (!mounted || bytes == null) return;
    ReportViewer.showStoredPdfDialog(
      context: context,
      reportCode: report['report_code']?.toString() ?? 'Report',
      pdfBytes: Future.value(bytes),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError)
          return Center(
            child: FilledButton.icon(
              onPressed: () => setState(_load),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry reports'),
            ),
          );
        final reports = snapshot.data?['items'] as List? ?? const [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Persisted compliance reports',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(_load),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh reports',
                ),
              ],
            ),
            Text(
              'Reports are generated from saved scan evidence and remain review documents, not enforcement notices.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            Expanded(
              child: reports.isEmpty
                  ? const Center(
                      child: Text('No reports have been generated yet.'),
                    )
                  : ListView.separated(
                      itemCount: reports.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (context, index) {
                        final report = Map<String, dynamic>.from(
                          reports[index] as Map,
                        );
                        return Card(
                          child: ListTile(
                            leading: const CircleAvatar(
                              child: Icon(Icons.picture_as_pdf_outlined),
                            ),
                            title: Text(
                              report['report_code']?.toString() ?? 'Report',
                            ),
                            subtitle: Text(
                              'Scan ${report['scan_id'] ?? '-'} · ${report['created_at'] ?? 'Date unavailable'}',
                            ),
                            trailing: FilledButton.icon(
                              onPressed: () => _open(report),
                              icon: const Icon(Icons.visibility_outlined),
                              label: const Text('Open'),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        );
      },
    );
  }
}

class _LegacyReportRepositoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isMobile = MediaQuery.of(context).size.width < 600;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Sample Report Repository',
          style: TextStyle(
            color: theme.brightness == Brightness.dark
                ? Colors.white
                : Colors.black,
            fontSize: isMobile ? 22 : 28,
            fontWeight: FontWeight.bold,
          ),
        ),
        SizedBox(height: 16),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.separated(
              padding: const EdgeInsets.all(8),
              itemCount: mockViolations.length,
              separatorBuilder: (_, __) =>
                  Divider(color: theme.dividerColor, height: 1),
              itemBuilder: (context, index) {
                final v = mockViolations[index];
                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 4,
                  ),
                  leading: CircleAvatar(
                    backgroundColor: Colors.redAccent.withValues(alpha: 0.15),
                    child: Icon(
                      Icons.picture_as_pdf,
                      color: Colors.redAccent,
                      size: 20,
                    ),
                  ),
                  title: Text(
                    '${v['product']}',
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white
                          : Colors.black,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: 2),
                      Text(
                        'ID: ${v['id']}  •  ${v['date'] ?? 'Recent'}',
                        style: TextStyle(
                          color: theme.brightness == Brightness.dark
                              ? Colors.white70
                              : Colors.black54,
                          fontSize: 12,
                        ),
                      ),
                      SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color:
                              (v['status'] == 'Pending Review'
                                      ? Colors.orange
                                      : Colors.blue)
                                  .withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          v['status'] ?? 'Logged',
                          style: TextStyle(
                            color: v['status'] == 'Pending Review'
                                ? Colors.orangeAccent
                                : Colors.blueAccent,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  trailing: IconButton(
                    icon: Icon(Icons.visibility, color: Colors.blueAccent),
                    onPressed: () => ReportViewer.showPdfDialog(
                      context: context,
                      reportId: v['id'],
                      product: v['product'],
                      findingsOrNotes: 'Sample: ${v["violation"]}',
                      noFlagsDetected: false,
                    ),
                    tooltip: 'View PDF Report',
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

class _AuditLogsScreen extends StatefulWidget {
  @override
  State<_AuditLogsScreen> createState() => _AuditLogsScreenState();
}

class _AuditLogsScreenState extends State<_AuditLogsScreen> {
  late Future<Map<String, dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _data = ApiService.getJson('/workspace/audit?limit=200');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError)
          return Center(
            child: FilledButton.icon(
              onPressed: () => setState(_load),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry audit log'),
            ),
          );
        final logs = snapshot.data?['items'] as List? ?? const [];
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    'Audit trail',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => setState(_load),
                  icon: const Icon(Icons.refresh),
                  tooltip: 'Refresh audit trail',
                ),
              ],
            ),
            Text(
              'Persisted account, scan, rule and workflow events visible to this administrator.',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            Expanded(
              child: logs.isEmpty
                  ? const Center(child: Text('No audit events recorded yet.'))
                  : ListView.separated(
                      itemCount: logs.length,
                      separatorBuilder: (_, __) => const Divider(height: 1),
                      itemBuilder: (context, index) {
                        final log = Map<String, dynamic>.from(
                          logs[index] as Map,
                        );
                        return ListTile(
                          leading: const Icon(Icons.history_rounded),
                          title: Text(
                            log['action']?.toString() ?? 'Event',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                          subtitle: Text(
                            '${log['entity_type'] ?? 'record'} · ${log['entity_id'] ?? '-'}\n${log['created_at'] ?? 'Date unavailable'}',
                          ),
                        );
                      },
                    ),
            ),
          ],
        );
      },
    );
  }
}

class _LegacyAuditLogsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Sample Audit Log',
          style: TextStyle(
            color: theme.brightness == Brightness.dark
                ? Colors.white
                : Colors.black,
            fontSize: 28,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 6),
        Text(
          'Static demo activity; no user account, enforcement record or system event is connected.',
          style: TextStyle(
            color: theme.brightness == Brightness.dark
                ? Colors.white70
                : Colors.black87,
          ),
        ),
        SizedBox(height: 8),
        Text(
          'Static demonstration log; this screen is not connected to authentication or an audit ledger.',
          style: TextStyle(
            color: theme.brightness == Brightness.dark
                ? Colors.white70
                : Colors.black87,
          ),
        ),
        SizedBox(height: 24),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: auditLogs.length,
              separatorBuilder: (context, index) => Divider(
                color: theme.brightness == Brightness.dark
                    ? Colors.white70
                    : Colors.black87,
              ),
              itemBuilder: (context, index) {
                final log = auditLogs[index];
                return ListTile(
                  leading: Icon(
                    log['type'] == 'Authentication'
                        ? Icons.security
                        : Icons.radar,
                    color: Colors.orangeAccent,
                  ),
                  title: Text(
                    log['action']!,
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white
                          : Colors.black,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  subtitle: Text(
                    'Category: ${log['type']} | Timestamp: ${log['timestamp']}',
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark
                          ? Colors.white70
                          : Colors.black87,
                      fontSize: 13,
                    ),
                  ),
                  trailing: Text(
                    log['status']!,
                    style: TextStyle(
                      color: Colors.blueAccent,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

class _ProfileScreen extends StatefulWidget {
  @override
  State<_ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<_ProfileScreen> {
  late Future<Map<String, dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _data = ApiService.getJson('/auth/me');

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting)
          return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError)
          return Center(
            child: FilledButton.icon(
              onPressed: () => setState(_load),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry profile'),
            ),
          );
        final user = Map<String, dynamic>.from(
          (snapshot.data?['user'] as Map?) ?? const {},
        );
        return ListView(
          children: [
            Text(
              'Administrator profile',
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(22),
                child: Row(
                  children: [
                    CircleAvatar(
                      radius: 32,
                      child: Text(
                        (user['full_name']?.toString() ?? 'A')
                            .substring(0, 1)
                            .toUpperCase(),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            user['full_name']?.toString() ?? 'Administrator',
                            style: theme.textTheme.titleLarge?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          Text(
                            user['email']?.toString() ?? '',
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Chip(
                            label: Text(
                              (user['role']?.toString() ?? 'admin')
                                  .toUpperCase(),
                            ),
                            avatar: const Icon(
                              Icons.verified_user_outlined,
                              size: 16,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Card(
              child: Column(
                children: [
                  _profileLine(
                    context,
                    Icons.business_outlined,
                    'Organization',
                    user['organization_name']?.toString() ?? 'Not provided',
                  ),
                  const Divider(height: 1),
                  _profileLine(
                    context,
                    Icons.shield_outlined,
                    'Access',
                    'Administrator controls enabled',
                  ),
                  const Divider(height: 1),
                  _profileLine(
                    context,
                    Icons.lock_outline,
                    'Session',
                    'Authenticated through the True Label API',
                  ),
                ],
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _profileLine(
    BuildContext context,
    IconData icon,
    String label,
    String value,
  ) => ListTile(
    leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
    title: Text(label),
    subtitle: Text(value),
  );
}

class _LegacyProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Center(
      child: SingleChildScrollView(
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 60,
                backgroundColor: theme.brightness == Brightness.dark
                    ? Colors.blueAccent.withValues(alpha: 0.2)
                    : Colors.blue.shade100,
                child: Icon(
                  Icons.admin_panel_settings,
                  size: 60,
                  color: theme.brightness == Brightness.dark
                      ? Colors.blueAccent
                      : Colors.blue.shade800,
                ),
              ),
              SizedBox(height: 24),
              Text(
                'Sample Administrator Profile',
                style: theme.textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              SizedBox(height: 8),
              Text(
                'Demo only • no authentication is connected',
                style: theme.textTheme.titleMedium?.copyWith(
                  color: Colors.grey,
                ),
              ),
              SizedBox(height: 32),
              Card(
                color: theme.cardColor,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    children: [
                      _buildProfileItem(
                        Icons.email,
                        'Email',
                        'Not connected',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.phone,
                        'Phone',
                        'Not connected',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.location_on,
                        'Jurisdiction',
                        'Sample only',
                        theme,
                      ),
                      Divider(height: 32),
                      _buildProfileItem(
                        Icons.security,
                        'Access Level',
                        'Not authenticated',
                        theme,
                      ),
                    ],
                  ),
                ),
              ),
              SizedBox(height: 32),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30),
                  ),
                ),
                onPressed: null,
                icon: Icon(
                  Icons.edit,
                  color: theme.brightness == Brightness.dark
                      ? Colors.white
                      : Colors.black,
                ),
                label: Text(
                  'Profile editing not connected',
                  style: TextStyle(
                    color: theme.brightness == Brightness.dark
                        ? Colors.white
                        : Colors.black,
                    fontSize: 16,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileItem(
    IconData icon,
    String title,
    String value,
    ThemeData theme,
  ) {
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Row(
      children: [
        Icon(icon, color: Colors.blueAccent, size: 28),
        SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey),
              ),
              SizedBox(height: 4),
              Text(
                value,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _LogoutScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark
        ? Colors.white
        : Colors.black;
    final textMuted = theme.brightness == Brightness.dark
        ? Colors.white70
        : Colors.black87;
    return Center(
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
        onPressed: () async {
          await ApiService.signOut();
          if (context.mounted) {
            Navigator.of(context)
                .pushNamedAndRemoveUntil('/login', (route) => false);
          }
        },
        child: Text(
          'Confirm Logout',
          style: TextStyle(
            color: theme.brightness == Brightness.dark
                ? Colors.white
                : Colors.black,
          ),
        ),
      ),
    );
  }
}
