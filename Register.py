import tkinter as tk
from makeTransaction import *
from enteritem import *
from stateManager import *
from datetime import datetime
from escpos.printer import Usb
import pygame


printer = Usb(0x0fe6, 0x811e, 0) #File("/dev/usb/lp0")
pygame.mixer.init()
#Declaration of root window and all neccessary frames
root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")
root.tk.call('tk', 'scaling', 50)
state_manager = StateManager(root)

mode_select_frame = tk.Frame(root)
register_frame = tk.Frame(root, bg='black')
admin_frame = tk.Frame(root)
add_item_frame = tk.Frame(root)
update_inventory_frame = tk.Frame(root)
additional_register_functions_frame = tk.Frame(root)
update_buttons_frame = tk.Frame(update_inventory_frame)
reenter_frame = tk.Frame(add_item_frame)
add_item_yes_no = tk.Frame(add_item_frame)
additional_register_functions_yes_no = tk.Frame(additional_register_functions_frame)
update_inventory_yes_no = tk.Frame(update_inventory_frame)
register_widgets_frame = tk.Frame(register_frame)
add_item_listbox_frame = tk.Frame(root)
register_add_item_prompt_frame = tk.Frame(root)

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
# Widgets in column 1 will determine the width of the rest of the widgets
for frame in (mode_select_frame, register_frame, admin_frame, add_item_frame, update_inventory_frame, additional_register_functions_frame, add_item_listbox_frame, register_add_item_prompt_frame):
	frame.grid(row=0, column=0, sticky='nsew')
	frame.grid_columnconfigure(0, weight=1)
	frame.grid_columnconfigure(1, weight=0)
	frame.grid_columnconfigure(2, weight=1)

for frame in (update_buttons_frame, reenter_frame, add_item_yes_no, additional_register_functions_yes_no, register_widgets_frame):
	frame.grid_columnconfigure(0, weight=1)
	frame.grid_columnconfigure(1, weight=1)

#root.attributes("-fullscreen", True)

def enter_register_frame():
	global state_manager
	state_manager.new_transaction()
	register_frame.tkraise()
	invisible_entry.focus_force()
	invisible_entry.delete(0, tk.END)
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")
	

	
def enter_add_item_frame():
	global state_manager
	state_manager.new_add_item_object()
	state_manager.reentering = False
	state_manager.add_item_index = 0
	add_item_entry.focus_force()
	add_item_label.grid(column=1, row=0, sticky='ew')
	add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
	add_item_button.grid(column=1, row=3, sticky='ew')
	back_button.grid(column=1, row=4, sticky='ew')
	quit_button.grid(column=1, row=5, sticky='ew')
	add_item_yes_no.grid_forget()
	item_info_confirmation.grid_forget()
	reenter_frame.grid_forget()
	add_item_label.config(text="Please enter item's barcode: ")
	add_item_frame.tkraise()


def enter_void_frame(event=None):
	additional_register_functions_frame.tkraise()

def enter_update_inventory_frame(event=None):
	update_inventory_frame.tkraise()
	update_inventory_entry.focus_force()
	
def register_go_back(event=None):
	cancel_trans()
	mode_select_frame.tkraise()		

def process_sale(event=None):
	global state_manager
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")
	barcode = invisible_entry.get()
	invisible_entry.delete(0, tk.END)
	total, item_name, item_price, taxable = state_manager.trans.sell_item(barcode)
	if total == "item_not_found":
		register_add_item_prompt_frame.tkraise()
		root.wait_variable(state_manager.yes_no_var)
		yes_no_answer = state_manager.yes_no_var.get()
		if yes_no_answer == "yes":
			state_manager.coming_from_register = True
			enter_add_item_frame()
			return
		elif yes_no_answer == "no":
			enter_register_frame()
			return
	usr_entry.delete(0, tk.END)
	usr_entry.insert(0, "$" + f"{total:.2f}")
	sale_items.delete("1.0", "end")
	for i in range(len(state_manager.trans.items_list)):
		sale_info = state_manager.trans.items_list[i][0] + " $" + str(state_manager.trans.items_list[i][1]) + " "
		if state_manager.trans.items_list[i][2] == 1:
			sale_info += "TX"
		else:
			sale_info += "NT"
		sale_info += " QTY: " + str(state_manager.trans.quantity_sold_list[i][1]) + "\n" 
		sale_items.insert("end", sale_info)
	
