#!/usr/bin/env bash

# ==============================================================================
# OpenCode 手机端 / 远程终端直连与穿透脚本 (remote-connect.sh)
#
# 功能特性：
#   1. 自有云服务器模式 (SSH 反向隧道)：纯 IP 直连，无需域名，通过自带 SSH 安全映射
#   2. 局域网 Wi-Fi 模式：同一 Wi-Fi 下快速扫码配对，自动识别内网 IP
#   3. 免配置临时穿透模式 (Cloudflare Quick Tunnel)：备用零依赖临时 HTTPS 穿透
#
# 使用示例：
#   ./remote-connect.sh --server 1.2.3.4                # 映射到自有公网服务器 (默认远程端口 8080)
#   ./remote-connect.sh --server 1.2.3.4 --user ubuntu  # 指定服务器登录用户
#   ./remote-connect.sh --server 1.2.3.4 --remote-port 9090 # 指定远程服务器映射端口
#   ./remote-connect.sh --lan                           # 本地局域网快速配对
#   ./remote-connect.sh --quick                         # 启动免域名免注册的临时穿透
#   ./remote-connect.sh --server-guide                  # 查看自有服务器 SSH 配置指引
# ==============================================================================

set -eo pipefail

# 默认变量定义
SERVER_IP=""
SSH_USER="${USER}"
SSH_PORT=22
SSH_KEY=""
REMOTE_PORT=8888 # 默认改为腾讯云已放行且空闲的端口 8888
MODE="auto" # auto | ssh | lan | quick
TUNNEL_PID=""
CONFIG_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.remote.env"

# 尝试载入历史配置（如存在）
if [[ -f "${CONFIG_FILE}" ]]; then
  # shellcheck source=/dev/null
  source "${CONFIG_FILE}" 2>/dev/null || true
fi

# 颜色控制定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ------------------------------------------------------------------------------
# 退出清理函数：确保退出脚本时终止后台 SSH 隧道或穿透进程
# ------------------------------------------------------------------------------
cleanup() {
  if [[ -n "${TUNNEL_PID}" ]] && kill -0 "${TUNNEL_PID}" 2>/dev/null; then
    echo -e "\n${YELLOW}[INFO] 正在关闭后台转发隧道 (PID: ${TUNNEL_PID})...${NC}"
    kill "${TUNNEL_PID}" 2>/dev/null || true
    wait "${TUNNEL_PID}" 2>/dev/null || true
    echo -e "${GREEN}[OK] 远程通道已安全关闭。${NC}"
  fi
}
trap cleanup EXIT INT TERM

# ------------------------------------------------------------------------------
# 打印帮助信息
# ------------------------------------------------------------------------------
show_help() {
  echo -e "${BOLD}OpenCode 移动端连接与内网穿透管理工具${NC}"
  echo ""
  echo -e "${CYAN}用法:${NC}"
  echo "  $0 [选项]"
  echo ""
  echo -e "${CYAN}主要模式:${NC}"
  echo -e "  ${BOLD}--server <IP>${NC}             指定自有公网云服务器 IP，建立 SSH 反向隧道 (无需域名)"
  echo -e "  ${BOLD}--lan${NC}                     局域网 Wi-Fi 模式，手机连接同一路由器时直接扫码"
  echo -e "  ${BOLD}--quick${NC}                   免配置临时穿透 (Cloudflare Quick Tunnel，自动分配临时公网链接)"
  echo -e "  ${BOLD}--server-guide${NC}            查看自有公网服务器一分钟配置指引 (GatewayPorts 开启教程)"
  echo ""
  echo -e "${CYAN}自有服务器 SSH 选项:${NC}"
  echo "  --user <用户名>            SSH 登录用户名 (默认: ${USER})"
  echo "  --ssh-port <端口>          SSH 连接端口 (默认: 22)"
  echo "  --port, --remote-port <端口> 公网云服务器上对外开放的访问端口 (默认: 18080)"
  echo "  --key <私钥路径>           指定 SSH 私钥文件路径 (如 ~/.ssh/id_rsa)"
  echo "  --save                     保存当前服务器和端口配置到 .remote.env，下次直连"
  echo ""
  echo -e "${CYAN}通用选项:${NC}"
  echo "  -h, --help                 显示本帮助信息"
  echo ""
  echo -e "${CYAN}典型使用场景示例:${NC}"
  echo -e "  ${GREEN}1. 手机在室外蜂窝网络，连家里的 Mac (自有服务器，指定新端口如 18080):${NC}"
  echo "     $0 --server 123.57.10.20 --user root --port 18080"
  echo ""
  echo -e "${GREEN}2. 手机和 Mac 连同一个家里/办公室 Wi-Fi:${NC}"
  echo "     $0 --lan"
  echo ""
  echo -e "${GREEN}3. 临时无服务器可用，快速生成临时外网链接:${NC}"
  echo "     $0 --quick"
  echo ""
}

