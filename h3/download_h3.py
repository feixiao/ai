#!/usr/bin/env python3
"""
MiniMax-H3 权重下载与管理助手 (纯 Python 实现，零 git-lfs 依赖)
支持 HuggingFace (原生 snapshot_download) 与 ModelScope (REST API 下载)
默认仅下载核心 FL2VA 模式 (约 134 GB)，避免全量下载 Ref2VA (可省 ~125 GB 空间)
"""

import sys
import os
import shutil
import argparse
import urllib.request
import urllib.parse
import json
from pathlib import Path


def get_dir_size_str(path: str) -> str:
    """计算目录大小并格式化为人类可读字符串"""
    if not os.path.exists(path):
        return "0 MB"
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    if total_size >= 1024 * 1024 * 1024:
        return f"{total_size / (1024 * 1024 * 1024):.2f} GB"
    return f"{total_size / (1024 * 1024):.1f} MB"


def clean_extra_files(target_dir: str) -> None:
    """清理非核心的 Ref2VA 目录及临时缓存文件以释放磁盘空间"""
    print(f"\n🧹 开始检查与清理冗余模型目录: {target_dir}")
    ref2va_dir = os.path.join(target_dir, "Ref2VA")
    cache_dir = os.path.join(target_dir, ".cache")

    cleaned = False
    if os.path.exists(ref2va_dir):
        size_str = get_dir_size_str(ref2va_dir)
        print(f"🗑️  正在删除非必需的 Ref2VA 多参考目录 (占用 {size_str})...")
        try:
            shutil.rmtree(ref2va_dir)
            print("✅ Ref2VA 目录删除成功！")
            cleaned = True
        except Exception as e:
            print(f"❌ 删除 Ref2VA 失败: {e}")

    if os.path.exists(cache_dir):
        size_str = get_dir_size_str(cache_dir)
        print(f"🗑️  正在清理临时下载缓存目录 (占用 {size_str})...")
        try:
            shutil.rmtree(cache_dir)
            print("✅ 缓存目录清理成功！")
            cleaned = True
        except Exception as e:
            print(f"❌ 清理缓存失败: {e}")

    if not cleaned:
        print("✨ 当前目录中无冗余 Ref2VA 或缓存文件，无需清理。")
    else:
        print("🎉 冗余文件清理完毕，磁盘空间已释放！\n")


def download_from_huggingface(repo_id: str, target_dir: str, variant: str = "fl2va") -> None:
    """通过 HuggingFace 原生 snapshot_download 按需下载权重"""
    print(f"📦 正在使用 HuggingFace 官方源下载 {repo_id} (模式: {variant})...")
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("❌ 未检测到 huggingface_hub 库，请先执行: pip3 install huggingface_hub")
        sys.exit(1)

    os.makedirs(target_dir, exist_ok=True)

    kwargs = {
        "repo_id": repo_id,
        "local_dir": target_dir,
    }

    if variant == "fl2va":
        # 排除 Ref2VA 目录，只下载 FL2VA 与根目录元数据，节省 ~125 GB
        kwargs["ignore_patterns"] = ["Ref2VA/*", "Ref2VA/**"]
        print("💡 [精简模式] 已自动过滤 Ref2VA 多参考目录，仅下载 FL2VA 核心文生视频/首尾帧权重 (~134 GB)")
    elif variant == "ref2va":
        kwargs["allow_patterns"] = ["Ref2VA/*", "Ref2VA/**", "*.json", "*.md", "LICENSE", ".gitattributes"]
        print("💡 [增量模式] 仅下载 Ref2VA 多参考目录权重 (~125 GB)")
    else:
        print("💡 [全量模式] 下载完整模型仓库，包含 FL2VA 与 Ref2VA (~260 GB)")

    snapshot_download(**kwargs)
    print(f"✅ HuggingFace 下载完成: {target_dir}")


