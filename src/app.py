import tkinter as tk
from tkinter import ttk
from utils import open_img
from player import Player, Data
from typing import List
from pytube import YouTube
import os
import moviepy.editor as mp
import random
from ctypes import WinDLL

#If blurry uncomment, however, some text may get cutoff
# shcore = WinDLL('shcore')
# shcore.SetProcessDpiAwareness(1)

class App(tk.Tk):
    def __init__(self, assets_dir: str, data_dir: str):
        super().__init__()
        self.title("Music Player")
        self.geometry(f"600x700")
        self.resizable(False, False)

        self.data = Data(r"C:\Users\aisha\garbage\music_player-1\music")
        self.player = Player(r"C:\Users\aisha\garbage\music_player-1\music", self.data)

        self.data.add_new_playlist("random")
        print(type(self.data.get_playlist_songs("Something")))
        self.data.add_song_playlist(random.choice(self.data.get_songs()), "random")
        self.player.set_playlist("random")
        self.player.play_song()

        s = ttk.Style()
        s.configure("first.TFrame", background = "blue")
        s.configure("second.TFrame", background = "red")
        s.configure("child_frames.TFrame", highlightbackground="blue", highlightthickness=1,width=600, height=100, bd= 0)
        s.configure("noFocus.TButton", relief="flat", background="SystemButtonFace", borderwidth=0)
        self.container = ttk.Frame(self, height=600, width=600, style="first.TFrame")
        self.container.pack_propagate(False)
        self.container.pack()

        self.player_frame = PlayerFrame(self, assets_dir, self.player)
        self.tab_menu = TabMenu(self.container, self.data, self.player)

class TabMenu(ttk.Notebook):
    def __init__(self, parent, data: Data, player: Player) -> None:
        ttk.Notebook.__init__(self, parent, height=600, width=600)
        self.data = data
        self.pack()
        print(type(player))
        self.download_frame = DownloadFrame(self, data)
        self.playlist_frame = PlaylistFrame(self, data, player)
        self.add_playlist_frame = AddPlaylistFrame(self, data)
        self.edit_playlist_frame = EditPlaylistFrame(self, data)

        self.add(self.playlist_frame, text="Playlists")
        self.add(self.add_playlist_frame, text="Add Playlist")
        self.add(self.download_frame, text="Download")
        self.add(self.edit_playlist_frame, text="Edit Playlist")
        self.hide(3)

        self.bind("<<NotebookTabChanged>>", self.tab_changed)

    def tab_changed(self, _) -> None:
        if self.select() == ".!frame.!tabmenu.!downloadframe":
            self.download_frame.set_up()
        elif self.select() == ".!frame.!tabmenu.!playlistframe":
            self.playlist_frame.set_up()
        print(self.data.playlists)

