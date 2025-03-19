package com.example.trabalho2_sd.utils

import android.content.Context
import android.os.Environment
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.core.content.ContextCompat
import java.io.File
import java.text.SimpleDateFormat
import java.util.Locale

object CameraUtils {

    private var imageCapture: ImageCapture? = null

    fun captureImage(context: Context, onImageCaptured: (File?) -> Unit) {
        val file = createImageFile(context)
        if (file == null) {
            onImageCaptured(null)
            return
        }

        val outputOptions = ImageCapture.OutputFileOptions.Builder(file).build()

        imageCapture?.takePicture(
            outputOptions,
            ContextCompat.getMainExecutor(context),
            object : ImageCapture.OnImageSavedCallback {
                override fun onImageSaved(output: ImageCapture.OutputFileResults) {
                    onImageCaptured(file) // Retorna o arquivo quando a captura for concluída
                }

                override fun onError(exc: ImageCaptureException) {
                    onImageCaptured(null)
                }
            }
        )
    }

    private fun createImageFile(context: Context): File? {
        val storageDir = context.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return try {
            File.createTempFile(
                "JPEG_${SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(System.currentTimeMillis())}_",
                ".jpg",
                storageDir
            )
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
}
