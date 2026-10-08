import threading
import tkinter as tk
from decimal import Decimal, InvalidOperation
from pathlib import Path
from tkinter import messagebox

import pygame

from ..inventory_functions import update_barcode
from .base_frame import BaseFrame


class RegisterFrame(BaseFrame):

    def build_widgets(self):

        self.config(bg="black")

        self.invisible_entry_var = tk.StringVar()

        self.sale_items_listbox_var = tk.IntVar(self, -1)
        self.sale_items_listbox_var.trace_add("write", self.on_sale_items_listbox_var)

        self.return_var = tk.StringVar(self)
        self.return_var.trace_add("write", self.finish_return)

        self.info_frame = tk.Frame(self, bg="black")
        self.info_frame.grid(column=1, row=0, sticky="nsew")
        self.info_frame.columnconfigure(0, weight=1)
        self.info_frame.columnconfigure(1, weight=1)

        self.label = tk.Label(
            self.info_frame,
            font=("Arial", 30),
            text="Mode: Register",
            fg="#68FF00",
            bg="black",
        )
        self.label.grid(column=0, row=0, sticky="sw", pady=5)

        self.balance_entry = tk.Entry(
            self.info_frame,
            font=("Arial", 91),
            bg="black",
            fg="#68FF00",
            justify="right",
            width=9,
        )
        self.balance_entry.insert(tk.END, "$0.00")
        self.balance_entry.grid(column=1, row=0, sticky="e", padx=2)
        self.balance_entry.bind("<FocusIn>", self.return_invisible_entry_focus)

        self.invisible_entry = tk.Entry(self, textvariable=self.invisible_entry_var)
        self.invisible_entry.place(x=-100, y=-100)
        self.invisible_entry.bind("<Return>", self.process_sale)
        self.bind_invisible_entry_keys()

        self.user_entry = tk.Entry(
            self.info_frame,
            font=("Arial", 35),
            width=10,
            bg="black",
            fg="#68FF00",
        )
        self.user_entry.insert(tk.END, "$0.00")
        self.user_entry.grid(column=0, row=0, sticky="nw")
        self.user_entry.bind("<FocusIn>", self.return_invisible_entry_focus)

        self.sale_items_listbox = tk.Listbox(
            self,
            width=34,
            bg="black",
            height=8,
            font=("Courier New", 37),
            fg="white",
        )
        self.sale_items_listbox.grid(column=1, row=2, sticky="nsw")
        self.sale_items_listbox.bind("<FocusIn>", self.return_invisible_entry_focus)
        self.sale_items_listbox.bind(
            "<<ListboxSelect>>", lambda event: self.on_sale_items_listbox_select()
        )
        self.sale_items_scrollbar = tk.Scrollbar(
            self, bg="white", orient=tk.VERTICAL, width=40
        )
        self.sale_items_scrollbar.grid(column=1, row=2, sticky="nse")
        self.sale_items_listbox.config(yscrollcommand=self.sale_items_scrollbar.set)
        self.sale_items_scrollbar.config(command=self.sale_items_listbox.yview)

    def return_invisible_entry_focus(self, event):
        """Bound to FocusIn on register widgets. Returns focus to invisible
        entry, and returns 'break' to stop propagating event."""
        self.invisible_entry.focus_set()
        return "break"

    def on_show(self, resetting=False, first_time=False):
        if resetting:
            self.enter_register_frame()
        else:
            self.invisible_entry.delete(0, tk.END)
            self.update_entry(self.user_entry, "$0.00")
            self.invisible_entry.focus_set()

        if first_time:
            self.columnconfigure(0, weight=1)
            self.columnconfigure(1, weight=0)
            self.columnconfigure(2, weight=1)

    def number_pressed(self):

        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()

        string = self.invisible_entry_var.get().strip()

        if self.sale_items_listbox_var.get() != -1:
            self.update_entry(self.user_entry, string)
        else:
            while len(string) < 3:
                string = "0" + string
            self.update_entry(self.user_entry, f"${string[0:-2]}.{string[-2:]}")

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
        self.invisible_entry.bind("<KeyRelease-BackSpace>", self.clear)
        self.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.on_cash())
        self.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: self.on_cc())
        self.invisible_entry.bind(
            "<KeyRelease-KP_Multiply>", lambda event: self.wm.show_frame("main_menu")
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Divide>", lambda event: self.cancel_sale()
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Subtract>", lambda event: self.no_sale()
        )
        self.invisible_entry.bind(
            "<KeyRelease-backslash>", lambda event: self.controller.complete_decrement()
        )
        self.invisible_entry.unbind("<KeyRelease-Escape>")

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
            barcode = self.invisible_entry_var.get()
            if barcode == "":
                return "break"
            if len(barcode.lstrip("0")) != (len(barcode)):
                update_barcode(self.state_mgr, barcode)
            total, item_name, item_price, taxable = self.state_mgr.trans.sell_item(
                barcode, decimal_amount
            )
        if total == "item_not_found":
            self.wm.show_frame("register_add_item_prompt")
        else:
            self.finish_process_sale(total)

    def finish_process_sale(self, total: Decimal, *kwargs):

        self.invisible_entry.delete(0, tk.END)
        total = total.quantize(Decimal("0.01"))
        self.update_entry(self.balance_entry, f'${total.quantize(Decimal("0.01"))}')
        if self.controller.seg:
            self.controller.print_to_sevenseg(total)
        self.sale_items_listbox.delete(0, tk.END)
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

            self.sale_items_listbox.insert(tk.END, sale_info)
        self.sale_items_listbox.yview_moveto(1.0)
        self.update_entry(self.user_entry, "$0.00")

    def update_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def on_sale_items_listbox_select(self):
        selected_index = self.sale_items_listbox.curselection()
        if selected_index:
            selected_index = selected_index[0]
        else:
            return
        if self.sale_items_listbox_var.get() == -1:
            self.sale_items_listbox_var.set(selected_index)
        elif self.sale_items_listbox_var.get() == selected_index:
            self.sale_items_listbox_var.set(-1)
            self.sale_items_listbox.selection_clear(0, tk.END)

    def on_sale_items_listbox_var(self, *args):
        if self.sale_items_listbox_var.get() != -1:
            self.invisible_entry.unbind("<Return>")
            self.invisible_entry.bind(
                "<Return>", lambda event: self.process_sale_multiples()
            )
        else:
            self.invisible_entry.unbind("<Return>")
            self.invisible_entry.bind("<Return>", self.process_sale)
            self.sale_items_listbox.selection_clear(0, tk.END)

    def process_sale_multiples(self, event=None):
        try:
            quantity = Decimal(self.invisible_entry_var.get())
            self.remove_items_from_sale(self.sale_items_listbox_var.get(), False)
            self.state_mgr.trans.items_list[
                self.state_mgr.trans.listbox_indices[self.sale_items_listbox_var.get()]
            ]["quantity_sold"] = 0
            self.process_sale(
                None,
                self.state_mgr.trans.listbox_indices[self.sale_items_listbox_var.get()],
                quantity,
            )
        except InvalidOperation as e:
            print(f"{e} ERROR in register_frame.process_sale_multiples")
        finally:
            self.invisible_entry.delete(0, tk.END)
            self.update_entry(self.user_entry, "$0.00")
            self.sale_items_listbox_var.set(-1)

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
                Decimal(self.controller.config.data["tax_amount"]) * value_sold
            )
            self.state_mgr.trans.total -= (
                Decimal("1.0") + Decimal(self.controller.config.data["tax_amount"])
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

    def no_sale(self, event=None):
        self.controller.printer.kick_drawer()
        self.invisible_entry.delete(0, tk.END)
        self.state_mgr.update_no_sale()
        return "break"

    def cancel_sale(self, event=None):
        self.invisible_entry.delete(0, tk.END)
        self.update_entry(self.user_entry, "$0.00")
        if self.controller.seg:
            self.controller.print_to_sevenseg("0.00")
        if self.state_mgr.trans.cash_used != 0 or self.state_mgr.trans.cc_used != 0:
            return
        selected_index = self.sale_items_listbox_var.get()
        self.sale_items_listbox_var.set(-1)
        self.on_sale_items_listbox_var()
        if selected_index == -1:
            self.enter_register_frame()
        else:
            self.remove_items_from_sale(selected_index, True)
            self.update_entry(
                self.balance_entry, f"${abs(self.state_mgr.trans.total):.2f}"
            )
            if self.controller.seg:
                self.controller.print_to_sevenseg(
                    f"{abs(self.state_mgr.trans.total):.2f}"
                )
            self.sale_items_listbox.delete(0, tk.END)
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
                self.sale_items_listbox.insert(tk.END, sale_info)
            self.sale_items_listbox.yview_moveto(1.0)

    """def make_seasonal_sale(self):

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
        self.enter_register_frame()"""

    def clear(self, event=None):
        """Clear number user entered in register."""
        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()
        self.invisible_entry.delete(0, tk.END)
        self.update_entry(self.user_entry, "$0.00")

    def complete_sale(self, event=None):
        """Complete transaction, open cash drawer, print receipt, and reset register environment."""
        if self.state_mgr.trans.cash_used != 0:
            threading.Thread(target=self.controller.printer.kick_drawer).start()
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
        self.sale_items_listbox.delete(0, tk.END)
        self.state_mgr.new_transaction()
        if self.controller.seg:
            self.controller.print_to_sevenseg("0.00")

    def on_cash(self, event=None):
        """Handles when cashier attempts to finalize transaction using cash."""
        if self.state_mgr.trans.total == 0:
            messagebox.showerror("ERROR", "No Items Entered!")
            self.clear()
            return "break"

        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()

        entered_amount = self.invisible_entry_var.get().strip()
        self.invisible_entry.delete(0, tk.END)
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
            self.update_entry(self.user_entry, "C: $0.00")
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

        self.update_entry(self.user_entry, display_string)

        if complete:
            self.complete_sale()

    def on_cc(self, event=None):
        """Handles when cashier attempts to finalize transaction with cc."""
        if self.state_mgr.trans.total == 0:
            self.wm.popup_description_label_var.set("No Items Entered!")
            self.wm.popup_frame.tkraise()
            self.clear()
            return "break"

        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()

        entered_amount = self.invisible_entry_var.get().strip()
        entered_amount = entered_amount[:-1]
        self.invisible_entry.delete(0, tk.END)
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
            self.update_entry(self.user_entry, "C: $0.00")
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
            self.wm.popup_description_label_var.set(
                "CC Amount Entered\nExceeds Balance!"
            )
            self.wm.popup_frame.tkraise()
            self.update_entry(self.user_entry, f"B: ${balance}")
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

        self.update_entry(self.user_entry, display_string)

        if complete:
            self.complete_sale()

    def enter_register_frame(self, event=None):
        """Reset register environment to defaults."""
        pygame.mixer.music.load(Path(__file__).parent / "../short-beep.mp3")
        pygame.mixer.music.play()
        self.state_mgr.new_transaction()
        self.invisible_entry.delete(0, tk.END)
        self.sale_items_listbox.delete(0, tk.END)
        self.update_entry(self.user_entry, "$0.00")
        self.update_entry(self.balance_entry, "$0.00")
        self.label.config(text="Mode: Register", fg="#68FF00")
        self.bind_invisible_entry_keys()
        self.invisible_entry.focus_force()
        if self.controller.seg:
            self.controller.print_to_sevenseg("0.00")
        return "break"

    def complete_decrement(self):
        if self.state_mgr.trans.complete_as_decrement():
            self.enter_register_frame()
        else:
            self.wm.popup_description_label_var.set(
                "Cannot decrement inventory,\nnothing entered!"
            )
            self.wm.popup_frame.tkraise()

    def process_return(self, event=None):
        """Put register into 'return mode'. User can ring up items like a
        normal sale, but items will be returned instead."""
        self.enter_register_frame()
        self.label.config(text="Mode: Return", fg="red")
        self.state_mgr.trans.returning = True
        self.unbind_invisible_entry_keys()
        self.invisible_entry.bind(
            "<KeyRelease-KP_Enter>", lambda event: self.state_mgr.return_var.set("cash")
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Add>", lambda event: self.state_mgr.return_var.set("cc")
        )
        self.invisible_entry.bind(
            "<KeyRelease-Escape>", lambda event: self.enter_register_frame()
        )
        self.invisible_entry.bind(
            "<KeyRelease-KP_Divide>", lambda event: self.cancel_sale()
        )
        self.wm.show_frame("register")

    def finish_return(self, *args):

        button_pressed = self.return_var.get()
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
        self.controller.printer.print_receipt("return", item_results, dict(row))
        self.bind_invisible_entry_keys()
        self.enter_register_frame()
