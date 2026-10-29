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

class TestEnvironmentScript(unittest.TestCase):
    def test_setup_environment_check(self):
        import subprocess
        script = ROOT_DIR / "examples" / "multimodal_practice" / "setup_environment.sh"
        self.assertTrue(script.exists())
        res = subprocess.run(["bash", str(script), "--check"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("环境探测", res.stdout)

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

class TestBenchmarkSummary(unittest.TestCase):
    def test_generate_dashboard(self):
        from benchmark_summary import generate_dashboard
        output = generate_dashboard()
        self.assertIn("技术雷达", output)
        self.assertIn("GOLD STANDARD", output)
        self.assertIn("qwen2.5-vl-72b", output)
        self.assertIn("pixel_10_tensor_g5", output)

def run_suite():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