# ------------------------------------------------------------------------------
# 显示云服务器配置指引
# ------------------------------------------------------------------------------
show_server_guide() {
  echo -e "${BOLD}${CYAN}=== 自有公网云服务器一分钟配置指引 ===${NC}"
  echo ""
  echo "由于 SSH 反向代理默认仅监听服务器本地的 127.0.0.1，"
  echo "为了让手机等外网设备能直接通过 http://<服务器IP>:<端口> 访问，"
  echo "仅需在云服务器上开启 GatewayPorts 功能："
  echo ""
  echo -e "${YELLOW}第一步：在您的公网云服务器上执行：${NC}"
  echo "  sudo sed -i 's/^#*GatewayPorts.*/GatewayPorts yes/' /etc/ssh/sshd_config"
  echo "  # 若系统中未配置该项，直接追加："
  echo "  grep -q \"^GatewayPorts yes\" /etc/ssh/sshd_config || echo \"GatewayPorts yes\" | sudo tee -a /etc/ssh/sshd_config"
  echo "  # 重启 SSH 服务生效："
  echo "  sudo systemctl restart sshd || sudo service ssh restart"
  echo ""
  echo -e "${YELLOW}第二步：开放云服务器防火墙/安全组端口：${NC}"
  echo "  在阿里云/腾讯云/华为云/AWS 等控制台安全组入方向规则中，放行对应的端口（如 TCP 8080）。"
  echo ""
  echo -e "${GREEN}配置完成后，在 Mac 本机直接运行：${NC}"
  echo "  ./remote-connect.sh --server <您的服务器公网IP>"
  echo "  手机扫描终端生成的二维码即可畅享 OpenCode！"
  echo ""
}

# ------------------------------------------------------------------------------
# 检查并确保 OpenCode 服务就绪，并提取本地监听端口
# 返回值：全局变量 LOCAL_PORT
# ------------------------------------------------------------------------------
ensure_opencode_service() {
  if ! command -v opencode &>/dev/null; then
    echo -e "${RED}[ERROR] 未检测到 opencode 命令，请先安装 OpenCode CLI。${NC}" >&2
    exit 1
  fi

  echo -e "${CYAN}[INFO] 正在检测 OpenCode 后台服务状态...${NC}"

  # 确保服务绑定在 0.0.0.0 避免跨设备拦截
  local current_host
  current_host=$(opencode service get 2>/dev/null | grep -o '"hostname": *"[^"]*"' | cut -d'"' -f4 || echo "")
  if [[ "${current_host}" != "0.0.0.0" ]]; then
    echo -e "${YELLOW}[INFO] 设置 OpenCode 服务绑定地址为 0.0.0.0...${NC}"
    opencode service set hostname 0.0.0.0 >/dev/null 2>&1 || true
    opencode service restart >/dev/null 2>&1 || true
    sleep 1
  fi

  # 获取服务 URL 和端口
  local raw_status
  raw_status=$(opencode service status 2>/dev/null | tail -n 1 || echo "")

  if [[ -z "${raw_status}" || "${raw_status}" != http* ]]; then
    echo -e "${YELLOW}[INFO] 正在启动 OpenCode 后台服务...${NC}"
    opencode service start >/dev/null 2>&1 || true
    sleep 2
    raw_status=$(opencode service status 2>/dev/null | tail -n 1 || echo "")
  fi

  LOCAL_PORT=$(echo "${raw_status}" | sed -E 's|.*:([0-9]+).*|\1|')

  if [[ -z "${LOCAL_PORT}" || ! "${LOCAL_PORT}" =~ ^[0-9]+$ ]]; then
    echo -e "${RED}[ERROR] 无法获取 OpenCode 服务端口，请手动运行 'opencode service status' 检查。${NC}" >&2
    exit 1
  fi

  echo -e "${GREEN}[OK] OpenCode 本地服务就绪，端口: ${LOCAL_PORT}${NC}"
}

