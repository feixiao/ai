#!/usr/bin/env python3
"""
代码仓库与研报文档打包工具 (Context Packer for Gemini)

用途：
    将本地代码仓库或多个研报/文档文件扫描并打包为单一结构化文本文件，
    自动过滤掉无关二进制、依赖目录及版本控制文件，
    便于一键上传至 Google AI Studio 或 Gemini 进行百万级 Token 深度分析。

代码规范：
    - 遵守全中文注释与类型标注规范
    - 严禁使用无意义命名与隐式类型
    - 单文件不超过 500 行
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Set, Tuple


# 默认忽略的目录集合
DEFAULT_IGNORE_DIRECTORIES: Set[str] = {
    ".git",
    ".svn",
    ".hg",
    ".vscode",
    ".idea",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "venv",
    ".next",
    ".turbo",
    ".superpowers",
}

# 默认忽略的文件名集合（如锁文件和系统元数据）
DEFAULT_IGNORE_FILENAMES: Set[str] = {
    ".DS_Store",
    "Thumbs.db",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "poetry.lock",
    "Cargo.lock",
    "go.sum",
}

# 默认忽略的文件扩展名集合（二进制、图片、音视频、模型权重）
DEFAULT_IGNORE_EXTENSIONS: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svg",
    ".mp3", ".wav", ".mp4", ".mov", ".avi", ".mkv",
    ".zip", ".tar", ".gz", ".7z", ".rar",
    ".pyc", ".pyo", ".pyd", ".class", ".o", ".obj", ".dll", ".so", ".dylib",
    ".exe", ".bin", ".wasm",
    ".safetensors", ".ckpt", ".bin", ".pt", ".pth", ".onnx", ".gguf",
}


def is_binary_file(file_path: Path, sample_size: int = 1024) -> bool:
    """
    通过读取前几个字节判断文件是否为二进制文件

    参数:
        file_path (Path): 待检查的文件路径
        sample_size (int): 采样读取字节数，默认为 1024 字节

    返回值:
        bool: 若包含空字节则判定为二进制文件返回 True，否则返回 False
    """
    try:
        with open(file_path, "rb") as probe_stream:
            sample_bytes = probe_stream.read(sample_size)
            if b"\x00" in sample_bytes:
                return True
            return False
    except (IOError, OSError) as error_message:
        sys.stderr.write(f"[警告] 无法读取文件采样 {file_path}: {error_message}\n")
        return True


def should_include_file(
    target_path: Path,
    root_directory: Path,
    custom_ignore_dirs: Set[str],
    custom_ignore_exts: Set[str],
) -> bool:
    """
    检查单个文件是否应该被纳入打包范围

    参数:
        target_path (Path): 待判定的文件路径
        root_directory (Path): 根扫描目录
        custom_ignore_dirs (Set[str]): 忽略目录集合
        custom_ignore_exts (Set[str]): 忽略后缀集合

    返回值:
        bool: 允许打包返回 True，被过滤返回 False
    """
    relative_parts = target_path.relative_to(root_directory).parts

    # 检查是否位于被忽略的目录层级中
    for directory_part in relative_parts[:-1]:
        if directory_part in custom_ignore_dirs:
            return False

    filename = target_path.name
    if filename in DEFAULT_IGNORE_FILENAMES:
        return False

    file_extension = target_path.suffix.lower()
    if file_extension in custom_ignore_exts:
        return False

    if is_binary_file(target_path):
        return False

    return True


def collect_valid_files(
    root_directory: Path,
    custom_ignore_dirs: Set[str],
    custom_ignore_exts: Set[str],
) -> List[Path]:
    """
    递归遍历扫描指定目录并筛选出所有有效文本文件

    参数:
        root_directory (Path): 目标起始目录
        custom_ignore_dirs (Set[str]): 目录忽略黑名单
        custom_ignore_exts (Set[str]): 扩展名忽略黑名单

    返回值:
        List[Path]: 排序后的有效文件路径列表
    """
    matched_files: List[Path] = []

    for current_root, directory_names, file_names in os.walk(root_directory):
        # 实时原地剪枝，避免进入巨大无用的目录（如 node_modules）
        directory_names[:] = [
            directory_name
            for directory_name in directory_names
            if directory_name not in custom_ignore_dirs
        ]

        for file_name in file_names:
            candidate_path = Path(current_root) / file_name
            if should_include_file(
                candidate_path,
                root_directory,
                custom_ignore_dirs,
                custom_ignore_exts,
            ):
                matched_files.append(candidate_path)

    matched_files.sort()
    return matched_files


def estimate_token_count(text_content: str) -> int:
    """
    估算文本的大致 Token 数量（混合中英文加权估算）

    参数:
        text_content (str): 输入的完整字符串

    返回值:
        int: 估算的 Token 数量
    """
    character_count = len(text_content)
    # 对于纯英文代码约 3.5~4 字符一个 Token，中文约 1.5~2 字符一个 Token，取均值 2.8 折算
    return int(character_count / 2.8)


def pack_files_to_stream(
    root_directory: Path,
    file_list: List[Path],
    output_filepath: Path,
) -> Tuple[int, int]:
    """
    将扫描到的文件逐一写入输出文件，并生成清晰的文件头尾标记与相对路径

    参数:
        root_directory (Path): 根目录路径
        file_list (List[Path]): 待打包的文件列表
        output_filepath (Path): 目标输出文件路径

    返回值:
        Tuple[int, int]: (写入的总字符数, 写入的总文件数)
    """
    total_written_characters = 0
    total_packed_files = 0

    with open(output_filepath, "w", encoding="utf-8") as output_stream:
        # 写入文件清单总览
        output_stream.write("# 上下文打包工程清单总览\n\n")
        output_stream.write(f"- 扫描根路径: `{root_directory.resolve()}`\n")
        output_stream.write(f"- 纳入文件总数: `{len(file_list)}`\n\n")
        output_stream.write("## 目录结构索引\n\n")

        for individual_file in file_list:
            relative_filepath = individual_file.relative_to(root_directory)
            output_stream.write(f"- `{relative_filepath}`\n")

        output_stream.write("\n" + "=" * 80 + "\n\n")

        # 逐个文件追加正文
        for individual_file in file_list:
            relative_filepath = individual_file.relative_to(root_directory)
            try:
                with open(individual_file, "r", encoding="utf-8", errors="replace") as source_stream:
                    file_content = source_stream.read()
            except (IOError, OSError) as read_error:
                sys.stderr.write(f"[错误] 无法读取文件 {relative_filepath}: {read_error}\n")
                continue

            header_banner = f"=== FILE: {relative_filepath} ===\n"
            footer_banner = f"\n=== END FILE: {relative_filepath} ===\n\n"

            output_stream.write(header_banner)
            output_stream.write(file_content)
            output_stream.write(footer_banner)

            total_written_characters += len(header_banner) + len(file_content) + len(footer_banner)
            total_packed_files += 1

    return total_written_characters, total_packed_files


def parse_arguments() -> argparse.Namespace:
    """
    解析命令行参数

    返回值:
        argparse.Namespace: 解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="将代码库或研报目录打包为单一长文本，投喂 Gemini 100万+ 超大上下文",
    )
    parser.add_argument(
        "source_directory",
        type=str,
        help="待打包的本地目录路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="gemini_context_bundle.txt",
        help="输出的打包文件路径 (默认: gemini_context_bundle.txt)",
    )
    return parser.parse_args()


