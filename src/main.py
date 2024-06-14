#Music Player called groovebox for my final culminating
#Name: Aisha n
#Date 6/11/2024
#Ver 1.0
from app import App

if __name__ == "__main__":
    app = App(r"C:\Users\aisha\garbage\music_player-1\assets", r"C:\Users\aisha\garbage\music_player-1\music")
    app.mainloop()
    if not app.data.save():
        print("Something went wrong saving to file")