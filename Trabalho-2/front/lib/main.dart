import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'dart:async';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart'; // Import for MediaType
import 'package:audioplayers/audioplayers.dart'; // For playing alarm sound
import 'package:proximity_sensor/proximity_sensor.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();

  final frontCamera = cameras.firstWhere(
    (camera) => camera.lensDirection == CameraLensDirection.front,
    orElse: () => cameras.first, // Fallback to first camera
  );

  runApp(MyApp(camera: frontCamera));
}

class MyApp extends StatelessWidget {
  final CameraDescription camera;

  const MyApp({Key? key, required this.camera}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Proximity Sensor with Camera',
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
  bool _isAlarmActive = false; // Controls the local alarm
  final AudioPlayer _audioPlayer = AudioPlayer(); // Audio player
  final String serverUrl = 'http://10.180.47.250:8000'; // Replace with your server URL

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    _initializeProximitySensor();
  }

  void _initializeCamera() async {
    _controller = CameraController(widget.camera, ResolutionPreset.medium);
    await _controller.initialize();
    if (mounted) {
      setState(() {});
    }
  }

  void _initializeProximitySensor() {
    ProximitySensor.events.listen((int event) {
      setState(() {
        _isNear = (event > 0);
        if (_isNear && !_isAlarmActive) {
          _activateAlarm();
          _sendImage(); // Send image when proximity is detected
        }
      });
    });
  }


  void _activateAlarm() async {
  print("🔊 Local alarm activated!");
  setState(() {
    _isAlarmActive = true;
  });

  // Configura o modo de liberação para loop ANTES de tocar o som.
  await _audioPlayer.setReleaseMode(ReleaseMode.loop);
  await _audioPlayer.play(AssetSource('alarm_sound.mp3'), mode: PlayerMode.lowLatency);
  }

  void _deactivateAlarm() async {
    print("🔇 Local alarm deactivated!");
    setState(() {
      _isAlarmActive = false;
    });
    _deactivateAlarmServe();
    await _audioPlayer.stop(); // Stop the alarm
  }

  void _deactivateAlarmServe() async {
    print("Serve alarm deactivated!");

    try {
      final response = await http.get(Uri.parse('http://10.180.47.250:8000/stop')); // URL DO BACK

      if (response.statusCode == 200) {
        // Imagem recebida com sucesso!
        print('Imagem recebida com sucesso!');

      await _audioPlayer.stop(); // Stop the alarm
      }
    } catch (e) {
      print('Erro ao conectar ao backend: $e');
    }
  }

  Future<void> _sendImage() async {
    if (_controller.value.isInitialized) {
       print("📤 Sending image to the server...");
      try {
        XFile image = await _controller.takePicture();
        _uploadImage(image);
      } catch (e) {
        print("❌ Error capturing image: $e");
      }
    }
  }


  Future<void> _uploadImage(XFile imageFile) async {

    var request = http.MultipartRequest(
      'POST',
      Uri.parse('http://10.180.47.250:8000/image'), // URL DO BACK
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
    _controller.dispose();
    _audioPlayer.dispose();
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
            if (_controller.value.isInitialized)
              Container(
                width: 200,
                height: 200,
                child: CameraPreview(_controller),
              ),
            SizedBox(height: 20),
            if (_isAlarmActive)
              ElevatedButton(
                onPressed: _deactivateAlarm,
                child: Text('Desativar Alarme'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }
}