def main() -> None:
    """
    主程序执行入口
    """
    arguments = parse_arguments()
    source_path = Path(arguments.source_directory).resolve()
    output_path = Path(arguments.output).resolve()

    if not source_path.exists() or not source_path.is_dir():
        sys.stderr.write(f"[严重错误] 指定的目标目录不存在或不是目录: {source_path}\n")
        sys.exit(1)

    print(f"[*] 正在扫描目录: {source_path}")
    matched_files = collect_valid_files(
        source_path,
        DEFAULT_IGNORE_DIRECTORIES,
        DEFAULT_IGNORE_EXTENSIONS,
    )

    if not matched_files:
        print("[!] 未找到符合打包条件的有效文本文件。")
        sys.exit(0)

    print(f"[*] 扫描到有效文件 {len(matched_files)} 个，开始合并打包...")
    written_chars, packed_count = pack_files_to_stream(source_path, matched_files, output_path)
    estimated_tokens = estimate_token_count(" " * written_chars)

    print("\n" + "=" * 50)
    print("✅ 打包完成！")
    print(f"- 输出文件: {output_path}")
    print(f"- 打包文件数: {packed_count} 个")
    print(f"- 总字符数: {written_chars:,} 字符")
    print(f"- 预估 Token: ~{estimated_tokens:,} Tokens")
    print(f"- 上下文利用率: 约占 Gemini 100万 Token 窗口的 {(estimated_tokens / 1_000_000) * 100:.2f}%")
    print("=" * 50)
    print("💡 提示: 您可以直接将该文件拖入 Google AI Studio (aistudio.google.com) 进行全量深度分析。")


if __name__ == "__main__":
    main()
