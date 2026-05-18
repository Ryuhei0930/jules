package com.example.mediapipe_image_gen_android

import android.graphics.Bitmap
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.ByteArrayOutputStream

class MainActivity: FlutterActivity() {
    private val CHANNEL = "com.example.mediapipe/image_gen"
    private var helper: ImageGenerationHelper? = null

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)

        helper = ImageGenerationHelper(context)
        // Set a default model path where user should push the converted weights
        // e.g. adb push <output_path>/. /data/local/tmp/image_generator/bins
        val defaultModelPath = "/data/local/tmp/image_generator/bins"
        helper?.initialize(defaultModelPath)

        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            if (call.method == "generateImage") {
                val prompt = call.argument<String>("prompt")
                if (prompt != null) {
                    // Run generation on a background thread
                    Thread {
                        val bitmap = helper?.generate(prompt)
                        runOnUiThread {
                            if (bitmap != null) {
                                val stream = ByteArrayOutputStream()
                                bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
                                val byteArray = stream.toByteArray()
                                result.success(byteArray)
                            } else {
                                result.error("UNAVAILABLE", "Failed to generate image.", null)
                            }
                        }
                    }.start()
                } else {
                    result.error("INVALID_ARGUMENT", "Prompt cannot be null", null)
                }
            } else {
                result.notImplemented()
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        helper?.close()
    }
}
