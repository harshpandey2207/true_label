import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../../core/api_service.dart';
import '../../core/report_viewer.dart';
import '../../core/svg_export.dart';

const _workspaceCategories = <String>[
  'General Packaged Commodity',
  'Food & Beverages',
  'Electronics & Appliances',
  'Cosmetics, Ointments & Pharma Goods',
  'Apparel & Textiles',
  'Medical Devices',
];

String _when(dynamic value) {
  final date = DateTime.tryParse(value?.toString() ?? '')?.toLocal();
  if (date == null) return 'Date unavailable';
  final hour = date.hour % 12 == 0 ? 12 : date.hour % 12;
  final minute = date.minute.toString().padLeft(2, '0');
  return '${date.day}/${date.month}/${date.year}  $hour:$minute ${date.hour >= 12 ? 'PM' : 'AM'}';
}

String _scanNotes(Map<String, dynamic> scan) {
  final result = Map<String, dynamic>.from((scan['result'] as Map?) ?? const {});
  final lines = <String>['Category: ${scan['category'] ?? 'Package'}'];
  final sides = result['results'] as List? ?? const [];
  for (var index = 0; index < sides.length; index++) {
    final side = Map<String, dynamic>.from(sides[index] as Map);
    final analysis = Map<String, dynamic>.from((side['analysis'] as Map?) ?? const {});
    lines.add('\n${side['filename'] ?? 'Package side ${index + 1}'}');
    for (final raw in analysis['declarations'] as List? ?? const []) {
      final declaration = Map<String, dynamic>.from(raw as Map);
      final tag = declaration['tag']?.toString() ?? 'Declaration';
      if (tag.toUpperCase() == 'GENERAL') continue;
      final text = declaration['text']?.toString() ?? '';
      final confidence = declaration['confidence'] as num?;
      final confidenceText = confidence == null ? 'OCR confidence unavailable' : '${(confidence.toDouble() * 100).toStringAsFixed(0)}% OCR confidence';
      lines.add('• $tag: $text ($confidenceText)');
      final message = declaration['message']?.toString();
      if (message != null && message.isNotEmpty) lines.add('  $message');
    }
    final missing = (analysis['missing_tags'] as List? ?? const []).map((value) => value.toString()).toList();
    if (missing.isNotEmpty) lines.add('Not detected: ${missing.join(', ')}');
    for (final warning in analysis['warnings'] as List? ?? const []) {
      lines.add('Review note: $warning');
    }
  }
  return lines.join('\n');
}

String _scanMethod(Map<String, dynamic> scan) {
  final result = Map<String, dynamic>.from((scan['result'] as Map?) ?? const {});
  final sides = result['results'] as List? ?? const [];
  if (sides.isEmpty) return 'Configured OCR text recognition';
  final analysis = Map<String, dynamic>.from(((sides.first as Map)['analysis'] as Map?) ?? const {});
  return analysis['ocr_engine']?.toString() == 'paddle'
      ? 'PaddleOCR running locally'
      : 'OCR.Space service (images sent for text recognition)';
}

class WorkspaceOverviewScreen extends StatefulWidget {
  const WorkspaceOverviewScreen({super.key});

  @override
  State<WorkspaceOverviewScreen> createState() => _WorkspaceOverviewScreenState();
}

