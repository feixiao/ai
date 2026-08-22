# Mac Studio 上做短剧 / 短视频的落地方案

## 1. 结论

基于当前你已有的 ComfyUI + Wan 2.2 GGUF 工作流，以及 Mac Studio 的统一内存环境，最适合的方案不是“全程一键生成 1 分钟长片”，而是：

- 用 Wan 2.2 I2V 做分镜生成
- 用 T2V 做开场/过渡或动态镜头
- 每个镜头单独生成 3–6 秒
- 最后在剪辑软件里拼接成 15–30 秒短剧/短视频

这套方案最稳妥，也最符合 Mac Studio 的实际产能和已存在的工作流。

---

## 2. 为什么这个方案最适合你

你现有的文档和工作流里，已经明显体现出以下思路：

- 使用 GGUF 量化版模型，降低内存压力
- 利用 Lightning LoRA 压缩推理步数
- 使用分段式双模型架构（高噪 + 低噪）
- 针对 Mac 进行 MPS / Tiled VAE / 低显存优化

这些都说明你已经在做“节省显存 + 强控制 + 分段生成”的模型方案，而这正是短剧/短视频最适合的生产方式。

---

## 3. 可选方案

### 方案 A：最稳妥，适合当前环境

名称：分镜式本地短视频生产线

适用场景：
- 15–30 秒短视频
- 3–6 个镜头
- 有剧情线的短剧
- 人物动作、场景转换明显

流程：
1. 先写 3–6 个分镜
2. 每个镜头准备一张参考图 / 首帧图
3. 用 Wan 2.2 I2V 生成每个镜头
4. 生成后导入剪辑软件做拼接
5. 加字幕、音效、音乐

优点：
- 稳定性最高
- 最符合 Mac Studio
- 更容易控制故事节奏

缺点：
- 不是一键长片
- 需要人工分镜

---

### 方案 B：剧情短剧版

名称：关键帧 + 镜头式剧情生成

适用场景：
- 20–60 秒剧情短片
- 需要连续动作和情绪变化
- 角色/场景需要稳定一致

方法：
- 先用图片生成模型/静态图生成角色、场景封面
- 再用 I2V 生成每个关键动作镜头
- 最后剪辑成故事片段

优点：
- 角色和环境更统一
- 更适合“短剧”叙事

缺点：
- 前期策划更重
- 更需要稳定首帧图

---

### 方案 C：视觉型短视频版

名称：T2V / 动态过渡型生成

适用场景：
- 纯动态场景
- 视觉冲击型广告片
- 不是强叙事剧情

特点：
- 生成速度快
- 更适合做动态场景和节奏型内容

缺点：
- 角色连续性弱
- 不适合复杂剧情

---

## 4. 适合 Mac Studio 的模型路线

### 优先级 1：Wan 2.2 14B GGUF

这是最适合当前环境的路线，理由：
- 更适合统一内存架构
- GGUF 在 Mac 上更稳定
- 手机 / 电脑产能更加现实
- 适配你现有工作流

### 模型建议：
- Wan 2.2 14B GGUF
- Q4 / Q5 量化版本优先
- 配合 Lightning LoRA
- 使用高噪 + 低噪分段采样

---

## 5. 推荐参数

### 生成参数建议
- 分辨率：480p / 640p / 720p
- 帧数：8–16 帧/镜头
- 每个镜头时长：3–5 秒
- CFG：1.0
- Sampler：Euler
- 调度器：Simple
- VAE：Tiled VAE
- Tile Size：512
- 模型：Lightning LoRA 方案优先

### 说明
这组参数比“追求超长长视频 + 4K + 全程大分辨率”更适合 Mac Studio。更重要的是稳定和可控，而不是单纯追求极限分辨率。

---

## 6. 最优的输出结构

### 推荐长度
- 15 秒：最适合首轮测试
- 30 秒：适合正式发布
- 45–60 秒：建议拆成多个场景生成

