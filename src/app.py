import tkinter as tk
from tkinter import ttk
from utils import open_img
from player import Player

class App(tk.Tk):
    def __init__(self, assets_dir: str):
        super().__init__()
        self.title("Music Player")
        self.geometry(f"600x700")
        self.resizable(False, False)

        self.player = Player(r"C:\Users\aisha\garbage\music_player-1\music")

        s = ttk.Style()
        s.configure("first.TFrame", background = "blue")
        s.configure("second.TFrame", background = "red")
        s.configure("noFocus.TButton", relief="flat", background="SystemButtonFace", borderwidth=0)
        self.container = ttk.Frame(self, height=600, width=600, style="first.TFrame")
        self.container.pack_propagate(False)
        self.container.pack()

        self.player = PlayerFrame(self, assets_dir, self.player)
        self.tab_menu = TabMenu(self.container, self.player)

class TabMenu(ttk.Notebook):
    def __init__(self, parent, player: Player) -> None:
        ttk.Notebook.__init__(self, parent, height=600, width=600)
        self.pack()
        self.download_frame = DownloadFrame(self)
        self.playlist_frame = PlaylistFrame(self, player)
        self.add(self.playlist_frame, text="Playlists")
        self.add(self.download_frame, text="Download")

class DownloadFrame(ttk.Frame):
    def __init__(self, parent) -> None:
        ttk.Frame.__init__(self, parent, style="first.TFrame")

class PlaylistFrame(ttk.Frame):
    def __init__(self, parent, player: Player) -> None:
        self.player = player
        ttk.Frame.__init__(self, parent, style="first.TFrame")
class PlayerFrame(ttk.Frame):
    def __init__(self, parent, assets_dir:str, player:Player):
        self.player = player
        ttk.Frame.__init__(self, parent, height=100, width=600, style="second.TFrame")
        self.pack(fill = "both", expand=True)
        self.columnconfigure([x for x in range(20)], weight=1, uniform="a")
        self.rowconfigure([x for x in range(5)], weight=1, uniform="b")

        ttk.Scale(self, command=lambda value: self.player.set_vol(1 - float(value)), orient="vertical").grid(column=19, row=0, rowspan=4, sticky="ns")
        img = open_img(None, fr"{assets_dir}\sound_icon.png")
        sound_label = ttk.Label(self, image=img, anchor="center", background="red")
        sound_label.grid_propagate(False)
        sound_label.image = img
        sound_label.grid(column=19, row=4, sticky="nsew")

        self.song_info_frame = ttk.Frame(self, style="first.TFrame")
        self.song_info_frame.pack_propagate(False)
        self.song_info_frame.grid(column=0, row=3, columnspan=19, rowspan=2, sticky="nesw")
        self.song_title_label = ttk.Label(self.song_info_frame, text = self.change_label_text("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeb"))
        self.song_title_label.pack()
        self.song_artist_label = ttk.Label(self.song_info_frame, text = "eeeeeeeee")
        self.song_artist_label.pack()

        self.song_progress = ttk.Progressbar(self, value=0, maximum = 1, phase=True)
        self.song_progress.grid(column=0, columnspan=19, row=2, sticky="ew")
        self.after(1, self.updt_song_time)
        self.play_button = ttk.Button(self, compound="top", style="noFocus.TButton")
        self.play_button.grid_propagate(False)
        self.play_button.grid(column=9, row=1, sticky="nesw")
        self.pause_img = open_img((30, 15), fr"{assets_dir}\pause_icon.png")
        self.play_img = open_img((30, 15), fr"{assets_dir}\play_icon.png")
        self.play_button["image"] = self.play_img 
        self.next_img = open_img((30, 15), fr"{assets_dir}\next_icon.png")
        self.back_img = open_img((30, 15), fr"{assets_dir}\back_icon.png")
        self.next_button = ttk.Button(self, compound="top", image = self.next_img, style="noFocus.TButton")
        self.next_button.grid(column=10, row =1, sticky="nesw")
        self.back_button = ttk.Button(self, compound="top", image = self.back_img)
        self.back_button.grid(column=8, row=1, sticky="nsew")

        self.after(50, self.check_updt_song)
    
    def check_updt_song(self):
        self.updt_song_time()
        self.song_title_label["text"] = self.change_label_text(self.player.current.name)
        self.song_artist_label["text"] = self.change_label_text(self.player.current.artist)
        self.after(50, self.check_updt_song)

    def change_label_text(self, text: str) -> str:
        if len(text) <= 94:
            return text
        return text[:92] + "..."
    
    def updt_song_time(self):
        self.player.current.updt_time()
        self.song_progress["value"] = self.player.current.time/self.player.current.length

    def load_song(self, text: str) -> str:
        self.song_title_label(self.change_label_text("Best Of You"))
        self.song_artist_label(self.change_label_text(self.player.get_artist("Best Of You")))
        self.player.load_song("Best of You")
        
app = App(r"C:\Users\aisha\garbage\music_player-1\assets")
app.mainloop()