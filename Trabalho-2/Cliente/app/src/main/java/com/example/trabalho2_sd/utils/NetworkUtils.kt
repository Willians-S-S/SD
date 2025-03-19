package com.example.trabalho2_sd.utils

import android.content.Context
import android.widget.Toast
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException

object NetworkUtils {

    private val client = OkHttpClient()

    fun sendImageToServer(context: Context, imageFile: File) {
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart(
                "image",
                imageFile.name,
                imageFile.asRequestBody("image/jpeg".toMediaTypeOrNull()) // Forma correta no OkHttp 4.x
            )
            .build()

        val request = Request.Builder()
            .url("http://0.0.0.0:8000/image") // Substitua pelo IP do seu servidor
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                (context as? android.app.Activity)?.runOnUiThread {
                    Toast.makeText(context, "Falha ao enviar a imagem para o servidor.", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                val responseBody = response.body?.string()
                (context as? android.app.Activity)?.runOnUiThread {
                    if (response.isSuccessful) {
                        Toast.makeText(context, "Imagem enviada com sucesso! Resposta: $responseBody", Toast.LENGTH_SHORT).show()
                    } else {
                        Toast.makeText(context, "Erro ao enviar a imagem. Código: ${response.code}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }
}