def void_transaction(which_button):
	register_functions_buttons_frame.grid_forget()
	void_conn = sqlite3.connect("RegisterDatabase")
	void_cursor = void_conn.cursor()
	if which_button == "last":
		additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
		void_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = void_cursor.fetchall()
		row = results[0]
		print_void_transaction_info(row[0], row[4], row[5], row[8], row[9], row[7])
		additional_register_functions_yes_no.grid(column=1, row=2, sticky='nsew')
		additional_register_functions_label.config(text="Void This Transaction?")
		root.wait_variable(state_manager.yes_no_var)
		button_pressed = state_manager.yes_no_var.get()
		if button_pressed == "yes":
			try:
				void_cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
				void_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
				item_results = void_cursor.fetchall()
				print_receipt("void", row[0], item_results, row)
			except sqlite3.Error as e:
				additional_register_functions_text.delete("1.0", "end")
				additional_register_functions_text.insert("end", "ERROR, please try again")
			finally:
				void_conn.commit()
				void_conn.close()
				additional_register_functions_text.grid_forget()
				additional_register_functions_yes_no.grid_forget()
				enter_register_frame()
				additional_register_functions_label.config(text="Please select an option")
				last_button.grid(row=1, column=1, sticky='nsew')
				number_button.grid(row=2, column=1, sticky='nsew')
		elif button_pressed == "no":
			void_conn.close()
			additional_register_functions_text.grid_forget()
			additional_register_functions_yes_no.grid_forget()
			void_transaction("ref")
	elif which_button == "ref":
		additional_register_functions_label.config(text="Please enter the reference number:")
		additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')
		root.wait_variable(state_manager.reference_number_var)
		reference_number = state_manager.reference_number_var.get()
		additional_register_functions_entry.grid_forget()
		additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
		additional_register_functions_yes_no.grid(column=1, row=2, sticky='nsew')
		void_cursor.execute('''Select * FROM SALES WHERE "Transaction ID" = ?''', (reference_number, ))
		results = void_cursor.fetchall()
		row = results[0]
		additional_register_functions_label.config(text="Void this transaction?")
		print_void_transaction_info(row[0], row[4], row[5], row[8], row[9], row[7])
		root.wait_variable(state_manager.yes_no_var)
		button_pressed = state_manager.yes_no_var.get()
		if button_pressed == "yes":
			try:

				void_cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
				void_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
				item_results = void_cursor.fetchall()
				print_receipt("void", row[0], item_results, row)
			except sqlite3.Error as e:
				additional_register_functions_text.delete("1.0", "end")
				additional_register_functions_text.insert("end", "ERROR, please try again")
			finally:
				void_conn.commit()
				void_conn.close()
				additional_register_functions_text.grid_forget()
				additional_register_functions_yes_no.grid_forget()
				enter_register_frame()
				additional_register_functions_label.config(text="Please select an option")
				last_button.grid(row=1, column=1, sticky='nsew')
				number_button.grid(row=2, column=1, sticky='nsew')



def print_void_transaction_info(transaction_id, total, number_items_sold, cash_used, cc_used, time):
		additional_register_functions_text.delete("1.0", "end")
		additional_register_functions_text.insert("end", "Transaction ID: " + str(transaction_id) + " |\t")
		additional_register_functions_text.insert("end", "Total: $" + f"{total:.2f}" + "\n")
		additional_register_functions_text.insert("end", "# Items Sold: " + str(number_items_sold) + " |\t")
		additional_register_functions_text.insert("end", "Cash Used: $" + f"{cash_used:.2f}" + "\n")
		additional_register_functions_text.insert("end", "CC Used: $" + f"{cc_used:.2f}" + " |\t")
		additional_register_functions_text.insert("end", "Time: " + time)

def print_receipt(receipt_type, transaction_id, items, sale_info):
	if receipt_type == "void":
			printer.textln(("-" * 42))
			printer.textln(("-" * 12) + " Void Transaction " + ("-" * 12))
			printer.textln(("-" * 42))
			spaces = 17 - len(str(transaction_id))
			printer.textln("Original Transaction ID: " + (" " * spaces) + str(transaction_id))
	elif receipt_type == "sale":
			printer.textln(("-" * 18) + " Sale " + ("-" * 18))
			spaces = 26 - len(str(transaction_id))
			printer.textln("Transaction ID: " + (" " * spaces) + str(transaction_id))
	elif receipt_type == "return":
			printer.textln(("-" * 17) + " Return " + ("-" * 17))
			spaces = 26 - len(str(transaction_id))
			printer.textln("Transaction ID: " + (" " * spaces) + str(transaction_id))
			for i in (1, 2, 4, 5):
				sale_info[i] *= -1
	printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 27) + datetime.now().strftime("%H:%M"))
	printer.ln(2)
	for i in range(len(items)):
			printer.textln(items[i][1])
			if items[i][3] == 1:
				printer.text("TX ")
			else:
				printer.text("NT ")
			printer.textln("$" + f"{items[i][2]:.2f}" + " QTY " + str(items[i][5]))
	
	printer.ln(1)
	if sale_info[3] != 0:
		printer.ln(1)
		rounded = f"{sale_info[1]+sale_info[2]:.2f}"
		spaces = 31 - len(rounded)
		printer.textln("Subtotal: " + (" " * spaces) + "$" + rounded)
		rounded = f"{sale_info[3]:.2f}"
		spaces = 36 - len(rounded)
		printer.textln("Tax: " + (" " * spaces) + "$" + rounded)
	rounded = f"{sale_info[4]:.2f}"
	spaces = 34 - len(rounded)
	printer.textln("Total: " + (" " * spaces) + "$" + rounded)
	printer.ln(2)
	#printer.cut()
	

def on_additional_register_functions_entry(event=None):
	state_manager.reference_number_var.set(additional_register_functions_entry.get())

		
