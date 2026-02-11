from dotenv import load_dotenv
from livekit import agents,rtc
from livekit.agents import AgentServer, AgentSession, room_io, Agent
from livekit.plugins import silero, noise_cancellation, deepgram, elevenlabs, groq
from livekit.plugins.turn_detector.multilingual import MultilingualModel


load_dotenv('.env.local')
import os 
class Assistant(Agent):
    def __init__(self)->None:
        super().__init__(
            instructions="You are a helpful assistant that listens to the user's request and responds with a concise answer. Ignore the background noises and be fast in answer generation "
        )
server=AgentServer()

@server.rtc_session()
async def my_agent(ctx:agents.JobContext):
    session= AgentSession(

           stt=deepgram.STT(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
        ),
            tts=deepgram.TTS(
            api_key=os.getenv("DEEPGRAM_API_KEY"),
           
        ),
    vad=silero.VAD.load(),
    turn_detection=MultilingualModel(),
        llm=groq.LLM(model="llama-3.3-70b-versatile")
    )   

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
             audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: noise_cancellation.BVCTelephony() if params.participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP else noise_cancellation.BVC(),
        )),
    )
    await session.generate_reply(instructions="Greet the user and offer your assistance.")

if __name__ == "__main__":
    agents.cli.run_app(server)