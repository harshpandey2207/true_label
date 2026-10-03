import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'dart:typed_data';
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import 'package:sidebarx/sidebarx.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:printing/printing.dart';
import '../../core/report_generator.dart';
import '../../core/report_viewer.dart';
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
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return SidebarX(
      controller: _controller,
      theme: SidebarXTheme(
        decoration: BoxDecoration(color: Color(0xFF1E1E1E)),
        textStyle: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
        selectedTextStyle: TextStyle(color: Colors.blueAccent),
        iconTheme: IconThemeData(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
        selectedIconTheme: IconThemeData(color: Colors.blueAccent),
      ),
      extendedTheme: SidebarXTheme(
        width: 260,
        decoration: BoxDecoration(color: Color(0xFF1E1E1E)),
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
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    final isMobile = MediaQuery.of(context).size.width < 600;

    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      backgroundColor: theme.scaffoldBackgroundColor,
      appBar: AppBar(
        backgroundColor: theme.cardColor,
        title: Text('Admin Portal', style: theme.textTheme.titleLarge?.copyWith(fontSize: 18) ?? TextStyle(fontSize: 18)),
        iconTheme: theme.iconTheme,
        automaticallyImplyLeading: isMobile,
        actions: [
          IconButton(
            icon: Icon(themeProvider.isDarkMode ? Icons.light_mode : Icons.dark_mode),
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
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return AnimatedBuilder(
      animation: controller,
      builder: (context, child) {
        switch (controller.selectedIndex) {
          case 0: return _OverviewScreen();
          case 1: return _PendingViolationsScreen();
          case 2: return _RulesScreen();
          case 3: return _ReportRepositoryScreen();
          case 4: return _AuditLogsScreen();
          case 5: return _ProfileScreen();
          case 6: return _LogoutScreen();
          default: return Center(child: Text('Not found', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)));
        }
      },
    );
  }
}

class _OverviewScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    double compliancePercentage = (totalCompliant / totalScans) * 100;
    double violationPercentage = 100 - compliancePercentage;

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Sample Metrics & Heatmap', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
          const SizedBox(height: 6),
          Text('Static demonstration data; not live government records or enforcement metrics.', style: TextStyle(color: textMuted)),
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
                      Text('Sample screening counts', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                      SizedBox(height: 6),
                      Text('$totalCompliant Compliant', style: TextStyle(color: Colors.greenAccent, fontSize: 13, fontWeight: FontWeight.bold)),
                      SizedBox(height: 4),
                      Text('$totalViolations Non-Compliant', style: TextStyle(color: Colors.redAccent, fontSize: 13, fontWeight: FontWeight.bold)),
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
                              PieChartSectionData(color: Colors.greenAccent, value: compliancePercentage, title: '', radius: 8),
                              PieChartSectionData(color: Colors.redAccent, value: violationPercentage, title: '', radius: 8),
                            ],
                          ),
                        ),
                        Text(
                          '${compliancePercentage.toStringAsFixed(0)}%',
                          style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
          SizedBox(height: 12),

          _buildStatCard(
            title: 'Penalty estimate',
            value: 'Not calculated',
            subtitle: 'The prototype has no penalty calculation or payment service',
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
                  Text('Violations Over Time (Last 7 Days)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 18)),
                  SizedBox(height: 20),
                  SizedBox(
                    height: 200,
                    child: LineChart(
                      LineChartData(
                        gridData: FlGridData(
                          show: true,
                          drawVerticalLine: false,
                          getDrawingHorizontalLine: (value) => FlLine(color: Colors.white12, strokeWidth: 1),
                        ),
                        titlesData: FlTitlesData(
                          show: true,
                          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                          bottomTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 22,
                              interval: 1,
                              getTitlesWidget: (value, meta) {
                                final style = TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 12);
                                Widget text;
                                switch (value.toInt()) {
                                  case 0: text = Text('Mon', style: style); break;
                                  case 2: text = Text('Wed', style: style); break;
                                  case 4: text = Text('Fri', style: style); break;
                                  case 6: text = Text('Sun', style: style); break;
                                  default: text = Text('', style: style); break;
                                }
                                return SideTitleWidget(axisSide: meta.axisSide, child: text);
                              },
                            ),
                          ),
                          leftTitles: AxisTitles(
                            sideTitles: SideTitles(
                              showTitles: true,
                              reservedSize: 28,
                              interval: 1,
                              getTitlesWidget: (value, meta) {
                                return Text(value.toInt().toString(), style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 12));
                              },
                            ),
                          ),
                        ),
                        borderData: FlBorderData(
                          show: true,
                          border: Border(
                            bottom: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, width: 1),
                            left: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, width: 1),
                            right: BorderSide.none,
                            top: BorderSide.none,
                          ),
                        ),
                        minY: 0,
                        maxY: 6,
                        lineBarsData: [
                          LineChartBarData(
                            spots: [
                              FlSpot(0, 3), FlSpot(1, 1), FlSpot(2, 4), 
                              FlSpot(3, 2), FlSpot(4, 5), FlSpot(5, 3), FlSpot(6, 4)
                            ],
                            isCurved: true,
                            color: Colors.blueAccent,
                            barWidth: 4,
                            isStrokeCapRound: true,
                            belowBarData: BarAreaData(show: true, color: Colors.blueAccent.withValues(alpha: 0.3)),
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
                  Text('India State-wise Violation Heatmap', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 18, fontWeight: FontWeight.w600)),
                  Text('Hover over any state to see scan & violation details', style: TextStyle(color: Colors.grey, fontSize: 12)),
                  SizedBox(height: 16),
                  SizedBox(
                    height: 480,
                    child: InteractiveGeographicHeatmap(sharedData: regionalData),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard({required String title, required String value, required String subtitle, required IconData icon, required Color color, required ThemeData theme}) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Card(
      color: theme.cardColor,
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: color.withValues(alpha: 0.15), borderRadius: BorderRadius.circular(10)),
              child: Icon(icon, color: color, size: 28),
            ),
            SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(title, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 12)),
                  SizedBox(height: 4),
                  Text(value, style: TextStyle(color: color, fontSize: 22, fontWeight: FontWeight.bold)),
                  SizedBox(height: 2),
                  Text(subtitle, style: TextStyle(color: Colors.white38, fontSize: 11)),
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
  State<InteractiveGeographicHeatmap> createState() => _InteractiveGeographicHeatmapState();
}

