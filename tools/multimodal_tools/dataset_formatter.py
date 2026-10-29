#!/usr/bin/env python3
"""
Multimodal dataset formatting, conversion, and token distribution analytics utility.
Supports:
1. Alpaca format <-> ShareGPT / MLX-VLM format conversion.
2. Token length distribution estimation & truncation risk warning.
3. Train/validation split with deterministic seeding.
4. Schema validation for structured JSON assistant contracts.
Zero third-party dependencies (pure Python).
"""
import argparse
import json
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Tuple

def estimate_tokens(text: str, num_images: int = 1, image_tokens: int = 256) -> int:
    """
    Approximate token count for mixed Chinese/English multimodal prompts.
    - Text: roughly 1 token per 3.5 Chinese characters or 4 ASCII chars.
    - Image: standard patch grid (e.g. 448x448 -> ~256 tokens in Qwen2-VL).
    """
    if not text:
        return num_images * image_tokens
    
    char_count = len(text)
    # Estimate text tokens
    text_tokens = int(char_count / 3.0) + 4
    return text_tokens + (num_images * image_tokens)

def alpaca_to_sharegpt(alpaca_record: Dict[str, Any], image_tag: str = "<image>") -> Dict[str, Any]:
    """Convert an Alpaca-style record (instruction, input, output) to ShareGPT messages."""
    instruction = alpaca_record.get("instruction", "").strip()
    input_text = alpaca_record.get("input", "").strip()
    output_text = alpaca_record.get("output", "").strip()
    image_path = alpaca_record.get("image", None)

    prompt_parts = []
    if image_path or image_tag in instruction or image_tag in input_text:
        if image_tag not in instruction and image_tag not in input_text:
            prompt_parts.append(image_tag)

    if instruction:
        prompt_parts.append(instruction)
    if input_text:
        prompt_parts.append(input_text)

    user_content = "\n".join(prompt_parts)

    messages = [
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": output_text}
    ]

    record = {"messages": messages}
    if image_path:
        record["image"] = image_path
    return record

