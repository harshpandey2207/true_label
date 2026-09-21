import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:provider/provider.dart';
import '../../core/theme_provider.dart';
import 'package:sidebarx/sidebarx.dart';
import 'package:fl_chart/fl_chart.dart';
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
    int fineCollected = totalViolations * 2000; 

    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Temporal Analysis & Heatmap', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
          SizedBox(height: 20),
          
          _buildStatCard(
            title: 'Total Scans Recorded',
            value: totalScans.toString(),
            subtitle: 'Synced across all districts',
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
                      Text('Compliance Ratio', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
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
            title: 'Total Fines Collected',
            value: '₹$fineCollected',
            subtitle: 'Matched to active infractions',
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
    for (int i = 0; i < _shapes.length; i++) {
      if (_shapes[i].hitTest(pos, size)) { found = i; break; }
    }
    // Only notify when the hovered state actually changes — saves repaints
    final current = _hover.value;
    if (current.idx != found || (found != null && current.pos != pos)) {
      _hover.value = (idx: found, pos: pos);
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
                // ── Canvas layer — repaints only when _hover changes ──────
                CustomPaint(
                  size: size,
                  painter: _IndiaChoroplethPainter(
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

  _StateShape({
    required this.name, required this.polygons,
    required this.violations, required this.scans, required this.compliant,
    required this.minLon, required this.maxLon,
    required this.minLat, required this.maxLat,
  });

  List<List<Offset>> project(Size size) => _cache.putIfAbsent(size, () =>
    polygons.map((ring) => ring.map((pt) => _proj(pt[0], pt[1], size)).toList()).toList(),
  );

  Offset _proj(double lon, double lat, Size size) {
    const pad = 0.05;
    final lonSpan = maxLon - minLon;
    final latSpan = maxLat - minLat;
    final x = ((lon - minLon + lonSpan * pad) / (lonSpan * (1 + pad * 2))) * size.width;
    final y = (1 - (lat - minLat + latSpan * pad) / (latSpan * (1 + pad * 2))) * size.height;
    return Offset(x, y);
  }

  bool hitTest(Offset pos, Size size) {
    for (final ring in project(size)) {
      if (_pip(pos, ring)) return true;
    }
    return false;
  }

  static bool _pip(Offset pt, List<Offset> poly) {
    bool inside = false;
    int j = poly.length - 1;
    for (int i = 0; i < poly.length; i++) {
      final xi = poly[i].dx, yi = poly[i].dy;
      final xj = poly[j].dx, yj = poly[j].dy;
      if (((yi > pt.dy) != (yj > pt.dy)) &&
          (pt.dx < (xj - xi) * (pt.dy - yi) / (yj - yi) + xi)) {
        inside = !inside;
      }
      j = i;
    }
    return inside;
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
class _IndiaChoroplethPainter extends CustomPainter {
  final List<_StateShape> shapes;
  final ValueNotifier<_HoverState> hoverNotifier;
  final bool isDark;

  _IndiaChoroplethPainter({
    required this.shapes,
    required this.hoverNotifier,
    required this.isDark,
  }) : super(repaint: hoverNotifier);  // ← only repaints when hover changes

  @override
  void paint(Canvas canvas, Size size) {
    final strokeNormal = isDark ? Colors.white24 : Colors.black26;
    final strokeHover  = isDark ? Colors.white   : Colors.black87;
    final hovered      = hoverNotifier.value.idx;

    for (int i = 0; i < shapes.length; i++) {
      final shape = shapes[i];
      final isHovered = hovered == i;
      for (final ring in shape.project(size)) {
        if (ring.isEmpty) continue;
        final path = Path()..moveTo(ring[0].dx, ring[0].dy);
        for (int p = 1; p < ring.length; p++) path.lineTo(ring[p].dx, ring[p].dy);
        path.close();

        canvas.drawPath(path, Paint()
          ..color = shape.fillColor.withAlpha(isHovered ? 230 : 175)
          ..style = PaintingStyle.fill);

        canvas.drawPath(path, Paint()
          ..color = isHovered ? strokeHover : strokeNormal
          ..style = PaintingStyle.stroke
          ..strokeWidth = isHovered ? 1.8 : 0.5);
      }
    }
  }

  @override
  bool shouldRepaint(_IndiaChoroplethPainter old) => old.isDark != isDark;
  // Note: hover repaints are handled by the `repaint: hoverNotifier` above,
  // so shouldRepaint only needs to catch theme changes.
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
        Text('Pending Action Required (Violations Queue)', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
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
                          label: Text('Confirm & Issue E-Notice', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        ),
                      ),
                      SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          style: OutlinedButton.styleFrom(side: BorderSide(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87), padding: const EdgeInsets.symmetric(vertical: 14)),
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Violation dismissed successfully.'), backgroundColor: Colors.grey));
                          },
                          child: Text('Dismiss', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
    final textColor = theme.brightness == Brightness.dark ? Colors.white : Colors.black;
    final textMuted = theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87;
    bool sendSms = true;
    bool sendApp = true;
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setState) {
            return AlertDialog(
              backgroundColor: theme.dialogBackgroundColor,
              title: Text('Issue E-Notice: $product', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
              content: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    ListTile(
                      contentPadding: EdgeInsets.zero,
                      leading: Icon(Icons.phone, color: Colors.green),
                      title: Text('+91 98765 43210', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
                      subtitle: Text('Registered Phone Number Available', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
                    ),
                    Divider(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
                    SizedBox(height: 16),
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text('Send via SMS', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                      value: sendSms,
                      activeColor: Colors.blueAccent,
                      onChanged: (v) => setState(() => sendSms = v!),
                    ),
                    CheckboxListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text('Send via App Push', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                      value: sendApp,
                      activeColor: Colors.blueAccent,
                      onChanged: (v) => setState(() => sendApp = v!),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(onPressed: () => Navigator.pop(context), child: Text('Cancel', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87))),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent),
                  onPressed: () {
                    Navigator.pop(context);
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Notices dispatched across available channels!'), backgroundColor: Colors.green));
                  },
                  child: Text('Dispatch E-Notice', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                ),
              ],
            );
          },
        );
      },
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
      'code': 'Rule 2',
      'title': 'Definitions',
      'description': 'Provides definitions for standard terms such as "Retail Package", "Wholesale Package", "Principal Display Panel", and "Multi-piece package".',
      'penalty': 'Informational'
    },
    {
      'code': 'Rule 3',
      'title': 'Applicability',
      'description': 'States that the provisions apply to packages intended for retail sale. Exempts packages weighing more than 25 kg or 25 litres, and packages destined for industrial/institutional consumers.',
      'penalty': 'Informational'
    },
    {
      'code': 'Rule 4',
      'title': 'Regulation for Pre-packing and Sale',
      'description': 'No person shall pre-pack or cause or permit to be pre-packed any commodity for sale, distribution or delivery unless the package bears the mandatory declarations.',
      'penalty': 'Up to 5,000 INR'
    },
    {
      'code': 'Rule 5',
      'title': 'Specific Commodities Standard Packages',
      'description': 'Certain commodities like infant milk food, biscuits, and bottled water must be packed only in specified standard quantities.',
      'penalty': '2,000 to 5,000 INR'
    },
    {
      'code': 'Rule 6',
      'title': 'Declarations on Every Package',
      'description': 'Every pre-packaged commodity must declare the MRP, Net Quantity, Manufacturer details, Date of Manufacture, and Consumer Care details.',
      'penalty': '2,000 to 5,000 INR'
    },
    {
      'code': 'Rule 7', 
      'title': 'Principal Display Panel & Dimensions',
      'description': 'Net quantity and retail price declarations must meet minimum millimeter height specifications based on the principal display panel area.',
      'penalty': '1,000 to 3,000 INR'
    },
    {
      'code': 'Rule 9',
      'title': 'Manner of Declarations (Legibility)',
      'description': 'Every declaration shall be legible, prominent, definite, plain, and unambiguous, and must be strictly in Hindi or English.',
      'penalty': 'Up to 5,000 INR'
    },
    {
      'code': 'Rule 10',
      'title': 'Declaration of Manufacturer Identity',
      'description': 'The full name and address of the manufacturer, or the packer if different from the manufacturer, must be clearly stated on the label.',
      'penalty': '1,000 to 5,000 INR'
    },
    {
      'code': 'Rule 12',
      'title': 'Declaration of Net Quantity',
      'description': 'The net quantity shall be expressed in terms of standard metric units of weight, measure, or number (e.g., kg, g, L, ml).',
      'penalty': '2,000 to 5,000 INR'
    },
    {
      'code': 'Rule 13',
      'title': 'Statement of Units',
      'description': 'Specifies the correct symbols for standard units (e.g., "g" for gram, "kg" for kilogram) and forbids the use of pluralized symbols (e.g., "kgs").',
      'penalty': 'Up to 2,000 INR'
    },
    {
      'code': 'Rule 18',
      'title': 'Wholesale Package Provisions',
      'description': 'Every wholesale package must visibly bear the name and address of the manufacturer or importer and the identity/quantity of the commodity.',
      'penalty': 'Up to 5,000 INR'
    },
    {
      'code': 'Rule 19',
      'title': 'Imported Packages',
      'description': 'Imported packages must bear the name and address of the importer, the country of origin, and all standard Rule 6 declarations.',
      'penalty': 'Up to 5,000 INR'
    },
    {
      'code': 'Rule 24',
      'title': 'Declaration of Retail Price (MRP)',
      'description': 'The maximum retail price inclusive of all taxes must be clearly stated. The price cannot be altered or overwritten at the retail level.',
      'penalty': '2,000 to 5,000 INR'
    },
    {
      'code': 'Rule 26',
      'title': 'Exemption in Respect of Certain Packages',
      'description': 'Exempts very small packages (net weight under 10g/10ml) from certain declarations like manufacturing date, except for food and drugs.',
      'penalty': 'Informational'
    },
    {
      'code': 'Rule 32',
      'title': 'General Penalty for Contravention',
      'description': 'Whoever contravenes any provisions of these rules for which no specific penalty is provided shall be punished with a fine.',
      'penalty': 'Up to 5,000 INR'
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
          title: Text('Add New Compliance Rule', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(controller: codeController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Rule Code', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: titleController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Rule Title', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: descController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Description', labelStyle: TextStyle(color: Colors.blueAccent))),
                SizedBox(height: 12),
                TextField(controller: penaltyController, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black), decoration: const InputDecoration(labelText: 'Fine / Penalty Range', labelStyle: TextStyle(color: Colors.blueAccent))),
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
                      'penalty': penaltyController.text.isEmpty ? '1,000 INR' : penaltyController.text,
                    });
                  });
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('New rule successfully added!'), backgroundColor: Colors.green));
                }
              },
              child: Text('Save Rule', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
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
            Text('Compliance Rules Management', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 22, fontWeight: FontWeight.bold)),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blueAccent, padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12)),
              onPressed: () => _showAddRuleDialog(context),
              icon: Icon(Icons.add, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Add Rule', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontWeight: FontWeight.bold)),
            ),
          ],
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
                          Text(rule['code']!, style: TextStyle(color: Colors.blueAccent, fontSize: 18, fontWeight: FontWeight.bold)),
                          Text('Fine: ${rule['penalty']}', style: TextStyle(color: Colors.orangeAccent, fontWeight: FontWeight.w500)),
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
        Text('Secure Report Repository', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: isMobile ? 22 : 28, fontWeight: FontWeight.bold)),
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
                    onPressed: () => _showMockPdfDialog(context, v['id'], v['product'], v['violation']),
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

  void _showMockPdfDialog(BuildContext context, String id, String product, String violationStr) {
    showDialog(
      context: context,
      builder: (context) {
        final screenWidth = MediaQuery.of(context).size.width;
        final theme = Theme.of(context);
        final screenHeight = MediaQuery.of(context).size.height;
        
        return Dialog(
          backgroundColor: Colors.transparent,
          child: Container(
            width: screenWidth * 0.95,
            height: screenHeight * 0.8,
            decoration: BoxDecoration(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, borderRadius: BorderRadius.circular(8)),
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(color: Color(0xFFE0E0E0), borderRadius: BorderRadius.vertical(top: Radius.circular(8))),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(child: Text('$id - Official Report.pdf', overflow: TextOverflow.ellipsis, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontWeight: FontWeight.bold))),
                      Row(
                        children: [
                          Icon(Icons.print, color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
                          SizedBox(width: 16),
                          Icon(Icons.download, color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87),
                          SizedBox(width: 16),
                          InkWell(onTap: () => Navigator.pop(context), child: Icon(Icons.close, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black)),
                        ],
                      )
                    ],
                  ),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Center(child: Text('DEPARTMENT OF LEGAL METROLOGY', textAlign: TextAlign.center, style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 20, fontWeight: FontWeight.bold))),
                        Center(child: Text('Official Inspection Report', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 16))),
                        Divider(color: Colors.black26, height: 40),
                        Text('Report ID: $id', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                        SizedBox(height: 8),
                        Text('Target Product: $product', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                        SizedBox(height: 8),
                        Text('Date: October 16, 2026', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, fontSize: 14)),
                        SizedBox(height: 24),
                        Text('FINDINGS:', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16, fontWeight: FontWeight.bold)),
                        SizedBox(height: 8),
                        Text(
                          'Computer Vision analysis indicates a violation of the Legal Metrology (Packaged Commodities) Rules, 2011.\n\n'
                          'Identified Infraction: $violationStr\n\n'
                          'The mandatory declarations on the principal display panel do not meet the statutory requirements. '
                          'Immediate remediation or issuance of an e-notice is recommended per the standard operating procedure.', 
                          style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87, height: 1.5)
                        ),
                        SizedBox(height: 40),
                        Container(
                          padding: const EdgeInsets.all(16),
                          color: Colors.red.shade50,
                          child: Text('STATUS: NON-COMPLIANT - E-NOTICE DISPATCHED', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                        )
                      ],
                    ),
                  ),
                )
              ],
            ),
          ),
        );
      },
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
        Text('System Audit Logs & Activity Trail', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 28, fontWeight: FontWeight.bold)),
        SizedBox(height: 8),
        Text('Immutable ledger tracking login events and inspector scans with exact date & time.', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white70 : Colors.black87)),
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
            Text('Harsh Pandey', style: theme.textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('Chief Metrology Administrator', style: theme.textTheme.titleMedium?.copyWith(color: Colors.grey)),
            SizedBox(height: 32),
            Card(
              color: theme.cardColor,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    _buildProfileItem(Icons.email, 'Email', 'harsh.pandey@truelabel.gov.in', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.phone, 'Phone', '+91 98765 43210', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.location_on, 'Jurisdiction', 'National Headquarters, New Delhi', theme),
                    Divider(height: 32),
                    _buildProfileItem(Icons.security, 'Access Level', 'Tier-1 Root Administrator', theme),
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
              onPressed: () {},
              icon: Icon(Icons.edit, color: theme.brightness == Brightness.dark ? Colors.white : Colors.black),
              label: Text('Edit Profile', style: TextStyle(color: theme.brightness == Brightness.dark ? Colors.white : Colors.black, fontSize: 16)),
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