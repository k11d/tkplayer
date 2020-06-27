from tkinter import *


def main_ui(root, pc):
    _ui = {}
    btns_frame = Frame(root)
    btns_frame.pack(side="left", expand=0)
    label = Label(root)
    label.pack(side="right", expand=1)
    _ui['label'] = label

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

    seq_btns = Frame(btns_frame)
    seq_btns.grid(row=6, column=0)
    Button(seq_btns, text="A", command=pc.set_sequence_start).pack(side="left")
    Button(seq_btns, text="Reset", command=pc.reset_sequence).pack(side="left")
    Button(seq_btns, text="B", command=pc.set_sequence_end).pack(side="right")

    Button(btns_frame, text="Rotate", command=pc.rotate).grid(row=7, column=0)
    Button(btns_frame, text="Gray", command=pc.grayscale_toggle).grid(row=8, column=0)
    return _ui
