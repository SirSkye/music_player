import pygame
from screen_manager import ScreenManager
from download_screen import DownloadScreen
from player_screen import PlayerScreen

class App:
    def __init__(self):
        pygame.init()

        self.width, self.height = self.size = (800, 600)

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("Music Player")

        self.screen_manager = ScreenManager(self)

        self.screen_manager.add(DownloadScreen("downloader", self))
        self.screen_manager.add(PlayerScreen("player", self))

        self.screen_manager.set_state("downloader")

        self.fps = 60

        self.clock = pygame.time.Clock()
        self.running = True

        self.delta_time = 0

    def run(self):
        while self.running:
            self.delta_time = self.clock.tick(self.fps) / 1000.0
            self.events()
            self.update()
            self.draw()

    def events(self):
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

            self.screen_manager.handle_events(event)

    def update(self):
        self.screen_manager.update()

    def draw(self):
        self.screen.fill("white")

        self.screen_manager.draw()
        pygame.display.flip()