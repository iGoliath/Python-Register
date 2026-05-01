import tkinter as tk
import sqlite3
import inventory_functions as invf
import widget_functions as wf
from widget_manager import WidgetManager
from state_manager import StateManager
from config import Config
from datetime import datetime, timedelta
from escpos.printer import Usb
import pygame
import time
import threading
import os
import subprocess
import sys
from pathlib import Path

class Register:

	def __init__(self, root):
		"""Initialize UI, StateManager, Config, and Printer"""
		self.state_manager = StateManager(root)
		self.state_manager.browse_index.trace('w', self.browse_transactions)
		self.state_manager.item_lookup_var.trace('w', self.on_item_lookup)
		self.vcmd = (root.register(self.only_numbers), '%P')
		self.ui = WidgetManager(root, self)
		self.config = Config()
		self.state_manager.add_price_var.trace('w', self.on_price_entry_update)
		self.current_dir = Path(__file__).parent

		self.printer = Usb(0x0fe6, 0x811e, 0) #File("/dev/usb/lp0")

		self.entries = [
			self.ui.add_barcode_entry, self.ui.add_name_entry, self.ui.add_price_entry,
			self.ui.add_tax_entry, self.ui.add_category_entry,
			self.ui.add_subcategory_entry, self.ui.add_vendor_entry, self.ui.add_quantity_entry]

	def on_price_entry_update(self, *args):
		self.number_pressed(self.ui.add_price_invisible_entry, self.ui.add_price_entry)
		return "break"

	def on_item_lookup(self, *args):

		pattern = f'%{self.ui.lookup_items_entry.get()}%'
		self.state_manager.cursor.execute("SELECT Name FROM Inventory WHERE Name LIKE ?", (pattern, ))
		self.ui.lookup_items_listbox.delete(0, tk.END)
		results = self.state_manager.cursor.fetchall()

		for item in results:
			self.ui.lookup_items_listbox.insert(tk.END, f'{item[0]}\n')


	def confirm_lookup_items(self):
		index = self.ui.lookup_items_listbox.curselection()
		name = self.ui.lookup_items_listbox.get(index).strip()
		quantity = int(self.ui.lookup_items_quantity_spinbox.get())
		self.state_manager.cursor.execute('''SELECT Barcode FROM Inventory WHERE Name = ?''', (name, ))
		barcode = self.state_manager.cursor.fetchall()[0][0]
		
		for i in range(0, quantity):
			self.process_sale(None, barcode)
		self.ui.register_frame.tkraise()
		self.ui.invisible_entry.focus_set()

	def perform_backup(self):
		time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
		source_db = sqlite3.connect(self.current_dir / 'RegisterDatabase')
		dest_db = sqlite3.connect(f'/media/tbc/3CC9-2F54/RegisterDatabaseBackup_{time}.db')
		source_db.backup(dest_db)
		source_db.close()
		dest_db.close()

	def backup_scheduler(self):
		while True:
			time.sleep(self.config.data['backup_interval'])
			self.perform_backup()

	def remove_old_backups(self, days):
		cutoff = time.time() - (days * 86400)
		for filename in os.listdir('/media/tbc/3CC9-2F54/'):
			filepath = os.path.join('/media/tbc/3CC9-2F54/', filename)
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

	def only_numbers(self, P):
		"""Check if potential key is a number or space, return false if not"""
		if P.isdigit() or P == "":
			return True
		else:
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
				self.ui.error_description_label.config(text="No Transactions Yet!")
				self.ui.errors_frame.tkraise()
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
				self.print_seasonal_info(results)

			self.ui.setup_browse_seasonals()
				
			
		
	def print_seasonal_info(self, seasonal_info):
		self.ui.browse_text.delete("1.0", "end")
		#self.ui.browse_text.insert("end", f"ID: {seasonal_info[0]}  |  Site: {seasonal_info[3]}\n")
		self.ui.browse_text.insert("end", "ID: ", "bold")
		self.ui.browse_text.insert("end", seasonal_info[0])
		self.ui.browse_text.insert("end", "|Site: ", "bold")
		self.ui.browse_text.insert("end", f"{seasonal_info[3]}")
		self.ui.browse_text.insert("end", "|Balance: ", "bold")
		self.ui.browse_text.insert("end", f"{seasonal_info[4]:.2f}\n")
		self.ui.browse_text.insert("end", "Name: ", "bold")
		self.ui.browse_text.insert("end", f"{seasonal_info[1]}\n{seasonal_info[2]}\n")
		

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
			self.print_seasonal_info(results)



	def process_sale(self, event = None, entered_barcode=None):
		"""Check for existing barcode. If so, add item to running list of sold items
		and display info to cashier. Else, prompt user to enter the item."""
		if entered_barcode is not None:
			total, item_name, item_price, taxable = self.state_manager.trans.sell_item(entered_barcode)
		else:
			barcode = self.ui.invisible_entry.get()
			if barcode == "":
				return "break"
			if (len(barcode.lstrip('0')) != (len(barcode))):
				invf.update_barcode(self.state_manager, barcode)
			self.ui.invisible_entry.delete(0, tk.END)
			total, item_name, item_price, taxable  = self.state_manager.trans.sell_item(barcode)
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
		self.ui.update_entry(self.ui.balance_entry, f"${total:.2f}")
		self.ui.sale_items_listbox.delete(0, tk.END)
		for item in self.state_manager.trans.items_list:
			if len(item[0]) > 13:
				sale_info = f"{item[0][:13]}... ({str(item[-1])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
			else:
				sale_info = f"{item[0]} ({str(item[-1])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
			
			self.ui.sale_items_listbox.insert(tk.END, sale_info)
		self.ui.sale_items_listbox.yview_moveto(1.0)
		
	def void_transaction(self):

		if not self.enter_browse_transactions_frame(1, 0):
			return
		
		while True:
			root.wait_variable(self.state_manager.void_var)
			self.state_manager.cursor.execute('''SELECT Voided FROM Sales Where sale_id = ?''', (self.state_manager.browse_index.get(), ))
			voided = (self.state_manager.cursor.fetchall()[0])[0]
			if voided == 1:
				self.ui.error_description_label.config(text="This transaction is already voided!")
				self.ui.errors_frame.tkraise()
				continue
			else:
				break

		try:
			self.state_manager.cursor.execute('''UPDATE SALES SET Voided = ? WHERE sale_id = ?''', (1, self.state_manager.browse_index.get()))
			self.state_manager.cursor.execute('''SELECT * FROM Sales Where sale_id = ?''', (self.state_manager.browse_index.get(), ))
			transaction_info = list(self.state_manager.cursor.fetchall()[0])
			self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE sale_id = ?''', (self.state_manager.browse_index.get(), ))
			item_results = self.state_manager.cursor.fetchall()
			for i in range(len(item_results)):
				self.state_manager.cursor.execute('''UPDATE Inventory SET Quantity = Quantity + ? WHERE Barcode = ?''', (item_results[i][5], item_results[i][4]))
		except sqlite3.Error as e:
			self.ui.error_description_label.config(text=f"{e}")
			self.ui.errors_frame.tkraise()
		finally:
			self.state_manager.conn.commit()
			self.print_receipt("void", transaction_info[0], item_results, transaction_info)
			self.ui.remove_void_widgets()
			self.enter_register_frame()

	def print_transaction_info(
			self, text_widget, transaction_info):
			"""Print item info for transaction into a text widget. (Currently formatted for
			3 height)."""
			text_widget.delete("1.0", "end")
			text_widget.insert("end", f"Transaction ID: {str(transaction_info[0])} |\t")
			text_widget.insert("end", f"Total: ${transaction_info[4]:.2f}\n")
			text_widget.insert("end", f"Items Sold: {str(transaction_info[5])} |\t")
			text_widget.insert("end", f"Cash Used: ${transaction_info[8]:.2f}\n")
			text_widget.insert("end", f"CC Used: ${transaction_info[9]:.2f} |\t")
			text_widget.insert("end", f"Time: {transaction_info[7]}")



	def print_receipt(
			self, receipt_type, transaction_id,
			items, sale_info, cash_tend = None, cc_tend = None):
		"""Print receipt based on what type of transaction occured."""
		self.print_receipt_header(receipt_type, transaction_id)

		if receipt_type == "return":
			for i in (1, 2, 3, 4):
				sale_info[i] *= -1

		for sublist in items:
			self.printer.textln(sublist[1])
			if sublist[3] == 1:
				self.printer.text("TX ")
			else:
				self.printer.text("NT ")
			self.printer.textln(f"${sublist[2]:.2f} QTY {str(sublist[5])}")
		
		self.printer.ln(1)

		if sale_info[3] != 0:
			self.printer.ln(1)
			rounded = f"{sale_info[1]+sale_info[2]:.2f}"
			spaces = 31 - len(rounded)
			self.printer.textln(f"Subtotal: {' ' * spaces}${rounded}")
			rounded = f"{sale_info[3]:.2f}"
			spaces = 36 - len(rounded)
			self.printer.textln(f"Tax: {' ' * spaces}${rounded}")
		rounded = f"{sale_info[4]:.2f}"
		spaces = 34 - len(rounded)
		self.printer.textln(f"Total: {' '  * spaces}${rounded}")

		if cash_tend != 0 and cash_tend is not None:
			rounded = f"{cash_tend:.2f}"
			spaces = self.config.data['printing_width'] - 16 - len(rounded)
			self.printer.textln(f"Cash Tendered: {' ' * spaces}${rounded}")
		if cc_tend != 0 and cc_tend is not None:
			rounded = f"{cc_tend:.2f}"
			spaces = self.config.data['printing_width'] - 14 - len(rounded)
			self.printer.textln(f"CC Tendered: {' ' * spaces}${rounded}")
		change = f"{abs(sale_info[4] - (cash_tend if cash_tend is not None else 0) - (cc_tend if cc_tend is not None else 0)):.2f}"
		spaces = self.config.data['printing_width'] - 13 - len(change)
		self.printer.textln(f"Change Due: {' ' * spaces}${change}")
		self.printer.ln(2)
		self.printer.cut()

	def print_receipt_header(self, receipt_type, transaction_id):
		if receipt_type == "void":
			self.printer.textln(("-" * 42))
			self.printer.textln(f"{'-' * 12} Void Transaction {'-' * 12}")
			self.printer.textln(("-" * 42))
			spaces = 17 - len(str(transaction_id))
			self.printer.textln(f"Original Transaction ID: {' ' * spaces}{str(transaction_id)}")
		elif receipt_type == "sale":
			self.printer.textln(f"{'-' * 18} Sale {'-' * 18}")
			spaces = self.config.data['printing_width'] - 16 - len(str(transaction_id))
			self.printer.textln(f"Transaction ID: {' ' * spaces}{str(transaction_id)}")
		elif receipt_type == "return":
			self.printer.textln(f"{'-' * 17} Return {'-' * 17}")
			spaces = 26 - len(str(transaction_id))
			self.printer.textln(f"Transaction ID: {' ' * spaces}{str(transaction_id)}")
		elif receipt_type == "x":
			self.printer.textln(("-" * 42))
			self.printer.textln(f"{'-' * 14} Daily Report {'-' * 14}")
			self.printer.textln(f"{'-' * 12} {datetime.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M')} {'-' * 12}")
			self.printer.textln("-" * 42)
			self.printer.ln(2)
		elif receipt_type == "z":
			self.printer.textln(("-" * 42))
			self.printer.textln(f"{'-' * 13} Monthly Report {'-' * 13}")
			self.printer.textln(f"{'-' * 12} {datetime.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M')} {'-' * 12}")
			self.printer.textln("-" * 42)
			self.printer.ln(2)

		if receipt_type != "x" and receipt_type != "z":
			self.printer.textln(f"{datetime.today().strftime('%Y-%m-%d')}{' ' * 27}{datetime.now().strftime('%H:%M')}")
			self.printer.ln(2)

	def on_cash(self, event = None):
		"""Handles when cashier attempts to finalize transaction using cash."""
		if self.state_manager.trans.total == 0:
			self.ui.error_description_label.config(text="No Items Entered!")
			self.ui.errors_frame.tkraise()
			self.clear()
			return "break"
		
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		entered_amount = self.ui.invisible_entry.get().strip()
		self.ui.invisible_entry.delete(0, tk.END)
		length = len(entered_amount)
		
		balance = round(self.state_manager.trans.total - self.state_manager.trans.cash_used - self.state_manager.trans.cc_used, 2)
		amount_given = 0.0
		
		if length == 0:
			self.state_manager.trans.cash_tendered += balance
			self.state_manager.trans.cash_used += balance
			self.ui.update_entry(self.ui.user_entry, "C: $0.00")
			#self.ui.update_entry(self.ui.balance_entry, f"${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = float(f"0.0{entered_amount}")
		elif length == 2:
			amount_given = float(f"0.{entered_amount}")
		elif length >= 3:
			amount_given = float(f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}")
		
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
			self.ui.error_description_label.config(text="No Items Entered!")
			self.ui.errors_frame.tkraise()
			self.clear()
			return "break"
	
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		entered_amount = self.ui.invisible_entry.get().strip()
		entered_amount = entered_amount[:-1]
		self.ui.invisible_entry.delete(0, tk.END)
		length = len(entered_amount)

		balance = round(self.state_manager.trans.total - self.state_manager.trans.cash_used - self.state_manager.trans.cc_used, 2)
		amount_given = 0.0
		
		if length == 0:
			self.state_manager.trans.cc_used += balance
			self.state_manager.trans.cc_tendered += balance
			self.ui.update_entry(self.ui.user_entry, "C: $0.00")
			#self.ui.update_entry(self.ui.balance_entry, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = float(f"0.0{entered_amount}")
		elif length == 2:
			amount_given = float(f"0.{entered_amount}")
		elif length >= 3:
			amount_given = float(f"{entered_amount[0:length-2]}.{entered_amount[length-2:length]}")

		if amount_given > balance:
			self.ui.error_description_label.config(text="CC Amount Entered\nExceeds Balance!")
			self.ui.errors_frame.tkraise()
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
			self.printer.cashdraw(pin=2)
		if self.state_manager.used_coupon:
			self.state_manager.trans.complete_transaction([self.state_manager.coupon, self.state_manager.coupon_reason])
		else:
			self.state_manager.trans.complete_transaction()
		self.state_manager.cursor.execute('''SELECT * FROM SALES WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		sale_info = results[0]
		self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE sale_id = ?''', (sale_info[0], ))
		sale_items_list = self.state_manager.cursor.fetchall()
		self.print_receipt("sale", sale_info[0], sale_items_list, sale_info, self.state_manager.trans.cash_tendered, self.state_manager.trans.cc_tendered)
		self.ui.sale_items_listbox.delete(0, tk.END)
		self.state_manager.new_transaction()
		
	def number_pressed(self, input_widget=None, output_widget=None):
		"""Output formatted dollar amount when user inputs numbers"""
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()

		if input_widget is None:
			input_widget = self.ui.invisible_entry
		if output_widget is None:
			output_widget = self.ui.user_entry

		entry = input_widget.get().strip()
		length = len(entry)
		if length == 0:
			display_string = "$0.00"
		if length == 1:
			display_string = "$0.0" + str(entry)
		elif length == 2:
			display_string = "$0." + str(entry)
		elif length >= 3:
			display_string = "$" + entry[0:length-2] + "." + entry[length-2:length]

		output_widget.delete(0, tk.END)
		output_widget.insert(tk.END, display_string)


	def clear(self, event=None):
		"""Clear number user entered in register."""
		pygame.mixer.music.load(self.current_dir / "short-beep.mp3")
		pygame.mixer.music.play()
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.update_entry(self.ui.user_entry, "$0.00")

	def cancel_sale(self, event=None):
		self.ui.invisible_entry.delete(0, tk.END)
		if self.state_manager.trans.cash_used != 0 or self.state_manager.trans.cc_used != 0:
			return
		selected_index = self.ui.sale_items_listbox.curselection()
		if selected_index == ():
			self.enter_register_frame()
		else:
			index = selected_index[0]
			if (self.state_manager.trans.items_list[index][2] == 1):
				self.state_manager.trans.pretax -= self.state_manager.trans.items_list[index][1] * self.state_manager.trans.items_list[index][4]
				self.state_manager.trans.tax -= round(abs(self.config.data['tax_amount'] * (self.state_manager.trans.items_list[index][1] * self.state_manager.trans.items_list[index][4])), 2)
				self.state_manager.trans.total -= round(abs((1 + self.config.data['tax_amount']) * (self.state_manager.trans.items_list[index][1] * self.state_manager.trans.items_list[index][4])), 2)
				self.state_manager.trans.items_sold -= self.state_manager.trans.items_list[index][4]
			else:
				self.state_manager.trans.nontax -= self.state_manager.trans.items_list[index][1] * self.state_manager.trans.items_list[index][4]
				self.state_manager.trans.total -= self.state_manager.trans.items_list[index][1] * self.state_manager.trans.items_list[index][4]
				self.state_manager.trans.items_sold -= self.state_manager.trans.items_list[index][4]
			del self.state_manager.trans.items_list[index]
			self.ui.update_entry(self.ui.balance_entry, f"${abs(self.state_manager.trans.total):.2f}")
			self.ui.sale_items_listbox.delete(0, tk.END)
			for item in self.state_manager.trans.items_list:
				if len(item[0]) > 13:
					sale_info = f"{item[0][:13]}... ({str(item[-1])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
				else:
					sale_info = f"{item[0]} ({str(item[-1])}) ${str(item[1])} {'TX' if item[2] == 1 else 'NT'}"
				self.ui.sale_items_listbox.insert(tk.END, sale_info)
			self.ui.sale_items_listbox.yview_moveto(1.0)

		
			

	def no_sale(self, event=None):
		
		self.printer.cashdraw(pin=2)
		self.ui.invisible_entry.delete(0, tk.END)
		self.printer.textln(("-" * 22) + " NS " + ("-" * 22))
		self.printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 33) + datetime.now().strftime("%H:%M"))
		self.printer.ln(2)
		self.printer.cut()
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
			self.ui.error_description_label.config(text="No Items Entered!")
			self.ui.errors_frame.tkraise()
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
				self.ui.error_description_label.config(text = "Invalid Seasonal ID\nPlease try Again")
				self.ui.errors_frame.tkraise()
		self.ui.seasonal_id_entry_frame.lower()
		self.state_manager.trans.complete_transaction(self.state_manager.seasonal_id_var.get())
		self.ui.bind_invisible_entry_keys()
		self.enter_register_frame()
	
	def go_back(self):

		"""Changes index on back button press and resets environment accordingly."""
		if self.state_manager.add_item_index != 0:
			self.state_manager.add_item_index -= 1
		match self.state_manager.add_item_index:
			case 0:
				self.ui.add_barcode_frame.tkraise()
				self.ui.add_barcode_entry.focus_set()
			case 1:
				self.ui.add_name_frame.tkraise()
				self.ui.add_name_entry.focus_set()
			case 2:
				self.ui.add_price_frame.tkraise()
				self.ui.add_price_invisible_entry.delete(0, tk.END)
				self.ui.add_price_entry.focus_set()
			case 3:
				self.ui.add_tax_frame.tkraise()
			case 4:
				self.ui.add_category_frame.tkraise()
			case 5:
				self.ui.populate_subcategory_listbox(self.state_manager.add_item_object.category)
				self.ui.add_subcategory_frame.tkraise()
			case 6:
				self.ui.add_vendor_frame.tkraise()
			case 7:
				self.ui.add_quantity_frame.tkraise()

	def reenter_button_pressed(self, which_button):
		"""Reset to add item interface according to button user presses."""
		
		self.state_manager.reentering = True

		match which_button:
			case "barcode":
				self.state_manager.add_item_index=0
				self.ui.add_barcode_frame.tkraise()
				self.ui.add_barcode_entry.focus_set()
			case "name":
				self.state_manager.add_item_index=1
				self.ui.add_name_frame.tkraise()
				self.ui.add_name_entry.focus_set()
			case "price":
				self.state_manager.add_item_index=2
				self.ui.add_price_frame.tkraise()
				self.ui.update_entry(self.ui.add_price_entry, "$0.00")
				self.ui.add_price_entry.focus_set()
			case "taxable":
				self.state_manager.add_item_index=3
				self.ui.add_tax_frame.tkraise()
			case "category":
				self.state_manager.add_item_index=4
				self.ui.add_category_frame.tkraise()
			case "subcategory":
				self.state_manager.add_item_index = 5
				self.ui.populate_subcategory_listbox(self.state_manager.add_item_object.category)
				self.ui.add_subcategory_frame.tkraise()
			case "vendor":
				self.state_manager.add_item_index = 6
				self.ui.add_vendor_frame.tkraise()
			case "quantity":
				self.ui.add_quantity_label.config(text=f"Current quantity is: {self.state_manager.add_item_object.quantity}\nNew quantity will be: ")
				self.state_manager.add_item_index=7
				self.state_manager.reentering_quantity = True
				self.state_manager.reentering = False
				self.ui.add_quantity_frame.tkraise()
				self.ui.add_quantity_entry.focus_set()

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
	
	def on_add_item_enter(self, event=None, entered_barcode=None):
		"""Handle user pressing enter or next in the context of adding an item.
		Process is handled in a series of steps."""
	
		if entered_barcode is not None:
			item_info_entered = entered_barcode
		else: 
			item_info_entered = self.entries[self.state_manager.add_item_index].get().strip()
			self.entries[self.state_manager.add_item_index].delete(0, tk.END)

		'''if item_info_entered == '' or self.check_zero_integer(item_info_entered):
			return
		elif item_info_entered == "$0.00":
			self.ui.add_price_entry.insert(tk.END, "$0.00")
			self.ui.add_price_invisible_entry.delete(0, tk.END)
			return'''
		
		match self.state_manager.add_item_index:
			case 0:
				if not self.state_manager.reentering:
					if invf.check_item_exists(self.state_manager, item_info_entered):
						self.on_add_item_enter()
					else:
						self.ui.add_name_frame.tkraise()
						self.ui.add_name_entry.focus_set()
				else:
					invf.enter_item_barcode(self.state_manager, item_info_entered)
					self.on_add_item_enter()
			case 1:
				if invf.enter_item_name(self.state_manager, item_info_entered):
					self.on_add_item_enter()
				else:
					self.ui.add_price_frame.tkraise()	
					self.ui.update_entry(self.ui.add_price_entry, "$0.00")
					self.ui.add_price_invisible_entry.focus_set()
			case 2:
				self.ui.add_price_invisible_entry.delete(0, tk.END)
				if invf.enter_item_price(self.state_manager, item_info_entered):
					self.on_add_item_enter()
				else:
					self.ui.add_tax_frame.tkraise()
			case 3:
				if invf.enter_item_taxable(item_info_entered, self.state_manager):
					self.on_add_item_enter()	
				else:
					self.ui.add_category_frame.tkraise()	
			case 4:
				if invf.enter_item_category(self.state_manager, self.ui):
					self.on_add_item_enter()
				else:
					self.ui.populate_subcategory_listbox(self.state_manager.add_item_object.category)
					self.ui.add_subcategory_frame.tkraise()
			case 5:
				if invf.enter_item_subcategory(self.state_manager, self.ui):
					self.on_add_item_enter()
				else:
					self.ui.add_vendor_frame.tkraise()
			case 6:
				if invf.enter_item_vendor(self.state_manager, self.ui):
					self.on_add_item_enter()
				else:
					self.ui.add_quantity_frame.tkraise()
					self.ui.add_quantity_entry.focus_set()
			case self.state_manager.ADD_ITEM_LAST_STEP:
				self.ui.add_item_frame.tkraise()
				return_value = invf.enter_item_confirmation(
					self.state_manager, item_info_entered, root, self.ui)
				if return_value == True:
					self.process_sale(None, self.state_manager.add_item_object.barcode)
					self.state_manager.coming_from_register = False
					self.ui.register_frame.tkraise()
					self.ui.invisible_entry.focus_set()
				elif return_value == False:
					self.enter_add_item_frame()
				elif return_value == None:
					self.ui.reenter_frame.tkraise()
			case _:
				self.ui.error_description_label.config("Add item index out of bounds!\nPlease try again.")
				self.ui.errors_frame.tkraise()

		
	def on_add_category_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_category_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_category_listbox.get(selected_index)
		self.ui.update_entry(self.ui.add_category_entry, selected_item)
		self.on_add_item_enter()

	def on_add_subcategory_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_subcategory_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_subcategory_listbox.get(selected_index)
		self.ui.update_entry(self.ui.add_subcategory_entry, selected_item)
		self.on_add_item_enter()

	def on_add_vendor_listbox_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_vendor_listbox.curselection()
		if selected_index == ():
			return
		selected_item = self.ui.add_vendor_listbox.get(selected_index)
		self.ui.update_entry(self.ui.add_vendor_entry, selected_item)
		self.on_add_item_enter()

	def run_x(self, event=None, running_z = None):
		"""Sum daily totals and print them to a receipt."""
		
		if not running_z:
			self.print_receipt_header("x", None)
		else:
			self.print_receipt_header("z", None)
		gross_total = 0

		for category in ("Cash Used", "CC Used", "Non-Tax", "Pre-Tax", "Tax"):
			self.state_manager.cursor.execute('''SELECT SUM("%s") FROM SALES WHERE Date >= ? AND Date <= ? AND Voided != 1''' % (category), (self.config.data['tally_begin_date'], datetime.today().strftime('%Y-%m-%d'), ))
			results = self.state_manager.cursor.fetchone()[0]
			sum_in_question = results if results is not None else 0
			if category in ("Non-Tax", "Pre-Tax", "Tax"):
				gross_total += sum_in_question
			rounded = f"{sum_in_question:.2f}"
			spaces = 29 - len(category.split()[0]) - len(rounded)
			self.printer.textln(f"{category.split()[0]} Collected: {' ' * spaces}${rounded}\n")
		
		self.state_manager.cursor.execute('''SELECT SUM("Price") FROM saleitems JOIN sales ON saleitems.sale_id = sales.sale_id WHERE saleitems."Barcode" IN ('20LB PROPANE', '30LB PROPANE', '40LB Propane', '100LB Propane', 'GALLON PROPANE') AND sales."Date" >= ? AND sales."Date" <= ?''', (self.config.data['tally_begin_date'], datetime.today().strftime('%Y-%m-%d'), ))
		results = self.state_manager.cursor.fetchone()[0]
		propane_sold = results if results is not None else 0
		spaces = 42 - 15 - len(f"{propane_sold:.2f}")
		self.printer.textln(f"Propane Sold: {' ' * spaces}${propane_sold:.2f}\n")


		spaces = 42 - 14 - len(f"{gross_total:.2f}")
		self.printer.textln(f"Gross Total: {' ' * spaces}${gross_total:.2f}\n")

		self.state_manager.cursor.execute('''SELECT SUM("Total") FROM Sales WHERE TOTAL < 0 AND Date = ?''', (datetime.today().strftime('%Y-%m-%d'), ))
		results = self.state_manager.cursor.fetchone()[0]
		total_returns = (results * -1) if results is not None else 0
		spaces = 42 - 16 - len(f"{total_returns:.2f}")
		self.printer.textln(f"Total Returns: {' ' * spaces}${total_returns:.2f}\n")

		self.state_manager.cursor.execute('''SELECT SUM(times_pressed) FROM no_sale WHERE Date >= ? AND Date <= ?''', (self.config.data['tally_begin_date'], datetime.today().strftime('%Y-%m-%d'), ))
		results = self.state_manager.cursor.fetchall()
		times_pressed = results[0]
		spaces = 28 - len((str(times_pressed)))
		self.printer.textln("# Times No Sale: " + (" " * spaces) + str(times_pressed[0]))
		self.printer.cut()

	def run_z(self, event=None):
		tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
		self.ui.error_label.config(text="NOTE:")
		self.ui.error_description_label.config(text=f"You are about to run a 'Z'\nThis will reset the beginning date to:\n{tomorrow}")
		self.ui.setup_errors_back_confirm()
		self.ui.errors_frame.tkraise()
		root.wait_variable(self.state_manager.error_var)
		answer = self.state_manager.error_var.get()
		if answer == 'Back':
			self.ui.errors_frame.lower()
			self.ui.setup_errors_ok()
			return
		self.ui.errors_frame.lower()
		self.setup_errors_ok()
		self.run_x(None, "Z")
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
		while True:
			root.wait_variable(self.state_manager.return_var)
			if self.state_manager.trans.total == 0:
				continue
			else:
				break
			
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
		self.state_manager.cursor.execute('''SELECT * FROM SALES WHERE sale_id = (SELECT MAX(sale_id) FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		row = list(results[0])
		self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE sale_id = ?''', (row[0], ))
		item_results = list(self.state_manager.cursor.fetchall())
		self.print_receipt("return", row[0], item_results, row)
		self.ui.bind_invisible_entry_keys()
		self.enter_register_frame()


	def return_invisible_entry_focus(self, event):
		"""Bound to FocusIn on register widgets. Returns focus to invisible
		entry, and returns 'break' to stop propagating event."""
		self.ui.invisible_entry.focus_set()
		return "break"

	def return_add_item_invisible_entry_focus(self, event):
		"""Bound to FocusIn on add item widgets. Returns focus to invisible
		entry, and returns 'break' to stop propagating event."""
		self.ui.add_item_invisible_entry.focus_set()
		return "break"
	
	def return_browse_entry_focus(self, event):
		"""Bound to FocusIn on browse items textbox. Returns focus to browse_entry,
		and returns 'break' to stop propagating event."""
		self.ui.browse_entry.focus_set()
		return "break"

	def on_yes_no(self, answer):
		"""Handles certain pressed of yes/no buttons."""
		if self.state_manager.add_item_index == 3:
			self.ui.update_entry(self.ui.add_tax_entry, answer)
			self.on_add_item_enter()
		elif self.state_manager.add_item_index == self.state_manager.ADD_ITEM_LAST_STEP:
			self.state_manager.yes_no_var.set(answer)
			self.ui.reenter_frame.tkraise()

	def apply_coupon(self):
		coupon_amount = float(self.ui.coupon_entry.get()[1:])
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

	backup_thread = threading.Thread(
		target = register.backup_scheduler,
		daemon=True
	)
	backup_thread.start()

	register.remove_old_backups(register.config.data['backup_removal_cutoff'])

	pygame.mixer.init()
	register.enter_register_frame()

	'''if register.config.data['manual_time_last_boot']:
		results = subprocess.run(
			['ping', '-c', '1', '-W', '10', '8.8.8.8'], capture_output=True, text=True)
		if results.returncode == 0:
			subprocess.run(['sudo', 'timedatectl', 'set-ntp', 'true'])
		else:
			register.ui.error_description_label.config(
				text="Internet connection could not be reached.\nPlease check your network connection."
			)
			register.ui.errors_frame.tkraise()
	elif not register.check_time_synced():
		register.ui.datetime_frame.tkraise()'''

	root.after(500, lambda: root.attributes("-fullscreen", True))

	root.mainloop()


