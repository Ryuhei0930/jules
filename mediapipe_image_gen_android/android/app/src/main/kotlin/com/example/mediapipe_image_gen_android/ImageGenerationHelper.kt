package com.example.mediapipe_image_gen_android

import android.content.Context
import android.graphics.Bitmap
import android.util.Log
import com.google.mediapipe.tasks.vision.imagegenerator.ImageGenerator
import java.io.File

class ImageGenerationHelper(private val context: Context) {
    private var imageGenerator: ImageGenerator? = null
    private val TAG = "ImageGenerationHelper"

    fun initialize(modelPath: String): Boolean {
        return try {
            val file = File(modelPath)
            if (!file.exists()) {
                Log.e(TAG, "Model directory does not exist: $modelPath")
                return false
            }

            val options = ImageGenerator.ImageGeneratorOptions.builder()
                .setImageGeneratorModelDirectory(modelPath)
                .build()

            imageGenerator = ImageGenerator.createFromOptions(context, options)
            true
        } catch (e: Exception) {
            Log.e(TAG, "Error initializing ImageGenerator: \${e.message}")
            false
        }
    }

    fun generate(prompt: String, iterations: Int = 20, seed: Int = 0): Bitmap? {
        val generator = imageGenerator ?: run {
            Log.e(TAG, "ImageGenerator not initialized")
            return null
        }

        return try {
            val result = generator.generate(prompt, iterations, seed)
            // Extract the bitmap. Note: The API might differ slightly based on the exact version,
            // but BitmapExtractor or similar is mentioned in the docs. If not, the result itself might
            // hold the bitmap. Assuming a structure based on common MediaPipe Tasks API.
            // As per docs: val bitmap = BitmapExtractor.extract(result?.generatedImage())
            // Or if generatedImage returns an MPImage, we need to convert it.
            // For simplicity in this demo, let's assume result provides the bitmap or MPImage to Bitmap conversion is available.
            // The exact conversion depends on the com.google.mediapipe.tasks.vision.imagegenerator.ImageGeneratorResult structure.
            // We will attempt a standard conversion here.

            // As per official docs:
            // val bitmap = BitmapExtractor.extract(result.generatedImage())
            // But since BitmapExtractor might be internal or specific, we will try to get the bitmap directly
            // from the returned MPImage.

            // If the official docs use BitmapExtractor:
            // return com.google.mediapipe.framework.image.BitmapExtractor.extract(result?.generatedImage())
            com.google.mediapipe.framework.image.BitmapExtractor.extract(result?.generatedImage())
        } catch (e: Exception) {
            Log.e(TAG, "Error generating image: \${e.message}")
            null
        }
    }

    fun close() {
        imageGenerator?.close()
        imageGenerator = null
    }
}
