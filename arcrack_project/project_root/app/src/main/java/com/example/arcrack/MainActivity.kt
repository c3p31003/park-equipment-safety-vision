package com.example.arcrack

import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.example.armeasureapp.FlaskApi
import com.example.armeasureapp.RetrofitClient
import com.google.ar.core.Anchor
import com.google.ar.core.HitResult
import com.google.ar.sceneform.AnchorNode
import com.google.ar.sceneform.math.Vector3
import com.google.ar.sceneform.rendering.Color
import com.google.ar.sceneform.rendering.MaterialFactory
import com.google.ar.sceneform.rendering.ShapeFactory
import com.google.ar.sceneform.ux.ArFragment
import com.google.ar.sceneform.rendering.ModelRenderable
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import java.io.ByteArrayOutputStream
import java.util.Base64
import kotlin.math.sqrt

class MainActivity : AppCompatActivity() {

    private lateinit var arFragment: ArFragment
    private lateinit var distanceText: TextView
    private lateinit var sendButton: Button
    private var anchorPoints = mutableListOf<Anchor>()
    private var measuredBitmap: Bitmap? = null
    private var measuredDistance: Float = 0f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        arFragment = supportFragmentManager.findFragmentById(R.id.arFragment) as ArFragment
        distanceText = findViewById(R.id.distanceText)
        sendButton = findViewById(R.id.sendButton)

        // === タップで測定開始 ===
        arFragment.setOnTapArPlaneListener { hitResult: HitResult, _, _ ->
            placeAnchorAndMeasure(hitResult)
        }

        // === Flaskに送信 ===
        sendButton.setOnClickListener {
            measuredBitmap?.let { bitmap ->
                sendToFlask(bitmap, measuredDistance)
            }
        }
    }

    private fun placeAnchorAndMeasure(hitResult: HitResult) {
        val anchor = hitResult.createAnchor()

        // --- 【変更】MaterialFactoryで赤い球を作成 ---
        MaterialFactory.makeOpaqueWithColor(this, Color(android.graphics.Color.RED))
            .thenAccept { material ->
                val sphere = ShapeFactory.makeSphere(
                    0.01f,          // 半径1cmの球
                    Vector3.zero(), // 【変更】Vector3.zero()を指定
                    material
                )

                val node = AnchorNode(anchor)
                node.renderable = sphere // 【変更】sphere.get() は不要
                node.setParent(arFragment.arSceneView.scene)

                // アンカーを保存
                if (anchorPoints.size < 2) {
                    anchorPoints.add(anchor)
                }

                // 2点目が登録されたら距離計算
                if (anchorPoints.size == 2) {
                    measuredDistance = calculateDistance(anchorPoints[0], anchorPoints[1])
                    distanceText.text = "距離: %.2f m".format(measuredDistance)

                    // 画像キャプチャ
                    captureARView()
                }
            }
    }

    // --- 距離計算 ---
    private fun calculateDistance(anchor1: Anchor, anchor2: Anchor): Float {
        val pose1 = anchor1.pose
        val pose2 = anchor2.pose
        val dx = pose1.tx() - pose2.tx()
        val dy = pose1.ty() - pose2.ty()
        val dz = pose1.tz() - pose2.tz()
        return sqrt(dx * dx + dy * dy + dz * dz)
    }

    // --- AR画面をビットマップ化 ---
    private fun captureARView() {
        val view = arFragment.arSceneView
        val bitmap = Bitmap.createBitmap(view.width, view.height, Bitmap.Config.ARGB_8888)

        // 【変更】PixelCopy用の正しい記述
        android.view.PixelCopy.request(
            view,
            bitmap,
            { copyResult ->
                if (copyResult == android.view.PixelCopy.SUCCESS) {
                    measuredBitmap = bitmap
                }
            },
            android.os.Handler(mainLooper)
        )
    }

    // --- Flask APIに送信 ---
    private fun sendToFlask(bitmap: Bitmap, distance: Float) {
        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.PNG, 100, stream)
        val base64Image = Base64.getEncoder().encodeToString(stream.toByteArray())

        val api = RetrofitClient.instance.create(FlaskApi::class.java)
        val call = api.sendMeasurement(base64Image, distance)

        call.enqueue(object : Callback<String> {
            override fun onResponse(call: Call<String>, response: Response<String>) {
                if (response.isSuccessful) {
                    distanceText.text = "結果: ${response.body()}"
                } else {
                    distanceText.text = "エラー: ${response.code()}"
                }
            }

            override fun onFailure(call: Call<String>, t: Throwable) {
                distanceText.text = "通信失敗: ${t.message}"
            }
        })
    }
}
