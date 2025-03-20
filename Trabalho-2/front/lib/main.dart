import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:async';
import 'dart:ui' as ui;
import 'dart:io';
import 'package:http/http.dart' as http;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();

  final frontCamera = cameras.firstWhere(
    (camera) => camera.lensDirection == CameraLensDirection.front,
    orElse: () => cameras.first,
  );

  runApp(MyApp(camera: frontCamera));
}

class MyApp extends StatelessWidget {
  final CameraDescription camera;

  const MyApp({Key? key, required this.camera}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sensor de Proximidade com Câmera',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: ProximitySensorScreen(camera: camera),
    );
  }
}

class ProximitySensorScreen extends StatefulWidget {
  final CameraDescription camera;

  const ProximitySensorScreen({Key? key, required this.camera})
    : super(key: key);

  @override
  _ProximitySensorScreenState createState() => _ProximitySensorScreenState();
}

class _ProximitySensorScreenState extends State<ProximitySensorScreen> {
  late CameraController _controller;
  bool _isNear = false;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }

  void _initializeCamera() async {
    _controller = CameraController(widget.camera, ResolutionPreset.medium);
    await _controller.initialize();
    _startFrameAnalysis();
  }

  void _startFrameAnalysis() {
    _timer = Timer.periodic(Duration(milliseconds: 500), (timer) async {
      if (!_controller.value.isInitialized) return;

      try {
        final frame = await _controller.takePicture();
        final image = await decodeImageFromList(await frame.readAsBytes());

        final brightness = await _calculateBrightness(image);
        print('Luminosidade: $brightness');

        setState(() {
          _isNear = brightness < 100;
        });

        if (_isNear) {
          _sendImage(File(frame.path));
        }
      } catch (e) {
        print('Erro ao capturar ou analisar o frame: $e');
      }
    });
  }

  Future<double> _calculateBrightness(ui.Image image) async {
    final byteData = await image.toByteData();
    if (byteData == null) return 0;

    final pixels = byteData.buffer.asUint8List();
    double brightness = 0;

    for (int i = 0; i < pixels.length; i += 4) {
      final r = pixels[i];
      final g = pixels[i + 1];
      final b = pixels[i + 2];
      brightness += (0.299 * r + 0.587 * g + 0.114 * b);
    }
    brightness /= (image.width * image.height);

    return brightness;
  }

  Future<void> _sendImage(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('http://192.168.1.100:8000/image'), // URL DO BACK
    );
    request.files.add(
      await http.MultipartFile.fromPath('image', imageFile.path),
    );

    try {
      var response = await request.send();
      if (response.statusCode == 200) {
        print('Imagem enviada com sucesso!');
      } else {
        print('Erro ao enviar imagem: ${response.statusCode}');
      }
    } catch (e) {
      print('Erro ao conectar ao backend: $e');
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _isNear ? Colors.red : Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              _isNear ? 'Objeto próximo!' : 'Nenhum objeto próximo',
              style: TextStyle(
                fontSize: 24,
                color: _isNear ? Colors.white : Colors.black,
              ),
            ),
            SizedBox(height: 20),
            Container(
              width: 200,
              height: 200,
              child: CameraPreview(_controller),
            ),
          ],
        ),
      ),
    );
  }
}