class _InteractiveGeographicHeatmapState extends State<InteractiveGeographicHeatmap> {
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
      final raw = await rootBundle.loadString('assets/maps/india_states.geojson');
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
        shapes.add(_StateShape(
          name: name,
          polygons: _extractPolygons(feat['geometry']),
          violations: (data?['violations'] as int?) ?? 0,
          scans: (data?['scans'] as int?) ?? 0,
          compliant: (data?['compliant'] as int?) ?? 0,
          minLon: minLon, maxLon: maxLon,
          minLat: minLat, maxLat: maxLat,
        ));
      }
      // Pre-bake paths at a common size so first hover is instant
      // (actual sizing happens in paint, this just warms the cache structure)
      setState(() { _shapes = shapes; _loading = false; });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  void _iterCoords(Map<String, dynamic> geom, void Function(double, double) fn) {
    final type = geom['type'] as String;
    final coords = geom['coordinates'];
    if (type == 'Polygon') {
      for (final ring in coords as List) {
        for (final pt in ring as List) { fn((pt[0] as num).toDouble(), (pt[1] as num).toDouble()); }
      }
    } else if (type == 'MultiPolygon') {
      for (final poly in coords as List) {
        for (final ring in poly as List) {
          for (final pt in ring as List) { fn((pt[0] as num).toDouble(), (pt[1] as num).toDouble()); }
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
      result.add(outer.map((p) => [(p[0] as num).toDouble(), (p[1] as num).toDouble()]).toList());
    } else if (type == 'MultiPolygon') {
      for (final poly in coords as List) {
        final outer = poly[0] as List;
        result.add(outer.map((p) => [(p[0] as num).toDouble(), (p[1] as num).toDouble()]).toList());
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
        if (_shapes[i].hitTest(pos, size)) { found = i; break; }
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

    return LayoutBuilder(builder: (ctx, constraints) {
      final size = Size(constraints.maxWidth, constraints.maxHeight);
      return RepaintBoundary(               // isolate this subtree from parent repaints
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
                Positioned(
                  bottom: 8, left: 8,
                  child: _buildLegend(isDark),
                ),
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
    });
  }

  Widget _buildLegend(bool isDark) {
    final items = [
      (_StateShape._colorForViolations(0),  '0 violations'),
      (_StateShape._colorForViolations(5),  '1–8'),
      (_StateShape._colorForViolations(12), '9–15'),
      (_StateShape._colorForViolations(20), '16–22'),
      (_StateShape._colorForViolations(30), '23+'),
    ];
    final bg = isDark ? Colors.black54 : Colors.white70;
    final fg = isDark ? Colors.white : Colors.black87;
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(6)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text('Violations', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: fg)),
          const SizedBox(height: 4),
          ...items.map((e) => Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(width: 14, height: 10, color: e.$1),
              const SizedBox(width: 4),
              Text(e.$2, style: TextStyle(fontSize: 9, color: fg)),
            ],
          )),
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
          border: Border.all(color: _StateShape._colorForViolations(shape.violations), width: 1.5),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(shape.name, style: TextStyle(color: fg, fontWeight: FontWeight.bold, fontSize: 12)),
            const Divider(height: 10),
            _ttRow('📦 Scans',           '${shape.scans}',      fg),
            _ttRow('⚠️ Violations',       '${shape.violations}', Colors.orangeAccent),
            _ttRow('✅ Compliant',         '${shape.compliant}',  Colors.greenAccent),
            _ttRow('📊 Violation Rate',   '$rate%',              fg),
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
        Text(val,   style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: valColor)),
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
    required this.name, required this.polygons,
    required this.violations, required this.scans, required this.compliant,
    required this.minLon, required this.maxLon,
    required this.minLat, required this.maxLat,
  });

  List<List<Offset>> project(Size size) => _cache.putIfAbsent(size, () =>
    polygons.map((ring) => ring.map((pt) => _proj(pt[0], pt[1], size)).toList()).toList(),
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
    final x = ((lon - minLon + lonSpan * pad) / (lonSpan * (1 + pad * 2))) * size.width;
    final y = (1 - (lat - minLat + latSpan * pad) / (latSpan * (1 + pad * 2))) * size.height;
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
    if (v == 0)  return const Color(0xFF1a9850);
    if (v <= 8)  return const Color(0xFF66bd63);
    if (v <= 15) return const Color(0xFFfee08b);
    if (v <= 22) return const Color(0xFFf46d43);
    return       const Color(0xFFd73027);
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

      canvas.drawPath(path, Paint()
        ..color = shape.fillColor.withAlpha(175)
        ..style = PaintingStyle.fill);

      canvas.drawPath(path, Paint()
        ..color = strokeNormal
        ..style = PaintingStyle.stroke
        ..strokeWidth = 0.5);
    }
  }

  @override
  bool shouldRepaint(covariant _IndiaStaticPainter oldDelegate) => oldDelegate.isDark != isDark;
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

    canvas.drawPath(path, Paint()
      ..color = shape.fillColor.withAlpha(230)
      ..style = PaintingStyle.fill);

    canvas.drawPath(path, Paint()
      ..color = strokeHover
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.8);
  }

  @override
  bool shouldRepaint(covariant _IndiaHoverPainter oldDelegate) => oldDelegate.isDark != isDark;
}


