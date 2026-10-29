# ==============================================================================
# AI 工程化与音视频多模态工作台根快捷指令 (Root Developer Makefile)
# ==============================================================================

PYTHON ?= python3

.PHONY: all help demo menu test benchmark check report server clean

all: demo

help:
	@echo "=================================================================="
	@echo "🤖 AI 工程化与音视频多模态实战工作台 (Mac Studio & Pixel 10)"
	@echo "=================================================================="
	@echo "  make demo        - 运行音视频多模态 6 阶段端到端实操练习流水线"
	@echo "  make menu        - 打开交互式终端控制台菜单 (选项 0~10)"
	@echo "  make test        - 运行全量 94 项标准单元测试套件 (unittest)"
	@echo "  make benchmark   - 执行 autoresearch 自动化技术基准评估"
	@echo "  make check       - 探测 Mac Studio 统一内存与 Pixel 10 ADB 环境"
	@echo "  make report      - 打印多模态技术雷达与基准全景看板"
	@echo "  make server      - 启动本地 OpenAI 兼容多模态微服务网关 (8000端口)"
	@echo "  make clean       - 清理临时音频与数据测试缓存"
	@echo "=================================================================="

demo:
	bash examples/multimodal_practice/run_all_labs.sh

menu:
	bash examples/multimodal_practice/run_all_labs.sh --menu

test:
	$(PYTHON) tools/multimodal_tools/test_multimodal_suite.py

benchmark:
	bash autoresearch.sh

check:
	bash examples/multimodal_practice/setup_environment.sh --check

report:
	$(PYTHON) tools/multimodal_tools/benchmark_summary.py

server:
	$(PYTHON) examples/multimodal_practice/05_local_multimodal_server.py --port 8000 --host 0.0.0.0

clean:
	rm -rf /tmp/test_multimodal_audio.wav /tmp/multimodal_lora_data
	@echo "🧹 临时缓存已清理完毕。"
