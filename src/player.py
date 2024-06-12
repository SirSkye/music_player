import pygame
import os
import time
import json
from typing import Dict, Tuple

#TODO: Finish the check broken function

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
    
    def add_song_playlist(self, song:str, playlist:str) -> None:
        self.playlists[playlist].append(song)

    def add_song(self, song:str, artist: str) -> None:
        self.artists[song] = artist

    def clear_playlist(self, playlist: str) -> None:
        self.playlists[playlist] = list()
    
    def change_playlist(self, playlist_songs: list, playlist:str) -> None:
        """Changes playlist to specified list of songs"""
        self.playlists[playlist] = playlist_songs
    
    def get_playlist_songs(self, playlist_name: str) -> list:
        """"Gets a list of songs in a playlist"""
        return self.playlists[playlist_name]
    
    def get_playlists(self) -> list:
        """Gets the names of all playlists, return as list"""
        return self.playlists.keys()
    
    def get_artist(self, song: str) -> str:
        return self.artists[song]
    
    def check_playlist_exist(self, playlist: str) -> bool:
        if playlist in self.playlists:
            return True
        return False
    
    def check_song_exist(self, song: str) -> bool:
        if song in self.artists:
            return True
        return False
    
    def add_new_playlist(self, playlist: str) -> None:
        self.playlists[playlist] = []

    def check_broken(self) -> bool:
        for file in os.listdir(self.directory):
            if file[-3:] == "mp3":
                if file[:-4] not in self.artists:
                    print("Broken Artist", file)
                    exit()
        for playlist in self.playlists.keys():
            pass

    def get_songs(self) -> list:
        """Gets all songs from the Artists dict, which are the valid songs, accessible by the music player"""
        return list(self.artists.keys())
    
    def save(self) -> bool:
        try:
            with open(fr"{self.directory}\data.json", "w") as f:
                data = {"Playlists" : self.playlists, "Artists":self.artists}
                json.dump(data, f)
        except:
            return False
        return True

data = Data(r"C:\Users\aisha\garbage\music_player-1\music")
data.check_broken()

class Player:
    def __init__(self, directory:str, data:Data, channel_id:int = 0) -> None:
        self.channel = pygame.mixer.Channel(channel_id)
        self.directory = directory
        self.data = data

        self.current_playlist:str = None
        self.current_song:Song = None
        self.index = None

        self.volume = 1

    def next_song(self) -> None:
        self.channel.stop()
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.index = (self.index+1)%len(self.data.get_playlist_songs(self.current_playlist))
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
        else:
            self.current_song = None
    
    def back_song(self) -> None:
        self.channel.stop()
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.index = (self.index-1)%len(self.data.get_playlist_songs(self.current_playlist))
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
        else:
            self.current_song = None

    def check_change(self) -> bool:
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
            return True
        else:
            return False

    def set_playlist(self, name: str) -> None:
        self.channel.stop()
        self.index = 0
        self.current_playlist = name
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(name)[self.index]}.mp3", self.data.get_playlist_songs(name)[self.index], self.data.get_artist(self.data.get_playlist_songs(name)[self.index]))
            self.play_song()
        else:
            self.current_song = None

    def get_playing(self) -> bool:
        return self.channel.get_busy()

    def play_song(self):
        if self.current_song != None:
            self.channel.play(self.current_song.sound)
            self.current_song.start()
    
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

    def unpause_song(self) -> None:
        self.current_song.start()
        self.channel.unpause()

    def pause_song(self) -> None:
        self.channel.pause()
        self.current_song.pause()
                
    
class Song:
    def __init__(self, path: str, name: str, artist: str) -> None:
        self.name = name
        self.artist = artist
        self.sound = pygame.mixer.Sound(path)
        self.length = self.sound.get_length()
        self.start_time = None
        self.time = 0
        self.pause_state = True
        print(self.length)
    
    def start(self):
        self.pause_state = False
        self.start_time = time.time()
    
    def pause(self):
        self.pause_state = True
        self.time += time.time() - self.start_time
    
    def updt_time(self) -> None:
        if not self.pause_state:
            self.time += time.time() - self.start_time
            self.start_time = time.time()