class DownloadFrame(ttk.Frame):
    def __init__(self, parent, data: Data) -> None:
        self.data = data

        ttk.Frame.__init__(self, parent, style="first.TFrame")
        self.columnconfigure([x for x in range(7)], weight=1, uniform="a")
        self.rowconfigure([x for x in range(30)], weight=1, uniform="b")

        ttk.Label(self, text="Link: ").grid(column=0, row=0, sticky="nsew")
        self.link_entry = ttk.Entry(self)
        self.link_entry.grid(column=1, row=0, columnspan=6, sticky="nsew")

        ttk.Label(self, text="Song Name: ").grid(column=0, row=1, sticky="nesw")
        self.song_name_entry = ttk.Entry(self)
        self.song_name_entry.grid(column=1, row=1, columnspan=6, sticky="nsew")

        ttk.Label(self, text="Artist Name: ").grid(column=0, row=2, sticky="nesw")
        self.artist_name_entry = ttk.Entry(self)
        self.artist_name_entry.grid(column=1, row=2, columnspan=6, sticky="nsew")

        ttk.Label(self, text="Playlists to add to: ").grid(column=0, columnspan=7, row=4)
        self.playlists_frame_container = ttk.Frame(self, style="first.TFrame")
        self.playlists_frame_container.grid(column=0, row=5, rowspan=22, columnspan=7, sticky="nsew")
        self.playlists_frame = ScollDownloadPlaylists(self.playlists_frame_container, data)

        ttk.Button(self, text = "Download", command=self.download_func).grid(column=2, columnspan=3, row=27, sticky="nesw")

        self.state_label = ttk.Label(self)
        self.state_label.propagate(False)

    def download_func(self) -> None:
        if self.data.check_song_exist(self.song_name_entry.get().strip()):
            self.state_label["text"] = "Caanot download. Song name already exists"
            self.state_label.grid(row=28, column=0, columnspan=7, sticky="nesw")
            return
        elif self.link_entry.get().strip() == "" or self.song_name_entry.get().strip() == "" or self.artist_name_entry.get().strip() == "":
            self.state_label["text"] = "Cannot download. Empty fields"
            self.state_label.grid(row=28, column=0, columnspan=7, sticky="nesw")
            return
        elif not self.check_link(self.link_entry.get().strip()):
            self.state_label["text"] = "Cannot download. Error with link"
            self.state_label.grid(row=28, column=0, columnspan=7, sticky="nesw")
            return
        self.state_label["text"] = "Downloading..."
        self.state_label.grid(row=28, column=0, columnspan=7, sticky="nesw")
        if(self.download_video(self.data.directory, self.song_name_entry.get().strip(), self.link_entry.get().strip())):
            self.state_label["text"] = "Downloaded"
        else:
            self.state_label["text"] = "Error occured"
            return
        
        for playlist in self.playlists_frame.get_selected():
            self.data.add_song_playlist(self.song_name_entry.get().strip(), playlist)
        
    def download_video(self, folder_path: str, filename: str, link: str) -> bool:
        if os.path.exists(fr"{folder_path}\{filename}.mp4"):
            return False
        try:
            YouTube(link).streams.filter(only_audio=True).first().download(folder_path, f"{filename}.mp4")
            mp3_file = mp.AudioFileClip(fr"{folder_path}\{filename}.mp4")
            mp3_file.write_audiofile(fr"{folder_path}\{filename}.mp3", verbose=False, logger=None)
            os.remove(fr"{folder_path}\{filename}.mp4")
        except:
            return False
        return True
    
    def check_link(self, link) -> bool:
        try:
            YouTube(link).check_availability()
        except:
            return False
        return True

    def set_up(self) -> None:
        self.playlists_frame.set_up()

class ScollDownloadPlaylists(ttk.Frame):
    def __init__(self, parent, data:Data) -> None:
        ttk.Frame.__init__(self, parent)
        self.pack(fill="both", expand=True)

        self.data = data

    def clean_up(self) -> None:
        try:
            self.canvas.forget()
        except:
            pass
        self.playlists = None
        self.playlist_num = None
        self.playlist_height = None
        self.canvas = None
        self.check_boxes = list()
        self.view_frame = None
        self.check_boxes_state:List[tk.BooleanVar] = list()

    def set_up(self) -> None:
        self.clean_up()
        self.playlists = self.data.get_playlists()
        self.playlist_num = len(self.playlists)
        self.playlist_height = self.playlist_num * 15

        self.canvas = tk.Canvas(self, background="red", scrollregion=(0, 0, 600, self.playlist_height))
        self.canvas.pack(expand=True, fill="both")

        self.check_boxes = list()
        self.view_frame = ttk.Frame(self)
        self.view_frame.rowconfigure([x for x in range(self.playlist_num)],  weight=1)
        self.view_frame.columnconfigure(0, weight=1)
        for index, playlist in enumerate(self.playlists):
            self.check_boxes_state.append(tk.BooleanVar(value=False))
            temp = tk.Checkbutton(self.view_frame, text=playlist, anchor="w", variable=self.check_boxes_state[index])
            temp.grid(column=0, row=index, sticky="nesw")
            self.check_boxes.append(temp)

        self.canvas.create_window((0, 0), window = self.view_frame, anchor="nw", height=self.playlist_height)
        if self.winfo_height() < self.playlist_height:
            self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))
        
    def get_selected(self) -> list:
        checked = list()
        for index, checkboxes in enumerate(self.check_boxes):
            if self.check_boxes_state[index].get():
                checked.append(checkboxes.cget("text"))
        return checked

