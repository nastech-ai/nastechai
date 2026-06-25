import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/settings_provider.dart';
import '../../../core/services/api/nastech_agent_service.dart';

class NasTechAgentPage extends StatefulWidget {
  const NasTechAgentPage({super.key});

  @override
  State<NasTechAgentPage> createState() => _NasTechAgentPageState();
}

class _NasTechAgentPageState extends State<NasTechAgentPage> {
  static const _providerId = 'NasTech Agent';

  late TextEditingController _urlController;
  late TextEditingController _tokenController;

  bool _testing = false;
  String? _testResult;
  bool _testOk = false;
  String _agentModel = '';
  bool _loadingModel = false;

  @override
  void initState() {
    super.initState();
    final cfg =
        context.read<SettingsProvider>().getProviderConfig(_providerId);
    _urlController = TextEditingController(text: cfg.baseUrl);
    _tokenController = TextEditingController(text: cfg.apiKey);
    if (cfg.baseUrl.isNotEmpty) {
      _loadAgentModel(cfg.baseUrl);
    }
  }

  @override
  void dispose() {
    _urlController.dispose();
    _tokenController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final settings = context.read<SettingsProvider>();
    final old = settings.getProviderConfig(_providerId);
    await settings.setProviderConfig(
      _providerId,
      old.copyWith(
        baseUrl: _urlController.text.trim(),
        apiKey: _tokenController.text.trim(),
        enabled: true,
        providerType: ProviderKind.nastechAgent,
      ),
    );
  }

  Future<void> _testConnection() async {
    await _save();
    setState(() {
      _testing = true;
      _testResult = null;
      _testOk = false;
      _agentModel = '';
    });
    final url = _urlController.text.trim();
    final err = await pingNasTechAgent(url);
    String model = '';
    if (err == null) {
      model = await fetchNasTechAgentModel(url);
    }
    if (!mounted) return;
    setState(() {
      _testing = false;
      _testOk = err == null;
      _testResult = err ?? 'Connected successfully!';
      _agentModel = model;
    });
  }

