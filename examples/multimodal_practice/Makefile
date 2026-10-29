# ==============================================================================
# 音视频多模态实操套件便捷指令集 (Developer Makefile)
# ==============================================================================

PYTHON ?= python3

.PHONY: all help demo menu test check report server clean

all: demo

help:
	@echo "=================================================================="
	@echo "🎬 音视频多模态实操练习套件快捷指令 (Mac Studio & Pixel 10)"
	@echo "=================================================================="
	@echo "  make demo        - 运行全部 6 阶段端到端实操练习流水线"
	@echo "  make menu        - 打开交互式终端控制台菜单 (选项 0~10)"
	@echo "  make test        - 运行 56 项全量标准单元测试套件 (unittest)"
	@echo "  make check       - 探测 Mac Studio 统一内存与 Pixel 10 ADB 环境"
	@echo "  make report      - 打印多模态技术雷达与基准全景看板"
	@echo "  make server      - 启动本地 OpenAI 兼容多模态微服务网关 (端口 8000)"
	@echo "=================================================================="

demo:
	bash run_all_labs.sh

menu:
	bash run_all_labs.sh --menu

test:
	$(PYTHON) ../../tools/multimodal_tools/test_multimodal_suite.py

check:
	bash setup_environment.sh --check

report:
	$(PYTHON) ../../tools/multimodal_tools/benchmark_summary.py

server:
	$(PYTHON) 05_local_multimodal_server.py --port 8000 --host 0.0.0.0

clean:
	rm -rf /tmp/test_multimodal_audio.wav /tmp/multimodal_lora_data
