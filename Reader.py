import tkinter as tk
from tkinter import filedialog

class Reader:
    def __init__(self):
        self.path = ""

    def openExplorer(self):
        root = tk.Tk()
        root.withdraw()
        self.path = filedialog.askopenfilename()

    def getPath(self):
        return self.path