from Register import *
import tkinter as tk
import pytest
import sqlite3



@pytest.fixture(scope="function")
def register_instance():
    root = tk.Tk()
    register = Register(root)
    pygame.mixer.init()
    root.withdraw()
    root.update()
    yield register
    root.destroy()

conn = sqlite3.connect("/tmp/RegisterDatabase")
c = conn.cursor()

def test_basic_sale_cash(register_instance):
    """Sale of one item, no specified cash amount"""

    global c
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.on_cash()


    c.execute('SELECT "Non-Tax", "Cash Used" FROM sales WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == 1.23
    assert row[1] == 1.23

def test_basic_sale_cc(register_instance):
    """Sale of one item, no specified cc amount"""

    global c
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.on_cc()

    c.execute('SELECT "Non-Tax", "CC Used" FROM sales WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == 1.23
    assert row[1] == 1.23

def test_sale_cash_cc(register_instance):
    """Sale of one item. $1.00 is paid in cash, and the rest CC"""

    global c
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry.insert(tk.END, "100")
    register_instance.on_cash()
    register_instance.on_cc()

    c.execute('SELECT "Non-Tax", "Cash Used", "CC Used" FROM sales WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == 1.23
    assert row[1] == 1.00
    assert row[2] == 0.23

def test_sale_cc_cash(register_instance):
    """Sale of one item. $1.00 is paid in CC, and the rest Cash"""
    global c
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry.insert(tk.END, "100+")
    register_instance.on_cc()
    register_instance.on_cash()

    c.execute('SELECT "Non-Tax", "Cash Used", "CC Used" FROM sales WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == 1.23
    assert row[1] == 0.23
    assert row[2] == 1.00

def test_cc_invalid(register_instance):
    """Sale of one item. The user enters an amount to be paid in CC that 
    exceeds the balance. Register should pause the sale and print to the
    user that this is invalid. Sales ending in a CC amount should not
    result in any change needing to be given."""

    global c
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry.insert(tk.END, "124+")
    register_instance.on_cc()

    result = register_instance.ui.total_entry.get()
    assert result == "$0.00ERR: CC"

def test_quantity_decrement_single(register_instance):

    global c

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    quantity = row[0]
    
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.on_cash()

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    new_quantity = row[0]

    assert new_quantity == (quantity - 1)

def test_quantity_decrement_double(register_instance):

    global c

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    item_one_starting_quantity = row[0]

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test1", ))
    results = c.fetchall()
    row = results[0]

    item_two_starting_quantity = row[0]

    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry.insert(tk.END, "Test1")
    register_instance.process_sale()
    register_instance.on_cash()

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    item_one_final_quantity = row[0]

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test1", ))
    results = c.fetchall()
    row = results[0]

    item_two_final_quantity = row[0]

    assert item_one_final_quantity == (item_one_starting_quantity - 2)
    assert item_two_final_quantity == (item_two_starting_quantity - 1)

def test_basic_return(register_instance):

    global c

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchone()[0]
    starting_quantity = results

    register_instance.process_return()
    register_instance.ui.invisible_entry.insert(tk.END, "Test")
    register_instance.process_sale()
    register_instance.state_manager.return_var.set("cash")

    c.execute('SELECT Quantity FROM inventory where Barcode = ?', ("Test", ))
    results = c.fetchone()[0]
    end_quantity = results

    assert end_quantity == starting_quantity - 1
