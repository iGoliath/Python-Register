from stateManager import StateManager
import tkinter as tk
import sqlite3

def check_item_exists(state_manager: StateManager, barcode: str, add_item_label: tk.Label) -> bool:
    """This function is the pre-requisite to adding an item. We want to
    make sure that the item does not already exist."""

    state_manager.cursor.execute("SELECT * FROM INVENTORY WHERE BARCODE=?", (barcode,))
    results = state_manager.cursor.fetchall()
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
        return True
    elif not results:
        enter_item_barcode(state_manager, barcode, add_item_label) 
        return False
		
def enter_item_barcode(state_manager: StateManager, barcode: str, 
                       add_item_label: tk.Label) -> bool:
    """Set the barcode variable of our add item object. If we are re-entering,
      skip to confirmation page"""

    state_manager.add_item_object.barcode = barcode
    if not state_manager.reentering:
        state_manager.add_item_index += 1
        add_item_label.config(text="Please enter item's name:")
    elif state_manager.reentering:
        state_manager.add_item_index = 5
        return True

def enter_item_name(state_manager: StateManager, name: str,
                     add_item_label: tk.Label) -> bool:
    """Same as barcode. Set variable to entered name, and check whether
    or not the user is re-entering or not."""

    state_manager.add_item_object.name = name
    if not state_manager.reentering:
        add_item_label.config(text="Please enter item's price:")
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = 5
        return True

def enter_item_price(
        state_manager: StateManager, price: float,
        add_item_label: tk.Label, add_item_yes_no: tk.Frame,
        add_item_button: tk.Button, add_item_entry: tk.Entry) -> bool:
    """Set the add item object's price. If we are not re-entering, change
    the necessary widgets to ask user whether the item is taxable."""

    state_manager.add_item_object.price = round(float(price[1:]), 2)
    print(state_manager.add_item_object.price)
    if not state_manager.reentering:
        add_item_label.config(text="Is the item Taxable?")
        add_item_yes_no.grid(column=1, row=2, sticky='nsew')
        add_item_button.grid_forget()
        add_item_entry.grid_forget()
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = 5
        return True

def enter_item_taxable(
        yes_no: str, state_manager: StateManager, root: tk.Tk,
        add_item_yes_no: tk.Frame, add_item_entry: tk.Entry,
        add_item_button: tk.Button, add_item_label: tk.Label,
        add_item_listbox_frame: tk.Frame) -> bool:
    """Waits for the user to click yes/no for whether the item is taxable. 
    Set the add_item_object variable accordingly, and clean up widgets."""

    #root.wait_variable(state_manager.yes_no_var)
    #yes_no_answer = state_manager.yes_no_var.get()
    if yes_no == "yes":
        state_manager.add_item_object.taxable = "1"
    else:
        state_manager.add_item_object.taxable = "0"
    if not state_manager.reentering:
        add_item_yes_no.grid_forget()
        add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
        add_item_button.grid(column=1, row=2, sticky='ew')
        add_item_label.config(text="Please enter the category:")
        add_item_listbox_frame.tkraise()
        state_manager.add_item_index+=1
        return False
    elif state_manager.reentering:
        state_manager.add_item_index=5
        return True

def enter_item_category(
        state_manager: StateManager, add_item_frame: tk.Frame, 
        add_item_entry: tk.Entry, add_item_label: tk.Label,
          add_item_listbox: tk.Listbox) -> bool:
    """Once user selects a category from listbox, set variable, and 
    clean up widgets.""" 

    state_manager.add_item_object.category = add_item_listbox.get(add_item_listbox.curselection())
    add_item_frame.tkraise()
    add_item_entry.focus_force()
    if not state_manager.reentering:
        add_item_label.config(text="Please enter the Quantity:")
        state_manager.add_item_index+=1
    elif state_manager.reentering:
        state_manager.add_item_index=5
        return True


