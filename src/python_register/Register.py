import tkinter as tk
import sqlite3
from . import inventory_functions as invf
from . import widget_functions as wf
from .widget_manager import WidgetManager
from .state_manager import StateManager
from .printing_manager import Printer
from .config import Config
from datetime import datetime, timedelta
import time
import threading
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import subprocess
import sys
from pathlib import Path
from decimal import *

class Register:
	def __init__(self, root, db_connection = None):
		"""Initialize UI, StateManager, Config"""
		self.config = Config()
		self.state_manager = StateManager(root, self.config.data['database_name'], db_connection)
		self.state_manager.browse_index.trace_add('write', self.browse_transactions)
		self.state_manager.item_lookup_var.trace_add('write', self.on_item_lookup)
		self.state_manager.sale_items_listbox_var.trace_add('write', self.on_sale_items_listbox_var)
		self.state_manager.return_var.trace_add('write', self.finish_return)
		self.ui = WidgetManager(root, self)
		self.ui.price_var.trace_add('write', self.on_price_entry_update)
		self.ui.tax_var.trace_add('write', lambda *args: self.on_add_item_enter())
		self.state_manager.yes_no_var.trace_add('write', self.finish_entering)

		self.current_dir = Path(__file__).parent
		self.printer = Printer(self.state_manager, self.config)

		self.add_variables = [
			self.ui.barcode_var, self.ui.name_var, self.ui.price_var,
			self.ui.tax_var, self.ui.category_var,
			self.ui.subcategory_var, self.ui.vendor_var, self.ui.quantity_var]

	def on_price_entry_update(self, *args):
		self.number_pressed(self.ui.add_price_invisible_entry, self.ui.add_price_entry)
		return "break"

	def on_item_lookup(self, *args):

		pattern = f'%{self.ui.lookup_items_entry.get()}%'
		self.state_manager.cursor.execute("SELECT item_name FROM Inventory WHERE item_name LIKE ?", (pattern, ))
		self.ui.lookup_items_listbox.delete(0, tk.END)
		results = self.state_manager.cursor.fetchall()

		for item in results:
			self.ui.lookup_items_listbox.insert(tk.END, f'{item[0]}\n')


	def enter_add_item_lookup(self):
		self.ui.register_lookup_items_frame.tkraise()
		self.ui.lookup_items_entry.focus_set()
		self.state_manager.looking_up_add_item = True
	
	def confirm_lookup_items(self):
		index = self.ui.lookup_items_listbox.curselection()
		name = self.ui.lookup_items_listbox.get(index).strip()
		quantity = int(self.ui.lookup_items_quantity_spinbox.get())
		self.state_manager.cursor.execute('''SELECT item_barcode FROM inventory WHERE item_name = ?''', (name, ))
		barcode = self.state_manager.cursor.fetchall()[0][0]
		
		if self.state_manager.looking_up_add_item:
			self.ui.barcode_var.set(barcode)
			self.state_manager.looking_up_add_item = False
			self.on_add_item_enter()
		else:
			for i in range(0, quantity):
				self.process_sale(None, barcode)
			self.ui.register_frame.tkraise()
			self.ui.invisible_entry.focus_set()

	def perform_backup(self):
		time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		source_db = sqlite3.connect(self.current_dir / self.config.data['database_name'])
		dest_db = sqlite3.connect(f'/media/tbc/aed49e02-11c4-40be-b39f-9711a0b3c457/RegisterDatabaseBackup_{time}.db')
		source_db.backup(dest_db)
		source_db.close()
		dest_db.close()

	def backup_scheduler(self):
		while True:
			time.sleep(self.config.data['backup_interval'])
			self.perform_backup()

	def remove_old_backups(self, days):
		cutoff = time.time() - (days * 86400)
		for filename in os.listdir('/media/tbc/aed49e02-11c4-40be-b39f-9711a0b3c457/'):
			filepath = os.path.join('/media/tbc/aed49e02-11c4-40be-b39f-9711a0b3c457/', filename)
			if os.path.getmtime(filepath) < cutoff and not os.path.isdir(filepath):
				os.remove(filepath)
				

	def check_time_synced(self):

		try:
			results = subprocess.run(
				['timedatectl', 'status'], capture_output=True, text=True
			)
			return 'System clock synchronized: yes' in results.stdout
		except Exception:
			return False
         
	def enter_register_frame(self, event = None):
		"""Reset register environment to defaults, and raise the register frame."""
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()
		self.state_manager.new_transaction()
		self.ui.enter_register_frame()
		return "break"
	
	def enter_add_item_frame(self, entered_barcode=None):
		"""Reset the necessary add item process parameters to defaults. If a barcode
		is present, send it to the add item process."""
		self.state_manager.new_add_item_object()
		self.state_manager.reentering = False
		self.state_manager.add_item_index = 0
		self.ui.enter_add_item_frame()

		if entered_barcode is not None:
			self.on_add_item_enter(None, entered_barcode)
		else:
			self.ui.add_item_label.config(text="Please enter item's barcode:")

	def enter_browse_transactions_frame(self, *args):
		'''Setup necessary information for browse transaction frame. If voiding,
		set up those widgets as well. args[0] -> Flag for voiding or not, 
		args[1] -> Flag for seasonal transaction or not''' 
		if args[1] == 0:
			self.state_manager.cursor.execute(
				'''SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
			results = self.state_manager.cursor.fetchone()
			if not results:
				self.ui.popup_description_label.config(text="No Transactions Yet!")
				self.ui.popup_frame.tkraise()
				return False
			else:
				self.state_manager.browse_index.set(results[0])
				self.print_transaction_info(self.ui.browse_text, results)
				self.ui.browse_label.config(text="Browsing Transactions")
				if args[0] == 1:
					self.ui.setup_void_widgets()
				self.ui.browse_transactions_frame.tkraise()
				return True
		elif args[1] == 1:
			self.state_manager.browsing_seasonals = True
			self.state_manager.cursor.execute(
				'''SELECT * FROM seasonals WHERE seasonal_id = (SELECT MAX(seasonal_id) FROM seasonals)''')
			results = self.state_manager.cursor.fetchone()
			if not results:
				self.ui.browse_text.delete("1.0", "end")
				self.ui.browse_text.insert("end",  "No Seasonals Yet...")
			else:
				self.state_manager.browse_index.set(results[0])
				self.ui.print_seasonal_info(results)

			self.ui.setup_browse_seasonals()
				

	def browse_transactions(self, *args):
		'''Called when state_manager.browse_index is written to. Move info to current index.'''
		self.ui.browse_entry.delete(0, tk.END)
		if not self.state_manager.browsing_seasonals:
			self.state_manager.cursor.execute(
				'''SELECT * FROM sales WHERE sale_id = ?''', (self.state_manager.browse_index.get(), )
			)
		else:
			self.state_manager.cursor.execute(
				'''SELECT * FROM seasonals WHERE seasonal_id = ?''', (self.state_manager.browse_index.get(), )
			)
		results = self.state_manager.cursor.fetchone()
		if not results:
			if self.state_manager.browse_index.get() == 0:
				self.state_manager.browse_index.set(1)
				return
			else:
				self.state_manager.browse_index.set(self.state_manager.browse_index.get() - 1)
				return
		
		if not self.state_manager.browsing_seasonals:
			self.print_transaction_info(self.ui.browse_text, list(results))
		else:
			self.ui.print_seasonal_info(results)

	def browse_print_receipt(self):
		self.state_manager.cursor.execute('''SELECT * FROM sales WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
		transaction_info = list(self.state_manager.cursor.fetchall()[0])
		self.state_manager.cursor.execute('''SELECT * FROM sale_items WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
		item_results = self.state_manager.cursor.fetchall()
		if transaction_info[10] == 1:
			self.printer.print_receipt("void", item_results, transaction_info)
		elif transaction_info[4] < 0:
			self.printer.print_receipt("return", item_results, transaction_info)
		else:
			self.printer.print_receipt("sale", item_results, transaction_info)
		self.ui.register_frame.tkraise()

	def process_sale(self, event = None, entered_barcode=None, decimal_amount = Decimal('1')):
		"""Check for existing barcode. If so, add item to running list of sold items
		and display info to cashier. Else, prompt user to enter the item."""
		if entered_barcode is not None:
			total, item_name, item_price, taxable = self.state_manager.trans.sell_item(entered_barcode, decimal_amount)
		else:
			barcode = self.ui.invisible_entry_var.get()
			if barcode == "":
				return "break"
			if (len(barcode.lstrip('0')) != (len(barcode))):
				invf.update_barcode(self.state_manager, barcode)
			self.ui.invisible_entry.delete(0, tk.END)
			total, item_name, item_price, taxable  = self.state_manager.trans.sell_item(barcode, decimal_amount)
		if total == "item_not_found":
			self.ui.register_add_item_prompt_frame.tkraise()
			root.wait_variable(self.state_manager.yes_no_var)
			yes_no_answer = self.state_manager.yes_no_var.get()
			if yes_no_answer == "yes":
				self.state_manager.coming_from_register = True
				self.enter_add_item_frame(barcode)
				return
			elif yes_no_answer == "no":
				self.ui.register_frame.tkraise()
				return
		self.ui.update_entry(self.ui.balance_entry, f'${total.quantize(Decimal("0.01"))}')
		self.ui.sale_items_listbox.delete(0, tk.END)
		for item in self.state_manager.trans.items_list:
			if len(item[0]) > 13:
				sale_info = f"{item[0][:13]}... ({str(item[-2])}) ${(item[1]):.2f} {'TX' if item[2] == 1 else 'NT'}"
			else:
				sale_info = f"{item[0]} ({str(item[-2])}) ${(item[1]):.2f} {'TX' if item[2] == 1 else 'NT'}"
			
			self.ui.sale_items_listbox.insert(tk.END, sale_info)
		self.ui.sale_items_listbox.yview_moveto(1.0)
		self.ui.update_entry(self.ui.user_entry, "$0.00")
		
	def void_transaction(self):

		if not self.enter_browse_transactions_frame(1, 0):
			return
		
		while True:
			root.wait_variable(self.state_manager.void_var)
			self.state_manager.cursor.execute('''SELECT is_voided FROM sales WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
			voided = (self.state_manager.cursor.fetchall()[0])[0]
			if voided == 1:
				self.ui.popup_description_label.config(text="This transaction is already voided!")
				self.ui.popup_frame.tkraise()
				continue
			else:
				break

		try:
			self.state_manager.cursor.execute('''UPDATE sales SET is_voided = ? WHERE sale_id = ?''', (1, self.state_manager.browse_index.get()))
			self.state_manager.cursor.execute('''SELECT * FROM sales WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
			transaction_info = list(self.state_manager.cursor.fetchall()[0])
			self.state_manager.cursor.execute('''SELECT * FROM sale_items WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
			item_results = self.state_manager.cursor.fetchall()
			for i in range(len(item_results)):
				current_quantity = self.state_manager.cursor.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", (item_results[i][4], )).fetchall()[0]
				self.state_manager.cursor.execute('''UPDATE inventory SET item_quantity = ? WHERE item_barcode = ?''', (current_quantity + item_results[i][5], item_results[i][4]))
		except sqlite3.Error as e:
			self.ui.popup_description_label.config(text=f"{e}")
			self.ui.popup_frame.tkraise()
		finally:
			self.state_manager.conn.commit()
			self.printer.print_receipt("void", item_results, transaction_info)
			self.ui.remove_void_widgets()
			self.enter_register_frame()

	def print_transaction_info(
			self, text_widget, transaction_info):
			"""Print item info for transaction into a text widget. (Currently formatted for
			4 height)."""
			text_widget.delete("1.0", "end")
			text_widget.insert("end", f"Transaction ID: {str(transaction_info[0])} |\t")
			text_widget.insert("end", f"Total: ${transaction_info[4]:.2f}\n")
			text_widget.insert("end", f"Items Sold: {str(transaction_info[5])} |\t")
			text_widget.insert("end", f"Cash: ${transaction_info[8]:.2f}\n")
			text_widget.insert("end", f"CC: ${transaction_info[9]:.2f} |\t")
			text_widget.insert("end", f"Date: {transaction_info[6]}\n")
			text_widget.insert("end", f"Time: {transaction_info[7]} | ")
			text_widget.insert("end", "Voided?: Yes" if transaction_info[10] == 1 else "Voided?: No")

	def on_cash(self, event = None):
		"""Handles when cashier attempts to finalize transaction using cash."""
		if self.state_manager.trans.total == 0:
			self.ui.popup_description_label.config(text="No Items Entered!")
			self.ui.popup_frame.tkraise()
			self.clear()
			return "break"
		
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		entered_amount = self.ui.invisible_entry_var.get().strip()
		self.ui.invisible_entry.delete(0, tk.END)
		length = len(entered_amount)
		
		balance = self.state_manager.trans.total - self.state_manager.trans.cash_used - self.state_manager.trans.cc_used
		amount_given = 0.0
		
		if length == 0:
			self.state_manager.trans.cash_tendered += balance
			self.state_manager.trans.cash_used += balance
			self.ui.update_entry(self.ui.user_entry, "C: $0.00")
			#self.ui.update_entry(self.ui.balance_entry, f"${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = Decimal(f"0.0{entered_amount}")
		elif length == 2:
			amount_given = Decimal(f"0.{entered_amount}")
		elif length >= 3:
			amount_given = Decimal(f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}")
		
		display_string = "" 
		complete = False

		if amount_given == balance:
			self.state_manager.trans.cash_tendered += amount_given
			self.state_manager.trans.cash_used += amount_given
			display_string = "C: $0.00"
			complete = True
		elif amount_given > balance:
			self.state_manager.trans.cash_tendered += amount_given
			self.state_manager.trans.cash_used += balance
			display_string = f"C: ${abs(balance-amount_given):.2f}"
			complete = True
		elif amount_given < balance:
			self.state_manager.trans.cash_tendered += amount_given
			self.state_manager.trans.cash_used += amount_given
			display_string = f"B: ${(balance - amount_given):.2f}"

		self.ui.update_entry(self.ui.user_entry, display_string)
		
		if complete:
			#self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()

	def on_cc(self, event = None):
		"""Handles when cashier attempts to finalize transaction with cc."""
		if self.state_manager.trans.total == 0:
			self.ui.popup_description_label.config(text="No Items Entered!")
			self.ui.popup_frame.tkraise()
			self.clear()
			return "break"
	
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		entered_amount = self.ui.invisible_entry_var.get().strip()
		entered_amount = entered_amount[:-1]
		self.ui.invisible_entry.delete(0, tk.END)
		length = len(entered_amount)

		balance = self.state_manager.trans.total - self.state_manager.trans.cash_used - self.state_manager.trans.cc_used
		amount_given = 0.0
		
		if length == 0:
			self.state_manager.trans.cc_used += balance
			self.state_manager.trans.cc_tendered += balance
			self.ui.update_entry(self.ui.user_entry, "C: $0.00")
			#self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = Decimal(f"0.0{entered_amount}")
		elif length == 2:
			amount_given = Decimal(f"0.{entered_amount}")
		elif length >= 3:
			amount_given = Decimal(f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}")

		if amount_given > balance:
			self.ui.popup_description_label_var.set("CC Amount Entered\nExceeds Balance!")
			self.ui.popup_frame.tkraise()
			self.ui.update_entry(self.ui.user_entry, f'B: ${balance}')
			return "break"
		
		display_string = "" 
		complete = False

		if amount_given == balance:
			self.state_manager.trans.cc_tendered += amount_given
			self.state_manager.trans.cc_used += amount_given
			display_string = "C: $0.00"
			complete = True
		elif amount_given < balance:
			self.state_manager.trans.cc_tendered += amount_given
			self.state_manager.trans.cc_used += amount_given
			display_string = "B: $" + f"{(balance - amount_given):.2f}"

		self.ui.update_entry(self.ui.user_entry, display_string)

		if complete:
			#self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()


	def complete_sale(self, event=None):
		"""Complete transaction, open cash drawer, print receipt, and reset register environment."""
		if self.state_manager.trans.cash_used != 0:
			self.printer.kick_drawer()
		if self.state_manager.used_coupon:
			self.state_manager.trans.complete_transaction([self.state_manager.coupon, self.state_manager.coupon_reason])
		else:
			self.state_manager.trans.complete_transaction()
		self.state_manager.cursor.execute('''SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		sale_info = results[0]
		self.state_manager.cursor.execute('''SELECT * FROM sale_items WHERE sale_id = ?''', (sale_info[0], ))
		sale_items_list = self.state_manager.cursor.fetchall()
		#self.printer.print_receipt("sale", sale_items_list, sale_info, self.state_manager.trans.cash_tendered, self.state_manager.trans.cc_tendered)
		self.ui.sale_items_listbox.delete(0, tk.END)
		self.state_manager.new_transaction()

	def complete_decrement(self):
		self.state_manager.trans.complete_as_decrement()
		self.enter_register_frame()
		
	def number_pressed(self, input_widget=None, output_widget=None):
		"""Output formatted dollar amount when user inputs numbers"""
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		if input_widget is None:
			input_widget = self.ui.invisible_entry
		if output_widget is None:
			output_widget = self.ui.user_entry

		entry = input_widget.get().strip()
		if self.state_manager.sale_items_listbox_var.get() == -1:
			length = len(entry)
			if length == 0:
				display_string = "$0.00"
			if length == 1:
				display_string = "$0.0" + str(entry)
			elif length == 2:
				display_string = "$0." + str(entry)
			elif length >= 3:
				display_string = "$" + entry[0:length-2] + "." + entry[length-2:length]

			self.ui.update_entry(output_widget, display_string)

		else:
			self.ui.update_entry(output_widget, entry)

	def clear(self, event=None):
		"""Clear number user entered in register."""
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.update_entry(self.ui.user_entry, "$0.00")

	def cancel_sale(self, event=None):
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.update_entry(self.ui.user_entry, "$0.00")
		self.state_manager.sale_items_listbox_var.set(-1)
		self.on_sale_items_listbox_var()
		if self.state_manager.trans.cash_used != 0 or self.state_manager.trans.cc_used != 0:
			return
		selected_index = self.ui.sale_items_listbox.curselection()
		if selected_index == ():
			self.enter_register_frame()
		else:
			index = selected_index[0]
			self.remove_items_from_sale(index, True)
			self.ui.update_entry(self.ui.balance_entry, f"${abs(self.state_manager.trans.total):.2f}")
			self.ui.sale_items_listbox.delete(0, tk.END)
			for item in self.state_manager.trans.items_list:
				if len(item[0]) > 13:
					sale_info = f"{item[0][:13]}... ({str(item[-2])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
				else:
					sale_info = f"{item[0]} ({str(item[-2])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
				self.ui.sale_items_listbox.insert(tk.END, sale_info)
			self.ui.sale_items_listbox.yview_moveto(1.0)

	def remove_items_from_sale(self, index, canceling):
		if (self.state_manager.trans.items_list[index][2] == 1):
				self.state_manager.trans.pretax -= Decimal(str(self.state_manager.trans.items_list[index][1])) * Decimal(str(self.state_manager.trans.items_list[index][4]))
				self.state_manager.trans.tax -= (Decimal(self.config.data['tax_amount']) * Decimal(str(self.state_manager.trans.items_list[index][1])) * Decimal(str(self.state_manager.trans.items_list[index][4])))
				self.state_manager.trans.total -= (Decimal('1.0') + Decimal(self.config.data['tax_amount'])) * Decimal(str(self.state_manager.trans.items_list[index][1])) * Decimal(str(self.state_manager.trans.items_list[index][4]))
				self.state_manager.trans.items_sold -= Decimal(str(self.state_manager.trans.items_list[index][4]))
		else:
			self.state_manager.trans.nontax -= Decimal(str(self.state_manager.trans.items_list[index][1])) * Decimal(str(self.state_manager.trans.items_list[index][4]))
			self.state_manager.trans.total -= Decimal(str(self.state_manager.trans.items_list[index][1])) * Decimal(str(self.state_manager.trans.items_list[index][4]))
			self.state_manager.trans.items_sold -= Decimal(str(self.state_manager.trans.items_list[index][4]))

		if canceling:
			del self.state_manager.trans.items_list[index]
			
	def on_sale_items_listbox_select(self):
		selected_index = self.ui.sale_items_listbox.curselection()
		if selected_index:
			selected_index = selected_index[0]
		else:
			return
		if self.state_manager.sale_items_listbox_var.get() == -1:
			self.state_manager.sale_items_listbox_var.set(selected_index)
		elif self.state_manager.sale_items_listbox_var.get() == selected_index:
			self.state_manager.sale_items_listbox_var.set(-1)
			self.ui.sale_items_listbox.selection_clear(0, tk.END)

	def on_sale_items_listbox_var(self, *args):
		if self.state_manager.sale_items_listbox_var.get() != -1:
			self.ui.invisible_entry.unbind("<Return>")
			self.ui.invisible_entry.bind("<Return>", lambda event: self.process_sale_multiples())
		else:
			self.ui.invisible_entry.unbind("<Return>")
			self.ui.invisible_entry.bind("<Return>", self.process_sale)

	def process_sale_multiples(self, event=None):
		self.remove_items_from_sale(self.state_manager.sale_items_listbox_var.get(), False)
		self.state_manager.trans.items_list[self.state_manager.sale_items_listbox_var.get()][-2] = 0
		if Decimal(self.ui.invisible_entry_var.get()) % 1 == 0:
			for i in range(0, int(self.ui.invisible_entry_var.get())):
				self.process_sale(None, self.state_manager.trans.items_list[self.state_manager.sale_items_listbox_var.get()][3])
		else:
			for i in range(0, int(Decimal(self.ui.invisible_entry_var.get()))):
				self.process_sale(None, self.state_manager.trans.items_list[self.state_manager.sale_items_listbox_var.get()][3])
			index = self.ui.invisible_entry_var.get().find('.')
			decimal_amount = self.ui.invisible_entry_var.get()[index:]
			self.process_sale(
				None,
				self.state_manager.trans.items_list[self.state_manager.sale_items_listbox_var.get()][3],
				decimal_amount)
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.update_entry(self.ui.user_entry, "$0.00")
		self.state_manager.sale_items_listbox_var.set(-1)	


	def no_sale(self, event=None):
		
		self.printer.kick_drawer()
		self.ui.invisible_entry.delete(0, tk.END)
		#self.printer.print_no_sale_receipt()
		self.state_manager.cursor.execute(
			"UPDATE no_sale SET times_pressed = times_pressed + 1 WHERE date = ?",
			(datetime.today().strftime('%Y-%m-%d'),))
		self.state_manager.conn.commit()
		return "break"
		
	def menu_back(self):
		self.state_manager.browsing_seasonals = False
		self.ui.main_menu_frame.tkraise()

	def make_seasonal_sale(self):
			
		if self.state_manager.trans.total == 0:
			self.ui.popup_description_label.config(text="No Items Entered!")
			self.ui.popup_frame.tkraise()
			return
			
		self.ui.seasonal_id_entry_frame.tkraise()
		self.ui.seasonal_id_entry.focus_set()
		while True:
			root.wait_variable(self.state_manager.seasonal_id_var)
			self.state_manager.cursor.execute("SELECT EXISTS(SELECT 1 FROM seasonals WHERE seasonal_id = ?) LIMIT 1", (self.state_manager.seasonal_id_var.get(), ))
			results = self.state_manager.cursor.fetchone()[0]
			if results:
				break
			else:
				self.ui.popup_description_label.config(text = "Invalid Seasonal ID\nPlease try Again")
				self.ui.popup_frame.tkraise()
		self.ui.seasonal_id_entry_frame.lower()
		self.state_manager.trans.complete_transaction(self.state_manager.seasonal_id_var.get())
		self.ui.bind_invisible_entry_keys()
		self.enter_register_frame()
	
	def go_back(self):

		"""Changes index on back button press and resets environment accordingly."""
		if self.state_manager.add_item_index != 0:
			self.state_manager.add_item_index -= 1
		self.ui.add_item_go_back(self.state_manager.add_item_index)

	def reenter_button_pressed(self, which_button):
		"""Reset to add item interface according to button user presses."""
		
		self.state_manager.reentering = True

		match which_button:
			case "barcode":
				self.state_manager.add_item_index=0
				self.ui.add_barcode_frame.tkraise()
				self.ui.add_barcode_back_button.config(command = lambda: self.reenter_back_button())
				self.ui.add_barcode_entry.focus_set()
			case "name":
				self.state_manager.add_item_index=1
				self.ui.add_name_frame.tkraise()
				self.ui.add_name_back_button.config(command = lambda: self.reenter_back_button())
				self.ui.add_name_entry.focus_set()
			case "price":
				self.state_manager.add_item_index=2
				self.ui.add_price_frame.tkraise()
				self.ui.update_entry(self.ui.add_price_entry, "$0.00")
				self.ui.add_price_back_button.config(command = lambda: self.reenter_back_button())
				self.ui.add_price_entry.focus_set()
			case "taxable":
				self.state_manager.add_item_index=3
				self.ui.add_tax_frame.tkraise()
				self.ui.add_tax_back_button.config(command = lambda: self.reenter_back_button())
			case "category":
				self.state_manager.add_item_index=4
				self.ui.add_category_frame.tkraise()
				self.ui.add_category_back_button.config(command = lambda: self.reenter_back_button())
			case "subcategory":
				self.state_manager.add_item_index = 5
				self.ui.populate_subcategory_listbox(self.state_manager.add_item_object.category)
				self.ui.add_subcategory_frame.tkraise()
				self.ui.add_subcategory_back_button.config(command = lambda: self.reenter_back_button())
			case "vendor":
				self.state_manager.add_item_index = 6
				self.ui.add_vendor_frame.tkraise()
				self.ui.add_vendor_back_button.config(command = lambda: self.reenter_back_button())
				self.ui.add_vendor_skip_button.grid_forget()
			case "quantity":
				self.ui.add_quantity_label.config(text=f"Current quantity is: {self.state_manager.add_item_object.quantity}\nNew quantity will be: ")
				self.state_manager.add_item_index=7
				self.state_manager.reentering_quantity = True
				self.state_manager.reentering = False
				self.ui.add_quantity_back_button.config(command = lambda: self.reenter_back_button())
				self.ui.add_quantity_frame.tkraise()
				self.ui.add_quantity_entry.focus_set()

	def reenter_back_button(self):
		self.state_manager.add_item_index = self.state_manager.ADD_ITEM_LAST_STEP
		self.ui.reenter_frame.tkraise()

	def skip_vendor_step(self):
		self.state_manager.add_item_object.vendor="N/A"
		self.state_manager.add_item_index += 1
		self.ui.add_quantity_frame.tkraise()
		self.ui.add_quantity_entry.focus_set()

	def check_zero_integer(self, input: str) -> bool:

		try:
			return int(input) == 0
		except(ValueError, TypeError):
			return False
	
	def on_add_item_enter(self, event=None, entered_barcode=None, skipping_ahead = False):
		"""Handle user pressing enter or next in the context of adding an item.
		Process is handled in a series of steps."""

		if entered_barcode is not None:
			item_info_entered = entered_barcode
		else: 
			item_info_entered = self.add_variables[self.state_manager.add_item_index].get().strip()
			self.add_variables[self.state_manager.add_item_index].set('')

		if not skipping_ahead and self.state_manager.add_item_index != 3:
			if item_info_entered == '' or self.check_zero_integer(item_info_entered):
				return
			elif item_info_entered == "$0.00":
				self.ui.add_price_entry.insert(tk.END, "$0.00")
				self.ui.add_price_invisible_entry.delete(0, tk.END)
				return
		
		match self.state_manager.add_item_index:
			case 0:
				if not self.state_manager.reentering:
					if invf.check_item_exists(self.state_manager, item_info_entered):
						self.on_add_item_enter(None, None, True)
					else:
						self.ui.add_name_frame.tkraise()
						self.ui.add_name_entry.focus_set()
				else:
					invf.enter_item_barcode(self.state_manager, item_info_entered)
					self.on_add_item_enter(None, None, True)
			case 1:
				if invf.enter_item_name(self.state_manager, item_info_entered):
					self.on_add_item_enter(None, None, True)
				else:
					self.ui.add_price_frame.tkraise()	
					self.ui.update_entry(self.ui.add_price_entry, "$0.00")
					self.ui.add_price_invisible_entry.focus_set()
			case 2:
				self.ui.add_price_invisible_entry.delete(0, tk.END)
				if invf.enter_item_price(self.state_manager, item_info_entered):
					self.on_add_item_enter(None, None, True)
				else:
					self.ui.add_tax_frame.tkraise()
			case 3:
				if invf.enter_item_taxable(item_info_entered, self.state_manager):
					self.on_add_item_enter(None, None, True)	
				else:
					self.ui.add_category_frame.tkraise()	
			case 4:
				if invf.enter_item_category(self.state_manager, self.ui):
					self.on_add_item_enter(None, None, True)
				else:
					self.ui.populate_subcategory_listbox(self.state_manager.add_item_object.category)
					self.ui.add_subcategory_frame.tkraise()
			case 5:
				if invf.enter_item_subcategory(self.state_manager, self.ui):
					self.on_add_item_enter(None, None, True)
				else:
					self.ui.add_vendor_frame.tkraise()
			case 6:
				if invf.enter_item_vendor(self.state_manager, self.ui):
					self.on_add_item_enter(None, None, True)
				else:
					self.ui.add_quantity_frame.tkraise()
					self.ui.add_quantity_entry.focus_set()
			case self.state_manager.ADD_ITEM_LAST_STEP:
				self.ui.add_item_frame.tkraise()
				if not skipping_ahead:
					return_value = invf.enter_item_confirmation(
						self.state_manager, item_info_entered, self.ui)
				else:
					return_value = invf.enter_item_confirmation(
						self.state_manager, item_info_entered, self.ui, True
					)
			case _:
				self.ui.popup_description_label.config("Add item index out of bounds!\nPlease try again.")
				self.ui.popup_frame.tkraise()

	def finish_entering(self, *args):
		yes_no_answer = self.state_manager.yes_no_var.get()

		if yes_no_answer == 'yes':
			if self.state_manager.coming_from_register:
				invf.yes_register(self.state_manager, self.ui)
				self.process_sale(None, self.state_manager.add_item_object.barcode)
				self.state_manager.coming_from_register = False
				self.ui.register_frame.tkraise()
				self.ui.invisible_entry.focus_set()
			elif self.state_manager.updating_existing_item:
				invf.yes_existing(self.state_manager, self.ui)
				self.enter_add_item_frame()
			elif not self.state_manager.coming_from_register:
				invf.yes_not_register(self.state_manager, self.ui)
				self.enter_add_item_frame()
		elif yes_no_answer == 'no':
			self.ui.reenter_frame.tkraise()

		
	def on_add_category_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_category_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_category_listbox.get(selected_index)
		self.ui.category_var.set(selected_item)
		self.on_add_item_enter()

	def on_add_subcategory_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_subcategory_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_subcategory_listbox.get(selected_index)
		self.ui.subcategory_var.set(selected_item)
		self.on_add_item_enter()

	def on_add_vendor_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_vendor_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_vendor_listbox.get(selected_index)
		self.ui.vendor_var.set(selected_item)
		self.on_add_item_enter()

	def run_z(self, event=None):
		tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
		self.ui.popup_label.config(text="NOTE:")
		self.ui.popup_description_label.config(text=f"You are about to run a 'Z'\nThis will reset the beginning date to:\n{tomorrow}")
		self.ui.setup_popup_back_confirm()
		self.ui.popup_frame.tkraise()
		root.wait_variable(self.state_manager.popup_var)
		answer = self.state_manager.popup_var.get()
		if answer == 'Back':
			self.ui.popup_frame.lower()
			self.ui.setup_popup_ok()
			return
		self.ui.popup_frame.lower()
		self.ui.setup_popup_ok()
		self.printer.run_x(None, "Z")
		self.config.data['tally_begin_date'] = tomorrow
		self.config.write_out_config()


	def process_return(self, event = None):
		"""Put register into 'return mode'. User can ring up items like a 
		normal sale, but items will be returned instead."""
		self.enter_register_frame()
		self.ui.register_label.config(text="Mode: Return", fg="red")
		self.state_manager.trans.returning = True
		self.ui.unbind_invisible_entry_keys()
		self.ui.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.state_manager.return_var.set("cash"))
		self.ui.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: self.state_manager.return_var.set("cc"))
		self.ui.invisible_entry.bind("<KeyRelease-Escape>", lambda event: self.enter_register_frame())
		
	def finish_return(self, *args):
			
		button_pressed = self.state_manager.return_var.get()
		self.state_manager.trans.nontax *= -1
		self.state_manager.trans.pretax *= -1
		self.state_manager.trans.tax *= -1
		self.state_manager.trans.total *= -1

		if button_pressed == "cash":
			self.state_manager.trans.cash_used = self.state_manager.trans.total 
		elif button_pressed == "cc":
			self.state_manager.trans.cc_used = self.state_manager.trans.total

		self.state_manager.trans.complete_transaction()
		self.state_manager.cursor.execute('''SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		row = list(results[0])
		self.state_manager.cursor.execute('''SELECT * FROM sale_items WHERE sale_id = ?''', (row[0], ))
		item_results = list(self.state_manager.cursor.fetchall())
		self.printer.print_receipt("return", item_results, row)
		self.ui.bind_invisible_entry_keys()
		self.enter_register_frame()

	def on_yes_no(self, answer):
		"""Handles certain pressed of yes/no buttons."""
		if self.state_manager.add_item_index == 3:
			self.ui.tax_var.set(answer)
			self.on_add_item_enter()
		elif self.state_manager.add_item_index == self.state_manager.ADD_ITEM_LAST_STEP:
			if answer == 'no':
				self.state_manager.yes_no_var.set(answer)
				self.ui.reenter_frame.tkraise()
			else:
				self.state_manager.yes_no_var.set(answer)
			
	def enter_add_item_frame_again(self):
			invf.enter_item_confirmation(
				self.state_manager, item_info_entered, self.ui
			)


	def apply_coupon(self):
		coupon_amount = Decimal(self.ui.coupon_entry.get()[1:])
		self.state_manager.coupon = coupon_amount
		self.state_manager.used_coupon = True
		coupon_reason = self.ui.coupon_reason_entry.get()
		self.state_manager.coupon_reason = coupon_reason
		self.state_manager.trans.total -= coupon_amount
		self.ui.setup_coupon()


if __name__ == "__main__":

	#Declaration of root window
	root = tk.Tk()
	root.title("TBC REGISTER")
	root.geometry("1024x600")
	#root.tk.call('tk', 'scaling', 1)
	root.columnconfigure(0, weight=1)
	root.rowconfigure(0, weight=1)
	
	register = Register(root)
	register.state_manager.cursor.execute(
		"INSERT INTO no_sale (date, times_pressed) VALUES (?, ?) ON CONFLICT (date)" \
		"DO NOTHING", (datetime.today().strftime('%Y-%m-%d'), 0))
	register.state_manager.conn.commit()
	getcontext().rounding = 'ROUND_HALF_UP'
	

	backup_thread = threading.Thread(
		target = register.backup_scheduler,
		daemon=True
	)
	backup_thread.start()

	register.remove_old_backups(register.config.data['backup_removal_cutoff'])
	
	register.perform_backup()

	pygame.mixer.init()
	register.enter_register_frame()

	if register.config.data['manual_time_last_boot']:
		results = subprocess.run(
			['ping', '-c', '1', '-W', '10', '8.8.8.8'], capture_output=True, text=True)
		if results.returncode == 0:
			subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'true'])
		else:
			register.ui.popup_description_label.config(
				text="Internet connection could not be reached.\nPlease check your network connection."
			)
			register.ui.popup_frame.tkraise()
	elif not register.check_time_synced():
		register.ui.datetime_frame.tkraise()

	root.after(500, lambda: root.attributes("-fullscreen", True))

	root.mainloop()