class _WorkspaceOverviewScreenState extends State<WorkspaceOverviewScreen> {
  late Future<List<dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _data = Future.wait([
      ApiService.getJson('/workspace/summary'),
      ApiService.getJson('/workspace/scans?limit=5'),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<List<dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final summary = Map<String, dynamic>.from(snapshot.data![0] as Map);
        final scans = (snapshot.data![1] as Map)['items'] as List? ?? const [];
        final metrics = <(String, String, IconData, Color)>[
          ('Products', '${summary['product_count'] ?? 0}', Icons.inventory_2_outlined, Colors.blue),
          ('Scans', '${summary['scan_count'] ?? 0}', Icons.document_scanner_outlined, Colors.teal),
          ('Needs review', '${summary['flagged_scan_count'] ?? 0}', Icons.rule_outlined, Colors.deepOrange),
          ('Label drafts', '${summary['generated_label_count'] ?? 0}', Icons.design_services_outlined, Colors.purple),
        ];
        return RefreshIndicator(
          onRefresh: () async => setState(_load),
          child: ListView(
            children: [
              _PageHeader(title: 'Workspace overview', subtitle: 'A live view of your product, screening and label activity.'),
              const SizedBox(height: 20),
              LayoutBuilder(builder: (context, constraints) {
                final columns = constraints.maxWidth > 1100 ? 4 : constraints.maxWidth > 650 ? 2 : 1;
                final width = (constraints.maxWidth - (columns - 1) * 12) / columns;
                return Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: metrics.map((item) => SizedBox(
                    width: width,
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Row(children: [
                          CircleAvatar(backgroundColor: item.$4.withValues(alpha: .12), child: Icon(item.$3, color: item.$4)),
                          const SizedBox(width: 14),
                          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Text(item.$2, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                            Text(item.$1, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                          ])),
                        ]),
                      ),
                    ),
                  )).toList(),
                );
              }),
              const SizedBox(height: 24),
              Text('Recent scans', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              if (scans.isEmpty)
                const _EmptyState(icon: Icons.document_scanner_outlined, title: 'Your scan history will appear here', body: 'Scan package panels to see findings and prepare a report.')
              else
                ...scans.map((raw) {
                  final scan = Map<String, dynamic>.from(raw as Map);
                  final clean = scan['status'] == 'NO_FLAGS';
                  return Card(
                    child: ListTile(
                      leading: Icon(clean ? Icons.check_circle_outline : Icons.warning_amber_rounded, color: clean ? Colors.green : Colors.deepOrange),
                      title: Text('${scan['category']} package'),
                      subtitle: Text('${_when(scan['created_at'])} · ${clean ? 'No flags detected' : 'Potential issues for review'}'),
                      trailing: const Icon(Icons.chevron_right),
                    ),
                  );
                }),
              const SizedBox(height: 28),
            ],
          ),
        );
      },
    );
  }
}

class WorkspaceRegistryScreen extends StatefulWidget {
  const WorkspaceRegistryScreen({super.key});

  @override
  State<WorkspaceRegistryScreen> createState() => _WorkspaceRegistryScreenState();
}

class _WorkspaceRegistryScreenState extends State<WorkspaceRegistryScreen> {
  late Future<List<dynamic>> _data;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() {
    _data = Future.wait([ApiService.getJson('/auth/me'), ApiService.getJson('/workspace/products')]);
  }

