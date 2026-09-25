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
from tkinter import messagebox, ttk

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
        self.state_mgr = StateManager(
            root,
            self.config.data["database_name"],
            db_connection,
            self.config.data["tax_amount"],
        )
        self.state_mgr.sale_items_listbox_var.trace_add(
            "write", self.on_sale_items_listbox_var
        )
        self.state_mgr.return_var.trace_add("write", self.finish_return)

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

    def enter_add_item_lookup(self):
        self.ui.show_frame("lookup_items")
        self.state_mgr.looking_up_add_item = True

    def handle_lookup_confirmed(self, barcode, quantity):
        if self.state_mgr.looking_up_add_item:
            self.state_mgr.looking_up_add_item = False
            self.ui.barcode_var.set(barcode)
            self.on_add_item_enter()
        else:
            self.process_sale(None, barcode, quantity)
            self.ui.return_to_register()

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

    def enter_register_frame(self, event=None):
        """Reset register environment to defaults, and raise the register frame."""
        pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
        pygame.mixer.music.play()
        self.state_mgr.new_transaction()
        if self.seg:
            self.print_to_sevenseg("0.00")
        self.ui.enter_register_frame()
        return "break"

    def enter_add_item_frame(self, entered_barcode=None):
        """Reset the necessary add item process parameters to defaults. If a barcode
        is present, send it to the add item process."""
        self.state_mgr.new_add_item_dict()
        self.state_mgr.reentering = False
        self.state_mgr.add_item_index = 0
        self.ui.enter_add_item_frame()

        if entered_barcode is not None:
            self.on_add_item_enter(None, entered_barcode)

    def process_sale(
        self, event=None, entered_barcode=None, decimal_amount=Decimal("1")
    ):
        """Check for existing barcode. If so, add item to running list of sold items
        and display info to cashier. Else, prompt user to enter the item."""
        if entered_barcode is not None:
            total, item_name, item_price, taxable = self.state_mgr.trans.sell_item(
                entered_barcode, decimal_amount
            )
        else:
            barcode = self.ui.invisible_entry_var.get()
            if barcode == "":
                return "break"
            if len(barcode.lstrip("0")) != (len(barcode)):
                invf.update_barcode(self.state_mgr, barcode)
            total, item_name, item_price, taxable = self.state_mgr.trans.sell_item(
                barcode, decimal_amount
            )
        if total == "item_not_found":
            self.ui.register_add_item_prompt_frame.tkraise()
        else:
            self.finish_process_sale(total)

    def finish_process_sale(self, total=None, *kwargs):

        self.ui.invisible_entry.delete(0, tk.END)
        total = total.quantize(Decimal("0.01"))
        self.ui.update_entry(
            self.ui.balance_entry, f'${total.quantize(Decimal("0.01"))}'
        )
        if self.seg:
            self.print_to_sevenseg(total)
        self.ui.sale_items_listbox.delete(0, tk.END)
        for key in self.state_mgr.trans.items_list.keys():
            if len(self.state_mgr.trans.items_list[key]["item_name"]) > 13:
                sale_info = (
                    f"{self.state_mgr.trans.items_list[key]['item_name'][:13]}... "
                    f"({str(self.state_mgr.trans.items_list[key]['quantity_sold'])}) "
                    f"${(self.state_mgr.trans.items_list[key]['item_price']):.2f} "
                    f"{'TX' if self.state_mgr.trans.items_list[key]['item_taxable'] == 1 else 'NT'}"
                )
            else:
                sale_info = (
                    f"{self.state_mgr.trans.items_list[key]['item_name']} "
                    f"({str(self.state_mgr.trans.items_list[key]['quantity_sold'])}) "
                    f"${(self.state_mgr.trans.items_list[key]['item_price']):.2f} "
                    f"{'TX' if self.state_mgr.trans.items_list[key]['item_taxable'] == 1 else 'NT'}"
                )

            self.ui.sale_items_listbox.insert(tk.END, sale_info)
        self.ui.sale_items_listbox.yview_moveto(1.0)
        self.ui.update_entry(self.ui.user_entry, "$0.00")

    def on_yes_no_var_update(self, *kwargs):
        yes_no_answer = self.state_mgr.register_yes_no_var.get()
        if yes_no_answer == "yes":
            self.state_mgr.coming_from_register = True
            self.enter_add_item_frame(self.ui.invisible_entry_var.get())
            return
        elif yes_no_answer == "no":
            self.ui.register_frame.tkraise()
            self.ui.invisible_entry.delete(0, tk.END)
            self.ui.invisible_entry.focus_set()
            return

    def print_transaction_info(self, text_widget, transaction_info):
        """Print item info for transaction into a text widget. (Currently formatted for
        4 height)."""
        text_widget.delete("1.0", "end")
        text_widget.insert("end", f"Trans ID: {str(transaction_info[0])} |\t")
        text_widget.insert("end", f"Total: ${transaction_info[4]:.2f}\n")
        text_widget.insert("end", f"Items Sold: {str(transaction_info[5])} |\t")
        text_widget.insert("end", f"Cash: ${transaction_info[8]:.2f}\n")
        text_widget.insert("end", f"CC: ${transaction_info[9]:.2f} |\t")
        text_widget.insert("end", f"Date: {transaction_info[6]}\n")
        text_widget.insert("end", f"Time: {transaction_info[7]} | ")
        text_widget.insert(
            "end", "Voided?: Yes" if transaction_info[10] == 1 else "Voided?: No"
        )

    def on_cash(self, event=None):
        """Handles when cashier attempts to finalize transaction using cash."""
        if self.state_mgr.trans.total == 0:
            messagebox.showerror("ERROR", "No Items Entered!")
            self.clear()
            return "break"

        pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
        pygame.mixer.music.play()

        entered_amount = self.ui.invisible_entry_var.get().strip()
        self.ui.invisible_entry.delete(0, tk.END)
        length = len(entered_amount)

        balance = (
            self.state_mgr.trans.total
            - self.state_mgr.trans.cash_used
            - self.state_mgr.trans.cc_used
        )
        amount_given = 0.0

        if length == 0:
            self.state_mgr.trans.cash_tendered += balance
            self.state_mgr.trans.cash_used += balance
            self.ui.update_entry(self.ui.user_entry, "C: $0.00")
            # self.ui.update_entry(self.ui.balance_entry, f"${self.state_mgr.trans.total:.2f}")
            self.complete_sale()
            return "break"
        elif length == 1:
            amount_given = Decimal(f"0.0{entered_amount}")
        elif length == 2:
            amount_given = Decimal(f"0.{entered_amount}")
        elif length >= 3:
            amount_given = Decimal(
                f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}"
            )

        display_string = ""
        complete = False

        if amount_given == balance:
            self.state_mgr.trans.cash_tendered += amount_given
            self.state_mgr.trans.cash_used += amount_given
            display_string = "C: $0.00"
            complete = True
        elif amount_given > balance:
            self.state_mgr.trans.cash_tendered += amount_given
            self.state_mgr.trans.cash_used += balance
            display_string = f"C: ${abs(balance-amount_given):.2f}"
            complete = True
        elif amount_given < balance:
            self.state_mgr.trans.cash_tendered += amount_given
            self.state_mgr.trans.cash_used += amount_given
            display_string = f"B: ${(balance - amount_given):.2f}"

        self.ui.update_entry(self.ui.user_entry, display_string)

        if complete:
            # self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_mgr.trans.total:.2f}")
            self.complete_sale()

    def on_cc(self, event=None):
        """Handles when cashier attempts to finalize transaction with cc."""
        if self.state_mgr.trans.total == 0:
            self.ui.popup_description_label_var.set("No Items Entered!")
            self.ui.popup_frame.tkraise()
            self.clear()
            return "break"

        pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
        pygame.mixer.music.play()

        entered_amount = self.ui.invisible_entry_var.get().strip()
        entered_amount = entered_amount[:-1]
        self.ui.invisible_entry.delete(0, tk.END)
        length = len(entered_amount)

        balance = (
            self.state_mgr.trans.total
            - self.state_mgr.trans.cash_used
            - self.state_mgr.trans.cc_used
        )
        amount_given = 0.0

        if length == 0:
            self.state_mgr.trans.cc_used += balance
            self.state_mgr.trans.cc_tendered += balance
            self.ui.update_entry(self.ui.user_entry, "C: $0.00")
            # self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_mgr.trans.total:.2f}")
            self.complete_sale()
            return "break"
        elif length == 1:
            amount_given = Decimal(f"0.0{entered_amount}")
        elif length == 2:
            amount_given = Decimal(f"0.{entered_amount}")
        elif length >= 3:
            amount_given = Decimal(
                f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}"
            )

        if amount_given > balance:
            self.ui.popup_description_label_var.set(
                "CC Amount Entered\nExceeds Balance!"
            )
            self.ui.popup_frame.tkraise()
            self.ui.update_entry(self.ui.user_entry, f"B: ${balance}")
            return "break"

        display_string = ""
        complete = False

        if amount_given == balance:
            self.state_mgr.trans.cc_tendered += amount_given
            self.state_mgr.trans.cc_used += amount_given
            display_string = "C: $0.00"
            complete = True
        elif amount_given < balance:
            self.state_mgr.trans.cc_tendered += amount_given
            self.state_mgr.trans.cc_used += amount_given
            display_string = "B: $" + f"{(balance - amount_given):.2f}"

        self.ui.update_entry(self.ui.user_entry, display_string)

        if complete:
            # self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_mgr.trans.total:.2f}")
            self.complete_sale()

    def complete_sale(self, event=None):
        """Complete transaction, open cash drawer, print receipt, and reset register environment."""
        if self.state_mgr.trans.cash_used != 0:
            threading.Thread(target=self.printer.kick_drawer).start()
        if self.state_mgr.used_coupon:
            self.state_mgr.trans.complete_transaction(
                [self.state_mgr.coupon, self.state_mgr.coupon_reason]
            )
        else:
            self.state_mgr.trans.complete_transaction()
        # self.state_mgr.cursor.execute('''SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
        # results = self.state_mgr.cursor.fetchall()
        # sale_info = results[0]
        # self.state_mgr.cursor.execute('''SELECT * FROM sale_items WHERE sale_id = ?''', (sale_info[0], ))
        # sale_items_list = self.state_mgr.cursor.fetchall()
        # self.printer.print_receipt("sale", sale_items_list, sale_info, self.state_mgr.trans.cash_tendered, self.state_mgr.trans.cc_tendered)
        self.ui.sale_items_listbox.delete(0, tk.END)
        self.state_mgr.new_transaction()
        if self.seg:
            self.print_to_sevenseg("0.00")

    def print_to_sevenseg(self, to_print):
        self.seg.text = f"{' ' * (9 - len(str(to_print)))}{to_print}"

    def complete_decrement(self):
        self.state_mgr.trans.complete_as_decrement()
        self.enter_register_frame()

    def clear(self, event=None):
        """Clear number user entered in register."""
        pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
        pygame.mixer.music.play()
        self.ui.invisible_entry.delete(0, tk.END)
        self.ui.update_entry(self.ui.user_entry, "$0.00")

    def cancel_sale(self, event=None):
        self.ui.invisible_entry.delete(0, tk.END)
        self.ui.update_entry(self.ui.user_entry, "$0.00")
        if self.seg:
            self.print_to_sevenseg("0.00")
        self.state_mgr.sale_items_listbox_var.set(-1)
        self.on_sale_items_listbox_var()
        if self.state_mgr.trans.cash_used != 0 or self.state_mgr.trans.cc_used != 0:
            return
        selected_index = self.ui.sale_items_listbox.curselection()
        if selected_index == ():
            self.enter_register_frame()
        else:
            index = selected_index[0]
            self.remove_items_from_sale(index, True)
            self.ui.update_entry(
                self.ui.balance_entry, f"${abs(self.state_mgr.trans.total):.2f}"
            )
            if self.seg:
                self.print_to_sevenseg(f"{abs(self.state_mgr.trans.total):.2f}")
            self.ui.sale_items_listbox.delete(0, tk.END)
            for key in self.state_mgr.trans.items_list.keys():
                if len(self.state_mgr.trans.items_list[key]["item_name"]) > 13:
                    sale_info = (
                        f"{self.state_mgr.trans.items_list[key]['item_name'][:13]}... "
                        f"({self.state_mgr.trans.items_list[key]['quantity_sold']}) "
                        f"${self.state_mgr.trans.items_list[key]['item_price']} "
                        f"{'TX' if self.state_mgr.trans.items_list[key]['item_taxable'] == 1 else 'NT'}"
                    )
                else:
                    sale_info = (
                        f"{self.state_mgr.trans.items_list[key]['item_name']} "
                        f"({self.state_mgr.trans.items_list[key]['quantity_sold']}) "
                        f"${self.state_mgr.trans.items_list[key]['item_price']} "
                        f"{'TX' if self.state_mgr.trans.items_list[key]['item_taxable']== 1 else 'NT'}"
                    )
                self.ui.sale_items_listbox.insert(tk.END, sale_info)
            self.ui.sale_items_listbox.yview_moveto(1.0)

    def remove_items_from_sale(self, index, canceling):
        quantity_sold = self.state_mgr.trans.items_list[
            self.state_mgr.trans.listbox_indices[index]
        ]["quantity_sold"]
        item_price = self.state_mgr.trans.items_list[
            self.state_mgr.trans.listbox_indices[index]
        ]["item_price"]
        value_sold = quantity_sold * item_price
        if (
            self.state_mgr.trans.items_list[
                self.state_mgr.trans.listbox_indices[index]
            ]["item_taxable"]
            == 1
        ):
            self.state_mgr.trans.pretax -= value_sold
            self.state_mgr.trans.tax -= (
                Decimal(self.config.data["tax_amount"]) * value_sold
            )
            self.state_mgr.trans.total -= (
                Decimal("1.0") + Decimal(self.config.data["tax_amount"])
            ) * value_sold
            self.state_mgr.trans.items_sold -= Decimal(str(quantity_sold))
        else:
            self.state_mgr.trans.nontax -= value_sold
            self.state_mgr.trans.total -= value_sold
            self.state_mgr.trans.items_sold -= quantity_sold

        if canceling:
            del self.state_mgr.trans.items_list[
                self.state_mgr.trans.listbox_indices[index]
            ]
            del self.state_mgr.trans.listbox_indices[index]

    def on_sale_items_listbox_select(self):
        selected_index = self.ui.sale_items_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
        else:
            return
        if self.state_mgr.sale_items_listbox_var.get() == -1:
            self.state_mgr.sale_items_listbox_var.set(selected_index)
        elif self.state_mgr.sale_items_listbox_var.get() == selected_index:
            self.state_mgr.sale_items_listbox_var.set(-1)
            self.ui.sale_items_listbox.selection_clear(0, tk.END)

    def on_sale_items_listbox_var(self, *args):
        if self.state_mgr.sale_items_listbox_var.get() != -1:
            self.ui.invisible_entry.unbind("<Return>")
            self.ui.invisible_entry.bind(
                "<Return>", lambda event: self.process_sale_multiples()
            )
        else:
            self.ui.invisible_entry.unbind("<Return>")
            self.ui.invisible_entry.bind("<Return>", self.process_sale)

    def process_sale_multiples(self, event=None):
        self.remove_items_from_sale(self.state_mgr.sale_items_listbox_var.get(), False)
        self.state_mgr.trans.items_list[
            self.state_mgr.trans.listbox_indices[
                self.state_mgr.sale_items_listbox_var.get()
            ]
        ]["quantity_sold"] = 0
        self.process_sale(
            None,
            self.state_mgr.trans.listbox_indices[
                self.state_mgr.sale_items_listbox_var.get()
            ],
            Decimal(self.ui.invisible_entry_var.get()),
        )
        self.ui.invisible_entry.delete(0, tk.END)
        self.ui.update_entry(self.ui.user_entry, "$0.00")
        self.state_mgr.sale_items_listbox_var.set(-1)

    def no_sale(self, event=None):

        self.printer.kick_drawer()
        self.ui.invisible_entry.delete(0, tk.END)
        # self.printer.print_no_sale_receipt()
        self.state_mgr.cursor.execute(
            "UPDATE no_sale SET times_pressed = times_pressed + 1 WHERE date = ?",
            (datetime.today().strftime("%Y-%m-%d"),),
        )
        self.state_mgr.conn.commit()
        return "break"

    def make_seasonal_sale(self):

        if self.state_mgr.trans.total == 0:
            self.ui.popup_description_label_var.set("No Items Entered!")
            self.ui.popup_frame.tkraise()
            return

        self.ui.seasonal_id_entry_frame.tkraise()
        self.ui.seasonal_id_entry.focus_set()
        while True:
            root.wait_variable(self.state_mgr.seasonal_id_var)
            self.state_mgr.cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM seasonals WHERE seasonal_id = ?) LIMIT 1",
                (self.state_mgr.seasonal_id_var.get(),),
            )
            results = self.state_mgr.cursor.fetchone()[0]
            if results:
                break
            else:
                self.ui.popup_description_label_var.set(
                    "Invalid Seasonal ID\nPlease try Again"
                )
                self.ui.popup_frame.tkraise()
        self.ui.seasonal_id_entry_frame.lower()
        self.state_mgr.trans.complete_transaction(self.state_mgr.seasonal_id_var.get())
        self.ui.bind_invisible_entry_keys()
        self.enter_register_frame()

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
                self.ui.show_frame("add_name", reentering=True)
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
                print("A")
                invf.yes_register(self.state_mgr)
                self.process_sale(None, self.state_mgr.add_item_dict.barcode)
                self.state_mgr.coming_from_register = False
                self.ui.register_frame.tkraise()
                self.ui.invisible_entry.focus_set()
            elif self.state_mgr.updating_existing_item:
                print("B")
                invf.yes_existing(self.state_mgr)
                self.enter_add_item_frame()
            elif not self.state_mgr.coming_from_register:
                print("C")
                invf.yes_not_register(self.state_mgr)
                self.enter_add_item_frame()
        elif yes_no_answer == "no":
            print("D")
            self.ui.show_frame("reenter")

    def process_return(self, event=None):
        """Put register into 'return mode'. User can ring up items like a
        normal sale, but items will be returned instead."""
        self.enter_register_frame()
        self.ui.register_label.config(text="Mode: Return", fg="red")
        self.state_mgr.trans.returning = True
        self.ui.unbind_invisible_entry_keys()
        self.ui.invisible_entry.bind(
            "<KeyRelease-KP_Enter>", lambda event: self.state_mgr.return_var.set("cash")
        )
        self.ui.invisible_entry.bind(
            "<KeyRelease-KP_Add>", lambda event: self.state_mgr.return_var.set("cc")
        )
        self.ui.invisible_entry.bind(
            "<KeyRelease-Escape>", lambda event: self.enter_register_frame()
        )

    def finish_return(self, *args):

        button_pressed = self.state_mgr.return_var.get()
        self.state_mgr.trans.nontax *= -1
        self.state_mgr.trans.pretax *= -1
        self.state_mgr.trans.tax *= -1
        self.state_mgr.trans.total *= -1

        if button_pressed == "cash":
            self.state_mgr.trans.cash_used = self.state_mgr.trans.total
        elif button_pressed == "cc":
            self.state_mgr.trans.cc_used = self.state_mgr.trans.total

        self.state_mgr.trans.complete_transaction()
        self.state_mgr.cursor.execute(
            """SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)"""
        )
        results = self.state_mgr.cursor.fetchall()
        row = results[0]
        self.state_mgr.cursor.execute(
            """SELECT * FROM sale_items WHERE sale_id = ?""", (row[0],)
        )
        item_results = self.state_mgr.cursor.fetchall()
        self.printer.print_receipt("return", item_results, dict(row))
        self.ui.bind_invisible_entry_keys()
        self.enter_register_frame()

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
    register.enter_register_frame()

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
