class File {
  final String path;
  File(this.path);
}

bool fileExistsSync(String path) => false;
Future<String> readFileAsString(String path) async => '';