  Future<void> _addProduct() async {
    final name = TextEditingController();
    final sku = TextEditingController();
    var category = _workspaceCategories.first;
    final values = await showDialog<Map<String, String>>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(builder: (context, setDialogState) => AlertDialog(
        title: const Text('Add a product'),
        content: SizedBox(
          width: 420,
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            TextField(controller: name, autofocus: true, decoration: const InputDecoration(labelText: 'Product name')),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              initialValue: category,
              decoration: const InputDecoration(labelText: 'Category'),
              items: _workspaceCategories.map((item) => DropdownMenuItem(value: item, child: Text(item))).toList(),
              onChanged: (value) => setDialogState(() => category = value ?? category),
            ),
            const SizedBox(height: 12),
            TextField(controller: sku, decoration: const InputDecoration(labelText: 'SKU (optional)')),
          ]),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(onPressed: () {
            if (name.text.trim().length < 2) return;
            Navigator.pop(dialogContext, {'name': name.text.trim(), 'category': category, 'sku': sku.text.trim()});
          }, child: const Text('Save product')),
        ],
      )),
    );
    name.dispose();
    sku.dispose();
    if (values == null) return;
    try {
      await ApiService.postJson('/workspace/products', {...values, 'declarations': <String, String>{}});
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted) _showError(context, error);
    }
  }

  Future<void> _deleteProduct(int id) async {
    try {
      await ApiService.delete('/workspace/products/$id');
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted) _showError(context, error);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<List<dynamic>>(
      future: _data,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final account = Map<String, dynamic>.from((snapshot.data![0] as Map)['user'] as Map);
        final products = (snapshot.data![1] as Map)['items'] as List? ?? const [];
        return ListView(children: [
          _PageHeader(
            title: 'Enterprise registry',
            subtitle: 'Manage your business profile and registered product catalogue.',
            action: FilledButton.icon(onPressed: _addProduct, icon: const Icon(Icons.add), label: const Text('Add product')),
          ),
          const SizedBox(height: 18),
          Card(child: Padding(padding: const EdgeInsets.all(20), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text('Business profile', style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 14),
            _InfoLine(label: 'Organization', value: account['organization_name']?.toString() ?? 'Not provided'),
            _InfoLine(label: 'Account owner', value: account['full_name']?.toString() ?? ''),
            _InfoLine(label: 'Email', value: account['email']?.toString() ?? ''),
          ]))),
          const SizedBox(height: 20),
          Text('Products', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          if (products.isEmpty)
            _EmptyState(icon: Icons.inventory_2_outlined, title: 'No products registered yet', body: 'Add your first product to keep its category, SKU and declaration values together.', action: FilledButton.icon(onPressed: _addProduct, icon: const Icon(Icons.add), label: const Text('Add product')))
          else
            ...products.map((raw) {
              final product = Map<String, dynamic>.from(raw as Map);
              return Card(child: ListTile(
                leading: const CircleAvatar(child: Icon(Icons.inventory_2_outlined)),
                title: Text(product['name']?.toString() ?? ''),
                subtitle: Text('${product['category']}${(product['sku']?.toString().isNotEmpty ?? false) ? ' · SKU ${product['sku']}' : ''}'),
                trailing: IconButton(tooltip: 'Remove product', icon: const Icon(Icons.delete_outline), onPressed: () => _deleteProduct(product['id'] as int)),
              ));
            }),
          const SizedBox(height: 24),
        ]);
      },
    );
  }
}

class WorkspaceReportsScreen extends StatefulWidget {
  const WorkspaceReportsScreen({super.key});

  @override
  State<WorkspaceReportsScreen> createState() => _WorkspaceReportsScreenState();
}

class _WorkspaceReportsScreenState extends State<WorkspaceReportsScreen> {
  late Future<Map<String, dynamic>> _scans;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _scans = ApiService.getJson('/workspace/scans?limit=100');

  void _openReport(Map<String, dynamic> scan) {
    ReportViewer.showPdfDialog(
      context: context,
      reportId: 'SCAN-${scan['id']}',
      product: '${scan['category']} package',
      findingsOrNotes: _scanNotes(scan),
      noFlagsDetected: scan['status'] == 'NO_FLAGS',
      analysisMethod: _scanMethod(scan),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _scans,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final scans = snapshot.data!['items'] as List? ?? const [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _PageHeader(title: 'Scan history & reports', subtitle: 'Review findings saved to your workspace and export a screening report.'),
          const SizedBox(height: 16),
          Expanded(child: scans.isEmpty
              ? const _EmptyState(icon: Icons.folder_open_outlined, title: 'No saved scan reports', body: 'Completed scans will be listed here with their detected declarations and review notes.')
              : ListView.builder(itemCount: scans.length, itemBuilder: (context, index) {
                  final scan = Map<String, dynamic>.from(scans[index] as Map);
                  final clean = scan['status'] == 'NO_FLAGS';
                  final fileNames = (scan['image_names'] as List? ?? const []).join(', ');
                  return Card(child: ListTile(
                    isThreeLine: true,
                    leading: Icon(clean ? Icons.check_circle_outline : Icons.warning_amber_rounded, color: clean ? Colors.green : Colors.deepOrange),
                    title: Text('${scan['category']} · Scan ${scan['id']}'),
                    subtitle: Text('${_when(scan['created_at'])}\n${clean ? 'No flags detected in the selected checks' : 'Potential issues need review'}${fileNames.isEmpty ? '' : '\n$fileNames'}'),
                    trailing: IconButton(tooltip: 'Open PDF report', icon: const Icon(Icons.picture_as_pdf_outlined), onPressed: () => _openReport(scan)),
                  ));
                })),
          const SizedBox(height: 20),
          Text('Screening results can miss or misread declarations and do not establish legal compliance.', style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
          const SizedBox(height: 8),
        ]);
      },
    );
  }
}