def validate_multimodal_dataset(filepath: str, max_seq_len: int = 2048) -> Dict[str, Any]:
    """
    Analyze JSONL dataset for formatting validity, token lengths, and schema health.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    total = 0
    valid = 0
    truncated_risk = 0
    token_lengths = []
    structured_json_valid = 0

    with open(p, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            total += 1
            line = line.strip()
            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Check messages format
            if "messages" not in row or not isinstance(row["messages"], list):
                continue
            
            msgs = row["messages"]
            if len(msgs) < 2:
                continue

            user_msg = next((m for m in msgs if m.get("role") == "user"), None)
            asst_msg = next((m for m in msgs if m.get("role") == "assistant"), None)
            if not user_msg or not asst_msg:
                continue

            # Estimate total tokens
            combined_text = user_msg.get("content", "") + " " + asst_msg.get("content", "")
            has_image = "<image>" in user_msg.get("content", "") or "image" in row
            num_imgs = 1 if has_image else 0
            tokens = estimate_tokens(combined_text, num_images=num_imgs)
            token_lengths.append(tokens)

            if tokens > max_seq_len:
                truncated_risk += 1

            # Check if assistant output is valid JSON contract
            try:
                json.loads(asst_msg.get("content", ""))
                structured_json_valid += 1
            except Exception:
                pass

            valid += 1

    avg_tokens = round(sum(token_lengths) / max(len(token_lengths), 1), 1)
    max_tokens = max(token_lengths) if token_lengths else 0
    min_tokens = min(token_lengths) if token_lengths else 0

    return {
        "file": str(p),
        "total_lines": total,
        "valid_records": valid,
        "invalid_records": total - valid,
        "avg_tokens": avg_tokens,
        "min_tokens": min_tokens,
        "max_tokens": max_tokens,
        "max_seq_len_threshold": max_seq_len,
        "truncation_risk_count": truncated_risk,
        "structured_json_outputs": structured_json_valid,
        "health_score": round((valid / max(total, 1)) * 100.0, 1)
    }

def split_multimodal_dataset(
    filepath: str,
    train_out: str,
    valid_out: str,
    train_ratio: float = 0.85,
    seed: int = 42
) -> Tuple[int, int]:
    """Deterministically split a JSONL dataset into train and validation sets."""
    random.seed(seed)
    with open(filepath, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    random.shuffle(lines)
    split_idx = int(len(lines) * train_ratio)
    train_lines = lines[:split_idx]
    valid_lines = lines[split_idx:]

    Path(train_out).parent.mkdir(parents=True, exist_ok=True)
    Path(valid_out).parent.mkdir(parents=True, exist_ok=True)

    with open(train_out, "w", encoding="utf-8") as f:
        for l in train_lines:
            f.write(l + "\n")

    with open(valid_out, "w", encoding="utf-8") as f:
        for l in valid_lines:
            f.write(l + "\n")

    return len(train_lines), len(valid_lines)

def build_multimodal_dataset_from_folder(
    image_dir: str,
    prompt: str = "请分析图像中的目标与状态",
    default_response: str = '{"status": "normal"}',
    output_file: str = "dataset.jsonl"
) -> int:
    """
    扫描目录中的图片文件，一键构建标准 ShareGPT 格式多模态微调标注数据集。
    支持 .jpg, .jpeg, .png, .bmp, .webp 图像后缀。
    """
    p = Path(image_dir)
    if not p.exists() or not p.is_dir():
        raise FileNotFoundError(f"Image directory not found: {image_dir}")

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = sorted([f for f in p.iterdir() if f.suffix.lower() in valid_exts])
    if not images:
        return 0

    records = []
    for img in images:
        record = {
            "messages": [
                {
                    "role": "user",
                    "content": f"<image>\n{prompt}"
                },
                {
                    "role": "assistant",
                    "content": default_response
                }
            ],
            "image": str(img.name)
        }
        records.append(record)

    out_p = Path(output_file)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return len(records)

def run_dataset_formatter_benchmark():
    """Deterministic validation test suite for dataset tools."""
    # 1. Test Alpaca conversion
    alpaca_sample = {
        "instruction": "检测作业人员是否佩戴安全帽",
        "input": "工厂一号车间监控切片",
        "output": '{"compliant": true}',
        "image": "images/worker1.jpg"
    }
    sharegpt = alpaca_to_sharegpt(alpaca_sample)
    assert len(sharegpt["messages"]) == 2
    assert "<image>" in sharegpt["messages"][0]["content"]
    assert sharegpt["messages"][1]["content"] == '{"compliant": true}'

    # 2. Test token estimation
    tokens = estimate_tokens("这是一段中文测试", num_images=1)
    assert tokens > 256  # Base image (256) + text tokens

    # 3. Test dataset validation on synthetic file
    tmp_file = "/tmp/test_dataset_formatter.jsonl"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(sharegpt, ensure_ascii=False) + "\n")
        bad_row = {"text": "invalid format"}
        f.write(json.dumps(bad_row, ensure_ascii=False) + "\n")

    stats = validate_multimodal_dataset(tmp_file)
    assert stats["total_lines"] == 2
    assert stats["valid_records"] == 1
    assert stats["invalid_records"] == 1
    assert stats["structured_json_outputs"] == 1

    if os.path.exists(tmp_file):
        os.remove(tmp_file)

    print("Dataset formatter test suite: ALL PASSED")

def main():
    parser = argparse.ArgumentParser(description="多模态微调数据集格式转换、校验与 Token 分布分析工具")
    parser.add_argument("--benchmark", action="store_true", help="运行确定性校验基准测试")
    parser.add_argument("--validate", type=str, default=None, help="待校验分析的 JSONL 数据集路径")
    parser.add_argument("--split", type=str, default=None, help="待切分的输入 JSONL 数据集路径")
    parser.add_argument("--train-out", type=str, default="train.jsonl", help="训练集输出路径")
    parser.add_argument("--valid-out", type=str, default="valid.jsonl", help="验证集输出路径")
    parser.add_argument("--ratio", type=float, default=0.85, help="训练集切分比例")
    parser.add_argument("--build-from-folder", type=str, default=None, help="扫描图片目录一键生成微调数据集")
    parser.add_argument("--prompt", type=str, default="请分析图像中的作业规范", help="用户指令模版")
    parser.add_argument("--response", type=str, default='{"compliant": true}', help="助手默认回复内容")
    parser.add_argument("--output", type=str, default="dataset.jsonl", help="生成输出路径")
    args = parser.parse_args()

    if args.build_from_folder:
        count = build_multimodal_dataset_from_folder(args.build_from_folder, args.prompt, args.response, args.output)
        print(f"扫描目录 {args.build_from_folder} 完成，成功生成 {count} 条样本 -> {args.output}")
        return

    if args.validate:
        stats = validate_multimodal_dataset(args.validate)
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return

    if args.split:
        n_tr, n_val = split_multimodal_dataset(args.split, args.train_out, args.valid_out, args.ratio)
        print(f"数据集切分完成: 训练集 {n_tr} 条 -> {args.train_out}, 验证集 {n_val} 条 -> {args.valid_out}")
        return

    run_dataset_formatter_benchmark()

if __name__ == "__main__":
    main()
