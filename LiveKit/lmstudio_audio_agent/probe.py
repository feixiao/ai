import os
import requests

LMSTUDIO_HOST = os.getenv("LMSTUDIO_HOST", "100.126.144.68")
LMSTUDIO_PORT = os.getenv("LMSTUDIO_PORT", "1234")
BASE_URL = f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}"

def probe_models(timeout: float = 5.0):
    """
    探测远端 LM Studio 主机的模型列表与加载状态
    """
    v0_url = f"{BASE_URL}/api/v0/models"
    v1_url = f"{BASE_URL}/v1/models"
    
    try:
        resp = requests.get(v0_url, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            models = []
            for item in data:
                models.append({
                    "id": item.get("id"),
                    "type": item.get("type"),
                    "state": item.get("state", "unknown"),
                    "arch": item.get("arch"),
                    "quantization": item.get("quantization"),
                    "context_length": item.get("max_context_length"),
                })
            return models
    except Exception:
        pass

    # 回退到标准 v1/models
    resp = requests.get(v1_url, timeout=timeout)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return [{"id": item.get("id"), "state": "available"} for item in data]

def pick_best_chat_model(models):
    """
    从模型列表中筛选最适合实时语音交互的模型 (优先已加载、轻量指令对话模型)
    """
    if not models:
        return "qwen/qwen3-vl-8b"
    
    # 1. 优先找当前已加载的模型 (state == 'loaded')
    loaded_models = [m for m in models if m.get("state") == "loaded" and m.get("type") != "embeddings"]
    if loaded_models:
        return loaded_models[0]["id"]
    
    # 2. 如果未显式加载，优先选择适合语音对话的轻量小模型 (8b 级别优先，低延迟)
    priority_keywords = ["8b", "7b", "it", "instruct", "qwen3"]
    chat_models = [m for m in models if m.get("type") != "embeddings"]
    
    for kw in priority_keywords:
        for m in chat_models:
            if kw in m["id"].lower():
                return m["id"]
    
    return chat_models[0]["id"] if chat_models else "qwen/qwen3-vl-8b"

if __name__ == "__main__":
    print(f"正在探测 LM Studio 节点 ({BASE_URL}) ...")
    models = probe_models()
    print(f"成功探测到 {len(models)} 个可用模型:")
    for idx, m in enumerate(models, 1):
        state_info = f" [{m.get('state')}]" if 'state' in m else ""
        type_info = f" ({m.get('type')})" if 'type' in m else ""
        print(f"  {idx}. {m['id']}{type_info}{state_info}")
    
    recommended = pick_best_chat_model(models)
    print(f"\n推荐用于实时语音 Agent 的模型: -> {recommended}")
