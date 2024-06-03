class ScreenManager:
    def __init__(self, app):
        self.app = app
        self.screens = dict()
        self.current_screen = None

    def add(self, screen):
        self.screens[screen.name] = screen

    def set_screen(self, name):
        self.current_screen = self.screens[name]

    def update(self):
        if self.current_screen is not None:
            self.current_screen.update()

    def draw(self):
        if self.current_screen is not None:
            self.current_screen.draw()

    def handle_events(self, event):
        if self.current_screen is not None:
            self.current_screen.handle_events(event)