def on_cash_cc(event, payment_method):
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	old_balance = state_manager.trans.total - state_manager.trans.cash_used - state_manager.trans.cc_used 	# Calculate current balance remaining on the sale
	if payment_method == "cc":
		entered_amount = invisible_entry.get()
		entered_amount = entered_amount[:-1]
	elif payment_method == "cash":
		entered_amount = invisible_entry.get().strip()	
	invisible_entry.delete(0, tk.END)
	length = len(entered_amount)
	if entered_amount == "":			# If user just pressed cash or credit card button, 
		if payment_method == "cash":	# entire balance is being settled as such
			state_manager.trans.cash_used += old_balance
		elif payment_method == "cc":
			state_manager.trans.cc_used += old_balance
		display_string = "C $0.00"
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
		complete_sale()
		return
	elif entered_amount != "":			# Otherwise, we need to format the user's input
		amount_given = 0
		if length==1:					# Then, update amount of cash or cc used in sale
				amount_given = float("0.0" + entered_amount)
		elif length==2:
				amount_given = float("0." + entered_amount)
		elif length>=3:					
				amount_given = float(entered_amount[0:length-2] + "." + entered_amount[length-2:length])
		
		new_balance = state_manager.trans.total - state_manager.trans.cash_used - state_manager.trans.cc_used - amount_given
		if new_balance<=0:
			display_string = "C: $" + f"{abs(new_balance):.2f}"
			if payment_method == "cc":
				state_manager.trans.cc_used += old_balance
			elif payment_method == "cash":
				state_manager.trans.cash_used += old_balance
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
			complete_sale()
		elif new_balance>0:
			display_string = "B: $" + f"{abs(new_balance):.2f}" 
			if payment_method == "cc":
				state_manager.trans.cc_used += old_balance
			elif payment_method == "cash":
				state_manager.trans.cash_used += old_balance
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
		elif new_balance==0:
			display_string = "C: $0.00"
			if payment_method == "cc":
				state_manager.trans.cc_used += old_balance
			elif payment_method == "cash":
				state_manager.trans.cash_used += old_balance
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
			complete_sale()

def cancel_trans(event=None):
	global state_manager
	state_manager.new_transaction()
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	sale_items.delete("1.0", "end")
	invisible_entry.delete(0, tk.END)
	usr_entry.delete(0, tk.END)
	usr_entry.insert(0, "$0.00")



def complete_sale(event=None):
	global state_manager
	printer.cashdraw(pin=2)
	state_manager.trans.complete_transaction()
	sale_conn = sqlite3.connect("RegisterDatabase")
	sale_cursor = sale_conn.cursor()
	sale_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
	results = sale_cursor.fetchall()
	sale_info = results[0]
	sale_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (sale_info[0], ))
	sale_items_list = sale_cursor.fetchall()
	sale_conn.close()
	print_receipt("sale", sale_info[0], sale_items_list, sale_info)
	sale_items.delete("1.0", "end")
	usr_entry.delete(0, tk.END)
	usr_entry.insert(0, "$0.00")
	state_manager.new_transaction()
	
def number_pressed(event=None):
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	entry = invisible_entry.get()
	length = len(entry)
	if length == 1:
		display_string = "$0.0" + str(entry)
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
	elif length == 2:
		display_string = "$0." + str(entry)
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
	elif length >= 3:
		display_string = "$" + entry[0:length-2] + "." + entry[length-2:length]
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)

def clear(event=None):
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	invisible_entry.delete(0, tk.END)
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")
		
def get_update_barcode(event=None):
	state_manager.update_inventory_var.set(update_inventory_entry.get())
	state_manager.update_inventory_entry.delete(0, tk.END)
	
def update_inventory(which_button, entered_barcode):
	update_conn = sqlite3.connect("RegisterDatabase")
	update_cursor = update_conn.cursor()
	update_buttons_frame.grid_forget()
	update_inventory_entry.grid(row=1, column=1, sticky='nsew')
	if (entered_barcode):
		barcode = entered_barcode
	else:
		update_inventory_label.config(text="Please scan barcode of item")
		root.wait_variable(state_manager.update_inventory_var)
		barcode = state_manager.update_inventory_var.get()
	update_cursor.execute("SELECT %s FROM INVENTORY WHERE barcode = ?" % (which_button), (barcode,))
	results = update_cursor.fetchall()
	row = results[0]
	current_value = row[0]
	while True:
		if which_button == "Taxable":
			if current_value == 1:
				update_inventory_label.config(text="Item is Currently Taxable\nSwitch to Non-Taxable?")
			elif current_value == 0:		
				update_inventory_label.config(text="Item is Currently Non-Taxable\nSwitch to Taxable?")

			update_inventory_entry.grid_forget()
			update_inventory_yes_no.grid(row=1, column=1, sticky='nsew')
			root.wait_variable(state_manager.yes_no_var)
			yes_no_answer = state_manager.yes_no_var.get()
			if yes_no_answer == "yes":
				update_cursor.execute("UPDATE INVENTORY SET Taxable = ? Where Barcode = ?", (not current_value, barcode,))
				break
			elif yes_no_answer == "no":
				update_inventory_yes_no.grid_forget()
				update_inventory_entry.grid(row=1, column=1, sticky='nsew')
				continue
		elif which_button != "Taxable":
			update_inventory_label.config(text=f"Current {which_button} is:\n" + str(current_value) + f"\nPlease Enter Item's New {which_button}")
			root.wait_variable(state_manager.update_inventory_var)
			new_value = state_manager.update_inventory_var.get()
			update_inventory_label.config(text=f"New {which_button} will be:\n" + new_value + "\nIs this correct?")
			update_inventory_entry.grid_forget()
			update_inventory_yes_no.grid(row=1, column=1, sticky='nsew')
			root.wait_variable(state_manager.yes_no_var)
			yes_no_answer = state_manager.yes_no_var.get()
			update_inventory_yes_no.grid_forget()
			if yes_no_answer == "yes":
				update_cursor.execute("UPDATE INVENTORY SET %s = ? WHERE %s = ?" % (which_button, which_button), (new_value, current_value, ))
				break
			elif yes_no_answer == "no":
				update_inventory_entry.grid(row=1, column=1, sticky='nsew')
				continue
	update_inventory_yes_no.grid_forget()
	update_buttons_frame.grid(column = 1, row=1, sticky='nsew')
	update_inventory_label.config(text="What would you\nlike to update?")
	update_conn.commit()
	update_conn.close()
	admin_frame.tkraise()

