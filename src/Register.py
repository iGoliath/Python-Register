import tkinter as tk
import inventory_functions as invf
import widget_functions as wf
from widget_manager import *
from makeTransaction import *
from enteritem import *
from stateManager import *
from config import Config
from datetime import datetime
from escpos.printer import Usb
import pygame


class Register:

	def __init__(self, root):
		"""Initialize UI, StateManager, Config, and Printer"""
		self.ui = WidgetManager(root, self)
		self.state_manager = StateManager(root)
		self.config = Config()
		self.vcmd = (root.register(self.only_numbers), '%P')
		self.printer = Usb(0x0fe6, 0x811e, 0) #File("/dev/usb/lp0")
		

	def only_numbers(self, P):
		"""Check if potential key is a number or space, return false if not"""
		if P.isdigit() or P == "":
			return True
		else:
			return False
         
	def enter_register_frame(self, event = None):
		"""Reset register environment to defaults, and raise the register frame."""
		pygame.mixer.music.load("short-beep.mp3")
		pygame.mixer.music.play()
		self.state_manager.new_transaction()
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.sale_items_listbox.delete(0, tk.END)
		self.ui.total_entry.delete(0, tk.END)
		self.ui.total_entry.insert(tk.END, "$0.00")
		self.ui.usr_entry.delete(0, tk.END)
		self.ui.usr_entry.insert(tk.END, "$0.00")
		self.ui.register_frame.tkraise()
		self.ui.invisible_entry.focus_force()
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
			self.ui.add_item_label.config(text="Please enter item's barcode: ")

	def enter_update_inventory_frame(self, event=None):
		self.ui.update_inventory_frame.tkraise()
		self.ui.update_inventory_entry.focus_force()	

	def enter_browse_transactions_frame(self):
		self.state_manager.cursor.execute(
			'''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = list(self.state_manager.cursor.fetchone())
		self.state_manager.browse_index = results[0]
		self.print_transaction_info(self.ui.browse_text, results)
		self.ui.browse_transactions_frame.tkraise()

	def browse_transactions(self, change):
		self.state_manager.browse_index += change
		self.state_manager.cursor.execute(
			'''SELECT * FROM sales WHERE "Transaction ID" = ?''', (self.state_manager.browse_index, )
		)
		results = self.state_manager.cursor.fetchone()
		if not results:
			self.state_manager.browse_index -= change
			return
		self.print_transaction_info(self.ui.browse_text, list(results))


	def process_sale(self, event=None, entered_barcode=None):
		"""Check for existing barcode. If so, add item to running list of sold items
		and display info to cashier. Else, prompt user to enter the item."""
		self.ui.total_entry.delete(0, tk.END)
		self.ui.total_entry.insert(tk.END, "$0.00")
		if entered_barcode is not None:
			total, item_name, item_price, taxable = self.state_manager.trans.sell_item(entered_barcode)
		else:
			barcode = self.ui.invisible_entry.get()
			self.ui.invisible_entry.delete(0, tk.END)
			total, item_name, item_price, taxable = self.state_manager.trans.sell_item(barcode)
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
		self.ui.usr_entry.delete(0, tk.END)
		self.ui.usr_entry.insert(0, f"${total:.2f}")
		self.ui.sale_items_listbox.delete(0, tk.END)
		for i in range(len(self.state_manager.trans.items_list)):
			sale_info = self.state_manager.trans.items_list[i][0] + " $" + str(self.state_manager.trans.items_list[i][1]) + " "
			if self.state_manager.trans.items_list[i][2] == 1:
				sale_info += "TX"
			else:
				sale_info += "NT"
			sale_info += " QTY: " + str(self.state_manager.trans.quantity_sold_list[i][1]) 
			self.ui.sale_items_listbox.insert(tk.END, sale_info)
		
	def void_transaction(self, which_button):
		"""Set voided field in database to 1 (True) for transaction user specifies."""
		self.ui.register_functions_buttons_frame.grid_forget()
		if which_button == "last":
			self.ui.additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
			self.state_manager.cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		elif which_button == "ref":
			self.ui.additional_register_functions_label.config(text="Please enter the reference number:")
			self.ui.additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')
			root.wait_variable(self.state_manager.reference_number_var)
			reference_number = self.state_manager.reference_number_var.get()
			self.ui.additional_register_functions_entry.grid_forget()
			self.state_manager.cursor.execute('''Select * FROM SALES WHERE "Transaction ID" = ?''', (reference_number, ))

		results = self.state_manager.cursor.fetchall()
		row = results[0]
		self.ui.additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
		self.print_transaction_info(self.ui.additional_register_functions_text, row)
		self.ui.additional_register_functions_yes_no.grid(column=1, row=2, sticky='nsew')
		self.ui.additional_register_functions_label.config(text="Void This Transaction?")
		root.wait_variable(self.state_manager.yes_no_var)
		button_pressed = self.state_manager.yes_no_var.get()
		if button_pressed == "yes":
			try:
				self.state_manager.cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
				self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
				item_results = self.state_manager.cursor.fetchall()
				#self.print_receipt("void", row[0], item_results, row)
			except sqlite3.Error as e:
				self.ui.additional_register_functions_text.delete("1.0", "end")
				self.ui.additional_register_functions_text.insert("end", "ERROR, please try again")
			finally:
				self.state_manager.conn.commit()
				self.ui.additional_register_functions_text.grid_forget()
				self.ui.additional_register_functions_yes_no.grid_forget()
				self.ui.additional_register_functions_label.config(text="Please select an option")
				self.ui.register_functions_buttons_frame.grid(row = 1, column = 1, sticky='nsew')
				self.ui.place_register_functions_buttons()
				self.enter_register_frame()
				
		elif button_pressed == "no":
			self.ui.additional_register_functions_text.grid_forget()
			self.ui.additional_register_functions_yes_no.grid_forget()
			self.void_transaction("ref")
		

	def print_transaction_info(
			self, text_widget, transaction_info):
			"""Print item info for transaction into a text widget. (Currently formatted for
			3 height)."""
			text_widget.delete("1.0", "end")
			text_widget.insert("end", "Transaction ID: " + str(transaction_info[0]) + " |\t")
			text_widget.insert("end", "Total: $" + f"{transaction_info[4]:.2f}" + "\n")
			text_widget.insert("end", "# Items Sold: " + str(transaction_info[5]) + " |\t")
			text_widget.insert("end", "Cash Used: $" + f"{transaction_info[8]:.2f}" + "\n")
			text_widget.insert("end", "CC Used: $" + f"{transaction_info[9]:.2f}" + " |\t")
			text_widget.insert("end", "Time: " + transaction_info[7])

	def print_receipt(
			self, receipt_type, transaction_id,
			items, sale_info, cash_tend = None, cc_tend = None):
		"""Print receipt based on what type of transaction occured."""
		if receipt_type == "void":
				self.printer.textln(("-" * 42))
				self.printer.textln(("-" * 12) + " Void Transaction " + ("-" * 12))
				self.printer.textln(("-" * 42))
				spaces = 17 - len(str(transaction_id))
				self.printer.textln("Original Transaction ID: " + (" " * spaces) + str(transaction_id))
		elif receipt_type == "sale":
				self.printer.textln(("-" * 18) + " Sale " + ("-" * 18))
				spaces = self.config.printing_width - 16 - len(str(transaction_id))
				self.printer.textln("Transaction ID: " + (" " * spaces) + str(transaction_id))
		elif receipt_type == "return":
				self.printer.textln(("-" * 17) + " Return " + ("-" * 17))
				spaces = 26 - len(str(transaction_id))
				self.printer.textln("Transaction ID: " + (" " * spaces) + str(transaction_id))
				for i in (1, 2, 4, 5):
					sale_info[i] *= -1
		self.printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 27) + datetime.now().strftime("%H:%M"))
		self.printer.ln(2)
		for i in range(len(items)):
				self.printer.textln(items[i][1])
				if items[i][3] == 1:
					self.printer.text("TX ")
				else:
					self.printer.text("NT ")
				self.printer.textln("$" + f"{items[i][2]:.2f}" + " QTY " + str(items[i][5]))
		
		self.printer.ln(1)
		if sale_info[3] != 0:
			self.printer.ln(1)
			rounded = f"{sale_info[1]+sale_info[2]:.2f}"
			spaces = 31 - len(rounded)
			self.printer.textln("Subtotal: " + (" " * spaces) + "$" + rounded)
			rounded = f"{sale_info[3]:.2f}"
			spaces = 36 - len(rounded)
			self.printer.textln("Tax: " + (" " * spaces) + "$" + rounded)
		rounded = f"{sale_info[4]:.2f}"
		spaces = 34 - len(rounded)
		self.printer.textln("Total: " + (" " * spaces) + "$" + rounded)
		if cash_tend != 0 and cash_tend is not None:
			rounded = f"{cash_tend:.2f}"
			spaces = self.config.printing_width - 16 - len(rounded)
			self.printer.textln("Cash Tendered: " + (" " * spaces) + "$" + rounded)
		if cc_tend != 0 and cc_tend is not None:
			rounded = f"{cc_tend:.2f}"
			spaces = self.config.printing_width - 14 - len(rounded)
			self.printer.textln("CC Tendered: " + (" " * spaces) + "$" + rounded)
		change = f"{abs(sale_info[4] - (cash_tend if cash_tend is not None else 0) - (cc_tend if cc_tend is not None else 0)):.2f}"
		spaces = self.config.printing_width - 13 - len(change)
		self.printer.textln("Change Due: " + (" " * spaces) + "$" + change)
		self.printer.ln(2)
		self.printer.cut()
		
	def on_cash(self, event = None):
		"""Handles when cashier attempts to finalize transaction using cash."""
		if self.state_manager.trans.total == 0:
			return "break"
		
		pygame.mixer.music.load("short-beep.mp3")
		pygame.mixer.music.play()

		entered_amount = self.ui.invisible_entry.get().strip()
		self.ui.invisible_entry.delete(0, tk.END)
		length = len(entered_amount)
		
		balance = round(self.state_manager.trans.total - self.state_manager.trans.cash_used - self.state_manager.trans.cc_used, 2)
		amount_given = 0.0
		
		if length == 0:
			self.state_manager.trans.cash_tendered += balance
			self.state_manager.trans.cash_used += balance
			self.ui.total_entry.delete(0, tk.END)
			self.ui.total_entry.insert(tk.END, "C: $0.00")
			self.ui.usr_entry.delete(0, tk.END)
			self.ui.usr_entry.insert(tk.END, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = float("0.0" + entered_amount)
		elif length == 2:
			amount_given = float("0." + entered_amount)
		elif length == 3:
			amount_given = float(entered_amount[0:length-2] + "." + entered_amount[length-2:length])
		
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
			display_string = "C: $" + f"{abs(balance-amount_given):.2f}"
			complete = True
		elif amount_given < balance:
			self.state_manager.trans.cash_tendered += amount_given
			self.state_manager.trans.cash_used += amount_given
			display_string = "B: $" + f"{(balance - amount_given):.2f}"

		self.ui.total_entry.delete(0, tk.END)
		self.ui.total_entry.insert(tk.END, display_string)

		if complete:
			self.ui.usr_entry.delete(0, tk.END)
			self.ui.usr_entry.insert(tk.END, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()

	def on_cc(self, event = None):
		"""Handles when cashier attempts to finalize transaction with cc."""
		if self.state_manager.trans.total == 0:
			return "break"
		
		pygame.mixer.music.load("short-beep.mp3")
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
			self.ui.total_entry.delete(0, tk.END)
			self.ui.total_entry.insert(tk.END, "C: $0.00")
			self.ui.usr_entry.delete(0, tk.END)
			self.ui.usr_entry.insert(tk.END, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()
			return "break"
		elif length == 1:
			amount_given = float("0.0" + entered_amount)
		elif length == 2:
			amount_given = float("0." + entered_amount)
		elif length == 3:
			amount_given = float(entered_amount[0:length-2] + "." + entered_amount[length-2:length])
		
		if amount_given > balance:
			self.ui.total_entry.insert(tk.END, "ERR: CC")
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

		self.ui.total_entry.delete(0, tk.END)
		self.ui.total_entry.insert(tk.END, display_string)

		if complete:
			self.ui.usr_entry.delete(0, tk.END)
			self.ui.usr_entry.insert(tk.END, f"Sale Total: ${self.state_manager.trans.total:.2f}")
			self.complete_sale()


	def complete_sale(self, event=None):
		"""Complete transaction, open cash drawer, print receipt, and reset register environment."""
		#self.printer.cashdraw(pin=2)
		self.state_manager.trans.complete_transaction()
		self.state_manager.cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		sale_info = results[0]
		self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (sale_info[0], ))
		sale_items_list = self.state_manager.cursor.fetchall()
		#self.print_receipt("sale", sale_info[0], sale_items_list, sale_info, self.state_manager.trans.cash_tendered, self.state_manager.trans.cc_tendered)
		self.ui.sale_items_listbox.delete(0, tk.END)
		self.state_manager.new_transaction()
		
	def number_pressed(self, event=None, input_widget=None, output_widget=None):
		"""Output formatted dollar amount when user inputs numbers"""
		pygame.mixer.music.load("short-beep.mp3")
		pygame.mixer.music.play()

		if input_widget is None:
			input_widget = self.ui.invisible_entry
		if output_widget is None:
			output_widget = self.ui.total_entry

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
		pygame.mixer.music.load("short-beep.mp3")
		pygame.mixer.music.play()
		self.ui.invisible_entry.delete(0, tk.END)
		self.ui.total_entry.delete(0, tk.END)
		self.ui.total_entry.insert(tk.END, "$0.00")
			
	def get_update_barcode(self, event=None):
		self.state_manager.update_inventory_var.set(self.ui.update_inventory_entry.get())
		self.ui.update_inventory_entry.delete(0, tk.END)
		
	def update_inventory(self, which_button, entered_barcode):
		self.ui.update_buttons_frame.grid_forget()
		self.ui.update_inventory_entry.grid(row=1, column=1, sticky='nsew')
		if (entered_barcode):
			barcode = entered_barcode
		else:
			self.ui.update_inventory_label.config(text="Please scan barcode of item")
			root.wait_variable(self.state_manager.update_inventory_var)
			barcode = self.state_manager.update_inventory_var.get()
		self.state_manager.cursor.execute("SELECT %s FROM INVENTORY WHERE barcode = ?" % (which_button), (barcode,))
		results = self.state_manager.cursor.fetchall()
		row = results[0]
		current_value = row[0]
		while True:
			if which_button == "Taxable":
				if current_value == 1:
					self.ui.update_inventory_label.config(text="Item is Currently Taxable\nSwitch to Non-Taxable?")
				elif current_value == 0:		
					self.ui.update_inventory_label.config(text="Item is Currently Non-Taxable\nSwitch to Taxable?")

				self.ui.update_inventory_entry.grid_forget()
				self.ui.update_inventory_yes_no.grid(row=1, column=1, sticky='nsew')
				root.wait_variable(self.state_manager.yes_no_var)
				yes_no_answer = self.state_manager.yes_no_var.get()
				if yes_no_answer == "yes":
					self.state_manager.cursor.execute("UPDATE INVENTORY SET Taxable = ? Where Barcode = ?", (not current_value, barcode,))
					break
				elif yes_no_answer == "no":
					self.ui.update_inventory_yes_no.grid_forget()
					self.ui.update_inventory_entry.grid(row=1, column=1, sticky='nsew')
					continue
			elif which_button != "Taxable":
				self.ui.update_inventory_label.config(text=f"Current {which_button} is:\n" + str(current_value) + f"\nPlease Enter Item's New {which_button}")
				root.wait_variable(self.state_manager.update_inventory_var)
				new_value = self.state_manager.update_inventory_var.get()
				self.ui.update_inventory_label.config(text=f"New {which_button} will be:\n" + new_value + "\nIs this correct?")
				self.ui.update_inventory_entry.grid_forget()
				self.ui.update_inventory_yes_no.grid(row=1, column=1, sticky='nsew')
				root.wait_variable(self.state_manager.yes_no_var)
				yes_no_answer = self.state_manager.yes_no_var.get()
				self.ui.update_inventory_yes_no.grid_forget()
				if yes_no_answer == "yes":
					self.state_manager.cursor.execute("UPDATE INVENTORY SET %s = ? WHERE %s = ?" % (which_button, which_button), (new_value, current_value, ))
					break
				elif yes_no_answer == "no":
					self.ui.update_inventory_entry.grid(row=1, column=1, sticky='nsew')
					continue
		self.ui.update_inventory_yes_no.grid_forget()
		self.ui.update_buttons_frame.grid(column = 1, row=1, sticky='nsew')
		self.ui.update_inventory_label.config(text="What would you\nlike to update?")
		self.state_manager.conn.commit()
		self.state_manager.conn.close()
		self.ui.admin_frame.tkraise()

	def no_sale(self, event=None):
		
		self.ui.invisible_entry.delete(0, tk.END)
		self.printer.cashdraw(pin=2)
		self.printer.textln(("-" * 22) + " NS " + ("-" * 22))
		self.printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 33) + datetime.now().strftime("%H:%M"))
		self.printer.ln(2)
		self.state_manager.cursor.execute(
			"UPDATE no_sale SET times_pressed = times_pressed + 1 WHERE date = ?",
			(datetime.today().strftime('%Y-%m-%d'),))
		self.state_manager.conn.commit()
		return "break"
		

																					

	def go_back(self):
		"""Changes index on back button press and resets environment accordingly."""
		if self.state_manager.add_item_index != 0:
			self.state_manager.add_item_index -= 1
		match self.state_manager.add_item_index:
			case 0:
				self.ui.add_item_label.config(text="Please enter item's barcode:")
			case 1:
				self.ui.add_item_label.config(text="Please enter item's name:")
				self.ui.add_item_entry.unbind("<FocusIn>", self.state_manager.binding_manager)
				self.ui.add_item_entry.delete(0, tk.END)
				self.ui.add_item_entry.focus_set()
			case 2:
				self.state_manager.binding_manager = self.ui.add_item_entry.bind("<FocusIn>", self.return_add_item_invisible_entry_focus)
				self.ui.add_item_label.config(text="Please enter item's price:")
				self.ui.add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
				self.ui.add_item_button.grid(column=1, row=2, sticky='ew')
				self.ui.add_item_yes_no.grid_forget()
				self.ui.add_item_entry.delete(0, tk.END)
				self.ui.add_item_entry.insert(tk.END, "$0.00")
			case 3:
				self.ui.add_item_frame.tkraise()
				self.ui.add_item_entry.grid_forget()
				self.ui.add_item_button.grid_forget()
				self.ui.add_item_yes_no.grid(column=1, row=2, sticky='nsew')
				self.ui.add_item_label.config(text="Is the item taxable?")
			case 4:
				self.ui.add_item_label.config(text="Please enter the category:")
				self.ui.add_item_listbox_frame.tkraise()
			case 5:
				self.ui.add_item_label.config(text="Please enter the quantity:")
			
	def reenter_button_pressed(self, which_button):
		"""Reset to add item interface according to button user presses."""
		self.ui.reenter_frame.grid_forget()
		self.ui.add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
		self.ui.add_item_button.grid(column=1, row=2, sticky='ew')
		
		self.state_manager.reentering = True

		match which_button:
			case "barcode":
				self.state_manager.add_item_index=0
				self.ui.add_item_label.config(text="Please enter item's barcode:")
			case "name":
				self.state_manager.add_item_index=1
				self.ui.add_item_label.config(text="Please enter the item's name:")
			case "price":
				self.state_manager.add_item_index=2
				self.ui.add_item_label.config(text="Please enter the item's price:")
			case "taxable":
				self.state_manager.add_item_index=3
				self.ui.add_item_label.config(text="Is the item taxable?")
				self.ui.add_item_entry.grid_forget()
				self.ui.add_item_button.grid_forget()
				self.ui.add_item_yes_no.grid(column=1, row=2, sticky='nsew')
				#self.on_add_item_enter()
			case "category":
				self.state_manager.add_item_index=4
				self.ui.add_item_listbox_frame.tkraise()
			case "quantity":
				self.state_manager.add_item_index=5
				self.state_manager.reentering_quantity = True
				self.state_manager.reentering = False
				self.ui.add_item_label.config(text="Please enter the Quantity:")

		
	def quit_button_handler(self, event=None):
		"""Raises frame according to where quit button is pressed."""
		if not self.state_manager.coming_from_register:
			self.ui.admin_frame.tkraise()
		elif self.state_manager.coming_from_register:
			self.ui.register_frame.tkraise()


	def on_add_item_enter(self, event=None, entered_barcode=None):
		"""Handle user pressing enter or next in the context of adding and item.
		Process is handled in a series of steps."""
		
		print(self.state_manager.add_item_index)
		if entered_barcode is not None:
			item_info_entered = entered_barcode
		else: 
			item_info_entered = self.ui.add_item_entry.get().strip()
			self.ui.add_item_entry.delete(0, tk.END)
		
		match self.state_manager.add_item_index:
			case 0:
				if invf.check_item_exists(self.state_manager, item_info_entered, self.ui.add_item_label):
					self.on_add_item_enter()
			case 1:
				if invf.enter_item_name(self.state_manager, item_info_entered, self.ui.add_item_label):
					self.on_add_item_enter()
				self.ui.add_item_entry.insert(tk.END, "$0.00")
				self.ui.add_item_invisible_entry.config(validate='key', vcmd=self.vcmd)
				self.state_manager.add_item_var.trace('w', self.on_add_item_entry_update)
				self.ui.add_item_invisible_entry.config(textvariable=self.state_manager.add_item_var)
				self.state_manager.binding_manager = self.ui.add_item_entry.bind("<FocusIn>", self.return_add_item_invisible_entry_focus)
				self.ui.add_item_invisible_entry.focus_set()
			case 2:
				self.ui.add_item_invisible_entry.delete(0, tk.END)
				self.ui.add_item_entry.unbind("<FocusIn>", self.state_manager.binding_manager)
				if invf.enter_item_price(
					self.state_manager, item_info_entered, self.ui.add_item_label,
					self.ui.add_item_yes_no, self.ui.add_item_button, self.ui.add_item_entry):
					self.on_add_item_enter()
			case 3:
				if invf.enter_item_taxable(
					item_info_entered, self.state_manager, root, self.ui.add_item_yes_no,
					self.ui.add_item_entry, self.ui.add_item_button, 
					self.ui.add_item_label, self.ui.add_item_listbox_frame):
					self.on_add_item_enter()		
			case 4:
				if invf.enter_item_category(
					self.state_manager, self.ui.add_item_frame, self.ui.add_item_entry,
					self.ui.add_item_label, self.ui.add_item_listbox):
					self.on_add_item_enter()
				self.ui.add_item_entry.config(validate='key', vcmd=self.vcmd)
				self.ui.add_item_entry.focus_set()
			case 5:
				self.ui.add_item_entry.config(validate='none')
				if invf.enter_item_confirmation(
					self.state_manager, item_info_entered, self.ui.add_item_label,
					self.ui.add_item_entry, self.ui.add_item_button, self.ui.item_info_confirmation,
					self.ui.add_item_yes_no, self.ui.back_button, root, self.ui.reenter_frame):
					self.process_sale(None, self.state_manager.add_item_object.barcode)
					self.ui.register_frame.tkraise()
			case _:

				self.ui.add_item_entry.delete(0, tk.END)
				self.ui.add_item_entry.insert(tk.END, "ERROR")

		
	def on_add_item_scrollbar_next(self, event=None):
		"""Places entry in listbox user selected for on_add_item_enter() to pick up."""
		selected_index = self.ui.add_item_listbox.curselection()
		selected_item = self.ui.add_item_listbox.get(selected_index)
		self.ui.add_item_entry.delete(0, tk.END)
		self.ui.add_item_entry.insert(tk.END, selected_item)
		self.on_add_item_enter()

	def run_x(self, event=None):
		"""Sum daily totals and print them to a receipt."""
		self.state_manager.cursor.execute('''SELECT "Transaction ID" FROM sales where date = ?''', (datetime.today().strftime('%Y-%m-%d'), ))
		results = self.state_manager.cursor.fetchall()
		if not results:
			return "break"
		self.printer.textln(("-" * 42))
		self.printer.textln(("-" * 14) + " Daily Report " + ("-" * 14))
		self.printer.textln(("-" * 12) + " " + datetime.today().strftime('%Y-%m-%d') + " " + datetime.now().strftime("%H:%M") + " " + ("-" * 12))
		self.printer.textln("-" * 42)
		self.printer.ln(2)

		for category in ("Cash Used", "CC Used", "Non-Tax", "Pre-Tax", "Tax"):
			self.state_manager.cursor.execute('''SELECT SUM("%s") FROM SALES WHERE Date = ? AND Voided != 1''' % (category), (datetime.today().strftime('%Y-%m-%d'), ))
			results = self.state_manager.cursor.fetchone()[0]
			sum_in_question = results if results is not None else 0
			rounded = f"{sum_in_question:.2f}"
			spaces = 29 - len(category) - len(rounded)
			if category == "Cash Used" or category == "CC Used":
				spaces = 29 - len(category[:-5]) - len(rounded)
				self.printer.textln(f"{category[:-5]} Collected: " + (" " * spaces) + "$" + rounded)
			else:
				self.printer.textln(f"{category} Collected: " + (" " * spaces) + "$" + rounded)
			self.printer.ln(1)
			
		self.state_manager.cursor.execute('''SELECT times_pressed FROM no_sale WHERE date = ?''', (datetime.today().strftime('%Y-%m-%d'), ))
		results = self.state_manager.cursor.fetchall()
		times_pressed = results[0]
		spaces = 28 - len((str(times_pressed)))
		self.printer.textln("# Times No Sale: " + (" " * spaces) + str(times_pressed[0]))
		self.printer.cut()

	def process_return(self, event = None):
		"""Put register into 'return mode'. User can ring up items like a 
		normal sale, but items will be returned instead."""
		self.enter_register_frame()
		self.state_manager.trans.ret_or_void = True
		self.ui.unbind_invisible_entry_keys()
		self.ui.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.state_manager.return_var.set("cash"))
		self.ui.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: self.state_manager.return_var.set("cc"))
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
		self.state_manager.cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = self.state_manager.cursor.fetchall()
		row = list(results[0])
		self.state_manager.cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
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

	def on_add_item_entry_update(self, *args):
		"""Handler for when user is inputting numbers during add item process."""
		self.number_pressed(None, self.ui.add_item_invisible_entry, self.ui.add_item_entry)

	def on_yes_no(self, answer):
		"""Handles certain pressed of yes/no buttons."""
		if self.state_manager.add_item_index == 3:
			self.ui.add_item_entry.delete(0, tk.END)
			self.ui.add_item_entry.insert(tk.END, answer)
			self.on_add_item_enter()
		elif self.state_manager.add_item_index == 5:
			self.state_manager.yes_no_var.set(answer)

if __name__ == "__main__":
	#Declaration of root window
	root = tk.Tk()
	root.title("TBC REGISTER")
	root.geometry("1024x600")
	root.tk.call('tk', 'scaling', 1)
	root.grid_columnconfigure(0, weight=1)
	root.grid_rowconfigure(0, weight=1)
	#root.attributes("-fullscreen", True)
	register = Register(root)
	register.state_manager.cursor.execute(
		"INSERT INTO no_sale (date, times_pressed) VALUES (?, ?) ON CONFLICT (date)" \
		"DO NOTHING",
		(datetime.today().strftime('%Y-%m-%d'), 0))
	register.state_manager.conn.commit()
	pygame.mixer.init()
	register.ui.mode_select_frame.tkraise()
	root.mainloop()


