from Register import *
import tkinter as tk
import pytest
import sqlite3



@pytest.fixture(scope="function")
def register_instance():
    root = tk.Tk()
    register = Register(root)
    root.withdraw()
    root.update()
    yield register
    root.destroy()

conn = sqlite3.connect("/tmp/RegisterDatabase")
c = conn.cursor()

def test_enter_item(register_instance):

    """Test that the basic add item process functions as expected"""
    global c

    register_instance.enter_add_item_frame()
    register_instance.ui.add_item_entry.insert(tk.END, "Test Item")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.barcode == "Test Item"

    register_instance.ui.add_item_entry.insert(tk.END, "Test Item")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.name == "Test Item"