import sqlite3
import tkinter as tk
from decimal import Decimal

from .add_item_data import Dec4
from .state_manager import StateManager
from .widget_manager import WidgetManager


def update_barcode(state_manager: StateManager, barcode: str) -> None:
    try:
        state_manager.cursor.execute(
            """INSERT INTO updated_barcodes SELECT item_id, item_barcode, ? FROM inventory WHERE item_barcode = ?""",
            (barcode, barcode.lstrip("0")),
        )
        state_manager.cursor.execute(
            """UPDATE inventory SET item_barcode = ? WHERE item_barcode = ?""",
            (barcode, barcode.lstrip("0")),
        )
        state_manager.conn.commit()
    except sqlite3.Error as e:
        print(
            f"Error when updating item's barcode. inventory_functions line 9/10. Error: {e}"
        )
        state_manager.conn.rollback()


def check_item_exists(state_manager: StateManager, barcode: str) -> bool:
    """This function is the pre-requisite to adding an item. We want to
    make sure that the item does not already exist."""

    if len(barcode.lstrip("0")) != (len(barcode)):
        update_barcode(state_manager, barcode)

    results = state_manager.cursor.execute(
        "SELECT * FROM inventory WHERE item_barcode = ?", (barcode,)
    ).fetchall()
    if results:
        found_item_info = results[0]
        state_manager.add_item_dict.name = found_item_info["item_name"]
        state_manager.add_item_dict.price = found_item_info["item_price"]
        state_manager.add_item_dict.taxable = found_item_info["item_taxable"]
        state_manager.add_item_dict.barcode = found_item_info["item_barcode"]
        state_manager.add_item_dict.old_barcode = found_item_info["item_barcode"]
        state_manager.add_item_dict.quantity = found_item_info["item_quantity"]
        category = state_manager.cursor.execute(
            """SELECT category_name FROM categories WHERE category_id = ?""",
            (found_item_info["category_id"],),
        ).fetchone()
        state_manager.add_item_dict.category = (
            category["category_name"] if category else None
        )
        subcategory = state_manager.cursor.execute(
            """SELECT category_name FROM categories WHERE category_id = ?""",
            (found_item_info["subcategory_id"],),
        ).fetchone()
        state_manager.add_item_dict.subcategory = (
            subcategory["category_name"] if subcategory else None
        )
        vendor = state_manager.cursor.execute(
            """SELECT vendor_name FROM vendors WHERE vendor_id = ?""",
            (found_item_info["vendor_id"],),
        ).fetchone()
        state_manager.add_item_dict.vendor = vendor["vendor_name"] if vendor else None
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        state_manager.updating_existing_item = True
        return True
    elif not results:
        enter_item_barcode(state_manager, barcode)
        return False


def enter_item_barcode(state_manager: StateManager, barcode: str) -> bool:
    """Set the barcode variable of our add item object. If we are re-entering,
    skip to confirmation page"""

    state_manager.add_item_dict.barcode = barcode
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_name(state_manager: StateManager, name: str) -> bool:
    """Same as barcode. Set variable to entered name, and check whether
    or not the user is re-entering or not."""

    state_manager.add_item_dict.name = name
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_price(state_manager: StateManager, price: Decimal) -> bool:
    """Set the add item object's price. If we are not re-entering, change
    the necessary widgets to ask user whether the item is taxable."""

    state_manager.add_item_dict.price = (Decimal(price) / Decimal("100")).quantize(
        Decimal("0.01")
    )
    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_taxable(yes_no: str, state_manager: StateManager) -> bool:
    """Waits for the user to click yes/no for whether the item is taxable.
    Set the add_item_dict variable accordingly, and clean up widgets."""

    if yes_no == "1":
        state_manager.add_item_dict.taxable = 1
    elif yes_no == "0":
        state_manager.add_item_dict.taxable = 0

    if not state_manager.reentering:
        state_manager.add_item_index += 1
        return False
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_category(state_manager: StateManager, category: str) -> bool:
    """Once user selects a category from listbox, set variable, and
    clean up widgets."""
    state_manager.add_item_dict.category = category

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_subcategory(state_manager: StateManager, subcategory: str) -> bool:

    state_manager.add_item_dict.subcategory = subcategory

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_vendor(state_manager: StateManager, vendor: str) -> bool:

    state_manager.add_item_dict.vendor = vendor

    if not state_manager.reentering:
        state_manager.add_item_index += 1
    elif state_manager.reentering:
        state_manager.add_item_index = state_manager.ADD_ITEM_LAST_STEP
        return True


def enter_item_confirmation(
    state_manager: StateManager, quantity: int, ui: WidgetManager, skipping_ahead=False
) -> bool:
    """Last step of the 'add item' process."""
    if not skipping_ahead:
        if state_manager.updating_existing_item:
            if state_manager.reentering:
                state_manager.reentering = False
            elif state_manager.reentering_quantity:
                state_manager.add_item_dict.quantity = Dec4(quantity)
                state_manager.reentering_quantity = False
        elif not state_manager.reentering:
            state_manager.add_item_dict.quantity = Dec4(quantity)
        elif state_manager.reentering:
            state_manager.reentering = False
        elif state_manager.reentering_quantity:
            state_manager.add_item_dict.quantity = Dec4(quantity)
            state_manager.reentering_quantity = False

    ui.show_frame("add_item")


def yes_register(state_manager: StateManager) -> None:
    """Commit the changes when coming from register frame"""

    try:
        state_manager.commit_item()
    except sqlite3.Error as e:
        print(f"{e} occured when entering item and" "coming from register")
    finally:
        state_manager.add_item_index = 0


def yes_existing(state_manager: StateManager) -> None:
    """Commit changes when updating an existing item"""
    state_manager.updating_existing_item = False

    try:
        state_manager.update_item(state_manager.add_item_dict.old_barcode)
    except sqlite3.Error as e:
        print(f"{e} when updating an existing item")
    finally:
        state_manager.add_item_index = 0


def yes_not_register(state_manager: StateManager) -> None:
    """Commit changes when adding item normally"""

    try:
        state_manager.commit_item()
    except sqlite3.Error as e:
        print(f"{e} Error when committing item normally")
        # Return user to step 1