class _PendingViolationsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Sample Violations Queue', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text('These rows are sample data; no notice or case action is connected.', style: TextStyle(color: textMuted)),
        SizedBox(height: 24),
        Expanded(
          child: ListView.builder(
            itemCount: mockViolations.length,
            itemBuilder: (context, index) {
              final violation = mockViolations[index];
              return Card(
                color: theme.cardColor,
                margin: const EdgeInsets.only(bottom: 16),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(child: Text(violation['product'], style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 22, fontWeight: FontWeight.bold))),
                          Text(violation['id'], style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                        ],
                      ),
                      SizedBox(height: 12),
                      Text('Violation: ${violation['violation']}', style: TextStyle(color: Colors.redAccent, fontSize: 18, fontWeight: FontWeight.bold)),
                      SizedBox(height: 20),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(vertical: 14)),
                          onPressed: () => _showNoticeDialog(context, violation['product']),
                          icon: Icon(Icons.send, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
                          label: Text('Preview notice workflow (demo)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        ),
                      ),
                      SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          style: OutlinedButton.styleFrom(side: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), padding: const EdgeInsets.symmetric(vertical: 14)),
                          onPressed: null,
                          child: Text('Case actions are not connected', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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

  void _showNoticeDialog(BuildContext context, String product) {
    final theme = Theme.of(context);
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: theme.dialogBackgroundColor,
        title: Text('Notice workflow demo', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
        content: Text(
          'This sample case is for $product. The app is not connected to a regulator or messaging service, so no notice can be issued or sent.',
          style: TextStyle(color: textMuted),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
          ),
        ],
      ),
    );
  }
}

