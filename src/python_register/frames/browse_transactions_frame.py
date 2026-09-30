import sqlite3
import tkinter as tk

from ..add_item_data import Dec4
from .base_frame import BaseFrame


class BrowseTransactionsFrame(BaseFrame):

    def build_widgets(self):

        self.browse_index = tk.IntVar()
        self.browse_index.trace_add("write", self.browse_transactions)

        self.browse_mode = tk.StringVar()

        self.label = tk.Label(self, text="Browsing Transactions", font=("Arial", 40))
        self.label.grid(column=1, row=0, sticky="ew", pady=10)

        self.prev_button = tk.Button(
            self,
            text="<<",
            font=("Arial", 55),
            command=lambda: self.browse_index.set(self.browse_index.get() - 1),
        )
        self.prev_button.grid(column=0, row=1, sticky="nsw")

        self.next_button = tk.Button(
            self,
            text=">>",
            font=("Arial", 55),
            command=lambda: self.browse_index.set(self.browse_index.get() + 1),
        )
        self.next_button.grid(column=2, row=1, sticky="nse")

        self.text = tk.Text(self, width=28, height=4, font=("Bebas Neue", 37))
        self.text.tag_configure("bold", font=("Courier New", 40, "bold"))
        self.text.grid(column=1, row=1, sticky="ew", pady=10)
        self.text.bind("<FocusIn>", self.return_browse_entry_focus)

        self.browse_entry_frame = tk.Frame(self)
        self.browse_entry_frame.grid(column=1, row=2, sticky="ew", pady=30)
        self.browse_entry_frame.columnconfigure(1, weight=1)
        self.browse_entry_frame.columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            self.browse_entry_frame,
            font=("Arial", 35),
            width=10,
            validate="key",
            vcmd=self.wm.vcmd,
        )
        self.entry.bind(
            "<Return>", lambda event: self.browse_index.set(int(self.entry.get()))
        )
        self.entry.grid(column=0, row=0, sticky="nsew")

        self.go_button = tk.Button(
            self.browse_entry_frame,
            font=("Arial", 40),
            text="-> GO",
            command=lambda: self.browse_index.set(int(self.entry.get())),
        )
        self.go_button.grid(column=1, row=0, sticky="nsew")

        browse_back_quit_frame = tk.Frame(self)
        browse_back_quit_frame.columnconfigure(0, weight=1, uniform="equal")
        browse_back_quit_frame.columnconfigure(1, weight=1, uniform="equal")
        browse_back_quit_frame.grid(column=1, row=3, sticky="nsew")

        self.back_button = tk.Button(
            browse_back_quit_frame,
            text="Back",
            font=("Arial", 50),
            command=lambda: self.wm.show_frame("main_menu"),
        )
        self.back_button.grid(column=0, row=0, sticky="nsew")

        self.print_button = tk.Button(
            browse_back_quit_frame,
            text="Print",
            font=("Arial", 50),
            command=lambda: self.browse_print_receipt(),
        )

        self.print_button.grid(column=1, row=0, sticky="nsew")

        self.void_print_button = tk.Button(
            browse_back_quit_frame,
            text="Print",
            font=("Arial", 50),
            command=lambda: self.void_print_pressed(),
        )

    def on_show(self, browse_mode):
        self.max_browse_index = self.state_mgr.get_max_sale_id()
        self.browse_mode.set(browse_mode)
        enter = self.enter_browse_transactions_frame()
        if enter:
            pass
        else:
            self.wm.return_to_register()
            self.wm.popup_description_label_var.set("No Transactions Yet!")
            self.wm.popup_frame.tkraise()

    def return_browse_entry_focus(self, event):
        """Bound to FocusIn on browse items textbox. Returns focus to browse_entry,
        and returns 'break' to stop propagating event."""
        self.entry.focus_set()
        return "break"

    def setup_void_widgets(self):
        self.label.config(text="Void Transaction")
        self.print_button.grid_forget()
        self.void_print_button.grid(column=1, row=0, sticky="nsew")
        self.entry.focus_set()

    def remove_void_widgets(self):
        self.label.config(text="Browsing Transactions")
        self.void_print_button.grid_forget()
        self.print_button.grid(column=1, row=0, sticky="nsew")

    def enter_browse_transactions_frame(self) -> bool:
        """Setup necessary information for browse transaction frame. If voiding,
        set up those widgets as well. Returns boolean dependant on whether or not
        there are transactions in the database."""
        results = self.controller.state_mgr.cursor.execute(
            """SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)"""
        ).fetchone()
        if results == None:
            return False
        else:
            self.browse_index.set(results["sale_id"])
            transaction_string = self.print_transaction_info(results)
            self.text.delete("1.0", "end")
            self.text.insert("end", transaction_string)
            self.label.config(text="Browsing Transactions")
            if self.browse_mode.get() == "void":
                self.setup_void_widgets()
            self.entry.focus_set()
            return True
        """elif args[1] == 1:
            self.state_mgr.browsing_seasonals = True
            self.state_mgr.cursor.execute(
                "SELECT * FROM seasonals WHERE seasonal_id = (SELECT MAX(seasonal_id) FROM seasonals)")
            results = self.state_mgr.cursor.fetchone()
            if not results:
                self.ui.browse_text.delete("1.0", "end")
                self.ui.browse_text.insert("end",  "No Seasonals Yet...")
            else:
                self.state_mgr.browse_index.set(results[0])
                self.ui.print_seasonal_info(results)

            self.ui.setup_browse_seasonals()"""

    def browse_transactions(self, *args):
        """Called when browse_index is written to. Move info to current index."""
        self.entry.delete(0, tk.END)
        if not self.controller.state_mgr.browsing_seasonals:
            self.controller.state_mgr.cursor.execute(
                """SELECT * FROM sales WHERE sale_id = ?""", (self.browse_index.get(),)
            )
        else:
            self.state_mgr.cursor.execute(
                """SELECT * FROM seasonals WHERE seasonal_id = ?""",
                (self.browse_index.get(),),
            )

        results = self.controller.state_mgr.cursor.fetchone()
        if not results:
            if self.browse_index.get() <= 0:
                self.browse_index.set(1)
                self.browse_transactions()
                return
            else:
                self.browse_index.set(self.state_mgr.get_max_sale_id())
                self.browse_transactions()
                return

        if not self.controller.state_mgr.browsing_seasonals:
            transaction_string = self.print_transaction_info(results)
            self.text.delete("1.0", "end")
            self.text.insert("end", transaction_string)
        else:
            self.wm.print_seasonal_info(results)

    def browse_print_receipt(self):
        self.controller.state_mgr.cursor.execute(
            """SELECT * FROM sales WHERE sale_id = ?""", (self.browse_index.get(),)
        )
        transaction_info = self.controller.state_mgr.cursor.fetchall()[0]
        self.controller.state_mgr.cursor.execute(
            """SELECT * FROM sale_items WHERE sale_id = ?""", (self.browse_index.get(),)
        )
        item_results = self.controller.state_mgr.cursor.fetchall()
        if transaction_info["is_voided"] == 1:
            self.controller.printer.print_receipt(
                "void", item_results, transaction_info
            )
        elif transaction_info["total"] < 0:
            self.controller.printer.print_receipt(
                "return", item_results, transaction_info
            )
        else:
            self.controller.printer.print_receipt(
                "sale", item_results, transaction_info
            )
        self.wm.return_to_register()

    def void_print_pressed(self):
        if self.controller.state_mgr.check_voided(self.browse_index.get()):
            self.wm.popup_description_label_var.set(
                "This transaction has already been voided!"
            )
            self.wm.popup_frame.tkraise()
        else:
            self.finish_void()

    def finish_void(self):
        try:
            self.controller.state_mgr.set_voided(self.browse_index.get())
            transaction_info = self.controller.state_mgr.get_sale_info(
                self.browse_index.get()
            )[0]
            items = self.controller.state_mgr.get_sale_items(self.browse_index.get())
            for item in items:
                current_quantity = self.controller.state_mgr.get_item_quantity_id(
                    item["item_id"]
                )
                self.controller.state_mgr.update_quantity(
                    current_quantity + Dec4(item["quantity"]), item["item_id"]
                )
            self.controller.state_mgr.conn.commit()
        except sqlite3.Error as e:
            self.controller.state_mgr.conn.rollback()
        finally:
            self.controller.printer.print_receipt("void", items, transaction_info)
            self.remove_void_widgets()
            self.wm.return_to_register()

    def print_transaction_info(self, transaction_info: sqlite3.Row) -> str:
        """Print item info for transaction into a text widget. (Currently formatted for
        4 height)."""
        transaction_string = ""
        transaction_string += f"Trans ID: {str(transaction_info["sale_id"])} |\t"
        transaction_string += f"Total: ${transaction_info["total"]:.2f}\n"
        transaction_string += (
            f"Items Sold: {str(transaction_info["num_items_sold"])} |\t"
        )
        transaction_string += f"Cash: ${transaction_info["cash_used"]:.2f}\n"
        transaction_string += f"CC: ${transaction_info["cc_used"]:.2f} |\t"
        transaction_string += f"Date: {transaction_info["sale_date"]}\n"
        transaction_string += f"Time: {transaction_info["sale_time"]} | "
        transaction_string += (
            "Voided?: Yes" if transaction_info["is_voided"] == 1 else "Voided?: No"
        )
        return transaction_string

    def print_seasonal_info(self, seasonal_info):
        self.text.delete("1.0", "end")
        # self.ui.text.insert("end", f"ID: {seasonal_info[0]}  |  Site: {seasonal_info[3]}\n")
        self.text.insert("end", "ID: ", "bold")
        self.text.insert("end", seasonal_info[0])
        self.text.insert("end", "|Site: ", "bold")
        self.text.insert("end", f"{seasonal_info[3]}")
        self.text.insert("end", "|Balance: ", "bold")
        self.text.insert("end", f"{seasonal_info[4]:.2f}\n")
        self.text.insert("end", "Name: ", "bold")
        self.text.insert("end", f"{seasonal_info[1]}\n{seasonal_info[2]}\n")
