import youtube_dl
import moviepy.editor as mp
import os
from pathlib import Path

# Define paths
video_path = r"C:\Users\szhang\Downloads\PXL_20240803_204824804.mp4"  # Update this if necessary
audio_url = "https://youtu.be/XcyxqunCmb8"
desktop_path = str(Path.home() / "Desktop")
audio_path = os.path.join(desktop_path, "downloaded_audio.mp3")
output_path = "output_video.mp4"

# Download audio from YouTube
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': audio_path,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([audio_url])

# Load video and audio
video = mp.VideoFileClip(video_path)
audio = mp.AudioFileClip(audio_path)

# Trim audio if longer than video
if audio.duration > video.duration:
    audio = audio.subclip(0, video.duration)

# Overlay audio onto video
final_video = video.set_audio(audio)

# Save the result
final_video.write_videofile(output_path, codec='libx264')

# Cleanup: remove the downloaded audio file from Desktop
os.remove(audio_path)

print("The final video has been saved to:", output_path)
