import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

/// Ping the agent's status endpoint.
/// Returns null on success, or an error string on failure.
Future<String?> pingNasTechAgent(String baseUrl) async {
  final url = baseUrl.trim().replaceAll(RegExp(r'/$'), '');
  if (url.isEmpty) return 'No URL provided';
  try {
    // Try /api/status first
    for (final path in ['/api/status', '/api/health', '/health']) {
      try {
        final resp = await http
            .get(Uri.parse('$url$path'))
            .timeout(const Duration(seconds: 8));
        if (resp.statusCode == 200) return null;
      } catch (_) {
        continue;
      }
    }
    return 'Agent did not respond on $url — is it running?';
  } on TimeoutException {
    return 'Connection timed out — is the agent running?';
  } on SocketException catch (e) {
    return 'Cannot reach agent: ${e.message}';
  } catch (e) {
    return 'Connection failed: $e';
  }
}

/// Fetch the model the agent is currently configured to use.
/// Returns e.g. "anthropic/claude-opus-4" or empty string.
Future<String> fetchNasTechAgentModel(String baseUrl) async {
  final url = baseUrl.trim().replaceAll(RegExp(r'/$'), '');
  if (url.isEmpty) return '';
  try {
    final resp = await http
        .get(Uri.parse('$url/api/status'))
        .timeout(const Duration(seconds: 8));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body);
      if (data is Map) {
        return data['model']?.toString() ??
            data['current_model']?.toString() ??
            data['config']?['model']?.toString() ??
            '';
      }
    }
  } catch (_) {}
  return '';
}
