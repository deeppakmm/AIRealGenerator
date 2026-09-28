import subprocess

from test_to_autio import text_to_speech_file
from paths import REELS_FOLDER, UPLOAD_FOLDER

def text_to_audio(folder):
    with open(UPLOAD_FOLDER / folder / "desc.txt", "r", encoding="utf-8") as f:
        text = f.read() 
    print("Text to convert:", text, folder)
    text_to_speech_file(text, folder)

def create_real(folder):
    print("Creating real for folder:", folder)
    upload_dir = UPLOAD_FOLDER / folder
    REELS_FOLDER.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(upload_dir / "input.txt"),
        "-i", str(upload_dir / "audio.mp3"),
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        "-r", "30",
        "-pix_fmt", "yuv420p",
        str(REELS_FOLDER / f"{folder}.mp4"),
    ]
    subprocess.run(command, cwd=upload_dir, check=True)

def start1(folder):
    text_to_audio(folder)
    create_real(folder)