def no_sale(event=None):
	invisible_entry.delete(0, tk.END)
	printer.cashdraw(pin=2)
	printer.textln(("-" * 22) + " NS " + ("-" * 22))
	printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 33) + datetime.now().strftime("%H:%M"))
	printer.ln(2)
	#printer.cut()

	

def go_back():
	global state_manager
	# Logic for back button during adding an item
	# If you're not on the first page, go back one
	# If state_manager.add_item_index is 0, it should stay as such
	if state_manager.add_item_index!=0:
		state_manager.add_item_index-=1
	# Acording to what state_manager.add_item_index you've gone back to, update
	# label so it is asking for correct information
	match state_manager.add_item_index:
		case 0:
			add_item_label.config(text="Please enter item's barcode:")
		case 1:
			add_item_label.config(text="Please enter item's name:")
		case 2:
			add_item_label.config(text="Please enter item's price:")
			add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
			add_item_button.grid(column=1, row=2, sticky='ew')
			add_item_yes_no.grid_forget()
		case 3:
			add_item_frame.tkraise()
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			add_item_yes_no.grid(column=1, row=2, sticky='nsew')
			add_item_label.config(text="Is the item taxable?")
			on_add_item_enter()
		case 4:
			add_item_label.config(text="Please enter the category:")
			add_item_listbox_frame.tkraise()
		case 5:
			add_item_label.config(text="Please enter the quantity:")
		
def reenter_button_pressed(which_button):
	# Essentially go back to the add item interface
	reenter_frame.grid_forget()
	add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
	add_item_button.grid(column=1, row=2, sticky='ew')
	global state_manager
	state_manager.reentering = True
	# Add item logic looks for reentering flag
	# Set flag, and reenter the logic, setting labels
	# and any necessary buttons accordingly
	match which_button:
		case "barcode":
			state_manager.add_item_index=0
			add_item_label.config(text="Please enter item's barcode:")
		case "name":
			state_manager.add_item_index=1
			add_item_label.config(text="Please enter the item's name:")
		case "price":
			state_manager.add_item_index=2
			add_item_label.config(text="Please enter the item's price:")
		case "taxable":
			state_manager.add_item_index=3
			add_item_label.config(text="Is the item taxable?")
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			add_item_yes_no.grid(column=1, row=2, sticky='nsew')
			on_add_item_enter()
		case "category":
			state_manager.add_item_index=4
			add_item_listbox_frame.tkraise()
		case "quantity":
			state_manager.add_item_index=5
			add_item_label.config(text="Please enter the Quantity:")