# ------------------------------------------------------------------------------
# 获取本机局域网 IP
# ------------------------------------------------------------------------------
get_local_ip() {
  local ip=""
  # macOS 优先检查常见活跃网卡
  for iface in en0 en1 en2 en3; do
    ip=$(ipconfig getifaddr "${iface}" 2>/dev/null || true)
    if [[ -n "${ip}" ]]; then
      break
    fi
  done

  # Linux 备选
  if [[ -z "${ip}" ]]; then
    ip=$(hostname -I 2>/dev/null | awk '{print $1}' || true)
  fi

  if [[ -z "${ip}" ]]; then
    ip="127.0.0.1"
  fi
  echo "${ip}"
}

# ------------------------------------------------------------------------------
# 模式 1：自有服务器 SSH 反向隧道直连 (主力推荐)
# ------------------------------------------------------------------------------
run_ssh_mode() {
  local target_url="http://${SERVER_IP}:${REMOTE_PORT}"

  echo ""
  echo -e "${BOLD}${CYAN}================================================================${NC}"
  echo -e "${BOLD}${CYAN}         OpenCode 自有服务器反向隧道模式 (纯 IP 直连)           ${NC}"
  echo -e "${BOLD}${CYAN}================================================================${NC}"
  echo -e "公网服务器 IP:   ${GREEN}${SERVER_IP}${NC}"
  echo -e "远程映射端口:    ${GREEN}${REMOTE_PORT}${NC}"
  echo -e "本地服务端口:    ${GREEN}${LOCAL_PORT}${NC}"
  echo -e "SSH 登录账户:    ${GREEN}${SSH_USER}@${SERVER_IP}:${SSH_PORT}${NC}"
  echo -e "移动端访问地址:  ${BOLD}${YELLOW}${target_url}${NC}"
  echo -e "${CYAN}----------------------------------------------------------------${NC}"

  # 构建 SSH 隧道命令
  local ssh_opts=(-N -T -o "ExitOnForwardFailure=yes" -o "ServerAliveInterval=30" -o "ServerAliveCountMax=3")
  if [[ -n "${SSH_KEY}" ]]; then
    ssh_opts+=(-i "${SSH_KEY}")
  fi
  if [[ "${SSH_PORT}" != "22" ]]; then
    ssh_opts+=(-p "${SSH_PORT}")
  fi

  echo -e "${CYAN}[INFO] 正在建立 SSH 远程端口转发隧道 (0.0.0.0:${REMOTE_PORT} -> 127.0.0.1:${LOCAL_PORT})...${NC}"

  # 后台启动 SSH 隧道
  ssh "${ssh_opts[@]}" -R "0.0.0.0:${REMOTE_PORT}:127.0.0.1:${LOCAL_PORT}" "${SSH_USER}@${SERVER_IP}" &
  TUNNEL_PID=$!

  # 延时检测 SSH 进程是否成功维持
  sleep 2
  if ! kill -0 "${TUNNEL_PID}" 2>/dev/null; then
    echo -e "${RED}[ERROR] SSH 隧道启动失败！请排查：${NC}" >&2
    echo -e "  1. 远程端口是否冲突：云服务器上的 ${REMOTE_PORT} 端口可能已被占用，可尝试指定其他空闲端口，例如：$0 --server ${SERVER_IP} --port 18080" >&2
    echo -e "  2. 远程网关端口未开启：云服务器 /etc/ssh/sshd_config 必须设置 'GatewayPorts yes' (运行 $0 --server-guide 查看)" >&2
    echo -e "  3. 认证权限问题：是否能通过 'ssh -p ${SSH_PORT} ${SSH_USER}@${SERVER_IP}' 免密或正常登录？" >&2
    exit 1
  fi

  echo -e "${GREEN}[OK] SSH 反向隧道建立成功！${NC}"
  echo -e "${CYAN}[INFO] 正在生成手机端专属安全配对二维码...${NC}\n"

  # 调用 opencode 原生配对生成命令
  opencode pair --url "${target_url}"

  echo ""
  echo -e "${BOLD}${GREEN}提示：${NC}"
  echo -e "  1. 用手机自带相机或微信扫描上方二维码即可直接使用！"
  echo -e "  2. 进入页面后可点击浏览器菜单 -> ${BOLD}“添加到主屏幕”${NC}，获得原生 App 级操作体验。"
  echo -e "  3. 按 ${BOLD}Ctrl + C${NC} 可随时终止本次远程连接并安全清理隧道。"
  echo ""

  # 挂起保持隧道进程
  wait "${TUNNEL_PID}"
}

