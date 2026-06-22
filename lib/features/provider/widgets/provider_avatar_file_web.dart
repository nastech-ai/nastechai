import 'dart:async';
import 'package:flutter/widgets.dart';

class File {
  final String path;
  File(this.path);
  bool existsSync() => false;
  Future<String> readAsString() async => '';
}

class FileImage extends ImageProvider<FileImage> {
  final File file;
  const FileImage(this.file);

  @override
  Future<FileImage> obtainKey(ImageConfiguration configuration) async => this;

  @override
  ImageStreamCompleter loadImage(FileImage key, ImageDecoderCallback decode) {
    throw UnsupportedError('FileImage is not supported on web');
  }
}
