import pygame
from pytube import YouTube
import moviepy.editor as mp
import os
from PIL import ImageTk, Image, ImageOps


def download_video(folder_path: str, filename: str, link: str) -> bool:
    if os.path.exists(fr"{folder_path}\{filename}.mp4"):
        return False
    try:
        YouTube(link).streams.filter(only_audio=True).first().download(folder_path, f"{filename}.mp4")
        mp3_file = mp.AudioFileClip(fr"{folder_path}\{filename}.mp4")
        mp3_file.write_audiofile(fr"{folder_path}\{filename}.mp3", verbose=False, logger=None)
        os.remove(fr"{folder_path}\{filename}.mp4")
    except:
        return False
    return True

def play(channel: pygame.mixer.Channel, audio: pygame.mixer.Sound) -> None:
    channel.play(audio)

def pause(channel: pygame.mixer.Channel) -> None:
    channel.pause()

def open_img(size: tuple, img_path: str):
    img = Image.open(img_path)
    if size is not None:
        # Get the dimensions of the image and the button
        img_width, img_height = img.size
        width, height = size
        
        # Calculate the aspect ratio of the image
        aspect_ratio = img_width / img_height
        
        # Calculate the new dimensions to fit within the button
        if width / height > aspect_ratio:
            new_width = int(height * aspect_ratio)
            new_height = height
        else:
            new_width = width
            new_height = int(width / aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)
    
if __name__ == "__main__":
    pygame.init()
    download_video(r"C:\Users\aisha\garbage\music_player-1\music", "Best of You", "https://www.youtube.com/watch?v=kjT-YBzqMCE")
    # audio = pygame.mixer.Sound(r"C:\Users\aisha\garbage\music_player\music\e.mp3")
    # pygame.math.veccotyoue
    # channel = pygame.mixer.Channel(0)
    # play(channel, audio)
    # input()