### 推荐镜头安排
一个 15–20 秒短视频，可以按下面结构来：

- 镜头 1：开场 3–4 秒
- 镜头 2：动作 3–4 秒
- 镜头 3：情绪 / 变化 3–4 秒
- 镜头 4：收尾 3–4 秒

不要追求“一条视频一镜到底”，否则很容易出现画面失控和整体一致性差的问题。

---

## 7. 提示词模板

### 通用公式

[主体] + [动作] + [场景] + [镜头运动] + [光效] + [风格]

### 示例

1. “young woman walking slowly in rainy street, cinematic composition, slow motion, warm neon lighting, realistic film look”
2. “close-up of man turning around in corridor, dramatic light, shallow depth of field, emotional expression”
3. “car driving at night through city, dynamic camera movement, moody atmosphere, cinematic 24fps look”

### 注意事项
对 I2V 来说，重点应该放在：
- 动作
- 场景
- 光线
- 镜头语言
- 情绪

不要写过长的人物特征列表，否则容易崩。

---

## 8. 生产流程（推荐执行顺序）

### 第一步：先定分镜
写 3–6 个镜头，不要太多。

### 第二步：准备首帧图
每个镜头一张参考图，用于控制人物和环境。

### 第三步：用 I2V 生成镜头
对每个镜头都单独生成。不要强行生成一整条长视频。

### 第四步：用 T2V 做开场 / 过渡 / 动态镜头
如果需要更强视觉冲击，可以把 T2V 作为辅助手段。

### 第五步：后期剪辑
在剪辑软件中：
- 拼接镜头
- 加字幕
- 增加音效
- 设定节奏
- 添加 BGM

### 第六步：导出
例如：720p / 24fps 或 30fps

---

## 9. 适合你现在的实际落地方式

### 最推荐的实际路线

- ComfyUI
- Wan 2.2 GGUF
- I2V 为主
- T2V 辅助
- Lightning LoRA
- Tiled VAE
- CapCut / DaVinci Resolve 后期

这是最现实、最稳定、最适配你 Mac Studio 的方式。

---

## 10. 一句总结

如果要一句话概括：

“在你现在的 Mac Studio + ComfyUI + Wan 2.2 GGUF 环境下，最适合做的是‘分镜式短剧’，按镜头逐段生成，再在剪辑软件里拼接成 15–30 秒短视频。”

---

## 11. 单一主 workflow 的合并方案

如果你希望“合并成一个 workflow”，更现实的方式不是直接把几个完全独立的 JSON 文件硬拼在一起，而是做一条“主流程 + 分支扩展”的统一结构。

### 11.1 统一主流程结构

输入层：
- Story Prompt
- Scene Prompt
- First Frame Image
- Negative Prompt
- Resolution
- FPS
- Frame Count

参考图分支：
- T2I / I2I 生成场景图或人物图
- 作为 I2V 的参考首帧

主生成链：
- Load GGUF UNet
- Load VAE
- Load CLIP
- Load LoRA
- KSampler
- VAE Decode (Tiled)
- Save Video

扩展分支：
- T2V 生成开场片段
- T2V 生成过渡镜头
- 作为整体短剧的导入与转场

输出层：
- Video Combine
- FFmpeg
- Export MP4

### 11.2 一条“合并版”workflow 的设计思路

- 以 Wan 2.2 I2V 为主链路：这是最关键的主体镜头生成能力
- T2V 作为辅助链路：负责开场 / 过渡 / 强视觉动态片段
- T2I / I2I 作为前置分支：制造首帧图、题图、人物图、场景图
- 最终输出统一为一个短视频项目

这样做的优点是：
- 一次打开就能走主流程
- 便于镜头拆分和批量生成
- 更适合短剧 / 短视频生产
- 稳定性高于“全能大 workflow”

### 11.3 最现实的判断

对于你当前的 Mac Studio 环境，真正可执行的合并方案不是“一个大而全的 JSON”，而是：

