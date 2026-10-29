// Android (Pixel 10) CameraX + LiteRT 零拷贝极速推理模板
class EdgeVisionAnalyzer(private val context: Context) : ImageAnalysis.Analyzer {
    private val litertEngine by lazy {
        LiteRtModel.load(
            context = context,
            assetPath = "models/qwen2.5_vl_3b_w4a16.task",
            delegate = AcceleratorDelegate.TENSOR_G5_NPU
        )
    }

    override fun analyze(imageProxy: ImageProxy) {
        // 1. 硬件级零拷贝提取图像缓冲区
        val hardwareBuffer = imageProxy.image?.hardwareBuffer
        if (hardwareBuffer != null) {
            // 2. 直通 NPU 执行 INT4 视觉多模态推理
            val result = litertEngine.inferVisionToken(hardwareBuffer, "检测违章行为")
            Log.i("Pixel10AI", "端侧分析结果: ${result.summary}, 延迟: ${result.latencyMs}ms")
        }
        imageProxy.close() // 务必关闭，归还 CameraX 帧环形缓冲区
    }
}