part of '../chat_api_service.dart';

/// NasTech Agent WebSocket stream.
///
/// Connects to the agent's tui_gateway at [config.baseUrl]/api/ws using
/// newline-delimited JSON-RPC — the same wire protocol used by the TUI.
///
/// Supported server → client events:
///   gateway.ready          – connection confirmed
///   gateway.stream         – {"delta": "text"}
///   gateway.thinking       – {"delta": "reasoning text"}
///   gateway.tool_start     – {"tool": name, "input": {…}}
///   gateway.tool_end       – {"tool": name, "output": "…", "error": bool}
///   gateway.done           – turn finished
///   gateway.error          – {"message": "…"}
///
/// Client → server:
///   {"jsonrpc":"2.0","id":"<uuid>","method":"send_message",
///    "params":{"text":"…","session_id":"…"}}

Stream<ChatStreamChunk> _sendNasTechAgentStream(
  ProviderConfig config,
  String modelId,
  List<Map<String, dynamic>> messages, {
  String? requestId,
}) async* {
  final baseUrl = config.baseUrl.trim().replaceAll(RegExp(r'/$'), '');
  if (baseUrl.isEmpty) {
    yield ChatStreamChunk(
      content: '⚠️ NasTech Agent URL is not configured. Go to Settings → NasTech Agent to set your agent host.',
      isDone: true,
      totalTokens: 0,
    );
    return;
  }

  // Convert http(s) to ws(s)
  final wsBase = baseUrl
      .replaceFirst(RegExp(r'^https://'), 'wss://')
      .replaceFirst(RegExp(r'^http://'), 'ws://');
  final wsUri = Uri.tryParse('$wsBase/api/ws');
  if (wsUri == null) {
    yield ChatStreamChunk(
      content: '⚠️ Invalid agent URL: $baseUrl',
      isDone: true,
      totalTokens: 0,
    );
    return;
  }

  // Extract last user message text
  final lastUserMsg = messages.lastWhere(
    (m) => m['role'] == 'user',
    orElse: () => {},
  );
  final userText = _extractTextFromMessage(lastUserMsg);

  // Build system prompt from messages if present
  final systemMsg = messages.firstWhere(
    (m) => m['role'] == 'system',
    orElse: () => {},
  );
  final systemText = _extractTextFromMessage(systemMsg);

  // Session ID – reuse requestId if available so turns chain correctly
  final sessionId = (requestId ?? '').isNotEmpty ? requestId! : const Uuid().v4();
  final rpcId = const Uuid().v4();

  WebSocket? ws;
  final StringBuffer contentBuffer = StringBuffer();
  final StringBuffer reasoningBuffer = StringBuffer();
  final List<ToolCallInfo> toolCalls = [];
  final List<ToolResultInfo> toolResults = [];

  try {
    final headers = <String, dynamic>{};
    final apiKey = config.apiKey.trim();
    if (apiKey.isNotEmpty) {
      headers['Authorization'] = 'Bearer $apiKey';
    }

    ws = await WebSocket.connect(
      wsUri.toString(),
      headers: headers.isNotEmpty ? headers : null,
    ).timeout(
      const Duration(seconds: 15),
      onTimeout: () => throw TimeoutException('Cannot reach agent at $baseUrl — is it running?'),
    );

    // Wait for gateway.ready then send message
    bool ready = false;
    bool done = false;
    String? pendingToolName;
    Map<String, dynamic>? pendingToolInput;
    String? pendingToolId;

    final outbound = jsonEncode({
      'jsonrpc': '2.0',
      'id': rpcId,
      'method': 'send_message',
      'params': {
        'text': userText,
        if (systemText.isNotEmpty) 'system': systemText,
        'session_id': sessionId,
        if (modelId.isNotEmpty) 'model': modelId,
      },
    });

    await for (final raw in ws) {
      if (done) break;
      Map<String, dynamic> frame;
      try {
        frame = jsonDecode(raw as String) as Map<String, dynamic>;
      } catch (_) {
        continue;
      }

      final method = frame['method'] as String? ?? '';
      final params = frame['params'] as Map<String, dynamic>? ?? {};
      final result = frame['result'] as Map<String, dynamic>?;

      // Combine params and result for event data
      final data = params.isNotEmpty ? params : (result ?? {});

      switch (method) {
        case 'gateway.ready':
          if (!ready) {
            ready = true;
            ws!.add(outbound);
          }

        case 'gateway.stream':
          final delta = data['delta'] as String? ?? '';
          if (delta.isNotEmpty) {
            contentBuffer.write(delta);
            yield ChatStreamChunk(
              content: delta,
              isDone: false,
              totalTokens: 0,
            );
          }

        case 'gateway.thinking':
          final delta = data['delta'] as String? ?? '';
          if (delta.isNotEmpty) {
            reasoningBuffer.write(delta);
            yield ChatStreamChunk(
              content: '',
              reasoning: delta,
              isDone: false,
              totalTokens: 0,
            );
          }

        case 'gateway.tool_start':
          pendingToolName = data['tool'] as String? ?? data['name'] as String? ?? 'tool';
          pendingToolId = const Uuid().v4();
          final input = data['input'];
          pendingToolInput = input is Map<String, dynamic>
              ? input
              : {'input': input?.toString() ?? ''};
          // Yield tool call so UI can show it immediately
          final tc = ToolCallInfo(
            id: pendingToolId!,
            name: pendingToolName!,
            arguments: pendingToolInput!,
          );
          toolCalls.add(tc);
          yield ChatStreamChunk(
            content: '',
            isDone: false,
            totalTokens: 0,
            toolCalls: [tc],
          );

        case 'gateway.tool_end':
          final toolName = data['tool'] as String? ?? data['name'] as String? ?? pendingToolName ?? 'tool';
          final output = data['output']?.toString() ?? '';
          final isError = data['error'] == true;
          final tr = ToolResultInfo(
            id: pendingToolId ?? const Uuid().v4(),
            name: toolName,
            arguments: pendingToolInput ?? {},
            content: isError ? '❌ $output' : output,
          );
          toolResults.add(tr);
          pendingToolName = null;
          pendingToolInput = null;
          pendingToolId = null;
          yield ChatStreamChunk(
            content: '',
            isDone: false,
            totalTokens: 0,
            toolResults: [tr],
          );

        case 'gateway.done':
          done = true;

        case 'gateway.error':
          final msg = data['message'] as String? ?? 'Agent returned an error';
          yield ChatStreamChunk(
            content: '\n\n⚠️ $msg',
            isDone: false,
            totalTokens: 0,
          );
          done = true;

        default:
          // Ignore unknown events (heartbeat, status, etc.)
          break;
      }

      if (done) break;
    }

    // Emit final done chunk
    yield ChatStreamChunk(
      content: '',
      isDone: true,
      totalTokens: 0,
      toolCalls: toolCalls.isEmpty ? null : toolCalls,
      toolResults: toolResults.isEmpty ? null : toolResults,
    );
  } on TimeoutException catch (e) {
    yield ChatStreamChunk(
      content: '⚠️ ${e.message ?? 'Connection timed out. Make sure NasTech Agent is running and reachable.'}',
      isDone: true,
      totalTokens: 0,
    );
  } on SocketException catch (e) {
    yield ChatStreamChunk(
      content: '⚠️ Cannot connect to NasTech Agent at $baseUrl\n${e.message}\n\nMake sure the agent is running and your device can reach it.',
      isDone: true,
      totalTokens: 0,
    );
  } catch (e) {
    yield ChatStreamChunk(
      content: '⚠️ Agent connection error: $e',
      isDone: true,
      totalTokens: 0,
    );
  } finally {
    try {
      await ws?.close();
    } catch (_) {}
  }
}

/// Extract plain text from a message map (handles string content and
/// content-block arrays from the OpenAI message format).
String _extractTextFromMessage(Map<String, dynamic> msg) {
  final content = msg['content'];
  if (content == null) return '';
  if (content is String) return content;
  if (content is List) {
    final parts = <String>[];
    for (final block in content) {
      if (block is Map && block['type'] == 'text') {
        parts.add(block['text']?.toString() ?? '');
      }
    }
    return parts.join('\n');
  }
  return content.toString();
}

