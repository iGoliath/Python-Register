import tkinter as tk

from .base_frame import BaseFrame


class SettingsFrame(BaseFrame):

    def build_widgets(self):

        canvas = tk.Canvas(self)
        canvas.grid(column=1, row=0, sticky="nsew")

        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.grid(column=2, row=0, sticky="nse")

        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        for i, field in enumerate(self.controller.config.data):
            name = field.replace("_", " ").title()
            tk.Label(frame, text=name, font=("Arial", 58)).grid(
                column=0, row=i, sticky="nsew"
            )

            entry = tk.Entry(
                frame,
                font=("Arial", 58),
            )
            entry.grid(column=1, row=i, sticky="nsew")

            entry.insert(tk.END, self.controller.config.data[field])
        """tk.Label(
            frame,
            text="Printing Width:",
            font=("Arial", 58)
            ).grid(column=0, row=0, sticky='nsew')

        tk.Entry(
            frame,
            font=("Arial", 58),
            width=4
        ).grid(column=1, row=0, sticky='nsew', padx=50)

        tk.Label(
            frame,
            text="Email Address"
        )"""
