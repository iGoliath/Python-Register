import logging
import os
import smtplib
import sqlite3
import ssl
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta
from email.message import EmailMessage
from tkinter import ttk

from . import inventory_functions as invf
from . import widget_functions as wf
from .config import Config
from .printing_manager import Printer
from .state_manager import StateManager
from .widget_manager import WidgetManager

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import subprocess
import sys
from decimal import *
from pathlib import Path

import pygame
from luma.core.error import DeviceNotFoundError
from luma.core.interface.serial import noop, spi
from luma.core.render import canvas
from luma.core.virtual import sevensegment
from luma.led_matrix.device import max7219


class Register:
    def __init__(self, root, db_connection=None):
        """Initialize UI, StateManager, Config"""
        try:
            serial = spi(port=0, device=0, gpio=noop())
            device = max7219(serial)
            self.seg = sevensegment(device)
        except FileNotFoundError as e:
            print(e)
            self.seg = None
        except DeviceNotFoundError as e:
            print(e)
            self.seg = None
        self.config = Config()
        self.state_mgr = StateManager(root, db_connection, self.config)

        self.ui = WidgetManager(root, self)

        self.ui.tax_var.trace_add("write", lambda *args: self.on_add_item_enter())
        self.state_mgr.yes_no_var.trace_add("write", self.finish_entering)
        self.state_mgr.register_yes_no_var.trace_add("write", self.on_yes_no_var_update)

        self.current_dir = Path(__file__).parent

        self.printer = Printer(self.state_mgr, self.config)

        self.add_variables = [
            self.ui.barcode_var,
            self.ui.name_var,
            self.ui.price_var,
            self.ui.tax_var,
            self.ui.category_var,
            self.ui.subcategory_var,
            self.ui.vendor_var,
            self.ui.quantity_var,
        ]

    def enter_reconciling_mode(self):
        """Check whether or not reconciling mode is set.
        If so, turn it off, if not turn it on."""
        if self.config.data["reconciling_mode"]:
            self.ui.popup_description_label_var.set("Reconciling mode is now OFF")
            self.config.data["reconciling_mode"] = False
        else:
            self.ui.popup_description_label_var.set("Reconciling mode is now ON")
            self.config.data["reconciling_mode"] = True
        self.config.write_out_config()
        self.ui.popup_frame.tkraise()

    def enter_add_item_lookup(self):
        self.ui.show_frame("lookup_items")
        self.state_mgr.looking_up_add_item = True

    def handle_lookup_confirmed(self, barcode, quantity):
        if self.state_mgr.looking_up_add_item:
            self.state_mgr.looking_up_add_item = False
            self.ui.barcode_var.set(barcode)
            self.on_add_item_enter()
        else:
            self.ui.frames["register"].process_sale(None, barcode, quantity)
            self.ui.show_frame("register")

    def perform_backup(self, backup_path):
        time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        source_db = sqlite3.connect(
            self.current_dir / self.config.data["database_name"]
        )
        dest_db = sqlite3.connect(f"{backup_path}/RegisterDatabaseBackup_{time}.db")

        source_db.backup(dest_db)
        source_db.close()
        dest_db.close()

    def backup_scheduler(self, backup_path):
        while True:
            time.sleep(self.config.data["backup_interval"])
            self.perform_backup(backup_path)

    def remove_old_backups(self, backup_path, days):
        cutoff = time.time() - (days * 86400)
        for filename in os.listdir(backup_path):
            if filename.split("_")[0] != "RegisterDatabaseBackup":
                continue
            filepath = os.path.join(backup_path, filename)
            if os.path.getmtime(filepath) < cutoff and not os.path.isdir(filepath):
                os.remove(filepath)

    def check_time_synced(self):

        try:
            results = subprocess.run(
                ["timedatectl", "status"], capture_output=True, text=True
            )
            return "System clock synchronized: yes" in results.stdout
        except Exception:
            return False

    def enter_add_item_frame(self, entered_barcode=None):
        """Reset the necessary add item process parameters to defaults. If a barcode
        is present, send it to the add item process."""
        self.state_mgr.new_add_item_dict()
        self.state_mgr.reentering = False
        self.state_mgr.add_item_index = 0
        self.ui.enter_add_item_frame()

        if entered_barcode is not None:
            self.on_add_item_enter(None, entered_barcode)

    def on_yes_no_var_update(self, *kwargs):
        yes_no_answer = self.state_mgr.register_yes_no_var.get()
        if yes_no_answer == "yes":
            self.state_mgr.coming_from_register = True
            self.enter_add_item_frame(
                self.ui.frames["register"].invisible_entry_var.get()
            )
        elif yes_no_answer == "no":
            self.ui.show_frame("register")

    def print_to_sevenseg(self, to_print):
        self.seg.text = f"{' ' * (9 - len(str(to_print)))}{to_print}"

    def go_back(self):
        """Changes index on back button press and resets environment accordingly."""
        if self.state_mgr.add_item_index != 0:
            self.state_mgr.add_item_index -= 1
        self.ui.add_item_go_back(self.state_mgr.add_item_index)

    def reenter_button_pressed(self, which_button):
        """Reset to add item interface according to button user presses."""

        self.state_mgr.reentering = True

        match which_button:
            case "barcode":
                self.state_mgr.add_item_index = 0
                self.ui.show_frame("add_barcode", reentering=True)
            case "name":
                self.state_mgr.add_item_index = 1
                self.ui.show_frame(
                    "add_name",
                    reentering=True,
                    item_name=self.state_mgr.add_item_dict.name,
                )
            case "price":
                self.state_mgr.add_item_index = 2
                self.ui.show_frame("add_price", reentering=True)
            case "taxable":
                self.state_mgr.add_item_index = 3
                self.ui.show_frame("add_tax", reentering=True)
            case "category":
                self.state_mgr.add_item_index = 4
                self.ui.show_frame("add_category", reentering=True)
            case "subcategory":
                self.state_mgr.add_item_index = 5
                self.ui.show_frame("add_subcategory", reentering=True)
            case "vendor":
                self.state_mgr.add_item_index = 6
                self.ui.show_frame("add_vendor", reentering=True)
            case "quantity":
                self.state_mgr.add_item_index = 7
                self.state_mgr.reentering_quantity = True
                self.state_mgr.reentering = False
                self.ui.show_frame("add_quantity", reentering=True)

    def reenter_back_button(self):
        self.state_mgr.add_item_index = self.state_mgr.ADD_ITEM_LAST_STEP
        self.ui.show_frame("reenter")

    def skip_vendor_step(self):
        self.state_mgr.add_item_dict.vendor = "N/A"
        self.state_mgr.add_item_index += 1
        self.ui.show_frame("add_quantity")

    def check_zero_integer(self, input: str) -> bool:

        try:
            return int(input) == 0
        except (ValueError, TypeError):
            return False

    def on_add_item_enter(self, event=None, entered_barcode=None, skipping_ahead=False):
        """Handle user pressing enter or next in the context of adding an item.
        Process is handled in a series of steps."""

        if entered_barcode is not None:
            item_info_entered = entered_barcode
        else:
            item_info_entered = (
                self.add_variables[self.state_mgr.add_item_index].get().strip()
            )
            self.add_variables[self.state_mgr.add_item_index].set("")

        if (
            not skipping_ahead
            and self.state_mgr.add_item_index != 3
            and self.state_mgr.add_item_index != self.state_mgr.ADD_ITEM_LAST_STEP
        ):
            if item_info_entered == "" or self.check_zero_integer(item_info_entered):
                return
            elif item_info_entered == "$0.00":
                self.ui.show_frame("add_price")
                return

        match self.state_mgr.add_item_index:
            case 0:
                if not self.state_mgr.reentering:
                    if invf.check_item_exists(self.state_mgr, item_info_entered):
                        self.on_add_item_enter(None, None, True)
                    else:
                        self.ui.show_frame("add_name")
                else:
                    invf.enter_item_barcode(self.state_mgr, item_info_entered)
                    self.on_add_item_enter(None, None, True)
            case 1:
                if invf.enter_item_name(self.state_mgr, item_info_entered):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_price")
            case 2:
                self.ui.price_var.set("")
                if invf.enter_item_price(self.state_mgr, item_info_entered):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_tax")
            case 3:
                if invf.enter_item_taxable(item_info_entered, self.state_mgr):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_category")
            case 4:
                if invf.enter_item_category(self.state_mgr, item_info_entered):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_subcategory")
            case 5:
                if invf.enter_item_subcategory(self.state_mgr, item_info_entered):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_vendor")
            case 6:
                if invf.enter_item_vendor(self.state_mgr, item_info_entered):
                    self.on_add_item_enter(None, None, True)
                else:
                    self.ui.show_frame("add_quantity")
            case self.state_mgr.ADD_ITEM_LAST_STEP:
                self.ui.show_frame("add_item")
                if not skipping_ahead:
                    return_value = invf.enter_item_confirmation(
                        self.state_mgr, item_info_entered, self.ui
                    )
                else:
                    return_value = invf.enter_item_confirmation(
                        self.state_mgr, item_info_entered, self.ui, True
                    )
            case _:
                self.ui.popup_description_label.config(
                    "Add item index out of bounds!\nPlease try again."
                )
                self.ui.popup_frame.tkraise()

    def finish_entering(self, *args):
        yes_no_answer = self.state_mgr.yes_no_var.get()
        if yes_no_answer == "yes":
            if self.state_mgr.coming_from_register:
                invf.yes_register(self.state_mgr)
                self.ui.frames["register"].process_sale(
                    None, self.state_mgr.add_item_dict.barcode
                )
                self.state_mgr.coming_from_register = False
                self.ui.show_frame("register")
            elif self.state_mgr.updating_existing_item:
                invf.yes_existing(self.state_mgr)
                self.enter_add_item_frame()
            elif not self.state_mgr.coming_from_register:
                invf.yes_not_register(self.state_mgr)
                self.enter_add_item_frame()
        elif yes_no_answer == "no":
            self.ui.show_frame("reenter")

    def on_yes_no(self, answer):
        """Handles certain pressed of yes/no buttons."""
        if self.state_mgr.add_item_index == 3:
            self.ui.tax_var.set(answer)
            self.on_add_item_enter()
        elif self.state_mgr.add_item_index == self.state_mgr.ADD_ITEM_LAST_STEP:
            if answer == "no":
                self.state_mgr.yes_no_var.set(answer)
                self.ui.show_frame("reenter")
            else:
                self.state_mgr.yes_no_var.set(answer)

    def enter_add_item_frame_again(self):
        invf.enter_item_confirmation(self.state_mgr, item_info_entered, self.ui)

    def apply_coupon(self):
        coupon_amount = Decimal(self.ui.coupon_entry.get()[1:])
        self.state_mgr.coupon = coupon_amount
        self.state_mgr.used_coupon = True
        coupon_reason = self.ui.coupon_reason_entry.get()
        self.state_mgr.coupon_reason = coupon_reason
        self.state_mgr.trans.total -= coupon_amount
        self.ui.setup_coupon()