class WorkspaceLabelDraftsScreen extends StatefulWidget {
  const WorkspaceLabelDraftsScreen({super.key});

  @override
  State<WorkspaceLabelDraftsScreen> createState() => _WorkspaceLabelDraftsScreenState();
}

class _WorkspaceLabelDraftsScreenState extends State<WorkspaceLabelDraftsScreen> {
  late Future<Map<String, dynamic>> _drafts;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _drafts = ApiService.getJson('/workspace/labels');

  Future<void> _downloadSide(String productName, String sideName, String svg) async {
    final base = productName.trim().replaceAll(RegExp(r'[^A-Za-z0-9_-]+'), '_');
    final side = sideName.trim().replaceAll(RegExp(r'[^A-Za-z0-9_-]+'), '_');
    final saved = await saveSvgDraft(
      '${base.isEmpty ? 'label' : base}_${side.isEmpty ? 'side' : side}.svg',
      svg,
    );
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
      content: Text(saved ? 'SVG side downloaded.' : 'SVG download is available in the web app.'),
    ));
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _drafts,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final drafts = snapshot.data!['items'] as List? ?? const [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _PageHeader(title: 'Saved label drafts', subtitle: 'Reopen generated package sides, review warnings and download editable SVG artwork.'),
          const SizedBox(height: 16),
          Expanded(child: drafts.isEmpty
              ? const _EmptyState(icon: Icons.layers_outlined, title: 'Your saved label drafts will appear here', body: 'Generated label artwork is saved to this business workspace for later review and export.')
              : RefreshIndicator(
                  onRefresh: () async => setState(_load),
                  child: ListView.builder(
                    itemCount: drafts.length,
                    itemBuilder: (context, index) {
                      final draft = Map<String, dynamic>.from(drafts[index] as Map);
                      final productName = draft['product_name']?.toString() ?? 'Product';
                      final sourceScanId = draft['source_scan_id'];
                      final labelData = Map<String, dynamic>.from((draft['label_data'] as Map?) ?? const {});
                      final sides = labelData['sides'] as List? ?? const [];
                      final warnings = (draft['warnings'] as List? ?? const []).map((item) => item.toString()).toList();
                      return Card(
                        margin: const EdgeInsets.only(bottom: 16),
                        child: Padding(
                          padding: const EdgeInsets.all(18),
                          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Wrap(alignment: WrapAlignment.spaceBetween, crossAxisAlignment: WrapCrossAlignment.center, spacing: 12, runSpacing: 8, children: [
                              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                Text(productName, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                                const SizedBox(height: 4),
                                Text('${draft['category'] ?? 'Package'} · Draft ${draft['id']} · ${_when(draft['created_at'])}${sourceScanId == null ? '' : ' · From scan $sourceScanId'}', style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
                              ]),
                              Chip(label: Text('${sides.length} ${sides.length == 1 ? 'side' : 'sides'}')),
                            ]),
                            const SizedBox(height: 16),
                            if (sides.isEmpty)
                              const Text('No SVG sides are stored in this draft record.')
                            else
                              Wrap(spacing: 12, runSpacing: 12, children: sides.map((rawSide) {
                                final side = Map<String, dynamic>.from(rawSide as Map);
                                final sideName = side['side_name']?.toString() ?? 'Package side';
                                final svg = side['svg_code']?.toString() ?? '';
                                return SizedBox(
                                  width: 245,
                                  child: Card(
                                    clipBehavior: Clip.antiAlias,
                                    child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
                                      Padding(padding: const EdgeInsets.fromLTRB(12, 12, 12, 6), child: Text(sideName, style: theme.textTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold))),
                                      Container(
                                        height: 245,
                                        color: theme.colorScheme.surfaceContainerHighest,
                                        padding: const EdgeInsets.all(12),
                                        child: svg.isEmpty ? const Center(child: Text('SVG preview unavailable')) : SvgPicture.string(svg, fit: BoxFit.contain),
                                      ),
                                      Padding(
                                        padding: const EdgeInsets.all(8),
                                        child: OutlinedButton.icon(
                                          onPressed: svg.isEmpty ? null : () => _downloadSide(productName, sideName, svg),
                                          icon: const Icon(Icons.download_outlined),
                                          label: const Text('Download SVG'),
                                        ),
                                      ),
                                    ]),
                                  ),
                                );
                              }).toList()),
                            if (warnings.isNotEmpty) ...[
                              const SizedBox(height: 12),
                              ExpansionTile(
                                tilePadding: EdgeInsets.zero,
                                title: const Text('Review before printing'),
                                children: warnings.map((warning) => ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  dense: true,
                                  leading: const Icon(Icons.info_outline, color: Colors.deepOrange),
                                  title: Text(warning),
                                )).toList(),
                              ),
                            ],
                          ]),
                        ),
                      );
                    },
                  ),
                )),
        ]);
      },
    );
  }
}

