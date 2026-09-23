from abc import ABC, abstractmethod
import tkinter as tk


class BaseFrame(tk.Frame, ABC):

    def __init__(self, parent, controller, wm):
        super().__init__(parent)
        self.controller = controller
        self.wm = wm
        self.build_widgets()


    @abstractmethod
    def build_widgets(self):
        """Build this frame (screen)'s widgets when the screen is initialized"""
        return NotImplementedError
    
    def on_show(self, **kwargs):
        """Called whenever the frame is needed. Useful for resetting state."""
        pass