def on_add_item_enter(event=None):
	item_info_entered = add_item_entry.get().strip()
	add_item_entry.delete(0, tk.END)
	global state_manager
	
	
	match state_manager.add_item_index:
		case 0:
			state_manager.add_item_object.c.execute("SELECT * FROM INVENTORY WHERE BARCODE=?", (item_info_entered,))
			results = state_manager.add_item_object.c.fetchall()
			if results:
				found_item_info = results[0]
				state_manager.add_item_object.name = found_item_info[1]
				state_manager.add_item_object.price = found_item_info[2]
				state_manager.add_item_object.taxable = found_item_info[3]
				state_manager.add_item_object.barcode = found_item_info[4]
				state_manager.add_item_object.old_barcode = found_item_info[4]
				state_manager.add_item_object.quantity = found_item_info[5]
				state_manager.add_item_object.category = found_item_info[6]
				state_manager.add_item_index = 5
				state_manager.updating_existing_item = True
				on_add_item_enter()
			elif not results:
				state_manager.add_item_object.barcode = item_info_entered
				if not reentering:
					add_item_label.config(text="Please enter item's name:")
					state_manager.add_item_index+=1
				elif reentering:
					state_manager.add_item_index=5
					on_add_item_enter()
		case 1:
			state_manager.add_item_object.name = item_info_entered
			if not reentering:
				add_item_label.config(text="Please enter item's price:")
				state_manager.add_item_index+=1
			elif reentering:
				state_manager.add_item_index=5
				on_add_item_enter()
		case 2:
			state_manager.add_item_object.price = item_info_entered
			if not reentering:
				add_item_label.config(text="Is the item Taxable?")
				add_item_yes_no.grid(column=1, row=2, sticky='nsew')
				add_item_button.grid_forget()
				add_item_entry.grid_forget()
				state_manager.add_item_index+=1
				on_add_item_enter()
			elif reentering:
				state_manager.add_item_index=5
				on_add_item_enter()
		case 3:
			root.wait_variable(state_manager.yes_no_var)
			yes_no_answer = state_manager.yes_no_var.get()
			if yes_no_answer == "yes":
				add_item_entry.delete(0, tk.END)
				add_item_entry.insert(tk.END, 1)
			else:
				add_item_entry.delete(0, tk.END)
				add_item_entry.insert(tk.END, 0)
			state_manager.add_item_object.taxable = add_item_entry.get()
			if not state_manager.reentering:
				add_item_yes_no.grid_forget()
				add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
				add_item_button.grid(column=1, row=2, sticky='ew')
				add_item_label.config(text="Please enter the category:")
				add_item_listbox_frame.tkraise()
				state_manager.add_item_index+=1
			elif state_manager.reentering:
				state_manager.add_item_index=5
				on_add_item_enter()
		case 4:
			add_item_frame.tkraise()
			add_item_entry.focus_force()
			state_manager.add_item_object.category = item_info_entered
			if not reentering:
				add_item_label.config(text = "Please enter the Quantity:")
				state_manager.add_item_index+=1
			elif reentering:
				state_manager.add_item_index=5
				on_add_item_enter()
		case 5:
			add_item_label_text = add_item_label.cget("text")
			if not state_manager.reentering and not state_manager.updating_existing_item:
				state_manager.add_item_object.quantity = item_info_entered
			elif not state_manager.reentering & state_manager.updating_existing_item:
				pass
			elif state_manager.reentering and add_item_label_text == "Please enter the Quantity:":
				state_manager.add_item_object.quantity = item_info_entered
				state_manager.reentering = False
			else:
				state_manager.reentering = False
			state_manager.add_item_index+=1
			add_item_label.config(text="Confirm item info is correct: ")
			confirm_string = ("Name: " + state_manager.add_item_object.name + "\nPrice: " + str(state_manager.add_item_object.price) + " | \tBarcode: " + str(state_manager.add_item_object.barcode) + "\nQty: " + str(state_manager.add_item_object.quantity) + " | Category: " + state_manager.add_item_object.category + "\tTax?: ")
			
			if state_manager.add_item_object.taxable == "1":
				confirm_string += "Y"
			else: 
				confirm_string += "N"
				
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			item_info_confirmation.grid(column=1, row=1, sticky='ew', padx=5)
			add_item_yes_no.grid(column=1, row=2, sticky='nsew')
			back_button.grid_forget()
			item_info_confirmation.delete("1.0", "end")
			item_info_confirmation.insert(tk.END, confirm_string)
			root.wait_variable(state_manager.yes_no_var)
			yes_no_answer = state_manager.yes_no_var.get()
			if yes_no_answer == "yes" and state_manager.coming_from_register:
				try:
					state_manager.add_item_object.commit_item()
				except sqlite3.Error as e:
					print("Error entering item when coming from register")
				finally:
					state_manager.add_item_index=0
					add_item_yes_no.grid_forget()
					item_info_confirmation.grid_forget()
					add_item_entry.grid(row=1, column=1, sticky='ew', pady=15)
					enter_register_frame()
					return
			elif yes_no_answer == "yes" and state_manager.updating_existing_item:
				state_manager.updating_existing_item = False
				state_manager.add_item_object.update_item(state_manager.add_item_object.old_barcode)
				state_manager.add_item_index = 0
				add_item_yes_no.grid_forget()
				item_info_confirmation.grid_forget()
				add_item_entry.grid(row=1, column=1, sticky='ew', pady=15)
				enter_add_item_frame()
				return
			elif yes_no_answer == "yes" and not state_manager.coming_from_register:
				try:
					state_manager.add_item_object.commit_item()
					item_info_confirmation.delete("1.0", "end")
					item_info_confirmation.grid_forget()
					add_item_label.config(text="Commit Successful!\n Enter Another Item?", font=("Arial", 50))
				except sqlite3.Error as e:
					add_item_label.config(text="ERROR")
				finally:
					pass
			elif yes_no_answer == "no":
				add_item_label.config(text="What would you like to change?")
				reenter_frame.grid(column = 1, row=1, sticky='nsew')
				add_item_yes_no.grid_forget()
				item_info_confirmation.grid_forget()
			root.wait_variable(state_manager.yes_no_var)
			yes_no_answer = state_manager.yes_no_var.get()
			if yes_no_answer == "yes":
				state_manager.add_item_index = 0
				enter_add_item_frame()
				
			elif yes_no_answer == "no":
				state_manager.add_item_index = 0
				admin_frame.tkraise()
				add_item_yes_no.grid_forget()
				add_item_entry.grid(row=1, column=1, sticky='ew', pady=15)
		case _:

			add_item_entry.delete(0, tk.END)
			add_item_entry.insert(tk.END, "ERROR")
	
def on_add_item_scrollbar_next(event=None):
	selected_index = add_item_listbox.curselection()
	selected_item = add_item_listbox.get(selected_index)
	add_item_entry.delete(0, tk.END)
	add_item_entry.insert(tk.END, selected_item)
	on_add_item_enter()
def run_x(event=None):
	x_conn = sqlite3.connect("RegisterDatabase")
	x_cursor = x_conn.cursor()
	printer.textln(("-" * 42))
	printer.textln(("-" * 14) + " Daily Report " + ("-" * 14))
	printer.textln(("-" * 12) + " " + datetime.today().strftime('%Y-%m-%d') + " " + datetime.now().strftime("%H:%M") + " " + ("-" * 12))
	printer.textln("-" * 42)
	printer.ln(2)

	for category in ("Cash Used", "CC Used", "Non-Tax", "Pre-Tax", "Tax"):
		x_cursor.execute('''SELECT SUM("%s") FROM SALES WHERE Date = ?''' % (category), (datetime.today().strftime('%Y-%m-%d'), ))
		results = x_cursor.fetchall()
		sum_in_question = results[0]
		rounded = f"{sum_in_question[0]:.2f}"
		spaces = 42 - len(category) - len(rounded)
		if category == "Cash Used" or category == "CC Used":
			spaces = 42 - len(category[:-5]) - len(rounded)
			printer.textln(f"{category[:-5]} Collected: " + (" " * spaces) + "$" + rounded)
		else:
			printer.textln(f"{category} Collected: " + (" " * spaces) + "$" + rounded)
	printer.cut
	

