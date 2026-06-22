from python_register.Register import Register
import tkinter as tk
import pytest
import sqlite3
from decimal import Decimal

class Dec4(Decimal): pass

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100")))
    sqlite3.register_converter("TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100"))
    sqlite3.register_adapter(Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000")))
    sqlite3.register_converter("FOURDECINT", lambda b: Dec4(b.decode()) / Dec4("10000"))
    _create_schema(conn)
    yield conn
    conn.close()

def _create_schema(conn):
    conn.executescript("""
        CREATE TABLE inventory(
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL, 
            item_price TWODECINT NOT NULL, 
            item_taxable BOOLEAN, 
            item_barcode TEXT, 
            item_quantity FOURDECINT, 
            category_id INTEGER, 
            subcategory_id INTEGER, 
            vendor_id INTEGER, 
            FOREIGN KEY (category_id) REFERENCES categories(category_id), 
            FOREIGN KEY (subcategory_id) REFERENCES categories(category_id), 
            FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id));

        CREATE TABLE no_sale(
            date TEXT UNIQUE, 
            times_pressed INT);

        CREATE TABLE inventory_decrements(
            decrement_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            datetime TEXT);

        CREATE TABLE inventory_decrements_items(
            decrement_id INTEGER, 
            item_id INTEGER, 
            decrement_quantity INTEGER, 
            FOREIGN KEY(decrement_id) REFERENCES inventory_decrements(decrement_id), 
            FOREIGN KEY(item_id) REFERENCES inventory(item_id));

        CREATE TABLE categories(
            category_id INTEGER PRIMARY KEY NOT NULL,
            category_name TEXT NOT NULL,
            parent_id INTEGER REFERENCES categories(category_id));

                       
        CREATE TABLE vendors(
            vendor_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
            vendor_name TEXT NOT NULL);

        INSERT INTO categories VALUES(0, 'Camping', NULL);
        INSERT INTO categories VALUES(1, 'BBQ Supplies', 0);
        INSERT INTO vendors VALUES(0, 'ABC 123');
        INSERT INTO inventory VALUES(NULL, 'Test', 123, 0, 'Test', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test1', 123, 1, 'Test1', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test2', 123, 0, 'Test2', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test3', 123, 1, 'Test3', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test4', 123, 0, 'Test4', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test5', 123, 1, 'Test5', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test6', 123, 0, 'Test6', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test7', 123, 1, 'Test7', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test8', 123, 0, 'Test8', 1000000, 0, 0, 0);
        INSERT INTO inventory VALUES(NULL, 'Test9', 123, 1, 'Test9', 1000000, 0, 0, 0);
    """)

@pytest.fixture(scope="function")
def register_instance(db):
    root = tk.Tk()
    register = Register(root, db)
    root.withdraw()
    root.update()
    yield register
    root.destroy()




def test_enter_item(register_instance, db):

    """Test that the basic add item process functions as expected"""
    c = db.cursor()

    register_instance.enter_add_item_frame()
    register_instance.ui.barcode_var.set("Test Item")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.barcode == "Test Item"

    register_instance.ui.name_var.set("Test Item")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.name == "Test Item"

    register_instance.ui.price_var.set("123")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.price == Decimal("1.23")

    register_instance.ui.tax_var.set("1")

    assert register_instance.state_manager.add_item_object.taxable == 1

    register_instance.ui.add_category_listbox.selection_set(0)
    register_instance.on_add_category_listbox_next()

    assert register_instance.state_manager.add_item_object.category == "Camping"

    register_instance.ui.add_subcategory_listbox.selection_set(0)
    register_instance.on_add_subcategory_listbox_next()

    assert register_instance.state_manager.add_item_object.subcategory == "BBQ Supplies"

    register_instance.ui.add_vendor_listbox.selection_set(0)
    register_instance.on_add_vendor_listbox_next()

    assert register_instance.state_manager.add_item_object.vendor == "ABC 123"

    register_instance.ui.quantity_var.set("100")
    register_instance.on_add_item_enter()

    assert register_instance.state_manager.add_item_object.quantity == Decimal('100')

    register_instance.state_manager.yes_no_var.set("yes")

    item_info = c.execute("SELECT * FROM inventory WHERE item_barcode = 'Test Item'").fetchall()[0]

    assert item_info['item_id'] == 11
    assert item_info['item_name'] == 'Test Item'
    assert item_info['item_price'] == Decimal('1.23')
    assert item_info['item_taxable'] == 1
    assert item_info['item_barcode'] == 'Test Item'
    assert item_info['item_quantity'] == Dec4('100')
    assert item_info['category_id'] == 0
    assert item_info['subcategory_id'] == 1
    assert item_info['vendor_id'] == 0

