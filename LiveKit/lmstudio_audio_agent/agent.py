import os
import asyncio
from dotenv import load_dotenv

from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice import Agent
from livekit.plugins import silero, openai, deepgram
from probe import probe_models, pick_best_chat_model

load_dotenv()

# 远端 LM Studio 节点配置
LMSTUDIO_HOST = os.getenv("LMSTUDIO_HOST", "100.126.144.68")
LMSTUDIO_PORT = os.getenv("LMSTUDIO_PORT", "1234")
LMSTUDIO_BASE_URL = f"http://{LMSTUDIO_HOST}:{LMSTUDIO_PORT}/v1"

# 动态探测或指定模型
PROBED_MODELS = probe_models()
CONFIGURED_MODEL = os.getenv("LMSTUDIO_MODEL") or pick_best_chat_model(PROBED_MODELS)

def prewarm(proc: JobProcess):
    """预加载 Silero VAD (语音活动检测) 模型"""
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    """LiveKit Worker 入口，处理房间连入与语音管道生命周期"""
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 1. 实例化对接 LM Studio 的 LLM 客户端
    lmstudio_llm = openai.LLM(
        base_url=LMSTUDIO_BASE_URL,
        api_key="lm-studio",
        model=CONFIGURED_MODEL,
        temperature=0.6,
    )

    # 2. 构造语音交互 Agent (LiveKit Agents 1.8.8 voice.Agent 架构)
    agent = Agent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(language="zh-CN"),
        llm=lmstudio_llm,
        tts=deepgram.TTS(voice="zh-CN-Standard-A"),
        instructions=(
            "你是一个自然、幽默的实时语音对话助手。"
            "你由运行在局域网 LM Studio 上的本地大模型驱动。"
            "必须使用地道且简短的中文回答，回答尽量在 1~2 句话之内（控制在 30 字内）。"
            "绝对不要输出 Markdown 标签、Emoji 表情、括号动作或任何代码格式，确保生成的文本适合直接语音朗读。"
        ),
    )

    # 3. 监听用户进入房间事件，发起主动问候
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        asyncio.create_task(
            agent.say(
                f"你好！我已经接入远端 LM Studio 大模型 {CONFIGURED_MODEL}，请问有什么可以帮你？",
                allow_interruptions=True,
            )
        )

    # 4. 启动音频流处理
    agent.start(ctx.room)

if __name__ == "__main__":
    print(f"=== LiveKit LM Studio Audio Agent ===")
    print(f"LM Studio API: {LMSTUDIO_BASE_URL}")
    print(f"选用模型: {CONFIGURED_MODEL}")
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
