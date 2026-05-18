import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:typed_data';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'MediaPipe Image Gen',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const ImageGenScreen(),
    );
  }
}

class ImageGenScreen extends StatefulWidget {
  const ImageGenScreen({super.key});

  @override
  State<ImageGenScreen> createState() => _ImageGenScreenState();
}

class _ImageGenScreenState extends State<ImageGenScreen> {
  static const platform = MethodChannel('com.example.mediapipe/image_gen');

  final TextEditingController _promptController = TextEditingController();
  Uint8List? _generatedImage;
  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _generateImage() async {
    final prompt = _promptController.text;
    if (prompt.isEmpty) return;

    setState(() {
      _isLoading = true;
      _errorMessage = '';
      _generatedImage = null;
    });

    try {
      final Uint8List result = await platform.invokeMethod('generateImage', {'prompt': prompt});
      setState(() {
        _generatedImage = result;
      });
    } on PlatformException catch (e) {
      setState(() {
        _errorMessage = "画像生成に失敗しました: \${e.message}\\nモデルが /data/local/tmp/image_generator/bins に配置されているか確認してください。";
      });
    } catch (e) {
      setState(() {
        _errorMessage = "予期せぬエラーが発生しました: \$e";
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('MediaPipe Local Image Gen'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _promptController,
              decoration: const InputDecoration(
                labelText: 'プロンプトを入力してください',
                border: OutlineInputBorder(),
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _generateImage,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('画像を生成する'),
            ),
            const SizedBox(height: 16),
            if (_errorMessage.isNotEmpty)
              Text(
                _errorMessage,
                style: const TextStyle(color: Colors.red),
              ),
            const SizedBox(height: 16),
            Expanded(
              child: Center(
                child: _generatedImage != null
                    ? Image.memory(_generatedImage!)
                    : const Text('ここに生成された画像が表示されます'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