class _RulesScreen extends StatefulWidget {
  @override
  __RulesScreenState createState() => __RulesScreenState();
}

class __RulesScreenState extends State<_RulesScreen> {
  final List<Map<String, String>> _rulesList = [
    {
      'code': 'Example 1',
      'title': 'Package identity',
      'description': 'Prototype OCR check for manufacturer, packer or importer details and the product name. Exact wording and applicability need current rule review.',
      'penalty': 'Not evaluated'
    },
    {
      'code': 'Example 2',
      'title': 'Quantity and price declarations',
      'description': 'Prototype OCR looks for a net quantity and retail price. Unit sale price and exemptions depend on package details that this demo does not evaluate.',
      'penalty': 'Not evaluated'
    },
    {
      'code': 'Example 3',
      'title': 'Dates and batch information',
      'description': 'Prototype OCR looks for date and batch text. Which declarations apply varies by product and sector-specific requirements.',
      'penalty': 'Not evaluated'
    },
    {
      'code': 'Example 4',
      'title': 'Consumer contact details',
      'description': 'Prototype OCR looks for consumer-care contact text. OCR output does not confirm that the details are complete or usable.',
      'penalty': 'Not evaluated'
    },
    {
      'code': 'Example 5',
      'title': 'Category-specific information',
      'description': 'Food, cosmetics, medical devices and other products may have separate declarations. This small prototype catalogue is not a complete ruleset.',
      'penalty': 'Not evaluated'
    },
  ];

  void _showAddRuleDialog(BuildContext context) {
    final TextEditingController codeController = TextEditingController();
    final TextEditingController titleController = TextEditingController();
    final TextEditingController descController = TextEditingController();
    final TextEditingController penaltyController = TextEditingController();
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          backgroundColor: theme.dialogBackgroundColor,
          title: Text('Add Demo Catalogue Entry', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: codeController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Example ID', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: titleController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Example title', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: descController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Description', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: penaltyController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Example note (not a verified penalty)', labelStyle: TextStyle(color: Colors.blueAccent))),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context), child: Text('Cancel', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87))),
            ElevatedButton(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
              onPressed: () {
                if (codeController.text.isNotEmpty && titleController.text.isNotEmpty) {
                  setState(() {
                    _rulesList.add({
                      'code': codeController.text,
                      'title': titleController.text,
                      'description': descController.text,
                      'penalty': penaltyController.text.isEmpty ? 'Not specified' : penaltyController.text,
                    });
                  });
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Added to this screen only. It was not saved to the backend.'), backgroundColor: Colors.blueGrey));
                }
              },
              child: Text('Add demo entry', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          alignment: WrapAlignment.spaceBetween,
          crossAxisAlignment: WrapCrossAlignment.center,
          spacing: 12,
          runSpacing: 12,
          children: [
            Text('Prototype Rule Catalogue', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 22, fontWeight: FontWeight.bold)),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12)),
              onPressed: () => _showAddRuleDialog(context),
              icon: Icon(Icons.add, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Add Demo Entry', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text('Example data only. Entries are not verified against current law and changes are not saved to the backend.', style: TextStyle(color: textMuted)),
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
                          Text(rule['code']!, style: TextStyle(color: Colors.blueAccent, fontSize: 18, fontWeight: FontWeight.bold)),
                          Text('Demo note: ${rule['penalty']}', style: TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.w500)),
                        ],
                      ),
                      SizedBox(height: 8),
                      Text(rule['title']!, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.w600)),
                      SizedBox(height: 8),
                      Text(rule['description']!, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14, height: 1.4)),
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

