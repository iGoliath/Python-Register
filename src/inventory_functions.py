from state_manager import StateManager
from widget_manager import * 
import tkinter as tk
import sqlite3

def update_barcode(state_manager: StateManager, barcode: str) -> None:
    state_manager.cursor.execute('''INSERT INTO updated_barcodes SELECT item_id, barcode, ? FROM Inventory WHERE Barcode = ?''', (barcode, barcode.lstrip('0')))
    state_manager.cursor.execute('''UPDATE Inventory SET Barcode = ? WHERE Barcode = ?''', (barcode, barcode.lstrip('0')))
    state_manager.conn.commit()
def check_item_exists(state_manager: StateManager, barcode: str) -> bool:
    """This function is the pre-requisite to adding an item. We want to
    make sure that the item does not already exist."""

    if (len(barcode.lstrip('0')) != (len(barcode))):
        update_barcode(state_manager, barcode)
    
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
        state_manager.add_item_object.subcategory = found_item_info[7]
        state_manager.add_item_object.vendor = found_item_info[8]
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        state_manager.updating_existing_item = True
        return True
    elif not results:
        enter_item_barcode(state_manager, barcode) 
        return False
		
def enter_item_barcode(state_manager: StateManager, barcode: str) -> bool:
    """Set the barcode variable of our add item object. If we are re-entering,
      skip to confirmation page"""

    state_manager.add_item_object.barcode = barcode
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_name(state_manager: StateManager, name: str) -> bool:
    """Same as barcode. Set variable to entered name, and check whether
    or not the user is re-entering or not."""

    state_manager.add_item_object.name = name
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_price(
        state_manager: StateManager, price: float) -> bool:
    """Set the add item object's price. If we are not re-entering, change
    the necessary widgets to ask user whether the item is taxable."""

    state_manager.add_item_object.price = round(float(price[1:]), 2)
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_taxable(
        yes_no: str, state_manager: StateManager) -> bool:
    """Waits for the user to click yes/no for whether the item is taxable. 
    Set the add_item_object variable accordingly, and clean up widgets."""

    if yes_no == "yes":
        state_manager.add_item_object.taxable = 1
    else:
        state_manager.add_item_object.taxable = 0
    if not state_manager.reentering:
        state_manager.add_item_index+=1
        return False
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_category(state_manager: StateManager, ui: WidgetManager) -> bool:
    """Once user selects a category from listbox, set variable, and 
    clean up widgets.""" 

    state_manager.add_item_object.category = ui.add_category_listbox.get(ui.add_category_listbox.curselection())

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_subcategory(state_manager: StateManager, ui: WidgetManager) -> bool:

    state_manager.add_item_object.subcategory = ui.add_subcategory_listbox.get(ui.add_subcategory_listbox.curselection())

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_vendor(state_manager: StateManager, ui: WidgetManager) -> bool:

    state_manager.add_item_object.vendor = ui.add_vendor_listbox.get(ui.add_vendor_listbox.curselection())

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True

def enter_item_confirmation(
        state_manager: StateManager, quantity: int, root: tk.Tk,
        ui: WidgetManager) -> bool:
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
        ui.add_quantity_label.config(text="Please enter item's quantity:")
        state_manager.add_item_object.quantity = quantity
        state_manager.reentering_quantity = False
    

    ui.add_item_label.config(text="Confirm item info is correct: ")
    print_confirmation_info(state_manager, ui.item_info_confirmation)
    root.wait_variable(state_manager.yes_no_var)
    yes_no_answer = state_manager.yes_no_var.get()

    if yes_no_answer == 'yes':
        if state_manager.coming_from_register:
            yes_register(state_manager, ui)
            return True
        elif state_manager.updating_existing_item:
           yes_existing(state_manager, ui)
           return False
        elif not state_manager.coming_from_register:
            yes_not_register(state_manager, ui)
            return False
    elif yes_no_answer == 'no':
        return None


def yes_register(
        state_manager: StateManager, ui: WidgetManager) -> None:
    """Commit the changes when coming from register frame"""

    try:
        state_manager.add_item_object.commit_item()
    except sqlite3.Error as e:
        print(f"{e} occured when entering item and"
                "coming from register")
    finally:
        state_manager.add_item_index = 0
        
def yes_existing(
        state_manager: StateManager, ui: WidgetManager) -> None:
    """Commit changes when updating an existing item"""
    state_manager.updating_existing_item = False

    try:
        state_manager.add_item_object.update_item(state_manager.add_item_object.old_barcode)
    except sqlite3.Error as e:
        print(f"{e} when updating an existing item")
    finally:
        state_manager.add_item_index = 0

def yes_not_register(
        state_manager: StateManager, ui: WidgetManager) -> None:
    
    """Commit changes when adding item normally"""

    try:
        state_manager.add_item_object.commit_item()
    except sqlite3.Error as e:
        print(f"{e} when committing item normally")
        ui.add_item_label.config(text="Commit errored. Please try again")
        #Return user to step 1
    finally:
        ui.item_info_confirmation.delete("1.0", "end")

def print_confirmation_info(state_manager: StateManager, item_info_confirmation: tk.Text) -> None:

    """Print the current information of the item the user has entered
    to the confirmation box."""

    item_info_confirmation.delete("1.0", "end")
    item_info_confirmation.insert(tk.END, "Name: " + state_manager.add_item_object.name)
    item_info_confirmation.insert(tk.END, "\nPrice : $" + f'{state_manager.add_item_object.price:.2f}')
    if state_manager.add_item_object.taxable == 1:
        item_info_confirmation.insert(tk.END, " | Tax?: Yes", "justify_right")
    else:
        item_info_confirmation.insert(tk.END, " | Tax? : No", "justify_right")
    item_info_confirmation.insert(tk.END, "\nCat.: " + state_manager.add_item_object.category)
    item_info_confirmation.insert(tk.END, f"\nSub Cat.: {state_manager.add_item_object.subcategory}")
    item_info_confirmation.insert(tk.END, "\nBarcode: " + str(state_manager.add_item_object.barcode))
    item_info_confirmation.insert(tk.END, " | Qty: " + str(state_manager.add_item_object.quantity), "justify_right")
    item_info_confirmation.insert(tk.END, f"\nVendor: {state_manager.add_item_object.vendor}")
    
    

    