class PlaylistFrame(ttk.Frame):
    def __init__(self, parent, data: Data, player: Player) -> None:
        self.data = data
        self.player = player
        print(type(self.player))
        ttk.Frame.__init__(self, parent)
        self.container_frame = ttk.Frame(self)
        self.container_frame.pack(expand=True, fill="both")
        self.scrolling_playlists = ScrollViewPlaylist(self.container_frame, self.data, parent, self.player)
        self.scrolling_playlists.set_up()
    
    def set_up(self) -> None:
        self.scrolling_playlists.set_up()
    
class PlayListViewWidget(ttk.Frame):
    def __init__(self, parent:ttk.Frame, playlist_name: str, playlist_songs:list, notebook:TabMenu, player: Player) -> None:
        self.player = player
        self.playlist_name = playlist_name
        self.playlist_songs = playlist_songs

        self.notebook:TabMenu = notebook

        ttk.Frame.__init__(self, parent, height=50, width=600, style="child_frames.TFrame")
        self.propagate(False)
        self.columnconfigure((0, 1), weight=1, uniform="a")
        self.rowconfigure((0, 1), weight=1, uniform="b")

        label = ttk.Label(self, text=self.playlist_name, anchor="center")
        label.grid_propagate(False)
        label.grid(column=0, row=0, sticky="nesw")
        label = ttk.Label(self, text=fr"Song count: {len(self.playlist_songs)}")
        label.grid_propagate(False)
        label.grid(column=0, row=1)
        button = ttk.Button(self, text="Play", command=self.play_button)
        button.grid_propagate(False)
        button.grid(column=1, row=0, sticky="nesw")
        button = ttk.Button(self, text="Edit", command=self.edit_button)
        button.grid_propagate(False)
        button.grid(column=1, row=1, sticky="nesw")

    def edit_button(self) -> None:
        self.notebook.edit_playlist_frame.set_up(self.playlist_name, self.playlist_songs)
        self.notebook.add(self.notebook.edit_playlist_frame)
        self.notebook.select(3)

    def play_button(self) -> None:
        self.player.set_playlist(self.playlist_name)

class ScrollViewPlaylist(ttk.Frame):
    def __init__(self, parent, data: Data, notebook, player: Player, height = 50) -> None:
        self.notebook = notebook
        self.data = data
        self.player = player
        self.height = height

        ttk.Frame.__init__(self, parent)
        self.pack(fill="both", expand=True)

        self.canvas:tk.Canvas = None
        self.playlist_widgets:List[PlayListViewWidget] = list()
        self.view_frame = None

    def clean_up(self) -> None:
        self.canvas.forget()
        self.canvas = None
        self.playlist_widgets = list()
        self.view_frame = None
    
    def set_up(self) -> None:
        try:
            self.clean_up()
        except:
            pass
        self.playlist_num = len(self.data.get_playlists())
        self.playlist_height = self.height * (self.playlist_num)

        self.canvas = tk.Canvas(self, background="green", scrollregion=(0, 0, 600, self.playlist_height))
        self.canvas.pack(expand=True, fill="both")

        self.view_frame = ttk.Frame(self, style="first.TFrame", width=600)
        self.view_frame.pack_propagate(False)

        self.playlist_widgets = list()
        for index, playlist in enumerate(self.data.get_playlists()):
            self.playlist_widgets.append(PlayListViewWidget(self.view_frame, playlist, self.data.get_playlist_songs(playlist), self.notebook, self.player))
            self.playlist_widgets[index].pack(fill="both", expand=True)

        self.canvas.create_window((0, 0), window = self.view_frame, anchor="nw", height=self.playlist_height)

        if self.winfo_height() < self.playlist_height:
            self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))