- 单一主 workflow：I2V 主链
- 可选分支：T2V / T2I / I2I
- 一条生产线：输入文案 → 生成首帧 → 生成镜头 → 拼接成视频

这比硬拼所有节点更稳定，也更利于批量做内容。

---

## 12. 合并版 workflow 结构图

```text
                               ┌─────────────────────┐
                               │  输入：脚本 / 文案   │
                               │  prompt + scene     │
                               └──────────┬──────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────────────────┐
                    │      参考图分支（T2I / I2I）                 │
                    │  生成角色图 / 场景图 / 首帧图               │
                    └───────────────┬─────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────────────┐
                    │      主流程：Wan 2.2 I2V 视频生成            │
                    │  1. Load GGUF UNet                          │
                    │  2. Load VAE / CLIP / LoRA                  │
                    │  3. KSampler + Tiled VAE Decode             │
                    │  4. 生成每个镜头（3–6秒）                  │
                    └───────────────┬─────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────────────┐
                    │      副流程：T2V 开场 / 过渡镜头            │
                    │  生成 2–4 秒动态开场或转场                 │
                    └───────────────┬─────────────────────────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────────────────────┐
                    │      输出合成：Video Combine / FFmpeg      │
                    │      导出 MP4 / 720p / 24fps / 30fps        │
                    └─────────────────────────────────────────────┘
```

---

## 13. 统一 workflow 的实际适配建议

### 主工作流：I2V
- 适合做主体剧情镜头
- 是你的核心生产链
- 最值得作为主节点链路保留

### 辅工作流：T2V
- 适合做开场、节奏推动、视觉冲击镜头
- 可以独立生成，再拼接到主镜头前后

### 参考工作流：T2I / I2I
- 适合做封面、人物、道具、场景图
- 作为首帧输入，稳定后续视频动作

### 最终落地方式
- 在单一项目里保留三条逻辑分支
- 让它们在同一个工程中进行串接
- 使用同一个 prompt 规范和模型目录

这样最适应你当前目录中已经存在的几份工作流。

---

## 14. 相关文件参考

- [ComfyUI/Wan2.2_ComfyUI_MacStudio_安装测试指南.md](ComfyUI/Wan2.2_ComfyUI_MacStudio_安装测试指南.md)
- [ComfyUI/工作流.md](ComfyUI/工作流.md)
- [ComfyUI/Z-Image-Turbo_ComfyUI_GGUF_部署指南.md](ComfyUI/Z-Image-Turbo_ComfyUI_GGUF_部署指南.md)
- [ComfyUI/wan22BasicGGUF720p_v10/WAN22 14B I2V.json](ComfyUI/wan22BasicGGUF720p_v10/WAN22%2014B%20I2V.json)
- [ComfyUI/wan22BasicGGUF720p_v10/WAN22 14B T2V.json](ComfyUI/wan22BasicGGUF720p_v10/WAN22%2014B%20T2V.json)
- [ComfyUI/z-image-turbo-t2i.json](ComfyUI/z-image-turbo-t2i.json)
- [ComfyUI/z-image-turbo-i2i.json](ComfyUI/z-image-turbo-i2i.json)


- [ComfyUI/Wan2.2_ComfyUI_MacStudio_安装测试指南.md](ComfyUI/Wan2.2_ComfyUI_MacStudio_安装测试指南.md)
- [ComfyUI/工作流.md](ComfyUI/工作流.md)
- [ComfyUI/Z-Image-Turbo_ComfyUI_GGUF_部署指南.md](ComfyUI/Z-Image-Turbo_ComfyUI_GGUF_部署指南.md)
- [ComfyUI/wan22BasicGGUF720p_v10/WAN22 14B I2V.json](ComfyUI/wan22BasicGGUF720p_v10/WAN22%2014B%20I2V.json)
- [ComfyUI/wan22BasicGGUF720p_v10/WAN22 14B T2V.json](ComfyUI/wan22BasicGGUF720p_v10/WAN22%2014B%20T2V.json)