class WorkspaceBillingScreen extends StatefulWidget {
  const WorkspaceBillingScreen({super.key});

  @override
  State<WorkspaceBillingScreen> createState() => _WorkspaceBillingScreenState();
}

class _WorkspaceBillingScreenState extends State<WorkspaceBillingScreen> {
  late Future<Map<String, dynamic>> _records;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _records = ApiService.getJson('/workspace/billing/records');

  Future<void> _newRecord() async {
    final description = TextEditingController();
    final amount = TextEditingController();
    final values = await showDialog<Map<String, dynamic>>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Add payment record'),
        content: SizedBox(width: 400, child: Column(mainAxisSize: MainAxisSize.min, children: [
          TextField(controller: description, autofocus: true, decoration: const InputDecoration(labelText: 'Description')),
          const SizedBox(height: 12),
          TextField(controller: amount, keyboardType: const TextInputType.numberWithOptions(decimal: true), decoration: const InputDecoration(labelText: 'Amount (INR)', prefixText: '₹ ')),
        ])),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')),
          FilledButton(onPressed: () {
            final rupees = double.tryParse(amount.text.trim());
            if (description.text.trim().length < 3 || rupees == null || rupees <= 0) return;
            Navigator.pop(dialogContext, {'description': description.text.trim(), 'amount_minor': (rupees * 100).round()});
          }, child: const Text('Save record')),
        ],
      ),
    );
    description.dispose();
    amount.dispose();
    if (values == null) return;
    try {
      await ApiService.postJson('/workspace/billing/records', values);
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted) _showError(context, error);
    }
  }

  Future<void> _reportExternalReference(Map<String, dynamic> record) async {
    final reference = TextEditingController(text: record['external_reference']?.toString() ?? '');
    final value = await showDialog<String>(context: context, builder: (dialogContext) => AlertDialog(
      title: const Text('Record an external reference'),
      content: TextField(controller: reference, autofocus: true, decoration: const InputDecoration(labelText: 'Receipt / transaction reference')),
      actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, reference.text.trim()), child: const Text('Submit for review'))],
    ));
    reference.dispose();
    if (value == null || value.length < 4) return;
    try {
      await ApiService.postJson('/workspace/billing/records/${record['id']}/external-reference', {'external_reference': value});
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted) _showError(context, error);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return FutureBuilder<Map<String, dynamic>>(
      future: _records,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final items = snapshot.data!['items'] as List? ?? const [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _PageHeader(title: 'Billing & payment records', subtitle: 'Keep payment references and amounts associated with this workspace.', action: FilledButton.icon(onPressed: _newRecord, icon: const Icon(Icons.add), label: const Text('Add record'))),
          const SizedBox(height: 12),
          Card(color: theme.colorScheme.secondaryContainer, child: const Padding(
            padding: EdgeInsets.all(16),
            child: Text('Online checkout is not configured. These entries are a workspace ledger only; reported external payments are not verified or marked paid.'),
          )),
          const SizedBox(height: 12),
          Expanded(child: items.isEmpty
              ? _EmptyState(icon: Icons.payments_outlined, title: 'No payment records', body: 'Add an amount and description to start a workspace payment ledger.', action: FilledButton.icon(onPressed: _newRecord, icon: const Icon(Icons.add), label: const Text('Add record')))
              : ListView.builder(itemCount: items.length, itemBuilder: (context, index) {
                  final record = Map<String, dynamic>.from(items[index] as Map);
                  final status = record['status'] == 'reported_unverified' ? 'Reported · awaiting verification' : 'Pending confirmation';
                  final amount = ((record['amount_minor'] as num).toInt() / 100).toStringAsFixed(2);
                  return Card(child: ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.receipt_long_outlined)),
                    title: Text(record['description']?.toString() ?? ''),
                    subtitle: Text('₹$amount · $status${record['external_reference'] == null ? '' : '\nReference: ${record['external_reference']}'}\n${_when(record['created_at'])}'),
                    isThreeLine: true,
                    trailing: IconButton(tooltip: 'Add payment reference', icon: const Icon(Icons.add_link), onPressed: () => _reportExternalReference(record)),
                  ));
                })),
        ]);
      },
    );
  }
}

