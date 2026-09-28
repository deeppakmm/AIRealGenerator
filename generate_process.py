import os
from test_to_autio import text_to_speech_file
import time
import subprocess

def text_to_audio(folder):
    # print("Converting text to audio for folder:", folder)
    with open(f'user_uploads/{folder}/desc.txt', 'r') as f:
        text = f.read() 
    print("Text to convert:", text, folder)
    text_to_speech_file(text, folder)
def create_real(folder):
    print("Creating real for folder:", folder)
    command = f'''ffmpeg -f concat -safe 0 -i user_uploads/{folder}/input.txt -i user_uploads/{folder}/audio.mp3 -vf "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black" -c:v libx264 -c:a aac -shortest -r 30 -pix_fmt yuv420p static/reels/{folder}.mp4'''
    subprocess.run(command, shell=True, check=True)

def start1():
    time.sleep(1)
    print("Checking for new folders to process...")
    with open('done.txt', 'r') as f:
        done_folder = f.readlines()
    folders = os.listdir('user_uploads')
    done_folder = [folder.strip() for folder in done_folder]
            # print("Done folders:", done_folder)
    for folder in folders:
        if(folder not in done_folder):
            text_to_audio(folder)
            time.sleep(3)
            create_real(folder)
            with open('done.txt', 'a') as f:
                f.write(folder + '\n')
    
    



    # text_to_audio(folder)
    # create_real()