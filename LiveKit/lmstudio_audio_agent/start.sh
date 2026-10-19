#!/usr/bin/env bash
# ==============================================================================
# LiveKit + LM Studio Audio Agent 一键启动与运行脚本
# ==============================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}  LiveKit + LM Studio Audio Agent 一键启动器         ${NC}"
echo -e "${BLUE}======================================================${NC}"

# 1. 检查或准备 Python 虚拟环境
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}[1/4] 创建 Python 虚拟环境...${NC}"
    uv venv .venv --python 3.12
    uv pip install --python .venv/bin/python -r requirements.txt
else
    echo -e "${GREEN}[1/4] Python 虚拟环境已就绪 (.venv)${NC}"
fi

# 2. 检查 .env 配置文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}[2/4] 未发现 .env，基于 .env.example 自动生成...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}请注意：若需语音识别/合成，请在 .env 中填入 DEEPGRAM_API_KEY${NC}"
fi

# 3. 探测远端 LM Studio 主机
echo -e "${YELLOW}[3/4] 探测 LM Studio 节点状态与大模型...${NC}"
.venv/bin/python probe.py

# 4. 检查并启动本地 livekit-server
echo -e "${YELLOW}[4/4] 检查本地 LiveKit Server...${NC}"
if ! nc -z 127.0.0.1 7880 2>/dev/null; then
    echo -e "正在后台拉起本地 livekit-server (dev 模式)..."
    livekit-server --dev > /tmp/livekit-server.log 2>&1 &
    LK_PID=$!
    sleep 2
    if nc -z 127.0.0.1 7880 2>/dev/null; then
        echo -e "${GREEN}✓ LiveKit Server 已成功在后台启动 (PID: $LK_PID, 端口: 7880)${NC}"
    else
        echo -e "${RED}✗ LiveKit Server 启动失败，请检查 /tmp/livekit-server.log${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ 本地 LiveKit Server 已经在运行中 (端口: 7880)${NC}"
fi

# 5. 生成浏览器连接 Token
ROOM_NAME="audio-room-$(date +%s)"
USER_NAME="tester-$(date +%s)"
TOKEN_OUTPUT=$(lk token create --dev --join --room "$ROOM_NAME" --identity "$USER_NAME" --token-only 2>/dev/null || true)

echo -e "\n${GREEN}================== 浏览器连接信息 ==================${NC}"
echo -e "1. 打开测试控制台: ${BLUE}https://agents-playground.livekit.io/${NC}"
echo -e "2. Server URL:     ${YELLOW}ws://localhost:7880${NC}"
if [ -n "$TOKEN_OUTPUT" ]; then
    echo -e "3. 一键房间 Token: ${GREEN}$TOKEN_OUTPUT${NC}"
    echo -e "   (直接复制上方 Token 粘贴到网页的 Token 输入框点击 Connect 即可)"
fi
echo -e "${GREEN}====================================================${NC}\n"

# 清理钩子：退出脚本时可选是否杀死后台的 livekit-server
cleanup() {
    echo -e "\n${YELLOW}正在停止 Agent...${NC}"
    if [ -n "$LK_PID" ]; then
        echo -e "正在关闭后台 LiveKit Server (PID: $LK_PID)..."
        kill "$LK_PID" 2>/dev/null || true
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${BLUE}正在前台启动 Audio Agent Worker... (按 Ctrl+C 可停止)${NC}"
.venv/bin/python agent.py dev
