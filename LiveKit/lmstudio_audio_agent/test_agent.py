import pytest
import asyncio
from probe import probe_models, pick_best_chat_model
from livekit.plugins import openai
from livekit.agents import llm

def test_probe_models_remote():
    """测试能够从 100.126.144.68:1234 成功探测到模型"""
    models = probe_models()
    assert len(models) > 0, "未能从远端 LM Studio 获取到任何模型"
    model_ids = [m["id"] for m in models]
    assert "qwen/qwen3-vl-8b" in model_ids

def test_pick_best_chat_model():
    """测试智能模型推荐算法"""
    mock_models = [
        {"id": "text-embedding-v1", "type": "embeddings", "state": "not-loaded"},
        {"id": "qwen3-vl-32b-thinking-mlx", "type": "vlm", "state": "not-loaded"},
        {"id": "qwen/qwen3-vl-8b", "type": "vlm", "state": "loaded"},
    ]
    picked = pick_best_chat_model(mock_models)
    assert picked == "qwen/qwen3-vl-8b"

@pytest.mark.asyncio
async def test_livekit_openai_plugin_remote_llm_stream():
    """测试 LiveKit openai.LLM 与远端 LM Studio 的流式交互"""
    models = probe_models()
    target_model = pick_best_chat_model(models)
    
    remote_llm = openai.LLM(
        base_url="http://100.126.144.68:1234/v1",
        api_key="lm-studio",
        model=target_model,
        temperature=0.5,
    )

    chat_ctx = llm.ChatContext()
    chat_ctx.add_message(
        role="user",
        content="请只回答两个字：你好"
    )

    stream = remote_llm.chat(chat_ctx=chat_ctx)
    chunks = []
    async for chunk in stream:
        if chunk.delta and chunk.delta.content:
            chunks.append(chunk.delta.content)

    full_text = "".join(chunks).strip()
    assert len(full_text) > 0, "LLM 返回的流式响应为空"
    print(f"\n[测试收到响应]: {full_text} (模型: {target_model})")