  Future<void> _loadAgentModel(String url) async {
    setState(() => _loadingModel = true);
    final model = await fetchNasTechAgentModel(url);
    if (!mounted) return;
    setState(() {
      _loadingModel = false;
      _agentModel = model;
    });
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('⚡', style: TextStyle(fontSize: 18)),
            SizedBox(width: 8),
            Text('NasTech Agent'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () async {
              await _save();
              if (context.mounted) Navigator.of(context).pop();
            },
            child: const Text('Save'),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        children: [
          _sectionHeader('Connection'),
          _card(cs, isDark, [
            _field(
              label: 'Agent URL',
              hint: 'http://192.168.1.x:8080  or  http://your-vps.com:8080',
              controller: _urlController,
              keyboardType: TextInputType.url,
              onChanged: (_) {
                setState(() {
                  _testResult = null;
                  _agentModel = '';
                });
              },
            ),
            const Divider(height: 1),
            _field(
              label: 'Auth Token',
              hint: 'Optional — only if your agent requires one',
              controller: _tokenController,
              obscure: true,
            ),
          ]),

          const SizedBox(height: 8),

          // Test button
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              onPressed: _testing ? null : _testConnection,
              icon: _testing
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white),
                    )
                  : const Icon(Icons.wifi_tethering),
              label: Text(_testing ? 'Testing…' : 'Test Connection'),
              style: FilledButton.styleFrom(
                backgroundColor: cs.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),

          if (_testResult != null) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: _testOk
                    ? Colors.green.withValues(alpha: 0.1)
                    : Colors.red.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: _testOk
                      ? Colors.green.withValues(alpha: 0.4)
                      : Colors.red.withValues(alpha: 0.4),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        _testOk ? Icons.check_circle : Icons.error_outline,
                        size: 16,
                        color: _testOk ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _testResult!,
                          style: TextStyle(
                            color: _testOk ? Colors.green[700] : Colors.red[700],
                            fontSize: 13,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (_agentModel.isNotEmpty) ...[
                    const SizedBox(height: 6),
                    Text(
                      'Model: $_agentModel',
                      style: TextStyle(
                        fontSize: 12,
                        color: cs.onSurface.withValues(alpha: 0.6),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],

          const SizedBox(height: 24),
          _sectionHeader('How to Use'),
          _card(cs, isDark, [
            _infoRow(
              icon: Icons.terminal,
              title: 'Start your agent',
              subtitle: 'Run  nastech  on your PC/VPS, or use the web dashboard.',
            ),
            const Divider(height: 1),
            _infoRow(
              icon: Icons.link,
              title: 'Enter the URL above',
              subtitle:
                  'Use your machine\'s local IP (192.168.x.x) on the same WiFi, or a public VPS address.',
            ),
            const Divider(height: 1),
            _infoRow(
              icon: Icons.flash_on,
              title: 'Select it as your model',
              subtitle:
                  'Open a chat → tap the model selector → choose NasTech Agent.',
            ),
          ]),

          const SizedBox(height: 24),
          _sectionHeader('What you get'),
          _card(cs, isDark, [
            _featureRow('🧠', '90+ tools', 'Web search, code execution, file access, and more'),
            const Divider(height: 1),
            _featureRow('📚', 'Skills & Memory', 'Agent remembers context across sessions'),
            const Divider(height: 1),
            _featureRow('⏰', 'Cron & Automations', 'Scheduled tasks running unattended'),
            const Divider(height: 1),
            _featureRow('💬', 'Multi-platform', 'Same agent connected to Telegram, Discord, Signal'),
            const Divider(height: 1),
            _featureRow('🔄', 'Real-time streaming', 'See tool calls and responses as they happen'),
          ]),

          const SizedBox(height: 24),
          _sectionHeader('Common Ports'),
          _card(cs, isDark, [
            _portRow('8080', 'Default NasTech Agent web dashboard'),
            const Divider(height: 1),
            _portRow('3000', 'Alternative / development port'),
          ]),

          const SizedBox(height: 32),

          // Quick copy helpers
          _sectionHeader('Quick Fill'),
          Row(
            children: [
              Expanded(
                child: _quickFill(
                  cs,
                  label: 'Local WiFi',
                  hint: 'Enter your machine IP',
                  onTap: () => _showQuickFillDialog(context, 'local'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _quickFill(
                  cs,
                  label: 'VPS / Remote',
                  hint: 'Enter server address',
                  onTap: () => _showQuickFillDialog(context, 'remote'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Future<void> _showQuickFillDialog(BuildContext context, String type) async {
    final controller = TextEditingController();
    final hint = type == 'local' ? '192.168.1.100' : 'my-server.com';
    final result = await showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(type == 'local' ? 'Local WiFi IP' : 'VPS / Remote Host'),
        content: TextField(
          controller: controller,
          autofocus: true,
          keyboardType: TextInputType.url,
          decoration: InputDecoration(
            hintText: hint,
            helperText: 'Port 8080 will be added automatically',
          ),
          onSubmitted: (v) => Navigator.of(ctx).pop(v.trim()),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(ctx).pop(controller.text.trim()),
            child: const Text('Set'),
          ),
        ],
      ),
    );
    if (result != null && result.isNotEmpty) {
      final url = result.startsWith('http')
          ? result
          : 'http://$result:8080';
      setState(() {
        _urlController.text = url;
        _testResult = null;
      });
    }
  }

  // ── UI helpers ────────────────────────────────────────────────────────────

  Widget _sectionHeader(String label) => Padding(
        padding: const EdgeInsets.only(left: 4, bottom: 8, top: 4),
        child: Text(
          label.toUpperCase(),
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.8,
            color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.45),
          ),
        ),
      );

  Widget _card(ColorScheme cs, bool isDark, List<Widget> children) => Container(
        margin: const EdgeInsets.only(bottom: 8),
        decoration: BoxDecoration(
          color: isDark
              ? cs.surface.withValues(alpha: 0.7)
              : cs.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.5)),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: children,
          ),
        ),
      );

  Widget _field({
    required String label,
    required String hint,
    required TextEditingController controller,
    TextInputType keyboardType = TextInputType.text,
    bool obscure = false,
    ValueChanged<String>? onChanged,
  }) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: cs.onSurface.withValues(alpha: 0.55),
            ),
          ),
          const SizedBox(height: 4),
          TextField(
            controller: controller,
            keyboardType: keyboardType,
            obscureText: obscure,
            autocorrect: false,
            onChanged: onChanged,
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: TextStyle(
                fontSize: 13,
                color: cs.onSurface.withValues(alpha: 0.3),
              ),
              border: InputBorder.none,
              isDense: true,
              contentPadding: EdgeInsets.zero,
            ),
            style: const TextStyle(fontSize: 14),
          ),
        ],
      ),
    );
  }

  Widget _infoRow({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 18, color: cs.primary),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                      fontSize: 13, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 2),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _featureRow(String emoji, String title, String subtitle) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 18)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: 13, fontWeight: FontWeight.w600)),
                Text(
                  subtitle,
                  style: TextStyle(
                    fontSize: 12,
                    color: cs.onSurface.withValues(alpha: 0.55),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _portRow(String port, String desc) {
    final cs = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      child: Row(
        children: [
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: cs.primaryContainer.withValues(alpha: 0.5),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              ':$port',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                fontFamily: 'monospace',
                color: cs.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Text(desc,
              style: TextStyle(
                  fontSize: 13,
                  color: cs.onSurface.withValues(alpha: 0.7))),
        ],
      ),
    );
  }

  Widget _quickFill(
    ColorScheme cs, {
    required String label,
    required String hint,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          border: Border.all(color: cs.outlineVariant.withValues(alpha: 0.6)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(Icons.add_circle_outline, size: 16, color: cs.primary),
            const SizedBox(width: 8),
            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.w600),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
