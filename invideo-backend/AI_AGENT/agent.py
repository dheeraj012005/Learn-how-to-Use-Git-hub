import os
import subprocess
import requests
from moviepy.editor import *
from datetime import datetime

os.makedirs("output", exist_ok=True)
os.makedirs("temp", exist_ok=True)

topic = input("Enter video topic: ")

print("Generating script...")

script = subprocess.check_output(
    f'ollama run llama3 "Write a short YouTube script in 5 scenes about: {topic}"',
    shell=True
).decode()

with open("temp/script.txt", "w") as f:
    f.write(script)

print("Generating voice...")

subprocess.run(
    'piper -m en_US-lessac-medium.onnx -f temp/voice.wav < temp/script.txt',
    shell=True
)

print("Downloading visuals...")

images = []
for i in range(5):
    url = f"https://picsum.photos/1280/720?random={i}"
    img_data = requests.get(url).content
    file = f"temp/img{i}.jpg"
    with open(file, 'wb') as f:
        f.write(img_data)
    images.append(file)

print("Creating video...")

clips = []
for img in images:
    clip = ImageClip(img).set_duration(5)
    clips.append(clip)

video = concatenate_videoclips(clips)

voice = AudioFileClip("temp/voice.wav")

music_url = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_2d1fcb6c9b.mp3"
music_data = requests.get(music_url).content
with open("temp/music.mp3", "wb") as f:
    f.write(music_data)

music = AudioFileClip("temp/music.mp3").volumex(0.2)

final_audio = CompositeAudioClip([voice, music])

video = video.set_audio(final_audio)

output = f"output/video_{datetime.now().strftime('%H%M%S')}.mp4"

video.write_videofile(output, fps=24)

print("DONE →", output)
