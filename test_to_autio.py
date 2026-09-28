
import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

from paths import UPLOAD_FOLDER

load_dotenv(Path(__file__).resolve().parent / ".env")


def text_to_speech_file(text: str, folder:str) -> str:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if not api_key:
        raise RuntimeError("Set ELEVENLABS_API_KEY in the environment before creating a reel.")

    elevenlabs = ElevenLabs(api_key=api_key)
    # Calling the text_to_speech conversion API with detailed parameters
    response = elevenlabs.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_flash_v2_5", # use the flash model for low latency
        # Optional voice settings that allow you to customize the output
        voice_settings=VoiceSettings(
            stability=0.0,
            similarity_boost=1.0,
            style=0.0,
            use_speaker_boost=True,
            speed=1.0,
        ),
    )

    # uncomment the line below to play the audio back
    # play(response)

    # Generating a unique file name for the output MP3 file
    save_file_path = str(UPLOAD_FOLDER / folder / "audio.mp3")

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path
# text_to_speech_file("Hello, this is a test.", "5e6561a1-b6a3-11f1-ac7a-b5c9e10a3daf")