class _ReportRepositoryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isMobile = MediaQuery.of(context).size.width < 600;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Sample Report Repository', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: isMobile ? 22 : 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 16),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.separated(
              padding: const EdgeInsets.all(8),
              itemCount: mockViolations.length,
              separatorBuilder: (_, __) => Divider(color: theme.dividerColor, height: 1),
              itemBuilder: (context, index) {
                final v = mockViolations[index];
                return ListTile(
                  contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  leading: CircleAvatar(
                    backgroundColor: Colors.redAccent.withValues(alpha: 0.15),
                    child: Icon(Icons.picture_as_pdf, color: Colors.redAccent, size: 20),
                  ),
                  title: Text(
                    '${v['product']}',
                    style: TextStyle(
                      color: theme.brightness == Brightness.dark ? Colors.white : Colors.black,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(height: 2),
                      Text('ID: ${v['id']}  •  ${v['date'] ?? 'Recent'}', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black54, fontSize: 12)),
                      SizedBox(height: 2),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                        decoration: BoxDecoration(
                          color: (v['status'] == 'Pending Review' ? Colors.orange : Colors.blue).withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          v['status'] ?? 'Logged',
                          style: TextStyle(
                            color: v['status'] == 'Pending Review' ? Colors.orangeAccent : Colors.blueAccent,
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  trailing: IconButton(
                    icon: Icon(Icons.visibility, color: Colors.blueAccent),
                    onPressed: () => ReportViewer.showPdfDialog(context: context, reportId: v['id'], product: v['product'], findingsOrNotes: 'Sample: ${v["violation"]}', noFlagsDetected: false),
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

class _AuditLogsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Sample Audit Log', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        Text('Static demo activity; no user account, enforcement record or system event is connected.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
        SizedBox(height: 8),
        Text('Static demonstration log; this screen is not connected to authentication or an audit ledger.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
        SizedBox(height: 24),
        Expanded(
          child: Card(
            color: theme.cardColor,
            child: ListView.separated(
              padding: const EdgeInsets.all(20),
              itemCount: auditLogs.length, 
              separatorBuilder: (context, index) => Divider(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
              itemBuilder: (context, index) {
                final log = auditLogs[index];
                return ListTile(
                  leading: Icon(log['type'] == 'Authentication' ? Icons.security : Icons.radar, color: Colors.orangeAccent),
                  title: Text(log['action']!, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.w500)),
                  subtitle: Text('Category: ${log['type']} | Timestamp: ${log['timestamp']}', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 13)),
                  trailing: Text(log['status']!, style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
                );
              },
            ),
          ),
        ),
      ],
    );
  }
}

class _ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
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
                backgroundColor: theme.brightness == Brightness.dark ? Colors.blueAccent.withValues(alpha: 0.2) : Colors.blue.shade100,
                child: Icon(Icons.admin_panel_settings, size: 60, color: theme.brightness == Brightness.dark ? Colors.blueAccent : Colors.blue.shade800),
            ),
            SizedBox(height: 24),
            Text('Sample Administrator Profile', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Demo only • no authentication is connected', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey)),
            SizedBox(height: 32),
            Card(
              color: theme.cardColor,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    _buildProfileItem(Icons.email, 'Email', 'Not connected', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.phone, 'Phone', 'Not connected', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.location_on, 'Jurisdiction', 'Sample only', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.security, 'Access Level', 'Not authenticated', theme),
                  ],
                ),
              ),
            ),
            SizedBox(height: 32),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blueAccent,
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
              ),
              onPressed: null,
              icon: Icon(Icons.edit, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Profile editing not connected', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16)),
            ),
          ],
        ),
      ),
      ),
    );
  }

  Widget _buildProfileItem(IconData icon, String title, String value, ThemeData theme) {
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Row(
      children: [
        Icon(icon, color: Colors.blueAccent, size: 28),
        SizedBox(width: 16),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey)),
              SizedBox(height: 4),
              Text(value, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w600)),
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
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    return Center(
      child: ElevatedButton(
        style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
        onPressed: () => Navigator.pop(context),
        child: Text('Confirm Logout', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
      ),
    );
  }
}
