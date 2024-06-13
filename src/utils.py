import pygame
from pytube import YouTube
import moviepy.editor as mp
import os
from PIL import ImageTk, Image, ImageOps

def open_img(size: tuple, img_path: str):
    img = Image.open(img_path)
    if size is not None:
        # Get the dimensions of the image and the button
        img_width, img_height = img.size
        width, height = size
        
        # Calculate the aspect ratio of the image
        aspect_ratio = img_width / img_height
        
        # Calculate the new dimensions to fit within the button
        if width / height > aspect_ratio:
            new_width = int(height * aspect_ratio)
            new_height = height
        else:
            new_width = width
            new_height = int(width / aspect_ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)