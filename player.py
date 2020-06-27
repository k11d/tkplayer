#!/usr/bin/env python3

import sys
from tkinter import Tk, Label, Frame, Button
# from tkinter.ttk import Label, Button  
from PIL import ImageTk, Image
import screeninfo
import time
import numpy as np
import cv2
import itertools as it


screen_h = screeninfo.get_monitors()[0].height
screen_w = screeninfo.get_monitors()[0].width
screen_dimension = [screen_h, screen_w]

class PlayerStates:
    def __init__(self):
        self.pos = 0
        self.count = 0
        self.paused = False
        self.flip_h = False
        self.flip_v = False
        self.rot90_steps = 0
        self.scale = 1.0
        self.scale_step = 0.1
        self.x_offset = 0
        self.y_offset = 0
        self.translate_step = 5
        self.grayscale = False
        self._next = True

        self.cached_frames = []
        self.frames_a = -1
        self.frames_b = -1
        self.loop_replay = False

    def pause(self):
        self.paused = not self.paused
        self._next = not self.paused
        
    def flip_horizontal(self):
        self.flip_h = not self.flip_h
        self._next = True

    def flip_vertical(self):
        self.flip_v = not self.flip_v
        self._next = True
    
    def rotate(self):
        self.rot90_steps = self.rot90_steps + 1
    
    def scale_up(self):
        self.scale += self.scale_step
    
    def scale_reset(self):
        self.scale = 1.0

    def scale_down(self):
        if self.scale > self.scale_step:
            self.scale -= self.scale_step
    
    def translate_reset(self):
        self.x_offset = 0
        self.y_offset = 0
    
    def translate_down(self):
        self.y_offset -= self.translate_step
    
    def translate_up(self):
        self.y_offset += self.translate_step
    
    def translate_left(self):
        self.x_offset -= self.translate_step
    
    def translate_right(self):
        self.x_offset += self.translate_step
    
    def grayscale_toggle(self):
        self.grayscale = not self.grayscale
        self._next = True
    
    def Next(self):
        self._next = True
        self.paused = True
    
    def set_sequence_start(self):
        self.reset_sequence()
        self.frames_a = self.pos

    def set_sequence_end(self):
        self.frames_b = self.pos
        self.loop_replay = True
    
    def reset_sequence(self):
        self.cached_frames.clear()
        self.frames_b = -1
        self.frames_a = -1
        self.loop_replay = False

class Player:
    def __init__(self, source):
        self.source = source
        self.root = Tk()
        self.root.geometry(f"{screen_w}x{screen_h}")
        self.pc = PlayerStates()
        self._ui = ui(self.root, self.pc)
        self.label = self._ui['label']
        
        self.cap = self._open_stream(self.source)
        self.frames = it.cycle(self._play_stream(self.cap))
        self.t0 = time.time()
        
        self.label.after(10, self._start_stream)
        self.root.mainloop()

    def _open_stream(self, source):
        if str(source).isdigit():
            cap = cv2.VideoCapture(int(source))
        else:
            cap = cv2.VideoCapture(source)
        self.pc.delay = cap.get(cv2.CAP_PROP_FPS)
        self.pc.count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return cap
    
    def _play_stream(self, cap):
        while True:
            ret, frame = cap.read()
            if not ret:
                self.pc.pos = 0
                cap.release()
                break
            else:
                yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _start_stream(self):

        def _as_photoimage(ar):
            if self.pc.scale != 1.0:
                ar = scale(ar, self.pc.scale, self.pc.x_offset, self.pc.y_offset)
            if self.pc.flip_v:
                ar = flip_v(ar)
            if self.pc.flip_h:
                ar = flip_h(ar)
            if self.pc.rot90_steps:
                ar = rotate(ar, self.pc.rot90_steps)
            if self.pc.grayscale:
                ar = grayscale(ar)
            return ImageTk.PhotoImage(Image.fromarray(ar))

        def loop(last_frame):
            try:
                if self.pc._next:
                    if self.pc.paused:
                        self.pc._next = False
                    frame_image = _as_photoimage(next(self.frames))
                    self.pc.pos = (self.pc.pos + 1) % self.pc.count
                else:
                    frame_image = last_frame
            except StopIteration:
                sys.exit(0)

            try:
                self.label.config(image=frame_image)
            except:
                self.label.config(image=last_frame)
                frame_image = last_frame

            self.label.image = frame_image
            t1 = time.time()
            dt = (t1 - self.t0) * 1000
            self.t0 = t1
            self.root.title(f"{self.pc.pos}/{self.pc.count}")
            self.label.after(int(max(1.0, self.pc.delay - dt)), lambda: loop(frame_image))

        loop(_as_photoimage(next(self.frames)))



