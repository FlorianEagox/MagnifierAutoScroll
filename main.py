import ctypes
import time
import tkinter as tk
from threading import Thread
import keyboard

# Constants
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]

class Input_I(ctypes.Union):
    _fields_ = [("mi", MouseInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

def move_mouse(x, y):
    inp = Input(type=INPUT_MOUSE, ii=Input_I(mi=MouseInput(dx=x, dy=y, mouseData=0, dwFlags=MOUSEEVENTF_MOVE, time=0, dwExtraInfo=None)))
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

class CursorMover:
    def __init__(self, tempo, start_x, end_x, start_y, end_y, line_height):
        self.tempo = tempo
        self.start_x = start_x
        self.end_x = end_x
        self.start_y = start_y
        self.end_y = end_y
        self.line_height = line_height
        self.running = False
        self.paused = False
        self.thread = None

    def move_cursor(self):
        current_y = self.start_y
        while current_y < self.end_y and self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            # Move cursor from start_x to end_x
            for x in range(self.start_x, self.end_x, 10):  # Adjust step size for smoother/faster movement
                if not self.running or self.paused:
                    break
                self.set_mouse_position(x, current_y)
                time.sleep(1 / (self.tempo * 10))  # Adjust sleep time to control the speed of the cursor

            current_y += self.line_height
            if current_y < self.end_y and self.running:
                # Move cursor to the start of the next line
                self.set_mouse_position(self.start_x, current_y)

    def start(self):
        self.running = True
        self.paused = False
        if self.thread is None or not self.thread.is_alive():
            self.thread = Thread(target=self.move_cursor)
            self.thread.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()

    def set_mouse_position(self, x, y):
        ctypes.windll.user32.SetCursorPos(x, y)
        move_mouse(x, y)

def create_gui(cursor_mover):
    root = tk.Tk()
    root.title("Cursor Mover")

    def on_start():
        cursor_mover.tempo = float(tempo_entry.get())
        cursor_mover.start_x = int(start_x_entry.get())
        cursor_mover.end_x = int(end_x_entry.get())
        cursor_mover.start_y = int(start_y_entry.get())
        cursor_mover.end_y = int(end_y_entry.get())
        cursor_mover.line_height = int(line_height_entry.get())
        cursor_mover.start()

    def on_pause():
        cursor_mover.pause()

    def on_resume():
        cursor_mover.resume()

    def on_stop():
        cursor_mover.stop()

    # Create labels and entries for each parameter
    tk.Label(root, text="Tempo (notes per second):").pack()
    tempo_entry = tk.Entry(root)
    tempo_entry.pack()
    tempo_entry.insert(0, str(cursor_mover.tempo))

    tk.Label(root, text="Start X:").pack()
    start_x_entry = tk.Entry(root)
    start_x_entry.pack()
    start_x_entry.insert(0, str(cursor_mover.start_x))

    tk.Label(root, text="End X:").pack()
    end_x_entry = tk.Entry(root)
    end_x_entry.pack()
    end_x_entry.insert(0, str(cursor_mover.end_x))

    tk.Label(root, text="Start Y:").pack()
    start_y_entry = tk.Entry(root)
    start_y_entry.pack()
    start_y_entry.insert(0, str(cursor_mover.start_y))

    tk.Label(root, text="End Y:").pack()
    end_y_entry = tk.Entry(root)
    end_y_entry.pack()
    end_y_entry.insert(0, str(cursor_mover.end_y))

    tk.Label(root, text="Line Height:").pack()
    line_height_entry = tk.Entry(root)
    line_height_entry.pack()
    line_height_entry.insert(0, str(cursor_mover.line_height))

    start_button = tk.Button(root, text="Start", command=on_start)
    start_button.pack()

    pause_button = tk.Button(root, text="Pause", command=on_pause)
    pause_button.pack()

    resume_button = tk.Button(root, text="Resume", command=on_resume)
    resume_button.pack()

    stop_button = tk.Button(root, text="Stop", command=on_stop)
    stop_button.pack()

    root.mainloop()

# Parameters
tempo = 4  # Notes per second (adjust to your needs)
start_x = 200  # Starting x coordinate
end_x = 800  # Ending x coordinate
start_y = 400  # Starting y coordinate
end_y = 800  # Ending y coordinate
line_height = 100  # Height of each line in pixels

cursor_mover = CursorMover(tempo, start_x, end_x, start_y, end_y, line_height)

keyboard.add_hotkey('ctrl+p', lambda: cursor_mover.pause())
keyboard.add_hotkey('r', lambda: cursor_mover.resume())
keyboard.add_hotkey('ctrl+alt+s', lambda: cursor_mover.stop())

create_gui(cursor_mover)
