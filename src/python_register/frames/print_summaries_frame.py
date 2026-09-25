import tkinter as tk
from datetime import datetime

from tkcalendar import DateEntry

from .base_frame import BaseFrame


class PrintSummariesFrame(BaseFrame):

    def build_widgets(self):

        text_explanation = tk.Label(
            self,
            text="Please select range of dates to\nprint a summary from, inclusive",
            font=("Arial", 50),
        )
        text_explanation.grid(column=1, row=0, sticky="ew")

        self.starting_date_entry = DateEntry(
            self, date_pattern="yyyy-mm-dd", width=15, font=("Arial", 15)
        )
        self.starting_date_entry.grid(column=1, row=1, pady=15)

        self.ending_date_entry = DateEntry(
            self, date_pattern="yyyy-mm-dd", width=15, font=("Arial", 15)
        )
        self.ending_date_entry.grid(column=1, row=2, pady=15)

        confirm_button = tk.Button(
            self,
            text="Confirm Summary",
            font=("Arial", 50),
            command=lambda: self.on_confirm(),
        )
        confirm_button.grid(column=1, row=3, pady=15)

        back_button = tk.Button(
            self,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("admin_menu"),
        )
        back_button.grid(column=1, row=4, pady=45)

        # back_button = tk.Button(self, text="Back", command = lambda: )

    def on_show(self):
        self.starting_date_entry.set_date(
            datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        )
        self.ending_date_entry.set_date(datetime.today())

    def set_today(self):
        self.starting_date_entry.set_date(datetime.today())
        self.ending_date_entry.set_date(datetime.today())

    def on_confirm(self):
        self.controller.printer.run_x(
            self.starting_date_entry.get_date(), self.ending_date_entry.get_date()
        )
        self.controller.ui.show_frame("main_menu")
