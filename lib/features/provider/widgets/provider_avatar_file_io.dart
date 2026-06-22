import 'dart:io' show File;
export 'dart:io' show File;

bool fileExistsSync(String path) => File(path).existsSync();
Future<String> readFileAsString(String path) => File(path).readAsString();