class EditPlaylistFrame(ttk.Frame):
    def __init__(self, parent, data:Data) -> None:
        self.notebook:TabMenu = parent
        self.data = data
        ttk.Frame.__init__(self, parent, style="first.TFrame")
        self.columnconfigure([x for x in range(7)], weight=1, uniform="a")
        self.rowconfigure([x for x in range(30)], weight=1, uniform="b")

        self.playlist_name = None
        self.playlist_songs = None

        self.name_label = ttk.Label(self, text="")
        self.name_label.grid_propagate(False)
        self.name_label.grid(column=2, row=0, columnspan=3)

        self.confirm_button = ttk.Button(self, text="Confirm", command=self.confirm_btn)
        self.confirm_button.grid(column=2, row=28, columnspan=3, sticky="nesw")

        self.container = ttk.Frame(self)
        self.container.grid(column=0, row=1, rowspan=27, columnspan=7, sticky="nesw")
        self.scroll_selection = ScrollEditPlaylists(self.container)

    def confirm_btn(self) -> None:
        self.data.change_playlist(self.scroll_selection.get_selected(), self.playlist_name)
        print(self.data.playlists)
        self.notebook.select(0)
        self.notebook.hide(3)        

    def set_up(self, playlist_name, playlist_songs) -> None:
        self.playlist_name = playlist_name
        self.playlist_songs = playlist_songs
        self.name_label["text"] = self.playlist_name
        self.scroll_selection.set_up(self.data.get_songs(), playlist_songs, playlist_name)

class ScrollEditPlaylists(ttk.Frame):
    def __init__(self, parent) -> None:
        ttk.Frame.__init__(self, parent)
        self.pack(fill="both", expand=True)

        self.song_num = None
        self.song_height = None
        self.songs = None
        self.canvas: tk.Canvas = None
        self.checkboxes: List[tk.Checkbutton] = list()
        self.checkboxes_state: List[tk.BooleanVar] = list()
        self.view_frame: ttk.Frame = None

    def clean_up(self) -> None:
        try:
            self.canvas.forget()
        except:
            pass
        self.checkboxes_state = list()
        self.song_num = None
        self.song_height = None
        self.songs = None
        self.canvas: tk.Canvas = None
        self.checkboxes: List[tk.Checkbutton] = list()
        self.view_frame: ttk.Frame = None

    def set_up(self, songs, playlist_songs:list, playlist_name: str) -> None:
        self.clean_up()
        self.songs = songs
        self.song_num = len(songs)
        self.song_height = 15 * self.song_num

        self.canvas = tk.Canvas(self, background="red", scrollregion=(0, 0, 600, self.song_height))
        self.canvas.pack(fill="both", expand=True)
        self.view_frame = ttk.Frame(self, style="second.TFrame")
        self.view_frame.columnconfigure(0, weight=1)
        self.view_frame.rowconfigure([x for x in range(self.song_num)], weight=1)

        for index, song in enumerate(songs):
            self.checkboxes_state.append(tk.BooleanVar(value=False))
            self.checkboxes.append(tk.Checkbutton(self.view_frame, text=song, anchor="w", variable=self.checkboxes_state[index]))
            if song in playlist_songs:
                self.checkboxes_state[index].set(True)
            self.checkboxes[index].grid(column=0, row=index, sticky="nesw")

        self.canvas.create_window((0, 0), window = self.view_frame, anchor="nw", height=self.song_height)

        if self.winfo_height() < self.song_height:
            self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(event.delta/60),"units"))

    def get_selected(self) -> list:
        checked = list()
        for index, checkbox in enumerate(self.checkboxes):
            if self.checkboxes_state[index].get():
                checked.append(checkbox.cget("text"))
        return checked