class WorkspaceNotesScreen extends StatefulWidget {
  const WorkspaceNotesScreen({super.key});

  @override
  State<WorkspaceNotesScreen> createState() => _WorkspaceNotesScreenState();
}

class _WorkspaceNotesScreenState extends State<WorkspaceNotesScreen> {
  late Future<Map<String, dynamic>> _notes;

  @override
  void initState() {
    super.initState();
    _load();
  }

  void _load() => _notes = ApiService.getJson('/workspace/notices');

  Future<void> _createNote() async {
    final title = TextEditingController();
    final body = TextEditingController();
    final values = await showDialog<List<String>>(context: context, builder: (dialogContext) => AlertDialog(
      title: const Text('Create a review note'),
      content: SizedBox(width: 440, child: Column(mainAxisSize: MainAxisSize.min, children: [
        TextField(controller: title, autofocus: true, decoration: const InputDecoration(labelText: 'Title')),
        const SizedBox(height: 12),
        TextField(controller: body, minLines: 3, maxLines: 5, decoration: const InputDecoration(labelText: 'Note')),
      ])),
      actions: [TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(dialogContext, [title.text.trim(), body.text.trim()]), child: const Text('Save note'))],
    ));
    title.dispose();
    body.dispose();
    if (values == null || values[0].length < 3 || values[1].length < 3) return;
    try {
      await ApiService.postJson('/workspace/notices', {'title': values[0], 'body': values[1]});
      if (mounted) setState(_load);
    } catch (error) {
      if (mounted) _showError(context, error);
    }
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<Map<String, dynamic>>(
      future: _notes,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) return const Center(child: CircularProgressIndicator());
        if (snapshot.hasError) return _LoadError(message: snapshot.error.toString(), onRetry: () => setState(_load));
        final items = snapshot.data!['items'] as List? ?? const [];
        return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _PageHeader(title: 'Review notes', subtitle: 'Keep internal follow-ups with the business workspace.', action: FilledButton.icon(onPressed: _createNote, icon: const Icon(Icons.add), label: const Text('New note'))),
          const SizedBox(height: 8),
          const Text('These notes stay within your workspace and are not official notices.'),
          const SizedBox(height: 12),
          Expanded(child: items.isEmpty
              ? _EmptyState(icon: Icons.mark_email_unread_outlined, title: 'No review notes', body: 'Add internal follow-ups for packaging changes, supporting documents or review decisions.', action: FilledButton.icon(onPressed: _createNote, icon: const Icon(Icons.add), label: const Text('New note')))
              : ListView.builder(itemCount: items.length, itemBuilder: (context, index) {
                  final note = Map<String, dynamic>.from(items[index] as Map);
                  return Card(child: ListTile(
                    leading: const Icon(Icons.sticky_note_2_outlined),
                    title: Text(note['title']?.toString() ?? ''),
                    subtitle: Text('${note['body']}\n${_when(note['created_at'])}'),
                    isThreeLine: true,
                  ));
                })),
        ]);
      },
    );
  }
}