def enter_item_confirmation(
        state_manager: StateManager, quantity: int, add_item_label: tk.Label,
        add_item_entry: tk.Entry, add_item_button: tk.Button,
        item_info_confirmation: tk.Text, add_item_yes_no: tk.Frame,
        back_button: tk.Button, root: tk.Tk, reenter_frame: tk.Frame) -> bool:
    """Last step of the 'add item' process. """
    if state_manager.updating_existing_item:
        if state_manager.reentering:
            state_manager.reentering = False
        elif state_manager.reentering_quantity:
            state_manager.add_item_object.quantity = quantity
            state_manager.reentering_quantity = False
    elif not state_manager.reentering:
        state_manager.add_item_object.quantity = quantity
    elif state_manager.reentering:
        state_manager.reentering = False
    elif state_manager.reentering_quantity:
        state_manager.add_item_object.quantity = quantity
        state_manager.reentering_quantity = False
    

    add_item_label.config(text="Confirm item info is correct: ")
    add_item_entry.grid_forget()
    add_item_button.grid_forget()
    item_info_confirmation.grid(column=1, row=1, sticky='ew', 
                                     padx=5)
    add_item_yes_no.grid(column=1, row=2, sticky='nsew')
    back_button.grid_forget()
    print_confirmation_info(state_manager, item_info_confirmation)
    root.wait_variable(state_manager.yes_no_var)
    yes_no_answer = state_manager.yes_no_var.get()

    if yes_no_answer == 'yes':
        if state_manager.coming_from_register:
            yes_register(
                state_manager, add_item_yes_no, item_info_confirmation,
                add_item_entry)
            return True
        elif state_manager.updating_existing_item:
           yes_existing(
               state_manager, add_item_yes_no, item_info_confirmation,
               add_item_entry)
           return False
        elif not state_manager.coming_from_register:
            yes_not_register(
                state_manager, add_item_label, item_info_confirmation)
            return False
    elif yes_no_answer == 'no':
        add_item_label.config(text="What would you like to change?")
        reenter_frame.grid(column = 1, row=1, sticky='nsew')
        add_item_yes_no.grid_forget()
        item_info_confirmation.grid_forget()


def yes_register(
        state_manager: StateManager, add_item_yes_no: tk.Frame,
        item_info_confirmation: tk.Text, add_item_entry: tk.Entry) -> None:
    """Commit the changes when coming from register frame"""

    try:
        state_manager.add_item_object.commit_item()
    except sqlite3.Error as e:
        print(f"{e} occured when entering item and"
                "coming from register")
    finally:
        state_manager.add_item_index = 0
        add_item_yes_no.grid_forget()
        item_info_confirmation.grid_forget()
        add_item_entry.grid(row=1, column=1, sticky='ew', 
                                    pady=15)
        
def yes_existing(
        state_manager: StateManager, add_item_yes_no: tk.Frame,
        item_info_confirmation: tk.Text, add_item_entry: tk.Entry) -> None:
    """Commit changes when updating an existing item"""
    state_manager.updating_existing_item = False

    try:
        state_manager.add_item_object.update_item(state_manager.add_item_object.old_barcode)
    except sqlite3.Error as e:
        print(f"{e} when updating an existing item")
    finally:
        state_manager.add_item_index = 0
        add_item_yes_no.grid_forget()
        item_info_confirmation.grid_forget()
        add_item_entry.grid(row = 1, column = 1, sticky = 'ew', pady = 15)

def yes_not_register(
        state_manager: StateManager, add_item_label: tk.Label,
        item_info_confirmation: tk.Text) -> None:
    
    """Commit changes when adding item normally"""

    try:
        state_manager.add_item_object.commit_item()
    except sqlite3.Error as e:
        print(f"{e} when committing item normally")
        add_item_label.config(text="Commit errored. Please try again")
        #Return user to step 1
    finally:
        item_info_confirmation.delete("1.0", "end")
        item_info_confirmation.grid_forget()
        add_item_label.config(text="Commit successful!\nEnter another item?")


def print_confirmation_info(state_manager: StateManager, item_info_confirmation: tk.Text) -> None:

    """Print the current information of the item the user has entered
    to the confirmation box."""

    item_info_confirmation.delete("1.0", "end")
    item_info_confirmation.insert(tk.END, "Name: " + state_manager.add_item_object.name)
    item_info_confirmation.insert(tk.END, "\nPrice : $" + f'{state_manager.add_item_object.price:.2f}')
    if state_manager.add_item_object.taxable == "1":
        item_info_confirmation.insert(tk.END, "Tax?: Yes", "justify_right")
    else:
        item_info_confirmation.insert(tk.END, "Tax? : No", "justify_right")
    item_info_confirmation.insert(tk.END, "\nCat.: " + state_manager.add_item_object.category)
    item_info_confirmation.insert(tk.END, "Qty: " + str(state_manager.add_item_object.quantity), "justify_right")
    item_info_confirmation.insert(tk.END, "\nBarcode: " + state_manager.add_item_object.barcode)
    
    

    