#!/usr/bin/env python3
"""
Comprehensive unit test suite for multimodal tools and practice modules.
Tests boundary conditions, edge cases, mathematical formulas, and schema invariants.
Zero external dependencies (uses standard library unittest).
"""
import unittest
import sys
import os
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
ROOT_DIR = TOOLS_DIR.parent.parent
sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(ROOT_DIR / "examples" / "multimodal_practice"))

from vram_and_budget import (
    estimate_inference_memory_gb,
    estimate_lora_finetune_memory_gb,
    check_hardware_feasibility,
    MODEL_REGISTRY,
    HARDWARE_PROFILES
)
from multimodal_pipeline import (
    sample_video_frames,
    build_multimodal_vlm_payload,
    chunk_audio_stream,
    validate_edge_export_spec
)
from dataset_formatter import (
    estimate_tokens,
    alpaca_to_sharegpt,
    validate_multimodal_dataset,
    split_multimodal_dataset
)

class TestVramAndBudget(unittest.TestCase):
    def test_inference_memory_scaling(self):
        m_fp16 = estimate_inference_memory_gb(params_b=3.0, precision="fp16")
        m_int4 = estimate_inference_memory_gb(params_b=3.0, precision="int4")
        self.assertLess(m_int4["weight_gb"], m_fp16["weight_gb"])
        self.assertAlmostEqual(m_int4["weight_gb"], 1.5, places=2)
        self.assertAlmostEqual(m_fp16["weight_gb"], 6.0, places=2)

    def test_lora_finetune_memory(self):
        lora_mem = estimate_lora_finetune_memory_gb(params_b=7.0, rank=16)
        self.assertGreater(lora_mem["total_training_gb"], 5.0)
        self.assertLess(lora_mem["total_training_gb"], 12.0)

    def test_hardware_feasibility(self):
        # 3B on Pixel 10 should be feasible
        res_pixel = check_hardware_feasibility("qwen2.5-vl-3b", "pixel_10_tensor_g5", "inference")
        self.assertTrue(res_pixel["feasible"])

        # 7B finetune on Pixel 10 must fail
        res_pixel_ft = check_hardware_feasibility("qwen2.5-vl-7b", "pixel_10_tensor_g5", "finetune")
        self.assertFalse(res_pixel_ft["feasible"])

        # 7B finetune on Mac Studio must succeed
        res_mac = check_hardware_feasibility("qwen2.5-vl-7b", "mac_studio_m2_max_64g", "finetune")
        self.assertTrue(res_mac["feasible"])

    def test_invalid_model_or_device(self):
        with self.assertRaises(ValueError):
            check_hardware_feasibility("non_existent_model", "mac_studio_m2_max_64g")
        with self.assertRaises(ValueError):
            check_hardware_feasibility("qwen2.5-vl-3b", "non_existent_device")

    def test_vram_and_budget_cli_model_and_device(self):
        import subprocess
        script = TOOLS_DIR / "vram_and_budget.py"
        p = subprocess.run([sys.executable, str(script), "--model", "qwen2.5-vl-3b", "--device", "pixel_10_tensor_g5"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("Optimal", p.stdout)
        self.assertIn("required_gb", p.stdout)

class TestMultimodalPipeline(unittest.TestCase):
    def test_sample_video_frames_edge_cases(self):
        # Zero frames
        self.assertEqual(sample_video_frames(0, 30.0, 8), [])
        # Fewer than max_frames
        self.assertEqual(sample_video_frames(5, 30.0, 8), [0, 1, 2, 3, 4])
        # Exactly max_frames
        self.assertEqual(len(sample_video_frames(8, 30.0, 8)), 8)
        # Large frame count
        sampled = sample_video_frames(1000, 30.0, 8)
        self.assertEqual(len(sampled), 8)
        self.assertEqual(sampled[0], 0)
        self.assertLess(sampled[-1], 1000)

    def test_build_vlm_payload(self):
        frames = [0, 30, 60]
        payload = build_multimodal_vlm_payload("巡检分析", frames, 30.0)
        self.assertEqual(payload["model"], "Qwen/Qwen2.5-VL-3B-Instruct")
        content = payload["messages"][0]["content"]
        self.assertEqual(len(content), 4)  # 3 frames + 1 text
        self.assertEqual(content[-1]["text"], "巡检分析")

    def test_chunk_audio_stream_bounds(self):
        # 1 second audio at 16kHz
        chunks_1s = chunk_audio_stream(16000, 16000, chunk_duration_sec=3.0)
        self.assertEqual(chunks_1s, [(0, 16000)])

        # 7 seconds audio
        chunks_7s = chunk_audio_stream(16000 * 7, 16000, chunk_duration_sec=3.0, overlap_sec=0.5)
        self.assertGreaterEqual(len(chunks_7s), 3)
        self.assertEqual(chunks_7s[0], (0, 48000))

    def test_validate_edge_export_spec(self):
        valid_spec = {
            "model_name": "qwen2.5-vl-3b-int4",
            "target_runtime": "litert",
            "quantization_type": "w4a16",
            "max_seq_len": 2048,
            "context_memory_budget_mb": 3200
        }
        self.assertTrue(validate_edge_export_spec(valid_spec)["valid"])

        # Exceeds Pixel memory limit
        invalid_spec = valid_spec.copy()
        invalid_spec["context_memory_budget_mb"] = 5500
        self.assertFalse(validate_edge_export_spec(invalid_spec)["valid"])

    def test_load_or_simulate_video_frames(self):
        import importlib.util
        lab01_path = ROOT_DIR / "examples" / "multimodal_practice" / "01_video_vlm_inference.py"
        spec = importlib.util.spec_from_file_location("lab01", str(lab01_path))
        lab01 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab01)
        frames, desc = lab01.load_or_simulate_video_frames(num_frames=4)
        self.assertEqual(len(frames), 4)
        self.assertIn("base64_data", frames[0])
        self.assertIn("预置样本目录", desc)

    def test_export_commands_and_android_snippet(self):
        import importlib.util
        lab04_path = ROOT_DIR / "examples" / "multimodal_practice" / "04_export_to_pixel10.py"
        spec = importlib.util.spec_from_file_location("lab04", str(lab04_path))
        lab04 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab04)
        cmds = lab04.get_export_cli_commands("qwen2.5-vl-3b")
        self.assertIn("LiteRT_Edge_TPU", cmds)
        self.assertIn("GGUF_llama_cpp", cmds)
        self.assertIn("ExecuTorch_Vulkan", cmds)
        snippet = lab04.generate_android_snippet()
        self.assertIn("EdgeVisionAnalyzer", snippet)
        self.assertIn("CameraX", snippet)

    def test_multimodal_pipeline_cli_flags(self):
        import subprocess
        script = TOOLS_DIR / "multimodal_pipeline.py"
        p = subprocess.run([sys.executable, str(script), "--sample-video"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("抽取关键帧索引", p.stdout)

class TestDatasetFormatter(unittest.TestCase):
    def test_estimate_tokens(self):
        self.assertEqual(estimate_tokens("", num_images=0), 0)
        self.assertEqual(estimate_tokens("", num_images=1), 256)
        toks = estimate_tokens("测试文本", num_images=1)
        self.assertGreater(toks, 256)

    def test_alpaca_to_sharegpt_conversion(self):
        alpaca = {
            "instruction": "检测作业规范",
            "input": "视频截帧",
            "output": '{"ok": true}',
            "image": "path/to/img.jpg"
        }
        sg = alpaca_to_sharegpt(alpaca)
        self.assertIn("messages", sg)
        self.assertEqual(len(sg["messages"]), 2)
        self.assertIn("<image>", sg["messages"][0]["content"])
        self.assertIn("检测作业规范", sg["messages"][0]["content"])

    def test_split_reproducibility(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w+", delete=False) as f_in:
            for i in range(20):
                f_in.write(f'{{"line": {i}}}\n')
            temp_path = f_in.name

        t1, v1 = tempfile.NamedTemporaryFile(delete=False).name, tempfile.NamedTemporaryFile(delete=False).name
        t2, v2 = tempfile.NamedTemporaryFile(delete=False).name, tempfile.NamedTemporaryFile(delete=False).name

        try:
            n_tr1, n_val1 = split_multimodal_dataset(temp_path, t1, v1, train_ratio=0.8, seed=42)
            n_tr2, n_val2 = split_multimodal_dataset(temp_path, t2, v2, train_ratio=0.8, seed=42)
            self.assertEqual((n_tr1, n_val1), (n_tr2, n_val2))
            with open(t1) as f1, open(t2) as f2:
                self.assertEqual(f1.read(), f2.read())
        finally:
            for p in [temp_path, t1, v1, t2, v2]:
                if os.path.exists(p):
                    os.remove(p)

    def test_dataset_formatter_cli_validate(self):
        import subprocess
        script = TOOLS_DIR / "dataset_formatter.py"
        sample_train = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "train.jsonl"
        p = subprocess.run([sys.executable, str(script), "--validate", str(sample_train)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("health_score", p.stdout)
        self.assertIn("100.0", p.stdout)

class TestNumericalLoRAOptimization(unittest.TestCase):
    def test_lora_gradient_descent(self):
        import importlib.util
        lab03_path = ROOT_DIR / "examples" / "multimodal_practice" / "03_vlm_lora_dataset_and_train.py"
        spec = importlib.util.spec_from_file_location("lab03", str(lab03_path))
        lab03 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab03)
        res = lab03.run_numerical_lora_optimization(d=16, r=4, alpha=8, steps=25)
        self.assertLess(res["final_loss"], res["init_loss"])
        self.assertGreater(res["loss_reduction_pct"], 70.0)

    def test_qwen_72b_feasibility(self):
        # 72B on Mac Studio 192G should be feasible
        res_mac_192 = check_hardware_feasibility("qwen2.5-vl-72b", "mac_studio_m4_ultra_192g", "inference")
        self.assertTrue(res_mac_192["feasible"])

        # 72B on Pixel 10 must fail
        res_pixel = check_hardware_feasibility("qwen2.5-vl-72b", "pixel_10_tensor_g5", "inference")
        self.assertFalse(res_pixel["feasible"])

    def test_gemma_3n_mobile_edge(self):
        res = check_hardware_feasibility("gemma-3n-2b", "pixel_10_pro_tensor_g5", "inference")
        self.assertTrue(res["feasible"])
        self.assertLess(res["required_gb"], 3.0)

    def test_lab03_use_sample_data_and_steps(self):
        import subprocess
        lab03_path = ROOT_DIR / "examples" / "multimodal_practice" / "03_vlm_lora_dataset_and_train.py"
        p = subprocess.run([sys.executable, str(lab03_path), "--use-sample-data", "--steps", "10"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("预置实体标注数据集", p.stdout)
        self.assertIn("10 步梯度下降", p.stdout)

class TestInteractiveMenu(unittest.TestCase):
    def test_menu_quit_and_probe(self):
        import importlib.util
        menu_path = ROOT_DIR / "examples" / "multimodal_practice" / "interactive_menu.py"
        spec = importlib.util.spec_from_file_location("interactive_menu", str(menu_path))
        menu = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(menu)
        # Choice 0 exits
        self.assertFalse(menu.run_choice("0"))
        # Choice 7 (probe) runs successfully
        self.assertTrue(menu.run_choice("7"))
        # Choice 9 (benchmark summary) runs successfully
        self.assertTrue(menu.run_choice("9"))
        # Choice 10 (client example) runs successfully
        self.assertTrue(menu.run_choice("10"))

class TestEnvironmentScript(unittest.TestCase):
    def test_setup_environment_check(self):
        import subprocess
        script = ROOT_DIR / "examples" / "multimodal_practice" / "setup_environment.sh"
        self.assertTrue(script.exists())
        res = subprocess.run(["bash", str(script), "--check"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("环境探测", res.stdout)

    def test_setup_environment_download_models(self):
        import subprocess
        script = ROOT_DIR / "examples" / "multimodal_practice" / "setup_environment.sh"
        p = subprocess.run(["bash", str(script), "--download-models"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("qwen2.5-vl", p.stdout)
        self.assertIn("Whisper", p.stdout)
        self.assertIn("Pixel 10", p.stdout)

    def test_makefile_exists_and_runs_help(self):
        import subprocess
        makefile = ROOT_DIR / "examples" / "multimodal_practice" / "Makefile"
        self.assertTrue(makefile.exists())
        p = subprocess.run(["make", "-C", str(makefile.parent), "help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("快捷指令", p.stdout)

    def test_root_makefile_exists_and_runs_help(self):
        import subprocess
        root_makefile = ROOT_DIR / "Makefile"
        self.assertTrue(root_makefile.exists())
        p = subprocess.run(["make", "-C", str(ROOT_DIR), "help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("工作台", p.stdout)

    def test_root_makefile_clean_target(self):
        import subprocess
        p = subprocess.run(["make", "-C", str(ROOT_DIR), "clean"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("已清理", p.stdout)

    def test_practice_readme_structure(self):
        readme = ROOT_DIR / "examples" / "multimodal_practice" / "README.md"
        self.assertTrue(readme.exists())
        content = readme.read_text(encoding="utf-8")
        self.assertIn("系统架构拓扑全景", content)
        self.assertIn("05_local_multimodal_server", content)
        self.assertIn("client_example", content)
        self.assertIn("setup_environment.sh", content)

    def test_quickstart_script_help(self):
        import subprocess
        qs_script = ROOT_DIR / "quickstart.sh"
        self.assertTrue(qs_script.exists())
        p = subprocess.run(["bash", str(qs_script), "--help"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("极速启动", p.stdout)


    def test_quickstart_script_check_and_report(self):
        import subprocess
        qs_script = ROOT_DIR / "quickstart.sh"
        p_check = subprocess.run(["bash", str(qs_script), "--check"], capture_output=True, text=True)
        self.assertEqual(p_check.returncode, 0)
        self.assertIn("环境探测", p_check.stdout)

        p_rep = subprocess.run(["bash", str(qs_script), "--report"], capture_output=True, text=True)
        self.assertEqual(p_rep.returncode, 0)
        self.assertIn("技术雷达", p_rep.stdout)

        p_clean = subprocess.run(["bash", str(qs_script), "--clean"], capture_output=True, text=True)
        self.assertEqual(p_clean.returncode, 0)
        self.assertIn("已清理", p_clean.stdout)

    def test_run_all_labs_script(self):
        import subprocess
        runner = ROOT_DIR / "examples" / "multimodal_practice" / "run_all_labs.sh"
        self.assertTrue(runner.exists())
        p = subprocess.run(["bash", str(runner)], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("全部 6 套", p.stdout)
    def test_multimodal_ci_workflow_exists(self):
        wf = ROOT_DIR / ".github" / "workflows" / "multimodal_ci.yml"
        self.assertTrue(wf.exists())
        content = wf.read_text(encoding="utf-8")
        self.assertIn("autoresearch.sh", content)
        self.assertIn("test_multimodal_suite.py", content)
        self.assertIn("quickstart.sh", content)

class TestSampleDataFixtures(unittest.TestCase):
    def test_sample_dataset_validation(self):
        sample_train = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "train.jsonl"
        self.assertTrue(sample_train.exists())
        stats = validate_multimodal_dataset(str(sample_train))
        self.assertEqual(stats["health_score"], 100.0)
        self.assertEqual(stats["invalid_records"], 0)
        self.assertEqual(stats["truncation_risk_count"], 0)

    def test_sample_frames_exist(self):
        frames_dir = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "frames"
        self.assertTrue(frames_dir.exists())
        bmps = list(frames_dir.glob("*.bmp"))
        self.assertEqual(len(bmps), 4)

    def test_sample_audio_properties(self):
        import wave
        audio_path = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "audio" / "sample_inspection_16k.wav"
        self.assertTrue(audio_path.exists())
        with wave.open(str(audio_path), "rb") as wf:
            self.assertEqual(wf.getframerate(), 16000)
            self.assertEqual(wf.getnchannels(), 1)
            self.assertEqual(wf.getsampwidth(), 2)
            self.assertGreater(wf.getnframes(), 16000)

    def test_sample_android_kotlin_and_manifest(self):
        import json
        kt_path = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "EdgeVisionAnalyzer.kt"
        manifest_path = ROOT_DIR / "examples" / "multimodal_practice" / "sample_data" / "pixel10_export_manifest.json"
        self.assertTrue(kt_path.exists())
        self.assertTrue(manifest_path.exists())

        kt_code = kt_path.read_text(encoding="utf-8")
        self.assertIn("EdgeVisionAnalyzer", kt_code)
        self.assertIn("CameraX", kt_code)
        self.assertIn("LiteRtModel", kt_code)

        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest_data["model_id"], "Qwen2.5-VL-3B-Instruct")
        self.assertTrue(manifest_data["memory_profile_gb"]["safe_to_deploy"])

class TestLocalMultimodalServer(unittest.TestCase):
    def test_server_demo_self_test(self):
        import importlib.util
        lab05_path = ROOT_DIR / "examples" / "multimodal_practice" / "05_local_multimodal_server.py"
        self.assertTrue(lab05_path.exists())
        spec = importlib.util.spec_from_file_location("lab05", str(lab05_path))
        lab05 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab05)
        self.assertTrue(lab05.run_demo_self_test())

class TestClientServerIntegration(unittest.TestCase):
    def test_live_clients_talking_to_server(self):
        import subprocess, socket, threading, time
        from http.server import HTTPServer
        import importlib.util

        lab05_path = ROOT_DIR / "examples" / "multimodal_practice" / "05_local_multimodal_server.py"
        spec = importlib.util.spec_from_file_location("lab05", str(lab05_path))
        lab05 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lab05)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]

        server = HTTPServer(("127.0.0.1", port), lab05.MultimodalAPIHandler)
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        time.sleep(0.05)

        try:
            # 1. Test Lab 01 calling Lab 05 chat completions endpoint
            lab01_script = ROOT_DIR / "examples" / "multimodal_practice" / "01_video_vlm_inference.py"
            p1 = subprocess.run(
                [sys.executable, str(lab01_script), "--endpoint", f"http://127.0.0.1:{port}/v1/chat/completions"],
                capture_output=True, text=True
            )
            self.assertEqual(p1.returncode, 0)
            self.assertIn("Live HTTP Endpoint", p1.stdout)

            # 2. Test Lab 02 calling Lab 05 audio transcriptions endpoint
            lab02_script = ROOT_DIR / "examples" / "multimodal_practice" / "02_audio_whisper_tts.py"
            p2 = subprocess.run(
                [sys.executable, str(lab02_script), "--endpoint", f"http://127.0.0.1:{port}/v1/audio/transcriptions"],
                capture_output=True, text=True
            )
            self.assertEqual(p2.returncode, 0)
            self.assertIn("Live Whisper Endpoint", p2.stdout)
        finally:
            server.shutdown()
            server.server_close()

    def test_client_example_standalone(self):
        import subprocess
        client_script = ROOT_DIR / "examples" / "multimodal_practice" / "client_example.py"
        self.assertTrue(client_script.exists())
        p = subprocess.run([sys.executable, str(client_script), "--demo"], capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn("客户端端到端调用", p.stdout)

class TestBenchmarkSummary(unittest.TestCase):
    def test_generate_dashboard(self):
        from benchmark_summary import generate_dashboard
        output = generate_dashboard()
        self.assertIn("技术雷达", output)
        self.assertIn("GOLD STANDARD", output)
        self.assertIn("qwen2.5-vl-72b", output)
        self.assertIn("pixel_10_tensor_g5", output)

    def test_generate_json_summary(self):
        from benchmark_summary import generate_json_summary
        data = generate_json_summary()
        self.assertEqual(data["overall_score"], 100.0)
        self.assertEqual(data["models_count"], 13)
        self.assertEqual(data["hardware_profiles_count"], 6)
        self.assertIn("qwen2.5-vl-72b", data["models"])
        self.assertIn("mac_studio_m4_ultra_192g", data["hardware_profiles"])

class TestLiveKitIntegration(unittest.TestCase):
    def test_livekit_agent_directory_and_scripts(self):
        livekit_dir = ROOT_DIR / "LiveKit" / "lmstudio_audio_agent"
        self.assertTrue(livekit_dir.exists())
        self.assertTrue((livekit_dir / "agent.py").exists())
        self.assertTrue((livekit_dir / "start.sh").exists())
        self.assertTrue((livekit_dir / "probe.py").exists())

def run_suite():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
