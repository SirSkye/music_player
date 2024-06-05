import pygame
from pytube import YouTube
import moviepy.editor as mp
import os


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
    
if __name__ == "__main__":
    pygame.init()
    #download_video(r"C:\Users\aisha\garbage\music_player\songs", "e", "https://www.youtube.com/watch?v=OKoSjxy0G2I")
    audio = pygame.mixer.Sound(r"C:\Users\aisha\garbage\music_player\songs\e.mp3")
    channel = pygame.mixer.Channel(0)
    play(channel, audio)
    input()