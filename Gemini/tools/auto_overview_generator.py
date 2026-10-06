#!/usr/bin/env python3
"""
Google AI Studio 多模态全套概览自动化生成器 (auto_overview_generator.py)
========================================================================

依托 Google 最新官方统一 `google-genai` (v1.0+) SDK，支持将任意本地长资料：
- PDF / Markdown / Word 文档
- MP3 / WAV / M4A 长录音
- MP4 / MOV 长视频
通过 Google Files API 上传并基于 Gemini 2.5/3.x 原生多模态模型批量生成：

1. 01_briefing_doc.md        - 高管决策备忘录 (Executive Briefing Doc)
2. 02_deep_report.md         - 结构化深度研报 (Comprehensive Research Report)
3. 03_podcast_script.md      - 双人深度对谈播客脚本 (Deep Dive Podcast Script)
4. 04_study_guide_and_faq.md - 概念学习指南与自测题库 (Study Guide, FAQ & Quiz)
5. 05_video_timeline.md      - (仅音视频有效) 带精准时间戳的音画导航 (Video/Audio Chapters)

依赖安装:
    pip install google-genai

使用示例:
    export GEMINI_API_KEY="your_api_key_here"
    python auto_overview_generator.py path/to/document.pdf
    python auto_overview_generator.py path/to/quarterly_meeting.mp4 --out-dir ./reports
"""

import os
import sys
import argparse
import time
from typing import Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[错误] 未检测到 google-genai SDK。请先运行: pip install google-genai", file=sys.stderr)
    sys.exit(1)


