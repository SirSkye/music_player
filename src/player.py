import pygame
import os
import time
import json
from typing import Dict, Tuple

class Data:
    #Contructor function
    #Pre: directory must be proper path to data dir
    #Post: None
    #Param: directory: str which is path to data dir
    def __init__(self, directory: str) -> None:
        self.directory = directory
        self.playlists, self.artists = self.load_data()

    #Loads data
    #Pre: None
    #Post: Returns tuple of dict of playlists and artists/songs
    def load_data(self) -> Tuple[dict, dict]:
        data = dict()
        try:
            with open(rf"{self.directory}\data.json", "r") as f:
                data = json.load(f)
        except:
            print(rf"ERROR: COULD NOT READ {self.directory}\data.json")
            exit()
        return data["Playlists"], data["Artists"]
    
    #Adds a song to self.playlists
    #Pre: song must be proper song, playlist must be proper playlists
    #Post: None
    #Param: song: str of song title, playlists: str of playlisy name
    def add_song_playlist(self, song:str, playlist:str) -> None:
        self.playlists[playlist].append(song)

    #Song for adding new song to the self.artists dict
    #Pre: song must be proper song
    #Post: None
    #Param: None
    def add_song(self, song:str, artist: str) -> None:
        self.artists[song] = artist

    #Song for clearing whole playlist
    #Pre: plalist must be proper playlist
    #Post: None
    #Param: playlist: str which is plylist to empty
    def clear_playlist(self, playlist: str) -> None:
        self.playlists[playlist] = list()
    
    #Changes playlist to specified list of songs
    #Pre: playlist_songs: must be proper list, playlist: must be proper playlist name
    #Post: None
    #Param:  playlist_songs: list of songs to add, playlist: str which is name of playlist
    def change_playlist(self, playlist_songs: list, playlist:str) -> None:
        self.playlists[playlist] = playlist_songs
    
    #Gets a list of songs in a playlist
    #Pre: playlist_name must be proper name
    #Post: List of songs in playlist
    #Param: playlist_name: str of playlist name to search in
    def get_playlist_songs(self, playlist_name: str) -> list:
        return self.playlists[playlist_name]
    
    #Gets the names of all playlists, return as list
    #Pre: None
    #Post: list of playlists
    #Param: None
    def get_playlists(self) -> list:
        return self.playlists.keys()
    
    #Gets the corresponding artist name to song
    #Pre: song must be valid song
    #Post: Str which is artist name
    #Param: song: str which will be song to search for
    def get_artist(self, song: str) -> str:
        return self.artists[song]
    
    #Gets if playlist exists
    #Pre: None
    #Post: returns true if exist, false if not exist
    #Param: playlist: str which is name of playlist to search for 
    def check_playlist_exist(self, playlist: str) -> bool:
        if playlist in self.playlists:
            return True
        return False
    
    #Gets if song exists
    #Pre: None
    #Post: returns true if exist, false if not exist
    #Param: song: str which is name of song  to search for 
    def check_song_exist(self, song: str) -> bool:
        if song in self.artists:
            return True
        return False
    
    #Adds new empty playlist
    #Pre: playlis must not exist
    #Post: None
    #Param: playlist: str which is playlist name to add
    def add_new_playlist(self, playlist: str) -> None:
        self.playlists[playlist] = list()

    #Checks validity of the stored data
    #Pre: None
    #Post: None
    #Param: None
    def check_broken(self) -> None:
        for file in os.listdir(self.directory):
            if file[-3:] == "mp3":
                if file[:-4] not in self.artists:
                    print("Broken Artist", file)
                    exit()
        for playlist in self.playlists.keys():
            for song in self.get_playlist_songs(playlist):
                if not os.path.exists(fr"{self.directory}\{song}.mp3"):
                    print(f"Invalid song name {song} in {playlist}")
                    exit()
        for song in self.artists.keys():
            if not os.path.exists(fr"{self.directory}\{song}.mp3"):
                    print(f"Invalid song name {song}")
                    exit()

    #Gets all songs from the Artists dict, which are the valid songs, accessible by the music player
    #Pre: None
    #Post: None
    #Param: None
    def get_songs(self) -> list:
        return list(self.artists.keys())
    
    #Saves to json file
    #Pre: None
    #Post: returns true if no issues, false if issues
    #Param: None
    def save(self) -> bool:
        try:
            with open(fr"{self.directory}\data.json", "w") as f:
                data = {"Playlists" : self.playlists, "Artists":self.artists}
                json.dump(data, f)
        except:
            return False
        return True

