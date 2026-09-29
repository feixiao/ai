# 06. Google Flow / Veo 视频生成与 1000 积分攻略

Google Flow 与 VideoFX 是基于 Google 旗舰视频生成大模型 **Veo** 构建的视觉生成工作台。Veo 在物理模拟真实性（重力、流体、光线折射）、主体一致性以及影视级运镜控制上表现极为出色。面对每月赠送的 1000 积分配额，通过科学的工作流设计，可以彻底告别盲目试错，将每一分积分转化为高品质的可视化资产。

---

## 1. Veo 核心生成优势与技术特性

与其他视频生成模型相比，Veo 具备以下显著特征：
1. **精准物理规律模拟**：自然呈现水体波浪、光影漫反射、布料摆动与烟尘扩散，避免传统 AI 视频常见的“物体融化”与空间塌陷。
2. **专业电影运镜指令理解**：原生理解专业电影摄影术语（如 Dolly Zoom, Pan, Tilt, Aerial Tracking, Slow Motion），能够严格按照机位轨迹运动。
3. **极佳的多模态一致性**：支持以高精图片（如 Imagen 3 生成的原图）作为关键帧首帧生成视频（Image-to-Video），确保人物、产品或场景构图高度一致。

---

## 2. 积分最大化策略：拒绝盲目文生视频（Text-to-Video）

每月 1000 积分看似充裕，但如果直接用纯文字无节制“抽卡”，极易因构图偏差而迅速耗尽配额。推荐采用 **三步渐进式低消耗流水线**：

```
[步骤 1: 零积分/极低消耗]
在 Imagen 3 / 绘图工具中生成静态分镜图片
确定光影、主体结构与构图
          │
          ▼
[步骤 2: 精准图生视频 (I2V)]
将满意的静态分镜作为首帧上传
附加精确的镜头运动提示词（Camera Prompt）
生成 5~8 秒基础动态切片
          │
          ▼
[步骤 3: 关键片段扩展 (Extend)]
仅对符合预期的成功切片追加镜头延展
最终导入本地剪辑工具（如 FFMPEG / 剪映）合成完整短片
```

---

## 3. 影视级视频提示词结构（5 要素法则）

写好 Veo 视频提示词的核心在于区分“静态元素”与“动态轨迹”：

| 提示词模块 | 核心作用 | 示例关键词 |
| :--- | :--- | :--- |
| **1. 画面主体 (Subject)** | 明确画面聚焦的核心对象及其材质、外观 | *A futuristic semiconductor fabrication cleanroom, robotic arms, glowing silicon wafers* |
| **2. 环境与氛围 (Environment)** | 交代环境深度、天气、粒子与空间构图 | *Steaming nitrogen fog, ultra-clean industrial facility, deep volumetric lighting* |
| **3. 运镜轨迹 (Camera)** | 明确机位运动方式、速度与视角角度 | *Cinematic slow dolly-in, camera smoothly tracks forward, low-angle perspective* |
| **4. 光影与色彩 (Lighting/Tone)**| 设定色温、主光源与电影质感 | *Cool blue and clean white neon illumination, cinematic anamorphic lens flare, 8k render* |
| **5. 物理动态 (Motion/Physics)** | 明确物体的动作幅度与速度节奏 | *Robotic arms precisely assembling parts, realistic mechanical sparks, ultra-smooth 60fps* |

---

## 4. 业务落地场景实战

### 4.1 场景一：投研路演与赛道科普视频（半导体前沿制程）
- **目标**：在制作先进封装或前沿半导体研报路演时，生动的 3D 级别动态展示能极大提升报告的专业度与冲击力。
- **实战提示词**：
  ```markdown
  A cinematic, ultra-detailed macro shot inside an advanced semiconductor packaging facility. 
  A glowing microscopic chip die is being seamlessly bonded using precision robotic vacuum needles. 
  Camera slowly orbits around the silicon chip in a 360-degree rotation, highlighting the intricate copper micro-bumps and reflective circuitry. 
  Diffuse cinematic laboratory lighting, high-tech teal and gold reflections, realistic physics, smooth slow motion, photorealistic 8k.
  ```

### 4.2 场景二：全栈软件系统与架构概念演示（分布式网络）
- **目标**：为自己的全栈开源项目或企业级产品制作官网 Hero 动态背景与架构演化动效。
- **实战提示词**：
  ```markdown
  Abstract visualization of global high-speed fiber data streams converging into a centralized server hub. 
  Glowing laser-like data packets flowing through transparent glass nodes suspended in dark space. 
  Camera pulls back with an expansive smooth crane shot, revealing a massive interconnected neural cloud network. 
  Cyberpunk deep blue and bright violet glow, depth of field, ray-traced reflections, highly polished corporate tech showcase style.
  ```

---

## 5. 防废片避坑指南

1. **避免单提示词包含过多相互冲突的动作**：
   - 错误范例：“一个男人跑进房间，坐下喝咖啡，然后站起来拉开窗帘并在纸上写字”（动作过多会导致肢体畸变）。
   - 正确做法：将复杂动作拆分为多个 5 秒分镜，每个分镜只专注一个单一流畅的动作。
2. **善用机位速度修饰词**：
   - 在机位指令中加入 `smooth`（平稳）、`steady`（稳定）、`cinematic slow`（电影级慢速），能够显著抑制画面抖动与畸变。
3. **优先使用图生视频锁定人物脸部与品牌标识**：
   - 纯文生视频在长镜头中很难维持同一张人脸或特定产品 Logo 的一致性，先用静态画作确认构图后再启动视频化是商业落地的铁律。
