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
    #Contructor function
    #Pre: assets_dir and data_dir must be valid directory to assets and music respectively
    #Post: None
    #Param: assets_dir: path to assets, data_dir: path to saved songs
    def __init__(self, assets_dir: str, data_dir: str) -> None:
        super().__init__()
        self.title("GrooveBox")
        self.geometry(f"600x700")
        self.resizable(False, False)

        self.data = Data(data_dir)
        self.player = Player(data_dir, self.data)

        self.data.add_new_playlist("random")
        self.data.add_song_playlist(random.choice(self.data.get_songs()), "random")
        self.player.set_playlist("random")
        self.player.play_song()

        s = ttk.Style()
        s.configure("first.TFrame", background = "#66669a")
        s.configure("music_player.TFrame", background = "#777B7E")
        s.configure("child_frames.TFrame", highlightbackground="blue", highlightthickness=1,width=600, height=100, bd= 0)
        s.configure("noFocus.TButton", relief="flat", background="SystemButtonFace", borderwidth=0)
        self.container = ttk.Frame(self, height=600, width=600, style="first.TFrame")
        self.container.pack_propagate(False)
        self.container.pack()

        self.player_frame = PlayerFrame(self, assets_dir, self.player)
        self.tab_menu = TabMenu(self.container, self.data, self.player)

class TabMenu(ttk.Notebook):
    #Contructor function
    #Pre: data and player must be an instance of data and player class respectively. Parent must be a tk.Tk
    #Post: None
    #Param: parent: master window, data: Data class, player: Player class
    def __init__(self, parent, data: Data, player: Player) -> None:
        ttk.Notebook.__init__(self, parent, height=600, width=600)
        self.data = data
        self.pack()
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

    #Function that runs when NotebookTabChanged occurs
    #Pre: None
    #Post: None
    #Param: _: event that tkinter provides as argument. Is not used.
    def tab_changed(self, _) -> None:
        if self.select() == ".!frame.!tabmenu.!downloadframe":
            self.download_frame.set_up()
        elif self.select() == ".!frame.!tabmenu.!playlistframe":
            self.playlist_frame.set_up()

class DownloadFrame(ttk.Frame):
    #Contructor function
    #Pre: data must be an instance of Data. Parent must be a ttk.Notebook
    #Post: None
    #Param: parent: ttk.Notebook, data: Data
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
    
    #Function that gets called when download is clicked
    #Pre: None
    #Post: None
    #Param: None
    def download_func(self) -> None:
        if self.data.check_song_exist(self.song_name_entry.get().strip()):
            self.state_label["text"] = "Cannot download. Song name already exists"
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
        self.data.add_song(self.song_name_entry.get().strip(), self.artist_name_entry.get().strip())
        for playlist in self.playlists_frame.get_selected():
            self.data.add_song_playlist(self.song_name_entry.get().strip(), playlist)

    #Actual function that downloads form yt
    #Pre: folder_path must be valid path to data dir, link must be working. filename must be unique
    #Post: returns true or false based on success or fail
    #Param: folder_path: str which will be path to folder, filename: str which will be the filename of mp3, link: str link of yt vid
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
    
    #Checks if link is valid
    #Pre: link which will be a url
    #Post: returns true or false based on if link is active
    #Param: link: str which is url of yt vid
    def check_link(self, link:str) -> bool:
        try:
            YouTube(link).check_availability()
        except:
            return False
        return True
    
    #Set up function that is used when tab of ttk.Notebook is changed
    #Pre: None
    #Post: None
    #Param: None
    def set_up(self) -> None:
        self.playlists_frame.set_up()

class ScollDownloadPlaylists(ttk.Frame):
    #Contructor function
    #Pre: data must be an instance of data class. Parent must be a ttk.Frame
    #Post: None
    #Param: parent: master frame, data: Data class
    def __init__(self, parent, data:Data) -> None:
        ttk.Frame.__init__(self, parent)
        self.pack(fill="both", expand=True)

        self.data = data
    
    #Cleans up the previous state of the frame so that it can be reused. Sets everything to none so values are garbage collected for set up for set_up
    #Pre: None
    #Post: None
    #Param: None
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

    #set_up which cleans and recontructs the whole frame
    #Pre: None
    #Post: None
    #Param: None    
    def set_up(self) -> None:
        self.clean_up()
        self.playlists = self.data.get_playlists()
        self.playlist_num = len(self.playlists)
        self.playlist_height = self.playlist_num * 15

        self.canvas = tk.Canvas(self, background="#aaa7cc", scrollregion=(0, 0, 600, self.playlist_height))
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
    
    #Gets all selected items of tk.Checkbutton
    #Pre:None
    #Post:None
    #Param:None
    def get_selected(self) -> list:
        checked = list()
        for index, checkboxes in enumerate(self.check_boxes):
            if self.check_boxes_state[index].get():
                checked.append(checkboxes.cget("text"))
        return checked