if __name__ == "__main__":

    # Declaration of root window
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("DateEntry", arrowsize=50)
    root.title("TBC REGISTER")
    root.geometry("1024x600")
    # root.tk.call('tk', 'scaling', 1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    register = Register(root)
    register.state_mgr.cursor.execute(
        "INSERT INTO no_sale (date, times_pressed) VALUES (?, ?) ON CONFLICT (date)"
        "DO NOTHING",
        (datetime.today().strftime("%Y-%m-%d"), 0),
    )
    register.state_mgr.conn.commit()
    getcontext().rounding = "ROUND_HALF_UP"

    backup_path = Path(register.config.data["backup_path"]).expanduser().resolve()
    if backup_path.exists() or os.path.ismount(backup_path):
        backup_thread = threading.Thread(
            target=register.backup_scheduler, args=(backup_path,), daemon=True
        )
        backup_thread.start()

        register.remove_old_backups(
            backup_path, register.config.data["backup_removal_cutoff"]
        )

        register.perform_backup(backup_path)
    else:
        register.ui.popup_description_label_var.set(
            "Backup path could not be resolved.\nTherefore, database will not actively be backing up!"
        )
        register.ui.popup_frame.tkraise()

    pygame.mixer.init()
    register.ui.show_frame("register", first_time=True)

    if register.config.data["manual_time_last_boot"]:
        results = subprocess.run(
            ["ping", "-c", "1", "-W", "10", "8.8.8.8"], capture_output=True, text=True
        )
        if results.returncode == 0:
            subprocess.run(["sudo", "timedatectl", "set-ntp", "true"])
        else:
            register.ui.popup_description_label_var.set(
                "Internet connection could not be reached.\nPlease check your network connection."
            )
            register.ui.popup_frame.tkraise()
    elif not register.check_time_synced():
        register.ui.datetime_frame.tkraise()

    root.after(500, lambda: root.attributes("-fullscreen", True))

    root.mainloop()