def is_media_file(filename: str) -> bool:
    """判断文件是否为音视频文件，以决定是否触发时间戳章节生成"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".mp4", ".mov", ".avi", ".mkv", ".webm"}


def generate_overview_suite(file_path: str, output_dir: str = "output_reports", model_name: str = "gemini-2.5-flash") -> None:
    if not os.path.exists(file_path):
        print(f"[错误] 输入文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[提示] 环境变量 GEMINI_API_KEY 未显式设置，将尝试默认凭证...", file=sys.stderr)

    client = genai.Client()
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n=======================================================")
    print(f"[*] 步骤 1/3: 正在上传本地多模态素材至 Google AI Studio...")
    print(f"[*] 文件路径: {file_path}")
    print(f"=======================================================")

    start_upload = time.time()
    uploaded_file = client.files.upload(file=file_path)
    upload_cost = time.time() - start_upload
    print(f"[+] 上传成功! (耗时 {upload_cost:.2f}s)")
    print(f"    - Remote URI : {uploaded_file.uri}")
    print(f"    - MIME Type  : {uploaded_file.mime_type}")
    print(f"    - Size (B)   : {uploaded_file.size_bytes}")

    # 针对大视频文件，等待其在云端转码处理就绪
    if uploaded_file.state == "PROCESSING":
        print("[*] 文件正在云端转码预处理，等待就绪...")
        while uploaded_file.state == "PROCESSING":
            time.sleep(5)
            uploaded_file = client.files.get(name=uploaded_file.name)
            print(".", end="", flush=True)
        print()

    if uploaded_file.state == "FAILED":
        print(f"[错误] 云端文件预处理失败: {uploaded_file.error}", file=sys.stderr)
        sys.exit(1)

    print(f"\n=======================================================")
    print(f"[*] 步骤 2/3: 编排 Overview & Reports 生成任务...")
    print(f"[*] 使用模型: {model_name}")
    print(f"=======================================================")

    tasks = [
        {
            "filename": "01_briefing_doc.md",
            "title": "高管决策备忘录 (Executive Briefing Doc)",
            "prompt": (
                "你是一名顶级战略管理咨询顾问。请仔细阅读/观看上传的素材，撰写一份高度精炼、供决策层审阅的《高管决策备忘录》。\n"
                "必须包含以下结构：\n"
                "1. **Executive Summary**：用 3 个无序列表句直击最核心现状、业务影响与推荐方案。\n"
                "2. **Key Strategic Findings**：列出 3~5 项关键事实与数据支撑。\n"
                "3. **Trade-off Matrix (方案权衡矩阵)**：以 Markdown 表格对比候选方案的【收益】、【成本】、【落地风险】与【技术债务】。\n"
                "4. **Actionable Next Steps**：明确列出可落地的具体待办事项、建议负责人与推进里程碑。\n"
                "风格务必客观凝练，杜绝空话套话。"
            ),
        },
        {
            "filename": "02_deep_report.md",
            "title": "多模态深度研报 (Comprehensive Research Report)",
            "prompt": (
                "你是一名资深投研与技术架构专家。请通读/观看素材，撰写一份详实深入的万字级《多模态深度研报》。\n"
                "结构规范：\n"
                "1. 引言与宏观背景（行业趋势或系统演进路线）\n"
                "2. 核心架构与机理解析（详尽拆解核心原理，必要时用 ASCII/Mermaid 图解）\n"
                "3. 关键指标与数据穿透对比\n"
                "4. 系统性风险、暗坑与边界条件分析\n"
                "5. 总结与前瞻建议\n"
                "请严格基于源材料内容，所有关键论点务必精准标注引文或出处依据。"
            ),
        },
        {
            "filename": "03_podcast_script.md",
            "title": "双人深度对谈播客脚本 (Deep Dive Podcast Script)",
            "prompt": (
                "你是一名世界顶尖播客制片人。请将素材改写为一份生动通透的双人深度对谈播客脚本（类似 NotebookLM Audio Overview）。\n"
                "主持人角色设定：\n"
                "- **Alex (男，主咖)**: 好奇心强，善于用日常生动比喻通俗化复杂概念，代表普通听众提出疑惑。\n"
                "- **Taylor (女，技术/领域专家)**: 严谨敏锐，善于引用具体数据纠偏主咖的简化假设，提供深度洞察。\n"
                "对话规则：\n"
                "- 融入真实口语习惯，如自然停顿、互相接梗、抢话插话，以及 `[laughs]`, `[pauses thoughtfully]`, `[sighs]` 等声学动作。\n"
                "- 禁止机械化的一问一答，必须通过戏剧性思想碰撞推进话题。\n"
                "- 每句对白显式以 `Alex:` 或 `Taylor:` 开头。"
            ),
        },
        {
            "filename": "04_study_guide_and_faq.md",
            "title": "学习指南、自测题库与 FAQ (Study Guide & Quiz)",
            "prompt": (
                "你是一名资深技术布道师与导师。请根据材料编制一份《学习指南与高频自测题库》。\n"
                "包含以下模块：\n"
                "1. **Glossary (核心概念术语表)**：提炼材料中出现的关键专业术语及通俗定义。\n"
                "2. **10 大核心 FAQ**：站在读者视角预判最关心的 10 个前置关键问题，并给出精准解答。\n"
                "3. **随堂实战模拟测试 (3 道题)**：包含场景选择题与简答题，每道题均须附带详细的参考答案与解析依据。"
            ),
        },
    ]

    # 如果是音视频文件，追加带精确时间戳的章节导读
    if is_media_file(file_path):
        tasks.append({
            "filename": "05_video_timeline.md",
            "title": "精确时间戳音画导航 (Timeline Chapters)",
            "prompt": (
                "你是一名视频/音频内容分析专家。请根据上传的音视频素材，生成一份精确到秒的章节导读与时间线脉络。\n"
                "要求：\n"
                "1. 每一节必须标注标准 [MM:SS] 时间戳（如 [04:15]）。\n"
                "2. 概括该时间段的核心讨论主题与关键结论。\n"
                "3. 如为视频，描述该时间戳下画面出现的关键视觉信息（如 PPT 标题、图表、代码行或操作手势）。"
            ),
        })

    print(f"\n=======================================================")
    print(f"[*] 步骤 3/3: 开始多任务自动化生成并写入磁盘...")
    print(f"=======================================================")

    for idx, task in enumerate(tasks, start=1):
        target_file = os.path.join(output_dir, task["filename"])
        print(f"\n[{idx}/{len(tasks)}] 正在生成: {task['title']} -> {target_file}")
        t_start = time.time()

        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[uploaded_file, task["prompt"]],
                config=types.GenerateContentConfig(
                    temperature=0.3,
                ),
            )
            elapsed = time.time() - t_start

            with open(target_file, "w", encoding="utf-8") as f:
                f.write(response.text)

            print(f"    ✓ 成功生成! (耗时 {elapsed:.2f}s, 大小 {len(response.text)} 字符)")
        except Exception as e:
            print(f"    ✗ 生成失败: {e}", file=sys.stderr)

    print(f"\n[🎉] 全套 Overview 自动化流水线执行完毕！结果保存在: {os.path.abspath(output_dir)}")


def main():
    parser = argparse.ArgumentParser(
        description="Google AI Studio 多模态全套概览自动化生成器 (Audio/Video Overview & Reports)"
    )
    parser.add_argument("file_path", help="待处理的本地文件路径 (支持 PDF, Doc, MP3, WAV, MP4, MOV 等)")
    parser.add_argument("-o", "--out-dir", default="output_reports", help="报告输出目录 (默认: ./output_reports)")
    parser.add_argument("-m", "--model", default="gemini-2.5-flash", help="Gemini 模型版本 (默认: gemini-2.5-flash)")

    args = parser.parse_args()
    generate_overview_suite(file_path=args.file_path, output_dir=args.out_dir, model_name=args.model)


if __name__ == "__main__":
    main()
