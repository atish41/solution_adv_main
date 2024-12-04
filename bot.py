import asyncio
import os
import sys
import argparse
import json
import  base64
from prompt import prompt
import datetime
from typing import Dict

from make_scenario import send_to_webhook
from pipecat.services.azure import AzureLLMService, AzureSTTService, AzureTTSService, Language

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.frames.frames import LLMMessagesFrame, EndFrame
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.services.openai import OpenAILLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.cartesia import CartesiaTTSService
from pipecat.transports.services.daily import DailyParams, DailyTransport, DailyTranscriptionSettings

from loguru import logger

from dotenv import load_dotenv

load_dotenv(override=True)

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")

daily_api_key = os.getenv("DAILY_API_KEY", "")
daily_api_url = os.getenv("DAILY_API_URL", "https://api.daily.co/v1")


async def save_message_log(context, participant_id: str):
    """Save the latest message log to a JSON file"""
    if context and context.get_messages():
        filename = f"message_log_{participant_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.abspath(filename)
        
        # Convert messages to a format that can be easily serialized
        messages_to_save = context.get_messages()
        
        #Removing the  first message because it's just the prompt
        messages_to_save=messages_to_save[1:]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(messages_to_save, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Message log saved to full path: {full_path}")


async def save_msg_and_email(context, participant_id:str, emails):
    """Save the latest message log to a JSON file"""
    if context and context.get_messages():
        filename = f"message_log_{participant_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        full_path = os.path.abspath(filename)
        
        # Convert messages to a format that can be easily serialized
        messages_to_save = context.get_messages()
        
        #Removing the  first message because it's just the prompt
        messages_to_save=messages_to_save[1:]

        send_to_webhook(emails,messages_to_save)
        



async def main(room_url: str, token: str , config_b64):

    transcriptions: Dict[str, list] = {}
    transport = DailyTransport(
        room_url,
        token,
        "Paddi",
        DailyParams(
            api_url=daily_api_url,
            api_key=daily_api_key,
            audio_in_enabled=True,
            audio_out_enabled=True,
            camera_out_enabled=False,
            vad_enabled=True,
            vad_analyzer=SileroVADAnalyzer(),
            transcription_enabled=True,
                    transcription_settings=DailyTranscriptionSettings(
                    language="en",  # Change to "es" for Spanish
                    tier="nova",
                    model="2-general"
                )

        ),
    )

    config_str = base64.b64decode(config_b64).decode()
    config = json.loads(config_str)


    tts_params = CartesiaTTSService.InputParams(
            speed=config["speed"],
            emotion=config["emotion"]
        )
    # tts = ElevenLabsTTSService(api_key=os.getenv("ELEVENLABS_API_KEY"), voice_id=os.getenv("ELEVENLABS_VOICE_ID"))
    # tts = CartesiaTTSService(
    #         api_key=os.getenv("CARTESIA_API_KEY"),
    #         voice_id=config['voice_id'],
    #         params=tts_params
      #  )

    tts_service = AzureTTSService(
        api_key=os.getenv("AZURE_API_KEY"),
        region=os.getenv("AZURE_REGION"),
        voice="en-NG-EzinneNeural",
        params=AzureTTSService.InputParams(
            language=Language.EN_US,
            rate="1.1",
            style="cheerful"
        )
    )


    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o")
    full_prompt=prompt+config['roadmap']
    messages = [
        {
            "role": "system",
            "content": full_prompt
        },
    ]

    context = OpenAILLMContext(messages)
    context_aggregator = llm.create_context_aggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),
            context_aggregator.user(),
            llm,
            tts_service,
            transport.output(),
            context_aggregator.assistant(),
        ]
    )

    task = PipelineTask(pipeline, PipelineParams(allow_interruptions=True))



    @transport.event_handler("on_transcription_message")
    async def on_transcription_message(transport, message):
        """Handle incoming transcriptions"""
        participant_id = message.get("participantId", "")
        if not participant_id:
            return

        if participant_id not in transcriptions:
            transcriptions[participant_id] = []
        
        # Store transcription with metadata
        transcriptions[participant_id].append({
            'text': message.get('text', ''),
            'timestamp': message.get('timestamp', datetime.datetime.now().isoformat()),
            'is_final': message.get('rawResponse', {}).get('is_final', False),
            'confidence': message.get('rawResponse', {}).get('confidence', 0.0)
        })
        
        # Print real-time transcription
        logger.info(f"Transcription from {participant_id}: {message.get('text', '')}")
        if message.get('rawResponse', {}).get('is_final'):
            logger.info(f"Final transcription confidence: {message.get('rawResponse', {}).get('confidence', 0.0)}")


    # @transport.event_handler("on_first_participant_joined")
    # async def on_first_participant_joined(transport, participant):
    #     await transport.capture_participant_transcription(participant["id"])
    #     await task.queue_frames([LLMMessagesFrame(messages)])

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        await transport.capture_participant_transcription(participant["id"])
        await task.queue_frames([LLMMessagesFrame(messages)])

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        """Handle participant leaving"""
        participant_id = participant['id']
        logger.info(f"Participant left: {participant_id}")
        
        # Print final transcriptions
        if participant_id in transcriptions:
            logger.info(f"\nFinal transcriptions for participant {participant_id}:")
            for entry in transcriptions[participant_id]:
                logger.info(f"[{entry['timestamp']}] {entry['text']}")
        

        #Extracting emails
        emails=config['emails']

        await task.queue_frame(EndFrame())
        
        
        await save_message_log(context, participant_id)
        await save_msg_and_email(context, participant_id, emails)


    @transport.event_handler("on_call_state_updated")
    async def on_call_state_updated(transport, state):
        if state == "left":
            await task.queue_frame(EndFrame())

    runner = PipelineRunner()

    await runner.run(task)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipecat Bot")
    parser.add_argument("-u", required=True,type=str, help="Room URL")
    parser.add_argument("-t",  required=True,type=str, help="Token")
    parser.add_argument("--config", required=True, help="Base64 encoded configuration")
    args = parser.parse_args()

    asyncio.run(main(args.u, args.t, args.config))