class WorkspaceProfileScreen extends StatelessWidget {
  const WorkspaceProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final user = ApiService.currentUser ?? const <String, dynamic>{};
    return ListView(children: [
      const _PageHeader(title: 'Account profile', subtitle: 'Account and business workspace details.'),
      const SizedBox(height: 18),
      Card(child: Padding(padding: const EdgeInsets.all(22), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        _InfoLine(label: 'Name', value: user['full_name']?.toString() ?? ''),
        _InfoLine(label: 'Email', value: user['email']?.toString() ?? ''),
        _InfoLine(label: 'Business', value: user['organization_name']?.toString() ?? ''),
        _InfoLine(label: 'Account role', value: user['role']?.toString() ?? ''),
      ]))),
    ]);
  }
}

class WorkspaceLogoutScreen extends StatelessWidget {
  const WorkspaceLogoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 480), child: Card(child: Padding(
      padding: const EdgeInsets.all(28),
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.logout, size: 48, color: Colors.deepOrange),
        const SizedBox(height: 14),
        Text('Sign out of True Label?', style: theme.textTheme.titleLarge),
        const SizedBox(height: 8),
        const Text('You can sign back in at any time to continue working.'),
        const SizedBox(height: 20),
        FilledButton.icon(
          onPressed: () async {
            await ApiService.signOut();
            if (context.mounted) Navigator.of(context).pushNamedAndRemoveUntil('/login', (route) => false);
          },
          icon: const Icon(Icons.logout),
          label: const Text('Log out'),
          style: FilledButton.styleFrom(backgroundColor: Colors.deepOrange),
        ),
      ]),
    ))));
  }
}

class _PageHeader extends StatelessWidget {
  const _PageHeader({required this.title, required this.subtitle, this.action});
  final String title;
  final String subtitle;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Wrap(alignment: WrapAlignment.spaceBetween, crossAxisAlignment: WrapCrossAlignment.center, spacing: 16, runSpacing: 12, children: [
      ConstrainedBox(constraints: const BoxConstraints(maxWidth: 720), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
        const SizedBox(height: 5),
        Text(subtitle, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant)),
      ])),
      ?action,
    ]);
  }
}

class _InfoLine extends StatelessWidget {
  const _InfoLine({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
      SizedBox(width: 150, child: Text(label, style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Theme.of(context).colorScheme.onSurfaceVariant))),
      Expanded(child: Text(value)),
    ]),
  );
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.icon, required this.title, required this.body, this.action});
  final IconData icon;
  final String title;
  final String body;
  final Widget? action;
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(child: Padding(padding: const EdgeInsets.all(28), child: Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
      Icon(icon, size: 42, color: theme.colorScheme.primary),
      const SizedBox(height: 12),
      Text(title, textAlign: TextAlign.center, style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
      const SizedBox(height: 6),
      ConstrainedBox(constraints: const BoxConstraints(maxWidth: 440), child: Text(body, textAlign: TextAlign.center, style: theme.textTheme.bodyMedium?.copyWith(color: theme.colorScheme.onSurfaceVariant))),
      if (action case final action?) ...[const SizedBox(height: 16), action],
    ]))));
  }
}

class _LoadError extends StatelessWidget {
  const _LoadError({required this.message, required this.onRetry});
  final String message;
  final VoidCallback onRetry;
  @override
  Widget build(BuildContext context) => _EmptyState(
    icon: Icons.cloud_off_outlined,
    title: 'Could not load workspace data',
    body: message.replaceFirst('Exception: ', ''),
    action: OutlinedButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('Try again')),
  );
}

void _showError(BuildContext context, Object error) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(error.toString().replaceFirst('Exception: ', '')), backgroundColor: Colors.redAccent));
}
