import 'dart:io' show File;
import 'package:flutter/material.dart';

bool fileExistsSync(String path) => File(path).existsSync();

Future<String> readFileAsString(String path) => File(path).readAsString();

Widget fileImageWidget(String path, double size) {
  return Image(
    image: FileImage(File(path)),
    width: size,
    height: size,
    fit: BoxFit.cover,
  );
}