def ui(root, pc):
    _ui = {}
    btns_frame = Frame(root)
    btns_frame.pack(side="left", expand=0)
    label = Label(root)
    label.pack(side="right", expand=1)
    _ui['label'] = label

    Button(btns_frame, text="Quit", command=lambda: sys.exit(0)).grid(row=0, column=0)
    Button(btns_frame, text="Pause", command=pc.pause).grid(row=1, column=0)

    Button(btns_frame, text="Frame+", command=pc.Next).grid(row=2, column=0)

    flip_pair_btn = Frame(btns_frame)
    flip_pair_btn.grid(row=3, column=0)
    Button(flip_pair_btn, text="F-H", command=pc.flip_horizontal).pack(side="left")
    Button(flip_pair_btn, text="F-V", command=pc.flip_vertical).pack(side="right")


    scale_btns = Frame(btns_frame)
    scale_btns.grid(row=4, column=0)
    Button(scale_btns, text="+", command=pc.scale_up).pack(side="left")
    Button(scale_btns, text="0", command=pc.scale_reset).pack(side="left")
    Button(scale_btns, text="-", command=pc.scale_down).pack(side="right")

    offset_btns = Frame(btns_frame)
    offset_btns.grid(row=5, column=0)
    Button(offset_btns, text="L", command=pc.translate_left).pack(side="left")
    Button(offset_btns, text="R", command=pc.translate_right).pack(side="right")
    Button(offset_btns, text="U", command=pc.translate_up).pack(side="top")
    Button(offset_btns, text="D", command=pc.translate_down).pack(side="bottom")
    Button(offset_btns, text="0", command=pc.translate_reset).pack()


    seq_btns = Frame(btns_frame)
    seq_btns.grid(row=6, column=0)
    Button(seq_btns, text="A", command=pc.set_sequence_start).pack(side="left")
    Button(seq_btns, text="Reset", command=pc.reset_sequence).pack(side="left")
    Button(seq_btns, text="B", command=pc.set_sequence_end).pack(side="right")

    Button(btns_frame, text="Rotate", command=pc.rotate).grid(row=7, column=0)
    Button(btns_frame, text="Gray", command=pc.grayscale_toggle).grid(row=8, column=0)
    return _ui


## EFFECTS

def grayscale(img):
    try:
        return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    except:
        ret = np.array(img, copy=True).astype(float)
        ret[:,:, 0] = ret[:,:, 1] = ret[:,:, 2] = (ret[:,:, 0] + ret[:,:, 1] + ret[:,:, 2]) / 3.0
        gret = ret[:,:, 0].astype(np.uint8)
        return gret

def flip_h(img):
    return img[:,::-1]

def flip_v(img):
    return img[::-1]

def rotate(img, steps):
    return np.rot90(img, k=steps)

def scale(img, fact, xoff, yoff):
    width = int(img.shape[1] * fact)
    height = int(img.shape[0] * fact)
    dim = (width, height)
    onscreen_width = max(screen_w, width)
    onscreen_height = max(screen_h, height)
    scaled = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
    ret = scaled[max(0, yoff):min(height, onscreen_height+yoff),max(0, xoff):min(width, onscreen_width+xoff)]
    return ret

def scrub(cap, deltaFrames):
    pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
    cap.set(cv2.CAP_PROP_POS_FRAMES, pos + deltaFrames)

###


def list_devices():
    devs = []
    for n in range(10):
        try:
            c = cv2.VideoCapture(n)
            ret, frame = c.read()
            if ret:
                devs.append(n)
                c.release()
        except:
            break
    return devs


if __name__ == '__main__':
    # print(list_devices())
    if len(sys.argv) == 1:
        Player(0)
    else:
        Player(sys.argv[1])