def download_from_modelscope_api(model_id: str, target_dir: str, variant: str = "fl2va") -> None:
    """通过 ModelScope REST API 按需下载权重 (零 git-lfs 依赖)"""
    print(f"📦 正在使用 ModelScope REST API 下载 {model_id} (模式: {variant})...")
    os.makedirs(target_dir, exist_ok=True)

    if variant == "fl2va":
        print("💡 [精简模式] 已自动过滤 Ref2VA 多参考目录，仅下载 FL2VA 核心文生视频/首尾帧权重 (~134 GB)")
    elif variant == "ref2va":
        print("💡 [增量模式] 仅下载 Ref2VA 多参考目录权重 (~125 GB)")
    else:
        print("💡 [全量模式] 下载完整模型仓库，包含 FL2VA 与 Ref2VA (~260 GB)")

    def get_files_recursive(prefix=""):
        url = f"https://modelscope.cn/api/v1/models/{model_id}/repo/files?Revision=master"
        if prefix:
            url += f"&Root={urllib.parse.quote(prefix)}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        file_paths = []
        for item in data.get("Data", {}).get("Files", []):
            item_path = item.get("Path", "")
            item_type = item.get("Type", "")

            # 根据变体模式进行目录级智能过滤
            if variant == "fl2va" and (item_path == "Ref2VA" or item_path.startswith("Ref2VA/")):
                continue
            if variant == "ref2va" and (item_path == "FL2VA" or item_path.startswith("FL2VA/")):
                continue

            if item_type == "tree":
                file_paths.extend(get_files_recursive(item_path))
            else:
                file_paths.append((item_path, item.get("Size", 0)))
        return file_paths

    try:
        print("🔍 正在拉取 ModelScope 文件清单...")
        files = get_files_recursive()
        total_bytes = sum(size for _, size in files)
        print(f"📋 共检索到 {len(files)} 个待下载文件，计划体积: {total_bytes / (1024 * 1024 * 1024):.2f} GB")
    except Exception as e:
        print(f"⚠️ 拉取清单失败: {e}，将自动切换为 HuggingFace 源下载...")
        download_from_huggingface("MiniMaxAI/MiniMax-H3", target_dir, variant)
        return

    # 依次断点续传下载各文件
    for idx, (rel_path, file_size) in enumerate(files, 1):
        dest_file = os.path.join(target_dir, rel_path)
        if os.path.exists(dest_file) and (file_size == 0 or os.path.getsize(dest_file) == file_size):
            continue

        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        encoded_path = urllib.parse.quote(rel_path)
        download_url = f"https://modelscope.cn/api/v1/models/{model_id}/repo?Revision=master&FilePath={encoded_path}"

        print(f"[{idx}/{len(files)}] 下载: {rel_path} ({file_size / (1024*1024):.1f} MB)...")
        req = urllib.request.Request(download_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(dest_file, "wb") as out:
            while True:
                chunk = resp.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)

    print(f"✅ ModelScope 下载完成: {target_dir}")


def main():
    parser = argparse.ArgumentParser(description="MiniMax-H3 权重下载管理工具")
    parser.add_argument("target_dir", nargs="?", default="", help="保存目录 (默认: models/MiniMax-H3)")
    parser.add_argument("source", nargs="?", default="modelscope", choices=["modelscope", "huggingface"], help="下载源 (默认: modelscope)")
    parser.add_argument("variant", nargs="?", default="fl2va", choices=["fl2va", "all", "ref2va", "clean"], help="下载模式或操作 (默认: fl2va 仅下核心)")
    parser.add_argument("--clean", action="store_true", help="清理非必需的 Ref2VA 目录与缓存文件")
    parser.add_argument("--variant-opt", dest="opt_variant", choices=["fl2va", "all", "ref2va"], default="", help="显示指定下载变体")
    args = parser.parse_args()

    # 优先解析 clean 意图
    is_clean = args.clean or args.variant == "clean" or args.source == "clean"
    variant = args.opt_variant or (args.variant if args.variant != "clean" else "fl2va")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = args.target_dir if args.target_dir else os.path.join(script_dir, "models", "MiniMax-H3")
    target_dir = os.path.abspath(target_dir)

    print("=================================================================")
    print("  MiniMax-H3 权重下载管理工具 (原生 Python，无需 git-lfs)")
    print(f"  目标保存目录: {target_dir}")
    print(f"  运行模式:     {'仅清理冗余文件' if is_clean else f'下载模式 [{variant}] (源: {args.source})'}")
    print("=================================================================")

    if is_clean:
        clean_extra_files(target_dir)
        return

    if args.source == "huggingface":
        download_from_huggingface("MiniMaxAI/MiniMax-H3", target_dir, variant)
    else:
        download_from_modelscope_api("MiniMax/MiniMax-H3", target_dir, variant)

    # 软链接至当前目录的 MiniMax-H3 方便直连
    link_path = os.path.join(script_dir, "MiniMax-H3")
    try:
        if os.path.islink(link_path) or os.path.exists(link_path):
            os.remove(link_path)
        os.symlink(target_dir, link_path)
    except OSError:
        pass

    config_path = os.path.join(target_dir, "FL2VA", "transformer", "config.json")
    if os.path.exists(config_path):
        print("🎉 MiniMax-H3 FL2VA 核心权重就绪，可直接运行 ./generate.sh 生成！")


if __name__ == "__main__":
    main()
