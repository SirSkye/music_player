import pygame
from screen_manager import ScreenManager

class App:
    def __init__(self):
        pygame.init()

        self.width, self.height = self.size = (800, 600)

        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption("My Game")

        self.game_state_manager = ScreenManager(self)

        self.game_state_manager.add(MenuState("menu", self))
        self.game_state_manager.add(PlayingState("game", self))

        self.game_state_manager.set_state("menu")

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

            self.game_state_manager.handle_events(event)

    def update(self):
        self.game_state_manager.update()
        pass

    def draw(self):
        self.screen.fill("white")

        self.game_state_manager.draw()
        pygame.display.flip()