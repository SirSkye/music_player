class ScreenManager:
    def __init__(self, app):
        self.app = app
        self.states = {}
        self.state = None

    def add(self, state):
        self.states[state.name] = state

    def set_state(self, name):
        self.state = self.states[name]

    def update(self):
        if self.state is not None:
            self.state.update()

    def draw(self):
        if self.state is not None:
            self.state.draw()

    def handle_events(self, event):
        if self.state is not None:
            self.state.handle_events(event)