class PlaylistFrame(ttk.Frame):
    #Contructor function
    #Pre: data and player must be an instance of data and player class respectively. Parent must be a ttk.Notebook
    #Post: None
    #Param: parent: master frame, data: Data class, player: Player class
    def __init__(self, parent, data: Data, player: Player) -> None:
        self.data = data
        self.player = player
        ttk.Frame.__init__(self, parent)
        self.container_frame = ttk.Frame(self)
        self.container_frame.pack(expand=True, fill="both")
        self.scrolling_playlists = ScrollViewPlaylist(self.container_frame, self.data, parent, self.player)
        self.scrolling_playlists.set_up()
    
    #function called when notebook tab change event occurs
    #Pre: None
    #Post: None
    #Param: None
    def set_up(self) -> None:
        self.scrolling_playlists.set_up()
    
class PlayListViewWidget(ttk.Frame):
    #Contructor function
    #Pre: player must be an instance player class. Parent must be a tk.Frame playlist_name and playlist_songs must be valid. notebook must be ttk.Notebook
    #Post: None
    #Param: parent: master window, data: Data class, player: Player class, playlist_name: str of name of playlist, playlist_songs: list of songs, notebook: ttk.Notebook - TabMenu
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

    #Function that gets called when edit button is clicked
    #Pre: None
    #Post: None
    #Param: None
    def edit_button(self) -> None:
        self.notebook.edit_playlist_frame.set_up(self.playlist_name, self.playlist_songs)
        self.notebook.add(self.notebook.edit_playlist_frame)
        self.notebook.select(3)

    #Function that gets called when play button is clicked
    #Pre: None
    #Post: None
    #Param: None
    def play_button(self) -> None:
        self.player.set_playlist(self.playlist_name)

class ScrollViewPlaylist(ttk.Frame):
    #Contructor function
    #Pre: data and player must be an instance of data and player class respectively. Parent must be a ttk.Frame. notebook: TabMenu, height of each widget for playlist
    #Post: None
    #Param: parent: master frame, data: Data instance, player: player instance, notebook: ttk.Notebook/TabMenu, height: default 50, can be changed
    def __init__(self, parent, data: Data, notebook: TabMenu, player: Player, height = 50) -> None:
        self.notebook = notebook
        self.data = data
        self.player = player
        self.height = height

        ttk.Frame.__init__(self, parent)
        self.pack(fill="both", expand=True)

        self.canvas:tk.Canvas = None
        self.playlist_widgets:List[PlayListViewWidget] = list()
        self.view_frame = None

    #Function for clean up so that widgets gets garbage collected
    #Pre: None
    #Post:None
    #Param: None
    def clean_up(self) -> None:
        self.canvas.forget()
        self.canvas = None
        self.playlist_widgets = list()
        self.view_frame = None
    
    #Function for set up widgets
    #Pre: None
    #Post: None
    #Param: None
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
    #Contructor function
    #Pre: player must be an instance  player class. Parent must be a ttk.Notebook
    #Post: None
    #Param: parent: master frame, data: Data class
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

    #Function that gets called when confirm btn is pressed
    #Pre: None
    #Post: None
    #Param: None
    def confirm_btn(self) -> None:
        self.data.change_playlist(self.scroll_selection.get_selected(), self.playlist_name)
        self.notebook.select(0)
        self.notebook.hide(3)        

    #Function for setting up the frame
    #Pre: None
    #Post: None
    #Param: None
    def set_up(self, playlist_name, playlist_songs) -> None:
        self.playlist_name = playlist_name
        self.playlist_songs = playlist_songs
        self.name_label["text"] = self.playlist_name
        self.scroll_selection.set_up(self.data.get_songs(), playlist_songs, playlist_name)