# ------------------------------------------------------------------------------
# 模式 2：局域网 Wi-Fi 模式
# ------------------------------------------------------------------------------
run_lan_mode() {
  local lan_ip
  lan_ip=$(get_local_ip)
  local target_url="http://${lan_ip}:${LOCAL_PORT}"

  echo ""
  echo -e "${BOLD}${CYAN}================================================================${NC}"
  echo -e "${BOLD}${CYAN}             OpenCode 本地局域网快速配对模式                   ${NC}"
  echo -e "${BOLD}${CYAN}================================================================${NC}"
  echo -e "当前局域网 IP:   ${GREEN}${lan_ip}${NC}"
  echo -e "服务端口:        ${GREEN}${LOCAL_PORT}${NC}"
  echo -e "连接地址:        ${BOLD}${YELLOW}${target_url}${NC}"
  echo -e "${CYAN}----------------------------------------------------------------${NC}"
  echo -e "${YELLOW}请确保手机与当前电脑连接在同一个 Wi-Fi 网络下。${NC}\n"

  opencode pair --url "${target_url}"

  echo ""
  echo -e "${BOLD}${GREEN}提示：${NC} 手机扫码后在浏览器中点击“添加到主屏幕”，即可像独立 App 一样随时使用。"
}

# ------------------------------------------------------------------------------
# 模式 3：Cloudflare Quick Tunnel 临时免域名穿透 (备选降级方案)
# ------------------------------------------------------------------------------
run_quick_tunnel_mode() {
  echo ""
  echo -e "${BOLD}${CYAN}================================================================${NC}"
  echo -e "${BOLD}${CYAN}       OpenCode 免配置临时穿透模式 (Cloudflare Quick Tunnel)    ${NC}"
  echo -e "${BOLD}${CYAN}================================================================${NC}"

  local cloudflared_bin
  if command -v cloudflared &>/dev/null; then
    cloudflared_bin="cloudflared"
  else
    local cache_dir="${HOME}/.cache/opencode"
    mkdir -p "${cache_dir}"
    cloudflared_bin="${cache_dir}/cloudflared"

    if [[ ! -x "${cloudflared_bin}" ]]; then
      echo -e "${YELLOW}[INFO] 未检测到 cloudflared 工具，正在自动下载官方独立运行时...${NC}"
      local arch="amd64"
      if [[ "$(uname -m)" == "arm64" ]]; then
        arch="arm64"
      fi
      local download_url="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-${arch}.tgz"

      echo -e "${CYAN}[INFO] 下载源: ${download_url}${NC}"
      curl -sSL --connect-timeout 10 -o "${cache_dir}/cloudflared.tgz" "${download_url}"
      tar -xzf "${cache_dir}/cloudflared.tgz" -C "${cache_dir}"
      chmod +x "${cloudflared_bin}"
      rm -f "${cache_dir}/cloudflared.tgz"
      echo -e "${GREEN}[OK] cloudflared 下载完毕！${NC}"
    fi
  fi

  echo -e "${CYAN}[INFO] 正在启动临时安全隧道...${NC}"
  local log_file
  log_file=$(mktemp -t opencode-tunnel.XXXXXX)

  "${cloudflared_bin}" tunnel --url "http://127.0.0.1:${LOCAL_PORT}" >"${log_file}" 2>&1 &
  TUNNEL_PID=$!

  echo -e "${CYAN}[INFO] 等待分配临时 HTTPS 安全域名...${NC}"
  local assigned_url=""
  local attempts=0
  while [[ ${attempts} -lt 30 ]]; do
    assigned_url=$(grep -Eo 'https://[a-zA-Z0-9-]+\.trycloudflare\.com' "${log_file}" | head -n 1 || true)
    if [[ -n "${assigned_url}" ]]; then
      break
    fi
    sleep 1
    attempts=$((attempts + 1))
  done

  rm -f "${log_file}"

  if [[ -z "${assigned_url}" ]]; then
    echo -e "${RED}[ERROR] 获取临时公网链接超时，请检查网络是否能访问 Cloudflare 边缘节点。${NC}" >&2
    exit 1
  fi

  echo -e "${GREEN}[OK] 临时穿透隧道就绪！公网地址: ${BOLD}${YELLOW}${assigned_url}${NC}\n"
  opencode pair --url "${assigned_url}"

  echo ""
  echo -e "${BOLD}${GREEN}提示：${NC} 临时隧道已启动，按 ${BOLD}Ctrl + C${NC} 退出并销毁临时公网链接。"
  wait "${TUNNEL_PID}"
}

