import pygame
import os
import time
import json
from typing import Dict, Tuple

class Data:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.playlists, self.artists = self.load_data()

    def load_data(self) -> Tuple[dict, dict]:
        data = dict()
        try:
            with open(rf"{self.directory}\data.json", "r") as f:
                data = json.load(f)
        except:
            print(rf"ERROR: COULD NOT READ {self.directory}\data.json")
            exit()
        return data["Playlists"], data["Artists"]
    
    def get_playlists(self) -> list:
        return self.playlists.keys()
    
    def get_artist(self, song: str) -> str:
        return self.artists[song]
    
    def check_playlist_exist(self, playlist: str) -> bool:
        if playlist in self.playlists:
            return True
        return False
    
    def add_new_playlist(self, playlist: str) -> None:
        self.playlists[playlist] = []

class Player:
    def __init__(self, directory:str, channel_id:int = 0) -> None:
        self.channel = pygame.mixer.Channel(channel_id)
        self.directory = directory

        self.data = self.load_data()

        self.loaded = list()
        self.load_song("Best of You")
        self.current: Song|None = self.loaded[0]
        self.play_song()
        self.volume = 1


    def play_song(self):
        self.channel.play(self.current.sound)
        self.current.start()
    
    def get_artist(self, key:str):
        return self.data["Artists"][key]
    
    def set_vol(self, new_vol: float) -> None:
        self.volume = new_vol
        self.channel.set_volume(self.volume)
        print(self.volume)
        
    def load_song(self, song: str) -> bool:
        if not os.path.exists(fr"{self.directory}\{song}.mp3"):
           return False
        self.loaded.append(Song(fr"{self.directory}\{song}.mp3", song, self.get_artist(song)))
        return True
    
    def load_data(self) -> dict:
        data = dict()
        try:
            with open(rf"{self.directory}\data.json", "r") as f:
                data = json.load(f)
        except:
            print(rf"ERROR: COULD NOT READ {self.directory}\data.json")
            exit()
        return data
                
    
class Song:
    def __init__(self, path: str, name: str, artist: str) -> None:
        self.name = name
        self.artist = artist
        self.sound = pygame.mixer.Sound(path)
        self.length = self.sound.get_length()
        self.start_time = None
        self.time = 0
        print(self.length)
    
    def start(self):
        self.start_time = time.time()
    
    def pause(self):
        self.time += time.time() - self.start_time
    
    def updt_time(self) -> None:
        self.time += time.time() - self.start_time
        self.start_time = time.time()

{
    "Playlists" : {

    },
    "Artists" : {
        "Best of You" : "Andy Grammer"
    }
}