class ScrollEditPlaylists(ttk.Frame):
    #Contructor function
    #Pre: Parent must be a ttk.Frame
    #Post: None
    #Param: parent: master frame
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

    #Function for clean up of widget for garbage collection
    #Pre: None
    #Post: None
    #Param: None
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

    #Funtion for setting up widgets
    #Pre: songs must be list of valid songs, playlist_songs must be list of valid songs
    #Post: None
    #Param: song: list of all songs, playlist_songs: list of songs in the playlist
    def set_up(self, songs:list, playlist_songs:list) -> None:
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

    #Function that gets all selectd items
    #Pre: None
    #Post: List of selected checkbuttons
    #Param: None
    def get_selected(self) -> list:
        checked = list()
        for index, checkbox in enumerate(self.checkboxes):
            if self.checkboxes_state[index].get():
                checked.append(checkbox.cget("text"))
        return checked

class AddPlaylistFrame(ttk.Frame):
    #Contructor function
    #Pre: data has to be an instance of data class
    #Post: None
    #Param: parent: ttk.Notebook, data: instance of data class
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

    #Function that gets called when submit is clicked
    #Pre: None
    #Param: None
    #Post: None
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
    
    #Function that gets called when new entry is clicked
    #Pre: None
    #Post: None
    #Param: None
    def clear_button(self) -> None:        
        self.notice_label.grid_remove()
        self.name_entry.delete(0, tk.END)
        
class PlayerFrame(ttk.Frame):
    #Contructor function
    #Pre: assets_dir must be valid path, parent must be initialized properly, player must also be intialized properly
    #Post: None
    #Param: parent: tk.Tk, assets_dir: str which is path to assets directory, player: instance of player class
    def __init__(self, parent, assets_dir:str, player:Player) -> None:
        self.player = player
        ttk.Frame.__init__(self, parent, height=100, width=600, style="music_player.TFrame")
        self.pack(fill = "both", expand=True)
        self.columnconfigure([x for x in range(20)], weight=1, uniform="a")
        self.rowconfigure([x for x in range(5)], weight=1, uniform="b")

        ttk.Scale(self, command=lambda value: self.player.set_vol(1 - float(value)), orient="vertical").grid(column=19, row=0, rowspan=4, sticky="ns")
        img = open_img(None, fr"{assets_dir}\sound_icon.png")
        sound_label = ttk.Label(self, image=img, anchor="center", background="#777B7E")
        sound_label.grid_propagate(False)
        sound_label.image = img
        sound_label.grid(column=19, row=4, sticky="nsew")

        self.song_info_frame = ttk.Frame(self, style="music_player.TFrame")
        self.song_info_frame.pack_propagate(False)
        self.song_info_frame.grid(column=0, row=3, columnspan=19, rowspan=2, sticky="nesw")
        self.song_title_label = ttk.Label(self.song_info_frame, text = self.change_label_text(""))
        self.song_title_label.pack()
        self.song_artist_label = ttk.Label(self.song_info_frame, text = "")
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

    #Function that gets called when next is clicked
    #Pre: None
    #Post: None
    #Param: None
    def next_song(self) -> None:
        self.player.next_song()
        self.play_state = True

    #Function that gets called when back is clicked
    #Pre: None
    #Post: None
    #Param: None
    def back_song(self) -> None:
        self.player.back_song()
        self.play_state = True

    #Function that gets called when pause is clicked
    #Pre: None
    #Post: None
    #Param: None
    def pause_song(self):
        if self.player.current_song == None:
            return
        self.play_state = not self.play_state
        if self.play_state:
            self.player.unpause_song()
        else:
            self.player.pause_song()
    
    #Function that gets called every 50ms to updt state of player
    #Pre: None
    #Post: None
    #Param: None
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

    #Returns proper length of string to prevent propogation of label
    #Pre: text must be str
    #Post: return string
    #Param: text: string to adjust
    def change_label_text(self, text: str) -> str:
        if len(text) <= 94:
            return text
        return text[:92] + "..."
    
    #Function that gets called in check_updt_song to updt the progress bar
    #Pre: None
    #Post: None
    #Param: None
    def updt_song_time(self):
        if self.player.current_song == None:
            self.song_progress["value"] = 0
            return
        self.player.current_song.updt_time()
        self.song_progress["value"] = self.player.current_song.time/self.player.current_song.length