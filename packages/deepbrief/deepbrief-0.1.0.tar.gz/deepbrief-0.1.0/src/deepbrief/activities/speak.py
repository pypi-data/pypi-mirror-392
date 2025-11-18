import io
import logging
from pathlib import Path
from typing import Any

from dapr.ext.workflow import WorkflowActivityContext
from dapr_agents import ElevenLabsSpeechClient
from pydub import AudioSegment

from deepbrief.services import store_bytes

logger = logging.getLogger(__name__)


def convert_transcript_to_audio(ctx: WorkflowActivityContext, input_data: dict) -> dict[str, str]:
    """
    Convert a transcript into a single audio file via ElevenLabs and pydub.
    """
    try:
        input_data = input_data or {}
        transcript_parts: list[dict[str, Any]] = input_data.get("transcript_parts") or []
        recordings_directory: str = input_data.get("recordings_directory", "output/recordings")
        file_name: str = input_data.get("file_name", "podcast_episode")
        host_config: dict[str, Any] = input_data.get("host_config") or {}
        participants_config: list[dict[str, Any]] = input_data.get("participants_config") or []
        model: str = input_data.get("model", "eleven_flash_v2_5")
        storage_prefix: str = input_data.get("storage_prefix", "recordings")
        persist_locally = bool(input_data.get("persist_locally", True))

        logger.info(f"Starting audio generation for paper: {file_name}")
        client = ElevenLabsSpeechClient(model=model, output_format="mp3_44100_192")
        combined_audio = AudioSegment.silent(duration=500)  # Start with a short silence

        # Build voice mapping
        default_host_name = host_config.get("name", "Host")
        default_host_voice = host_config.get("voice", "Matilda")
        voice_mapping = {default_host_name: default_host_voice}
        for participant in participants_config:
            name = participant.get("name")
            voice = participant.get("voice")
            if name and voice:
                voice_mapping[name] = voice

        total_parts = len(transcript_parts)
        for index, part in enumerate(transcript_parts, start=1):
            speaker_name = part["name"]
            speaker_text = part["text"]
            assigned_voice = voice_mapping.get(speaker_name, "Cyb3rWard0g")

            # Log the current progress
            logger.info(f"Processing part {index} of {total_parts} for speaker {speaker_name}")

            # Generate the audio
            audio_bytes = client.create_speech(
                text=speaker_text,
                voice=assigned_voice
            )

            # Create an AudioSegment from the audio bytes
            audio_chunk = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

            # Append the audio to the combined segment
            combined_audio += audio_chunk + AudioSegment.silent(duration=300)

        buffer = io.BytesIO()
        combined_audio.export(buffer, format="mp3")
        audio_bytes = buffer.getvalue()

        file_path: str | None = None
        if persist_locally:
            Path(recordings_directory).mkdir(parents=True, exist_ok=True)
            file_path_obj = Path(recordings_directory) / f"{file_name}.mp3"
            combined_audio.export(file_path_obj, format="mp3")
            file_path = str(file_path_obj)
            logger.info("Podcast audio successfully saved to %s", file_path)

        storage_key = f"{storage_prefix}/{file_name}.mp3"
        store_bytes(storage_key, audio_bytes, metadata={"contentType": "audio/mpeg"})
        logger.info("Podcast audio uploaded to shared storage at %s", storage_key)
        return {"file_path": file_path, "storage_key": storage_key}

    except Exception as e:
        logger.error(f"Error during audio generation: {e}")
        raise