def process_return(event=None):
	global state_manager
	state_manager.new_transaction()
	state_manager.trans.is_returning = True
	register_functions_buttons_frame.grid_forget()
	additional_register_functions_label.config(text="Please scan the item(s) to return\nWhen done, press continue")
	additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')
	additional_register_functions_entry.focus_force()
	continue_button.grid(row=2, column=1, sticky='nsew')
	while True:
		while True:
			root.wait_variable(state_manager.return_var)
			entry = state_manager.return_var.get()
			if entry == "continue":
				break
			else:
				state_manager.trans.c.execute('''SELECT * FROM INVENTORY WHERE BARCODE=?''', (entry,))
				results = state_manager.trans.c.fetchall()
				row = results[0]
				state_manager.trans.sell_item(row[4])
				additional_register_functions_entry.delete(0, tk.END)
		additional_register_functions_label.config(text="Return the following item(s)?")
		additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
		additional_register_functions_yes_no.grid(row=2, column=1, sticky='nsew')
		additional_register_functions_text.delete("1.0", "end")
		for i in range(len(state_manager.trans.quantity_sold_list)):
			additional_register_functions_text.insert("end", str(state_manager.trans.quantity_sold_list[i][0]) + " | QTY: " + str(state_manager.trans.quantity_sold_list[i][1]) + "\n")
		additional_register_functions_yes_no.grid(row=2, column=1, sticky='nsew')
		continue_button.grid_forget()
		root.wait_variable(state_manager.yes_no_var)
		button_pressed = state_manager.yes_no_var.get()
		if button_pressed == "yes":
			for i in range(len(state_manager.trans.quantity_sold_list)):
				state_manager.trans.c.execute("UPDATE INVENTORY SET Quantity = Quantity + ? WHERE Barcode = ?", (int(state_manager.trans.quantity_sold_list[i][1]), state_manager.trans.quantity_sold_list[i][0]))
			break
		elif button_pressed == "no":
			additional_register_functions_label.config(text="Please scan the item(s) to return\nWhen done, press continue")
			additional_register_functions_yes_no.grid_forget()
			continue_button.grid(row=2, column=1, sticky='nsew')
			additional_register_functions_text.grid_forget()
			additional_register_functions_text.delete("1.0", "end")
			additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')
			state_manager.new_transaction()
	state_manager.trans.conn_inventory.commit()
	state_manager.trans.nontax *= -1
	state_manager.trans.pretax *= -1
	state_manager.trans.tax *= -1
	state_manager.trans.total *= -1
	state_manager.trans.complete_transaction()
	additional_register_functions_yes_no.grid_forget()
	register_functions_buttons_frame.grid(row=1, column=1, sticky='nsew')
	additional_register_functions_label.config(text="Select an Option")
	additional_register_functions_text.grid_forget()
	additional_register_functions_entry.grid_forget()
	return_conn = sqlite3.connect("RegisterDatabase")
	return_cursor = return_conn.cursor()
	return_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
	results = return_cursor.fetchall()
	row = results[0]
	return_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
	item_results = return_cursor.fetchall()
	print_receipt("return", row[0], item_results, row)
	enter_register_frame()


def return_invisible_entry_focus(event):
    invisible_entry.focus_set()
    return "break"

	

# =============================
# Widgets for Mode select frame
# =============================

mode_select_label = tk.Label(mode_select_frame, text="Please select a mode: ", font=("Arial", 50))
mode_select_label.grid(column=1, row=0, sticky='ew', pady=10)
register_mode_button = tk.Button(mode_select_frame, text="Enter Register Mode", font=("Arial", 50), command=lambda: enter_register_frame()).grid(column=1, row=1, sticky='ew', pady=10)
admin_mode_button = tk.Button(mode_select_frame, text="Enter Admin Mode", font=("Arial", 50), command=lambda: admin_frame.tkraise()).grid(column=1, row=2, sticky='ew', pady=10)

# ===============================
# Widgets for Register Mode frame
# ===============================


#Entry box where numbers user is typing are being displayed 
usr_entry = tk.Entry(register_frame, font=("Arial", 91), bg="black", fg="#68FF00", justify="right", width=15)
usr_entry.insert(tk.END, "$0.00")
usr_entry.grid(column=1, row=0, sticky='ew', padx=2)
usr_entry.bind("<FocusIn>", return_invisible_entry_focus)

# Invisible entry where user input actually occurs. Allows user entry to be untampered so 
# same entry box can be used for barcodes and numberic values alike
invisible_entry = tk.Entry(register_frame)
invisible_entry.place(x=-100, y=-100)
invisible_entry.bind("<Return>", process_sale)
for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
	invisible_entry.bind(f"<KeyRelease-KP_{key}>", number_pressed)
invisible_entry.bind("<KeyRelease-BackSpace>", clear)
invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: on_cash_cc(event, "cash"))
invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: on_cash_cc(event, "cc"))
invisible_entry.bind("<KeyRelease-KP_Multiply>", enter_void_frame)
invisible_entry.bind("<KeyRelease-KP_Divide>", cancel_trans)
invisible_entry.bind("<KeyRelease-KP_Subtract>", no_sale)

register_widgets_frame.grid(column=1, row=1, sticky='nsew')



new_frame = tk.Frame(register_widgets_frame)
new_frame.grid_columnconfigure(0, weight=1)
new_frame.grid(column=0, row=0, sticky='nsew')
# Box where program outputs current running total
total_entry = tk.Entry(new_frame, font=("Arial", 35), width=9)
total_entry.insert(tk.END, "$0.00")
total_entry.grid(column = 0, row = 0, sticky='nw')
total_entry.bind("<FocusIn>", return_invisible_entry_focus)

register_back_button = tk.Button(new_frame, text="Back", font=("Arial", 35), height=5, command = lambda: register_go_back())
register_back_button.grid(column = 0, row = 1, sticky='nw')

