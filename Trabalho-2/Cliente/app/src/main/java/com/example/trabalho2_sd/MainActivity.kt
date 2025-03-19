package com.example.trabalho2_sd

import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.trabalho2_sd.utils.CameraUtils
import com.example.trabalho2_sd.utils.NetworkUtils

class MainActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager
    private var proximitySensor: Sensor? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        proximitySensor = sensorManager.getDefaultSensor(Sensor.TYPE_PROXIMITY)

        if (proximitySensor == null) {
            Toast.makeText(this, "Sensor de proximidade não disponível", Toast.LENGTH_SHORT).show()
        }
    }

    override fun onResume() {
        super.onResume()
        proximitySensor?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)
    }

    override fun onSensorChanged(event: SensorEvent?) {
        if (event?.sensor?.type == Sensor.TYPE_PROXIMITY) {
            val distance = event.values[0]
            if (distance < (proximitySensor?.maximumRange ?: 0f)) {
                // Intruso detectado
                Toast.makeText(this, "Intruso detectado!", Toast.LENGTH_SHORT).show()

                // Captura uma foto
                CameraUtils.captureImage(this) { imageFile ->
                    if (imageFile != null) {
                        // Envia a foto para o servidor
                        NetworkUtils.sendImageToServer(this, imageFile)
                    } else {
                        runOnUiThread {
                            Toast.makeText(this, "Erro ao capturar imagem.", Toast.LENGTH_SHORT).show()
                        }
                    }
                }
            }
        }
    }

    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
}
