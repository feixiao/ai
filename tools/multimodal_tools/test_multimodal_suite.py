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

def run_suite():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_suite()
    sys.exit(0 if success else 1)