#Log of what is being sold 
sale_items = tk.Text(register_widgets_frame, width=29, font=("Arial", 35), padx=10)
sale_items.grid(column = 1, row = 0, sticky='e')
sale_items.bind("<FocusIn>", return_invisible_entry_focus)

register_add_item_prompt_label=tk.Label(register_add_item_prompt_frame, text="Item not found\nAdd it?", font=("Arial", 50))
register_add_item_prompt_label.grid(row=0, column=1, sticky='ew')

register_add_item_yes_no_frame=tk.Frame(register_add_item_prompt_frame)
register_add_item_yes_no_frame.grid_columnconfigure(0, weight=1)
register_add_item_yes_no_frame.grid_columnconfigure(1, weight=1)
register_add_item_yes_no_frame.grid(row=1, column=1, sticky='nsew')

register_add_item_yes_button=tk.Button(register_add_item_yes_no_frame, text="Yes", font=("Arial", 90), command = lambda: state_manager.yes_no_var.set("yes"))
register_add_item_yes_button.grid(row=0, column=0, sticky='nsew')

register_add_item_no_button=tk.Button(register_add_item_yes_no_frame, text="No", font=("Arial", 90), command = lambda: state_manager.yes_no_var.set("no"))
register_add_item_no_button.grid(row=0, column=1, sticky='nsew')

# ============================
# Widgets for Admin Mode frame 
# ============================
new_item_button = tk.Button(admin_frame, text = "Add New Item", font=("Arial", 50), height = 5, command = lambda: enter_add_item_frame()) 
new_item_button.grid(column = 0, row = 1, sticky='s', padx = 5, pady = 5, ipadx=10, ipady=10)

update_quantity_button = tk.Button(admin_frame, text = "Update\nInventory", font=("Arial", 50), height = 5, command = lambda: run_x())
update_quantity_button.grid(column=1, row=1, sticky='e', padx=5, pady=5, ipadx=10, ipady=10)


admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: mode_select_frame.tkraise()).grid(column = 0, row = 0, sticky='nw')

# ==========================
# Widgets for Add Item frame
# ==========================

add_item_label = tk.Label(add_item_frame, text="Please enter the item's barcode:", font=("Arial", 50), width=27)

add_item_button = tk.Button(add_item_frame, text="Next", font=("Arial", 50), command=lambda: on_add_item_enter())

back_button = tk.Button(add_item_frame, text="Back", font=("Arial", 50), command=lambda: go_back())

quit_button = tk.Button(add_item_frame, text="Quit", font=("Arial", 50), command = lambda: admin_frame.tkraise())

add_item_entry = tk.Entry(add_item_frame, font=("Arial", 50), width=15, justify="right")
add_item_entry.bind("<Return>", on_add_item_enter)

item_info_confirmation = tk.Text(add_item_frame, font=("Arial", 40), width=6, height=3)

yes_button = tk.Button(add_item_yes_no, text="Yes", font=("Arial", 150), command= lambda: state_manager.yes_no_var.set("yes"))

no_button = tk.Button(add_item_yes_no, text="No", font=("Arial", 150), command=lambda: state_manager.yes_no_var.set("no"))

yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
no_button.grid(column=1, row=0, sticky='nsew', padx=10)

# =========================
# Widgets for Listbox Frame
# =========================

add_item_listbox = tk.Listbox(add_item_listbox_frame, width=20, height=5, font=("Arial", 50))
add_item_scrollbar = tk.Scrollbar(add_item_listbox_frame, orient=tk.VERTICAL, width=40)

add_item_listbox.grid(row=1, column=1, sticky='nw')
add_item_scrollbar.grid(row=1, column=1, sticky='nse')

add_item_scrollbar_label = tk.Label(add_item_listbox_frame, text="Please select category:", font=("Arial", 50))
add_item_scrollbar_label.grid(column=1, row=0, sticky='nsew')

add_item_scrollbar_next = tk.Button(add_item_listbox_frame, text="Next", font=("Arial", 50), command=lambda: on_add_item_scrollbar_next())
add_item_scrollbar_next.grid(row=2, column=1, sticky='nsew')

add_item_scrollbar_back = tk.Button(add_item_listbox_frame, text="Back", font=("Arial", 50), command=lambda: go_back())
add_item_scrollbar_back.grid(column=1, row=3, sticky='nsew')

add_item_scrollbar_quit = tk.Button(add_item_listbox_frame, text="Quit", font=("Arial", 50), command=lambda: admin_frame.tkraise())
add_item_scrollbar_quit.grid(column=1, row=4, sticky='nsew')

for values in ("Camping", "Candy", "Cleaning", "Clothes", "Cookies/Chips", "Drinks", "Dry Goods", "Fishing", "Gifts", "Ice Cream", "Kitchenware", "Medicinal", "Paper Products", "Pool", "Propane", "Refrigerated", "RV", "Toiletries", "Toys"):
	add_item_listbox.insert(tk.END, values)

add_item_listbox.config(yscrollcommand= add_item_scrollbar.set)
add_item_scrollbar.config(command = add_item_listbox.yview)

# Buttons for options when user wants to correct one of their inputs

add_name_button = tk.Button(reenter_frame, text="Name", font=("Arial", 75), command = lambda: reenter_button_pressed("name"))
add_name_button.grid(row=0, column=0, sticky='nsew')

add_price_button = tk.Button(reenter_frame, text="Price", font=("Arial", 75), command = lambda: reenter_button_pressed("price"))
add_price_button.grid(row=0, column=1, sticky='nsew')