# ------------------------------------------------------------------------------
# 命令行参数解析
# ------------------------------------------------------------------------------
parse_arguments() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --server)
        SERVER_IP="$2"
        MODE="ssh"
        shift 2
        ;;
      --user)
        SSH_USER="$2"
        shift 2
        ;;
      --ssh-port)
        SSH_PORT="$2"
        shift 2
        ;;
      --remote-port|--port|-p)
        REMOTE_PORT="$2"
        shift 2
        ;;
      --key)
        SSH_KEY="$2"
        shift 2
        ;;
      --save)
        SAVE_CONFIG=true
        shift
        ;;
      --lan)
        MODE="lan"
        shift
        ;;
      --quick)
        MODE="quick"
        shift
        ;;
      --server-guide)
        show_server_guide
        exit 0
        ;;
      -h|--help)
        show_help
        exit 0
        ;;
      *)
        echo -e "${RED}[ERROR] 未知参数: $1${NC}" >&2
        echo "运行 '$0 --help' 查看可用选项。"
        exit 1
        ;;
    esac
  done
}

# ------------------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------------------
main() {
  parse_arguments "$@"

  # 如果显式要求保存或指定了服务器并带 --save
  if [[ "${SAVE_CONFIG:-false}" == "true" && -n "${SERVER_IP}" ]]; then
    cat > "${CONFIG_FILE}" <<EOF
# OpenCode 远程穿透历史配置文件
SERVER_IP="${SERVER_IP}"
SSH_USER="${SSH_USER}"
SSH_PORT="${SSH_PORT}"
REMOTE_PORT="${REMOTE_PORT}"
SSH_KEY="${SSH_KEY}"
EOF
    echo -e "${GREEN}[OK] 远程配置已保存至 ${CONFIG_FILE}${NC}"
  fi

  # 确保 OpenCode 服务就绪并解析端口
  ensure_opencode_service

  # 如果未显式指定模式但已配置 SERVER_IP，自动切入 ssh 模式
  if [[ "${MODE}" == "auto" && -n "${SERVER_IP}" ]]; then
    echo -e "${CYAN}[INFO] 检测到已保存的服务器配置 (${SERVER_IP}:${REMOTE_PORT})，自动启用自有服务器模式...${NC}"
    MODE="ssh"
  fi

  case "${MODE}" in
    ssh)
      if [[ -z "${SERVER_IP}" ]]; then
        echo -e "${RED}[ERROR] SSH 模式必须指定公网服务器 IP (例如: $0 --server 1.2.3.4)${NC}" >&2
        exit 1
      fi
      run_ssh_mode
      ;;
    lan)
      run_lan_mode
      ;;
    quick)
      run_quick_tunnel_mode
      ;;
    auto)
      # 未指定时，提示用户选择或默认推荐局域网
      echo -e "${YELLOW}[TIP] 未指定运行模式。${NC}"
      echo -e "若需连接到您的公网云服务器，请运行:  ${GREEN}$0 --server <服务器IP> --port <端口>${NC}"
      echo -e "若需在同一 Wi-Fi 下快速扫码使用，请运行: ${GREEN}$0 --lan${NC}"
      echo -e "若需免配置临时外网穿透，请运行:         ${GREEN}$0 --quick${NC}"
      echo ""
      echo -e "${CYAN}默认启动局域网 Wi-Fi 快速配对模式...${NC}"
      run_lan_mode
      ;;
  esac
}

main "$@"