class Player:
    #Contructor function
    #Pre: directory must be valid directory path, channel_id must be avaiable channel number, data must be instance of data class
    #Post: None
    #Param: directory: str which is path to data dir, data: instance of data class, channel_id: int audio channel to use
    def __init__(self, directory:str, data:Data, channel_id:int = 0) -> None:
        self.channel = pygame.mixer.Channel(channel_id)
        self.directory = directory
        self.data = data

        self.current_playlist:str = None
        self.current_song:Song = None
        self.index = None

        self.volume = 1

    #Goes to next song
    #Pre: None
    #Post: None, self.index is changed as well as current_song
    #Param: None
    def next_song(self) -> None:
        self.channel.stop()
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.index = (self.index+1)%len(self.data.get_playlist_songs(self.current_playlist))
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
        else:
            self.current_song = None
    
    #Goes to previous song
    #Pre: None
    #Post: None, self.index is changed as well as current_song
    #Param: None
    def back_song(self) -> None:
        self.channel.stop()
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.index = (self.index-1)%len(self.data.get_playlist_songs(self.current_playlist))
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
        else:
            self.current_song = None

    #Checks if change has occured, if so updt the channel to reflect change
    #Pre: None
    #Post: song changed, if changes occur. Returns true if change
    #Param: None
    def check_change(self) -> bool:
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(self.current_playlist)[self.index]}.mp3", self.data.get_playlist_songs(self.current_playlist)[self.index], self.data.get_artist(self.data.get_playlist_songs(self.current_playlist)[self.index]))
            self.play_song()
            return True
        else:
            return False
        
    #Sets playing playlist
    #Pre: name must be valid playlist name
    #Post: None, just changes self.current_song, self.index
    #Param: name: str which is playlist name to change to
    def set_playlist(self, name: str) -> None:
        self.channel.stop()
        self.index = 0
        self.current_playlist = name
        if len(self.data.get_playlist_songs(self.current_playlist)) != 0:
            self.current_song = Song(fr"{self.directory}\{self.data.get_playlist_songs(name)[self.index]}.mp3", self.data.get_playlist_songs(name)[self.index], self.data.get_artist(self.data.get_playlist_songs(name)[self.index]))
            self.play_song()
        else:
            self.current_song = None

    #Gets if songs are playing
    #Pre: None
    #Post: true for playing, false for not
    #Param :None
    def get_playing(self) -> bool:
        return self.channel.get_busy()

    #Play the song
    #Pre: None
    #Post: None
    #Param: None
    def play_song(self) -> None:
        if self.current_song != None:
            self.channel.play(self.current_song.sound)
            self.current_song.start()
    
    #Gets the artist
    #Pre: key must be valid key
    #Post: returns str which is artist name
    #Param: key: str which is song to search
    def get_artist(self, key:str) -> str:
        return self.data["Artists"][key]
    
    #Sets volume of channel
    #Pre: new_vol must be valid vol between 0, 1
    #Post: None
    #Param: new_vol: float which will the new volume
    def set_vol(self, new_vol: float) -> None:
        self.volume = new_vol
        self.channel.set_volume(self.volume)
    
    #Loads the song
    #Pre: song must be valid
    #Post: false for no success, vice versa
    #Param: song: str which is song to load
    def load_song(self, song: str) -> bool:
        if not os.path.exists(fr"{self.directory}\{song}.mp3"):
           return False
        self.loaded.append(Song(fr"{self.directory}\{song}.mp3", song, self.get_artist(song)))
        return True
    
    #Unpauses song
    #pre: Must be paused before
    #Post: None
    #Param: None
    def unpause_song(self) -> None:
        self.current_song.start()
        self.channel.unpause()

    #Puases song
    #Pre: must be playing something
    #Post: None
    #Param: None
    def pause_song(self) -> None:
        self.channel.pause()
        self.current_song.pause()
                
    
class Song:
    #Contructor function
    #Pre: path which must be valid
    #Post: None
    #Param: path: str which is song path, name: str for song name, artist: str for artist name 
    def __init__(self, path: str, name: str, artist: str) -> None:
        self.name = name
        self.artist = artist
        self.sound = pygame.mixer.Sound(path)
        self.length = self.sound.get_length()
        self.start_time = None
        self.time = 0
        self.pause_state = True

    #Starts the time count
    #Pre: None
    #Post: None
    #PAram: None
    def start(self):
        self.pause_state = False
        self.start_time = time.time()
    
    #Pauses time count
    #Pre: None
    #Post: None
    #Param: None
    def pause(self):
        self.pause_state = True
        self.time += time.time() - self.start_time
    
    #updates the self.time var 
    #Pre: None
    #Post: self.time updated, self.start_time updated
    #PAram: None
    def updt_time(self) -> None:
        if not self.pause_state:
            self.time += time.time() - self.start_time
            self.start_time = time.time()