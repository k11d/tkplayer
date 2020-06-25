#!/usr/bin/env python3

import sys
import imageio
from tkinter import Tk, Label, Frame, Button
from PIL import ImageTk, Image
import screeninfo
import time
import numpy as np
import cv2


screen_h = screeninfo.get_monitors()[0].height
screen_w = screeninfo.get_monitors()[0].width
screen_dimension = [screen_h, screen_w]
source = sys.argv[1]


class PlayerConfigs:
    def __init__(self):
        self.paused = False
        self.flip_h = False
        self.flip_v = False
    def pause(self):
        self.paused = not self.paused
    def flip_horizontal(self):
        self.flip_h = not self.flip_h
    def flip_vertical(self):
        self.flip_v = not self.flip_v

## EFFECTS

def grayscale(img):
    ret = np.array(img, copy=True).astype(float)
    ret[:,:, 0] = (ret[:,:, 0] + ret[:,:, 1] + ret[:,:, 2]) / 3.0
    gret = ret[:,:, 0].astype(np.uint8)
    return gret

def flip_h(img):
    return img[:,::-1]

def flip_v(img):
    return img[::-1]

###

def start_stream():

    def _from_device(device):
        nonlocal delay
        cap = cv2.VideoCapture(int(device))
        delay = cap.get(cv2.CAP_PROP_FPS)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            else:
                yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _from_movie(vid):
        while True:
            try:
                image = vid.get_next_data()
            except:
                vid.close()
                return
            yield image

    def _as_photoimage(arrgen):
        for ar in arrgen:
            if pc.flip_v:
                ar = flip_v(ar)
            if pc.flip_h:
                ar = flip_h(ar)
            yield ImageTk.PhotoImage(Image.fromarray(ar))

    def loop(last_frame):
        nonlocal t0
        try:
            if not pc.paused:
                frame_image = next(frames)
            else:
                frame_image = last_frame
        except StopIteration:
            sys.exit(0)

        label.config(image=frame_image)
        label.image = frame_image
        t1 = time.time()
        dt = (t1 - t0) * 1000
        t0 = t1
        label.after(int(max(1.0, delay - dt)), lambda: loop(frame_image))

    if source.isdigit():
        delay = 1
        frames = _as_photoimage(_from_device(source))
    else:
        vid = imageio.get_reader(source)
        delay = int(1000 / vid.get_meta_data()['fps'])
        frames = _as_photoimage(_from_movie(vid))
    t0 = time.time()
    return loop(next(frames))


if __name__ == '__main__':
    root = Tk()
    pc = PlayerConfigs()
    root.geometry(f"{screen_w}x{screen_h}")

    label = Label(root)
    label.pack(side="bottom", expand=1)

    btns_frame = Frame(root)
    Button(btns_frame, text="Quit", command=lambda: sys.exit(0)).grid(row=0, column=0)
    Button(btns_frame, text="Pause", command=pc.pause).grid(row=0, column=1)
    Button(btns_frame, text="Flip H", command=pc.flip_horizontal).grid(row=0, column=2)
    Button(btns_frame, text="Flip V", command=pc.flip_vertical).grid(row=0, column=3)
    
    btns_frame.pack(side="top", expand=0)
    label.after(10, start_stream)
    root.mainloop()