class AddPlaylistFrame(ttk.Frame):
    def __init__(self, parent, data: Data) -> None:
        self.data = data
        ttk.Frame.__init__(self, parent, style="first.TFrame")
        self.columnconfigure([x for x in range(7)], weight=1, uniform="a")
        self.rowconfigure([x for x in range(30)], weight=1, uniform="b")

        ttk.Label(self, text="Name: ").grid(column=0, row=0, sticky="nsew")
        self.name_entry = ttk.Entry(self)
        self.name_entry.grid(column=1, row=0, columnspan=6, sticky="nsew")

        ttk.Button(self, text = "Submit", command=self.submit_button).grid(column=0, columnspan=7, row=15)
        ttk.Button(self, text="New Entry", command=self.clear_button).grid(column=0, columnspan=7, row=16)

        self.notice_label = ttk.Label(self, text="")
        self.notice_label.grid(column=0, columnspan=7, row=17)
        self.notice_label.grid_remove()

    def submit_button(self) -> None:
        name = self.name_entry.get()
        if self.data.check_playlist_exist(name):
            self.notice_label["text"] = "Unable to add. Already exists"
        elif not name.isalnum():
            self.notice_label["text"] = "Unable to add. Name is blank"
        else:
            self.data.add_new_playlist(name)
            self.notice_label["text"] = "Added Playlist"
        self.notice_label.grid()
        
    def clear_button(self) -> None:        
        self.notice_label.grid_remove()
        self.name_entry.delete(0, tk.END)
        
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

        self.playlist_name_label = ttk.Label(self, text="")
        self.playlist_name_label.grid_propagate(False)
        self.playlist_name_label.grid(column=0, row=0, columnspan=19, sticky="ns")

        self.song_progress = ttk.Progressbar(self, value=0, maximum = 1, phase=True)
        self.song_progress.grid(column=0, columnspan=19, row=2, sticky="ew")
        self.after(1, self.updt_song_time)
        self.play_button = ttk.Button(self, compound="top", style="noFocus.TButton", command=self.pause_song)
        self.play_button.grid_propagate(False)
        self.play_button.grid(column=9, row=1, sticky="nesw")
        self.pause_img = open_img((30, 15), fr"{assets_dir}\pause_icon.png")
        self.play_img = open_img((30, 15), fr"{assets_dir}\play_icon.png")
        self.play_button["image"] = self.pause_img
        self.next_img = open_img((30, 15), fr"{assets_dir}\next_icon.png")
        self.back_img = open_img((30, 15), fr"{assets_dir}\back_icon.png")
        self.next_button = ttk.Button(self, compound="top", image = self.next_img, style="noFocus.TButton", command=self.next_song)
        self.next_button.grid(column=10, row =1, sticky="nesw")
        self.back_button = ttk.Button(self, compound="top", image = self.back_img, command=self.back_song)
        self.back_button.grid(column=8, row=1, sticky="nsew")

        self.play_state = True

        self.after(50, self.check_updt_song)

    def next_song(self) -> None:
        self.player.next_song()
        self.play_state = True

    def back_song(self) -> None:
        self.player.back_song()
        self.play_state = True

    def pause_song(self):
        if self.player.current_song == None:
            return
        self.play_state = not self.play_state
        if self.play_state:
            self.player.unpause_song()
        else:
            self.player.pause_song()
    
    def check_updt_song(self):
        self.updt_song_time()
        if self.player.current_song == None:
            if self.player.check_change():
                self.play_state = True
            else:
                self.playlist_name_label["text"] = self.change_label_text(self.player.current_playlist)
                self.song_title_label["text"] = self.change_label_text("None")
                self.song_artist_label["text"] = self.change_label_text("None")
            self.after(50, self.check_updt_song)
            return
        if self.player.current_song.time > self.player.current_song.length:
            self.play_state = True
            self.player.next_song()
        if not self.player.current_song.pause_state:
            self.play_state = True
        self.play_button["image"] = self.pause_img if self.play_state else self.play_img
        self.playlist_name_label["text"] = self.change_label_text(self.player.current_playlist)
        self.song_title_label["text"] = self.change_label_text(self.player.current_song.name)
        self.song_artist_label["text"] = self.change_label_text(self.player.current_song.artist)
        self.after(50, self.check_updt_song)

    def change_label_text(self, text: str) -> str:
        if len(text) <= 94:
            return text
        return text[:92] + "..."
    
    def updt_song_time(self):
        if self.player.current_song == None:
            self.song_progress["value"] = 0
            return
        self.player.current_song.updt_time()
        self.song_progress["value"] = self.player.current_song.time/self.player.current_song.length

if __name__ == "__main__":        
    app = App(r"C:\Users\aisha\garbage\music_player-1\assets", "E")
    app.mainloop()
    if not app.data.save():
        print("Something went wrong saving to file")