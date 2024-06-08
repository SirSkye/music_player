import pygame
from queue import Queue
import os
import time

class Player:
    def __init__(self, directory:str, channel_id:int = 0) -> None:
        self.channel = pygame.mixer.Channel(channel_id)
        self.directory = directory

        self.loaded = list()
        self.current: Song|None = None
        self.volume = 1
        
    def load(self, song: str) -> bool:
        if not os.path.exists(fr"{self.directory}\{song}.mp3"):
           return False
        
        
        return True
    
class Song:
    def __init__(self, path: str) -> None:
        self.sound = pygame.mixer.Sound(path)
        self.time = None
    
    def start(self):
        