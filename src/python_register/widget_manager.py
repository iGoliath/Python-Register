import importlib
import inspect
import os
import pkgutil
import subprocess
import tkinter as tk
from datetime import datetime
from pathlib import Path

import pygame

from . import frames
from . import inventory_functions as invf
from . import widget_functions as wf


class WidgetManager:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.vcmd = (self.root.register(self.only_numbers), "%P")

        self.frames = {}
        self.frame_modules = self.frame_module_query()

        """Initialize all frames necessary for the program"""

        self.register_frame = tk.Frame(self.root, bg="black")
        self.register_info_frame = tk.Frame(self.register_frame, bg="black")
        self.register_add_item_prompt_frame = tk.Frame(self.root)
        self.register_add_item_yes_no_frame = tk.Frame(
            self.register_add_item_prompt_frame
        )
        self.popup_frame = tk.Frame(
            self.root, width=400, height=300, borderwidth=20, relief="ridge", bg="black"
        )
        self.seasonal_id_entry_frame = tk.Frame(
            self.root, width=400, height=300, borderwidth=20, relief="ridge", bg="black"
        )
        self.datetime_frame = tk.Frame(self.root)
        self.edit_seasonal_frame = tk.Frame(self.root)
        self.edit_seasonal_buttons_frame = tk.Frame(self.root)
        self.time_widgets_frame = tk.Frame(self.datetime_frame)
        self.date_widgets_frame = tk.Frame(self.datetime_frame)
        self.seasonal_buttons_frame = tk.Frame(self.root)
        self.coupon_frame = tk.Frame(self.root)
        self.coupon_buttons_frame = tk.Frame(self.coupon_frame)

        self.name_var = tk.StringVar()
        self.barcode_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.tax_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.subcategory_var = tk.StringVar()
        self.vendor_var = tk.StringVar()

        self.invisible_entry_var = tk.StringVar()
        self.popup_label_var = tk.StringVar()
        self.popup_description_label_var = tk.StringVar()

        # Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
        # Widgets in column 1 will determine the width of the rest of the widgets
        for frame in (
            self.register_frame,
            self.register_add_item_prompt_frame,
            self.edit_seasonal_frame,
            self.datetime_frame,
            self.coupon_frame,
        ):
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            frame.columnconfigure(2, weight=1)

        """These frames only need 2 columns of widgets, so
        configure them as such."""
        for frame in (
            self.edit_seasonal_buttons_frame,
            self.register_info_frame,
            self.register_add_item_yes_no_frame,
            self.coupon_buttons_frame,
        ):
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(0, weight=1)

        self.popup_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.popup_frame.columnconfigure(0, weight=1)
        self.popup_frame.columnconfigure(1, weight=0)
        self.popup_frame.columnconfigure(2, weight=1)

        self.seasonal_id_entry_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.seasonal_id_entry_frame.columnconfigure(0, weight=1)
        self.seasonal_id_entry_frame.columnconfigure(1, weight=0)
        self.seasonal_id_entry_frame.columnconfigure(2, weight=1)

        self.time_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.time_widgets_frame.columnconfigure(1, weight=1, uniform="equal")

        self.date_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(1, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(2, weight=1, uniform="equal")

        self.seasonal_buttons_frame.columnconfigure(0, weight=1, uniform="equal")
        self.seasonal_buttons_frame.columnconfigure(1, weight=1, uniform="equal")
        self.seasonal_buttons_frame.columnconfigure(2, weight=1, uniform="equal")

        # ===============================
        # Widgets for Register Mode frame
        # ===============================

        self.register_label = tk.Label(
            self.register_info_frame,
            font=("Arial", 30),
            text="Mode: Register",
            fg="#68FF00",
            bg="black",
        )
        self.register_label.grid(column=0, row=0, sticky="sw", pady=5)

        self.balance_entry = tk.Entry(
            self.register_info_frame,
            font=("Arial", 91),
            bg="black",
            fg="#68FF00",
            justify="right",
            width=9,
        )
        self.balance_entry.insert(tk.END, "$0.00")
        self.balance_entry.grid(column=1, row=0, sticky="e", padx=2)
        self.balance_entry.bind("<FocusIn>", self.return_invisible_entry_focus)

        # Invisible entry where user input actually occurs. Allows user entry to be untampered so
        # same entry box can be used for barcodes and numberic values alike

        self.invisible_entry = tk.Entry(
            self.register_frame, textvariable=self.invisible_entry_var
        )
        self.invisible_entry.place(x=-100, y=-100)
        self.invisible_entry.bind("<Return>", controller.process_sale)
        self.bind_invisible_entry_keys()

        self.user_entry = tk.Entry(
            self.register_info_frame,
            font=("Arial", 35),
            width=10,
            bg="black",
            fg="#68FF00",
        )
        self.user_entry.insert(tk.END, "$0.00")
        self.user_entry.grid(column=0, row=0, sticky="nw")
        self.user_entry.bind("<FocusIn>", self.return_invisible_entry_focus)

        self.register_info_frame.grid(column=1, row=0, sticky="nsew")
        self.sale_items_listbox = tk.Listbox(
            self.register_frame,
            width=34,
            bg="black",
            height=8,
            font=("Courier New", 37),
            fg="white",
        )
        self.sale_items_listbox.grid(column=1, row=2, sticky="nsw")
        self.sale_items_listbox.bind("<FocusIn>", self.return_invisible_entry_focus)
        self.sale_items_listbox.bind(
            "<<ListboxSelect>>", lambda event: controller.on_sale_items_listbox_select()
        )
        self.sale_items_scrollbar = tk.Scrollbar(
            self.register_frame, bg="white", orient=tk.VERTICAL, width=40
        )
        self.sale_items_scrollbar.grid(column=1, row=2, sticky="nse")
        self.sale_items_listbox.config(yscrollcommand=self.sale_items_scrollbar.set)
        self.sale_items_scrollbar.config(command=self.sale_items_listbox.yview)

        self.register_add_item_prompt_label = tk.Label(
            self.register_add_item_prompt_frame,
            text="Item not found\nAdd it?",
            font=("Arial", 50),
        )
        self.register_add_item_prompt_label.grid(row=0, column=1, sticky="ew")

        self.register_add_item_yes_no_frame.grid(row=1, column=1, sticky="nsew")

        self.register_add_item_yes_button = tk.Button(
            self.register_add_item_yes_no_frame,
            text="Yes",
            font=("Arial", 90),
            command=lambda: self.controller.state_mgr.register_yes_no_var.set("yes"),
        )
        self.register_add_item_yes_button.grid(row=0, column=0, sticky="nsew")

        self.register_add_item_no_button = tk.Button(
            self.register_add_item_yes_no_frame,
            text="No",
            font=("Arial", 90),
            command=lambda: self.controller.state_mgr.register_yes_no_var.set("no"),
        )
        self.register_add_item_no_button.grid(row=0, column=1, sticky="nsew")

        # =====================
        # Widgets for coupons
        # =====================

        self.coupon_label = tk.Label(
            self.coupon_frame,
            text="Please enter the amount to\nbe couponed.",
            font=("Arial", 50),
        )
        self.coupon_label.grid(column=1, row=0, sticky="ew", pady=10)

        self.coupon_entry = tk.Entry(self.coupon_frame, font=("Arial", 50))
        self.coupon_entry.grid(column=1, row=1, sticky="ew", pady=10)

        self.coupon_reason_label = tk.Label(
            self.coupon_frame,
            text="If desired, enter a coupon reason.",
            font=("Arial", 50),
        )
        self.coupon_reason_label.grid(column=1, row=2, sticky="ew", pady=10)

        self.coupon_reason_entry = tk.Entry(self.coupon_frame, font=("Arial", 50))
        self.coupon_reason_entry.grid(column=1, row=3, sticky="ew", pady=10)

        self.coupon_back_button = tk.Button(
            self.coupon_buttons_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.register_frame.tkraise(),
        )
        self.coupon_confirm_button = tk.Button(
            self.coupon_buttons_frame,
            text="Confirm",
            font=("Arial", 50),
            command=lambda: self.controller.apply_coupon(),
        )

        self.coupon_back_button.grid(column=0, row=0, sticky="ew")
        self.coupon_confirm_button.grid(column=1, row=0, sticky="ew")

        self.coupon_buttons_frame.grid(column=1, row=4, sticky="ew")

        # ================================================
        # Widgets for the seasonal version of browse frame
        # ================================================

        self.add_seasonal_button = tk.Button(
            self.seasonal_buttons_frame, font=("Arial", 35), text="Add"
        )

        self.remove_seasonal_button = tk.Button(
            self.seasonal_buttons_frame, font=("Arial", 35), text="Remove"
        )

        self.edit_seasonal_button = tk.Button(
            self.seasonal_buttons_frame,
            font=("Arial", 35),
            text="Edit",
            command=lambda: self.edit_seasonal_frame.tkraise(),
        )

        # self.seasonal_buttons_frame.grid(column = 1, row = 4, sticky='ew')

        self.add_seasonal_button.grid(column=0, row=0, sticky="nsew")
        self.remove_seasonal_button.grid(column=1, row=0, sticky="nsew")
        self.edit_seasonal_button.grid(column=2, row=0, sticky="nsew")

        # =================================
        # Widgets for Editing Seasonal Info
        # =================================

        # =============================
        # Widgets for Seasonal ID Entry
        # =============================

        self.seasonal_id_label = tk.Label(
            self.seasonal_id_entry_frame,
            font=("Arial", 50),
            text="Please enter\nSeasonal's ID",
        )
        self.seasonal_id_label.grid(column=1, row=0, sticky="nsew")

        self.seasonal_id_entry = tk.Entry(
            self.seasonal_id_entry_frame,
            font=("Arial", 50),
            validate="key",
            vcmd=self.vcmd,
        )
        self.seasonal_id_entry.grid(column=1, row=1, sticky="nsew")

        self.seasonal_id_button = tk.Button(
            self.seasonal_id_entry_frame,
            font=("Arial", 50),
            text="Confirm",
            command=lambda: self.controller.state_mgr.seasonal_id_var.set(
                self.seasonal_id_entry.get()
            ),
        )
        self.seasonal_id_button.grid(column=1, row=2, sticky="nsew")

        # ===========================
        # Widgets for the Popup Frame
        # ===========================

        self.popup_label = tk.Label(
            self.popup_frame,
            text="ERROR:",
            font=("Arial", 50),
            fg="red",
            justify="center",
        )
        self.popup_label.grid(column=1, row=0, sticky="ew")

        self.popup_description_label = tk.Label(
            self.popup_frame,
            text="",
            font=("Arial", 50),
            textvariable=self.popup_description_label_var,
        )
        self.popup_description_label.grid(column=1, row=1, sticky="ew")

        self.popup_ok_button = tk.Button(
            self.popup_frame,
            text="Ok",
            font=("Arial", 50),
            command=lambda: self.popup_frame.lower(),
        )
        self.popup_ok_button.grid(column=1, row=2, sticky="ew")

        self.popup_back_confirm_frame = tk.Frame(self.popup_frame)
        self.popup_back_confirm_frame.columnconfigure(0, weight=1, uniform="equal")
        self.popup_back_confirm_frame.columnconfigure(1, weight=1, uniform="equal")
        self.popup_back_button = tk.Button(
            self.popup_back_confirm_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.controller.state_mgr.popup_var.set("Back"),
        )
        self.popup_back_button.grid(column=0, row=0, sticky="nsew")

        self.popup_confirm_button = tk.Button(
            self.popup_back_confirm_frame,
            text="Confirm",
            font=("Arial", 50),
            command=lambda: self.controller.state_mgr.popup_var.set("Confirm"),
        )

        self.popup_confirm_button.grid(column=1, row=0, sticky="nsew")

        self.popup_listbox = tk.Listbox(
            self.popup_frame,
            font=("Courier New", 40),
            height=4,
            bg="black",
            fg="white",
            width=31,
        )

        # =============================
        # Widgets for Manual Time Entry
        # =============================

        self.datetime_frame.grid(column=0, row=0, sticky="nsew")

        self.datetime_label = tk.Label(
            self.datetime_frame,
            font=("Arial", 35),
            text="Current time could not be synced. Please\nenter the current time below, or exit the \nprogram and check for an internet connection.",
        )
        self.datetime_label.grid(column=1, row=0, sticky="nsew", pady=15)

        self.year_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Year"
        )

        self.month_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Month"
        )

        self.day_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Day"
        )

        self.date_widgets_frame.grid(column=1, row=1, sticky="nsew")
        self.year_label.grid(column=0, row=0, sticky="nsew")
        self.month_label.grid(column=1, row=0, sticky="nsew")
        self.day_label.grid(column=2, row=0, sticky="nsew")

        self.year_spinbox = tk.Spinbox(
            self.date_widgets_frame, from_=2026, to=2100, font=("Arial", 50), width=5
        )
        self.year_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.month_spinbox = tk.Spinbox(
            self.date_widgets_frame,
            from_=1,
            to=12,
            font=("Arial", 50),
            width=5,
            wrap=True,
        )
        self.month_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.date_spinbox = tk.Spinbox(
            self.date_widgets_frame,
            from_=1,
            to=31,
            font=("Arial", 50),
            width=5,
            wrap=True,
        )
        self.date_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.year_spinbox.grid(column=0, row=1, sticky="nsew")
        self.month_spinbox.grid(column=1, row=1, sticky="nsew")
        self.date_spinbox.grid(column=2, row=1, sticky="nsew")

        self.time_widgets_frame.grid(column=1, row=2, sticky="nsew")
        self.hours_label = tk.Label(
            self.time_widgets_frame, font=("Arial", 35), text=("Hour")
        )

        self.minutes_label = tk.Label(
            self.time_widgets_frame, font=("Arial", 35), text=("Minute")
        )

        self.hours_spinbox = tk.Spinbox(
            self.time_widgets_frame,
            from_=0,
            to=23,
            font=("Arial", 50),
            width=5,
            wrap=True,
        )
        self.hours_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.minute_spinbox = tk.Spinbox(
            self.time_widgets_frame,
            from_=0,
            to=59,
            font=("Arial", 50),
            width=5,
            wrap=True,
        )
        self.minute_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.hours_label.grid(column=0, row=0, sticky="nsew", pady=5)
        self.minutes_label.grid(column=1, row=0, sticky="nsew", pady=5)

        self.hours_spinbox.grid(column=0, row=1, sticky="nsew", pady=15)
        self.minute_spinbox.grid(column=1, row=1, sticky="nsew", pady=15)

        self.datetime_confirm_button = tk.Button(
            self.datetime_frame,
            font=("Arial, 50"),
            text="Confirm",
            command=lambda: self.set_system_time(),
        )

        self.datetime_confirm_button.grid(column=1, row=3, sticky="nsew")

    def show_frame(self, name, **kwargs):
        if name not in self.frames:
            module_name = self.frame_modules[name]
            module = importlib.import_module(module_name)
            frame_class = self._find_frame_class(module)
            frame = frame_class(
                parent=self.root,
                controller=self.controller,
                wm=self,
                state_mgr=self.controller.state_mgr,
            )
            frame.grid(row=0, column=0, sticky="nsew")
            frame.columnconfigure(0, weight=0)
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(2, weight=0)
            self.frames[name] = frame

        self.frames[name].tkraise()
        self.frames[name].on_show(**kwargs)

    def frame_module_query(self, package=frames):
        return {
            module_name.rsplit(".", 1)[-1].removesuffix("_frame"): module_name
            for _, module_name, is_pkg in pkgutil.iter_modules(
                package.__path__, prefix=package.__name__ + "."
            )
            if not is_pkg
        }

    @staticmethod
    def _find_frame_class(module):
        for attr_name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, tk.Frame) and obj.__module__ == module.__name__:
                return obj
        raise ValueError(f"No tk.Frame subclass found in {module.__name__}")

    def only_numbers(self, P):
        """Check if potential key is a number or space, return false if not"""
        if P.isdigit() or P == "":
            return True
        else:
            return False

    def return_to_register(self):
        self.register_frame.tkraise()
        self.invisible_entry.delete(0, tk.END)
        self.invisible_entry.focus_set()

    def enter_add_item_frame(self):
        self.show_frame("add_name")
        self.show_frame("add_price")
        self.show_frame("add_tax")
        self.show_frame("add_category")
        self.show_frame("add_subcategory")
        self.show_frame("add_vendor")
        self.show_frame("add_quantity")
        self.show_frame("add_barcode")
        self.reset_add_item_back_buttons()

    def reset_add_item_back_buttons(self):
        # self.add_barcode_back_button.config(command = lambda: self.controller.go_back())
        # self.add_name_back_button.config(command = lambda: self.controller.go_back())
        # self.add_price_back_button.config(command = lambda: self.controller.go_back())
        # self.add_tax_back_button.config(command = lambda: self.controller.go_back())
        # self.add_category_back_button.config(command = lambda: self.controller.go_back())
        # self.add_subcategory_back_button.config(command = lambda: self.controller.go_back())
        # self.add_vendor_back_button.config(command = lambda: self.controller.go_back())
        # self.add_quantity_back_button.config(command = lambda: self.controller.go_back())
        # self.add_vendor_skip_button.grid(column = 1, row = 4, sticky='ew')
        pass

    def enter_register_frame(self):
        self.invisible_entry.delete(0, tk.END)
        self.sale_items_listbox.delete(0, tk.END)
        self.update_entry(self.user_entry, "$0.00")
        self.update_entry(self.balance_entry, "$0.00")
        self.register_label.config(text="Mode: Register", fg="#68FF00")
        self.register_frame.tkraise()
        self.bind_invisible_entry_keys()
        self.invisible_entry.focus_force()

    def setup_seasonal_sale(self):
        self.register_label.config(text="Mode: Seasonal Sale", fg="red")
        self.unbind_invisible_entry_keys()
        self.invisible_entry.bind(
            "<KeyRelease-KP_Enter>", lambda event: self.controller.make_seasonal_sale()
        )
        self.invisible_entry.delete(0, tk.END)
        # Finish later->> self.invisible_entry.bind("<KeyRelease-KP_Decimal>", lambda event: self.return_register_widgets())
        self.register_frame.tkraise()
        self.invisible_entry.focus_set()

    def setup_browse_seasonals(self):
        self.browse_label.grid_forget()
        self.browse_transactions_frame.tkraise()
        self.popup_description_label.config(font=("Arial", 35))
        self.popup_description_label_var.set(
            "You are now browsing seasonals. "
            'Enter a\nseasonal ID in the entry box and select "GO"\nto jump to one. '
            "Press one of the buttons\nto delete, add, or edit that seasonal."
        )
        self.popup_frame.tkraise()
        self.browse_entry.focus_set()

    def bind_invisible_entry_keys(self):
        for key in (
            "Home",
            "Up",
            "Prior",
            "Left",
            "Begin",
            "Right",
            "End",
            "Down",
            "Next",
            "Insert",
            "Delete",
        ):
            self.invisible_entry.bind(
                f"<KeyRelease-KP_{key}>", lambda e: self.number_pressed()
            )
        self.invisible_entry.bind("<KeyRelease-BackSpace>", self.controller.clear)
        self.invisible_entry.bind(
            "<KeyRelease-KP_Enter>", lambda event: self.controller.on_cash()
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Add>", lambda event: self.controller.on_cc()
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Multiply>", lambda event: self.show_frame("main_menu")
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Divide>", lambda event: self.controller.cancel_sale()
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Subtract>", lambda event: self.controller.no_sale()
        )
        self.invisible_entry.bind(
            "<KeyRelease-backslash>", lambda event: self.controller.complete_decrement()
        )
        self.invisible_entry.unbind("<KeyRelease-Escape>")

    def number_pressed(self):

        pygame.mixer.music.load(Path(__file__).parent / "short-beep.mp3")
        pygame.mixer.music.play()

        string = self.invisible_entry_var.get().strip()

        while len(string) < 3:
            string = "0" + string

        self.update_entry(self.user_entry, f"${string[0:-2]}.{string[-2:]}")

    def unbind_invisible_entry_keys(self):
        for key in (
            "Home",
            "Up",
            "Prior",
            "Left",
            "Begin",
            "Right",
            "End",
            "Down",
            "Next",
            "Insert",
        ):
            self.invisible_entry.unbind(f"<KeyRelease-KP_{key}>")
        self.invisible_entry.unbind("<KeyRelease-BackSpace>")
        self.invisible_entry.unbind("<KeyRelease-KP_Enter>")
        self.invisible_entry.unbind("<KeyRelease-KP_Add>")
        self.invisible_entry.unbind("<KeyRelease-KP_Multiply>")
        self.invisible_entry.unbind("<KeyRelease-KP_Divide>")
        self.invisible_entry.unbind("<KeyRelease-KP_Subtract>")

    def update_entry(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def setup_coupon(self):
        self.update_entry(self.coupon_entry, "$0.00")
        self.coupon_reason_entry.delete(0, tk.END)
        self.update_entry(
            self.balance_entry, f"${self.controller.state_mgr.trans.total:.2f}"
        )
        self.register_frame.tkraise()
        self.invisible_entry.focus_set()

    def quit_program(self):
        self.controller.state_mgr.conn.commit()
        self.controller.state_mgr.conn.close()
        del self.controller.state_mgr
        del self.controller
        self.root.quit()
        self.root.destroy()

    def lose_spinbox_focus(self):
        self.datetime_label.focus_set()
        return "break"

    def set_system_time(self):
        time_string = ""

        time_string += f"{self.year_spinbox.get()}-"
        time_string += (
            f"{self.month_spinbox.get()}-"
            if len(self.month_spinbox.get()) == 2
            else f"0{self.month_spinbox.get()}-"
        )
        time_string += (
            f"{self.date_spinbox.get()} "
            if len(self.date_spinbox.get()) == 2
            else f"0{self.date_spinbox.get()}"
        )
        time_string += (
            f" {self.hours_spinbox.get()}:"
            if len(self.hours_spinbox.get()) == 2
            else f" 0{self.hours_spinbox.get()}:"
        )
        time_string += (
            f"{self.minute_spinbox.get()}:00"
            if len(self.minute_spinbox.get()) == 2
            else f"0{self.minute_spinbox.get()}:00"
        )

        # date_time = datetime.strptime(time_string, "%Y%m%d %H%M")

        subprocess.run(["sudo", "date", "-s", time_string])
        self.quit_program()

    def setup_popup_ok(self):
        self.popup_label.config(text="ERROR:")
        self.popup_ok_button.grid(column=1, row=2, sticky="nsew")
        self.popup_back_confirm_frame.grid_forget()

    def setup_popup_back_confirm(self):
        self.popup_label.config(text="NOTE:")
        self.popup_ok_button.grid_forget()
        self.popup_back_confirm_frame.grid(column=1, row=2, sticky="ew")

    def return_invisible_entry_focus(self, event):
        """Bound to FocusIn on register widgets. Returns focus to invisible
        entry, and returns 'break' to stop propagating event."""
        self.invisible_entry.focus_set()
        return "break"

    def add_item_go_back(self, add_item_index):

        match add_item_index:
            case 0:
                self.show_frame("add_barcode")
            case 1:
                self.show_frame("add_name")
            case 2:
                self.show_frame("add_price")
            case 3:
                self.show_frame("add_tax")
            case 4:
                self.show_frame("add_category")
            case 5:
                self.show_frame("add_subcategory")
            case 6:
                self.show_frame("add_vendor")
            case 7:
                self.show_frame("add_quantity")

    def print_seasonal_info(self, seasonal_info):
        self.browse_text.delete("1.0", "end")
        # self.ui.browse_text.insert("end", f"ID: {seasonal_info[0]}  |  Site: {seasonal_info[3]}\n")
        self.browse_text.insert("end", "ID: ", "bold")
        self.browse_text.insert("end", seasonal_info[0])
        self.browse_text.insert("end", "|Site: ", "bold")
        self.browse_text.insert("end", f"{seasonal_info[3]}")
        self.browse_text.insert("end", "|Balance: ", "bold")
        self.browse_text.insert("end", f"{seasonal_info[4]:.2f}\n")
        self.browse_text.insert("end", "Name: ", "bold")
        self.browse_text.insert("end", f"{seasonal_info[1]}\n{seasonal_info[2]}\n")