add_barcode_button = tk.Button(reenter_frame, text="Barcode", font=("Arial", 75), command = lambda: reenter_button_pressed("barcode"))
add_barcode_button.grid(row=1, column=0, sticky='nsew')

add_taxable_button = tk.Button(reenter_frame, text="Taxable", font=("Arial", 75), command = lambda: reenter_button_pressed("taxable"))
add_taxable_button.grid(row=1, column=1, sticky='nsew')

add_quantity_button = tk.Button(reenter_frame, text="Quantity", font=("Arial", 75), command = lambda: reenter_button_pressed("quantity"))
add_quantity_button.grid(row=2, column=0, sticky='nsew')

add_category_button = tk.Button(reenter_frame, text="Category", font=("Arial", 75), command = lambda: reenter_button_pressed("category"))
add_category_button.grid(row=2, column=1, sticky='nsew')

# ==================================
# Widgets for Update Inventory Frame
# ==================================

update_inventory_label=tk.Label(update_inventory_frame, text="What would you\nlike to update?", font=("Arial", 50))
update_inventory_label.grid(column=1, row=0, sticky='nsew')

update_inventory_entry=tk.Entry(update_inventory_frame, font=("Arial", 75), width=18)
update_inventory_entry.bind("<Return>", get_update_barcode)

update_buttons_frame.grid(column = 1, row=1, sticky='nsew')

update_yes_button = tk.Button(update_inventory_yes_no, text="Yes", font=("Arial", 150), command= lambda: state_manager.yes_no_var.set("yes"))

update_no_button = tk.Button(update_inventory_yes_no, text="No", font=("Arial", 150), command=lambda: state_manager.yes_no_var.set("no"))


update_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
update_no_button.grid(column=1, row=0, sticky='nsew', padx=10)

update_name_button = tk.Button(update_buttons_frame, text="Name", font=("Arial", 75), command = lambda: update_inventory("Name", None))
update_name_button.grid(row=0, column=0, sticky='nsew')

update_price_button = tk.Button(update_buttons_frame, text="Price", font=("Arial", 75), command = lambda: update_inventory("Price", None))
update_price_button.grid(row=0, column=1, sticky='nsew')

update_barcode_button = tk.Button(update_buttons_frame, text="Barcode", font=("Arial", 75), command = lambda: update_inventory("Barcode", None))
update_barcode_button.grid(row=1, column=0, sticky='nsew')

update_taxable_button = tk.Button(update_buttons_frame, text="Taxable", font=("Arial", 75), command = lambda: update_inventory("Taxable", None))
update_taxable_button.grid(row=1, column=1, sticky='nsew')

update_quantity_button = tk.Button(update_buttons_frame, text="Quantity", font=("Arial", 75), command = lambda: update_inventory("Quantity", None))
update_quantity_button.grid(row=2, column=0, sticky='nsew')

update_category_button = tk.Button(update_buttons_frame, text="Category", font=("Arial", 75), command = lambda: update_inventory("Category", None))
update_category_button.grid(row=2, column=1, sticky='nsew')

# ==========================================
# Widgets for Additional Register Functions 
# ==========================================

additional_register_functions_label = tk.Label(additional_register_functions_frame, text="Select an Option", font=("Arial", 50))
additional_register_functions_label.grid(column = 1, row = 0, sticky='ew')

register_functions_buttons_frame=tk.Frame(additional_register_functions_frame)
register_functions_buttons_frame.grid_columnconfigure(0, weight=1)
register_functions_buttons_frame.grid_columnconfigure(1, weight=1)
register_functions_buttons_frame.grid(row=1, column=1, sticky='nsew')

last_button = tk.Button(register_functions_buttons_frame, text="Void Last\nTransaction", font=("Arial", 70), command = lambda:void_transaction("last"))
last_button.grid(row=0, column=0, sticky='nsew')

number_button = tk.Button(register_functions_buttons_frame, text="Void by\nReference #", font=("Arial", 70), command = lambda:void_transaction("ref"))
number_button.grid(row=0, column=1, sticky='nsew')

print_receipt_button = tk.Button(register_functions_buttons_frame, text="Print a Receipt", font=("Arial", 70))
print_receipt_button.grid(row=1, column=0, sticky='nsew')

make_return_button = tk.Button(register_functions_buttons_frame, text="Process Return", font=("Arial", 70), command = lambda:process_return())
make_return_button.grid(row=1, column=1, sticky='nsew')

run_x_button = tk.Button(register_functions_buttons_frame, text="Run X", font=("Arial", 50), command = lambda:run_x())
run_x_button.grid(row=2, column=0, sticky='nsew')

continue_button = tk.Button(additional_register_functions_frame, text="Continue", font=("Arial", 50), command= lambda: state_manager.reference_number_var.set("continue"))

additional_register_functions_entry = tk.Entry(additional_register_functions_frame, font=("Arial", 50), justify="right")
additional_register_functions_entry.bind("<Return>", on_additional_register_functions_entry)

additional_register_functions_text = tk.Text(additional_register_functions_frame, width=30, height=3, font=("Arial", 40))


additional_register_functions_yes_button = tk.Button(additional_register_functions_yes_no, text="Yes", font=("Arial", 150), command= lambda: state_manager.yes_no_var.set("yes"))
additional_register_functions_no_button = tk.Button(additional_register_functions_yes_no, text="No", font=("Arial", 150), command=lambda: state_manager.yes_no_var.set("no"))


additional_register_functions_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
additional_register_functions_yes_button.grid(column=1, row=0, sticky='nsew', padx=10)

mode_select_frame.tkraise()
root.mainloop()


