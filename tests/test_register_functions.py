from python_register.Register import Register
import tkinter as tk
import pytest
import sqlite3
import pygame
from decimal import Decimal
from pathlib import Path

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

        CREATE TABLE sales(
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            non_tax TWODECINT NOT NULL,
            pre_tax TWODECINT NOT NULL,
            tax TWODECINT NOT NULL,
            total TWODECINT NOT NULL,
            num_items_sold FOURDECINT NOT NULL,
            sale_date TEXT NOT NULL, 
            sale_time TEXT NOT NULL, 
            cash_used TWODECINT NOT NULL, 
            cc_used TWODECINT NOT NULL, 
            is_voided BOOLEAN NOT NULL);
                       
        CREATE TABLE sale_items(
            sale_id INTEGER NOT NULL, 
            price_at_sale TWODECINT NOT NULL, 
            quantity FOURDECINT NOT NULL, 
            item_id INTEGER NOT NULL, 
            FOREIGN KEY(sale_id) REFERENCES sales(sale_id) ON DELETE RESTRICT, 
            FOREIGN KEY(item_id) REFERENCES inventory(item_id) ON DELETE RESTRICT);


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
    pygame.mixer.init()
    root.withdraw()
    root.update()
    yield register
    root.destroy()

class Dec4(Decimal): pass

sqlite3.register_adapter(Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100")))
sqlite3.register_converter("TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100"))

sqlite3.register_adapter(Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000")))
sqlite3.register_converter("FOURDECINT", lambda b: Dec4(b.decode()) / Dec4("10000"))


def assert_sale_empty(register):
    assert register.ui.user_entry.get() == '$0.00'
    assert register.ui.balance_entry.get() == '$0.00'
    assert register.state_manager.trans.items_sold == Decimal('0')
    assert register.state_manager.trans.nontax == Decimal('0')
    assert register.state_manager.trans.pretax == Decimal('0')
    assert register.state_manager.trans.tax == Decimal('0')
    assert register.state_manager.trans.total == Decimal('0')
    assert register.ui.sale_items_listbox.get(0, tk.END) == ()

@pytest.mark.parametrize("payment_method,cash_used,cc_used", [
    ("cash", Decimal('1.23'), Decimal('0')),
    ("cc", Decimal('0'), Decimal('1.23')),
])
def test_basic_sale_(register_instance, payment_method, cash_used, cc_used, db):
    """Sale of one item, no specified cash amount"""

    c = db.cursor()
    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    getattr(register_instance, f"on_{payment_method}")()


    row = c.execute(
        'SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)'
        ).fetchone()
   
    print(dict(row))
    assert row["cash_used"] == cash_used
    assert row["cc_used"] == cc_used
    assert row["is_voided"] == 0

def test_basic_sale_cc(register_instance, db):
    """Sale of one item, no specified cc amount"""

    c = db.cursor()

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.on_cc()

    c.execute('SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[1] == Decimal('1.23')
    assert row[2] == Decimal('0')
    assert row[3] == Decimal('0')
    assert row[4] == Decimal('1.23')
    assert row[5] == Decimal('1')
    assert row[8] == Decimal('0')
    assert row[9] == Decimal('1.23')
    assert row[10] == 0

def test_sale_cash_cc(register_instance, db):
    """Sale of one item. $1.00 is paid in cash, and the rest CC"""

    c = db.cursor()

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry_var.set("100")
    register_instance.on_cash()
    register_instance.on_cc()

    c.execute('SELECT non_tax, cash_used, cc_used FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == Decimal('1.23')
    assert row[1] == Decimal('1.00')
    assert row[2] == Decimal('0.23')

def test_sale_cc_cash(register_instance, db):
    """Sale of one item. $1.00 is paid in CC, and the rest Cash"""
    c = db.cursor()

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry_var.set("100+")
    register_instance.on_cc()
    register_instance.on_cash()

    c.execute('SELECT non_tax, cash_used, cc_used FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)')
    results = c.fetchall()
    row = results[0]
    assert row[0] == Decimal('1.23')
    assert row[1] == Decimal('0.23')
    assert row[2] == Decimal('1.00')

def test_cc_invalid(register_instance, db):
    """Sale of one item. The user enters an amount to be paid in CC that 
    exceeds the balance. Register should pause the sale and print to the
    user that this is invalid. Sales ending in a CC amount should not
    result in any change needing to be given."""

    c = db.cursor()

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry_var.set("124+")
    register_instance.on_cc()

    result = register_instance.ui.popup_description_label_var.get()
    assert result == 'CC Amount Entered\nExceeds Balance!'
    assert register_instance.state_manager.trans.total == Decimal('1.23')

def test_quantity_decrement_single(register_instance, db):

    c = db.cursor()

    quantity = c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", )).fetchone()[0]
    
    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.on_cash()

    new_quantity = c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", )).fetchone()[0]

    assert new_quantity == Decimal(quantity) - Decimal('1')

def test_quantity_decrement_double(register_instance, db):

    c = db.cursor()

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    item_one_starting_quantity = row[0]

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test1", ))
    results = c.fetchall()
    row = results[0]

    item_two_starting_quantity = row[0]

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.ui.invisible_entry_var.set("Test1")
    register_instance.process_sale()
    register_instance.on_cash()

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", ))
    results = c.fetchall()
    row = results[0]

    item_one_final_quantity = row[0]

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test1", ))
    results = c.fetchall()
    row = results[0]
    item_two_final_quantity = row[0]

    assert item_one_final_quantity == Decimal(item_one_starting_quantity) - Decimal('2')
    assert item_two_final_quantity == Decimal(item_two_starting_quantity) - Decimal('1')

def test_basic_return(register_instance, db):

    c = db.cursor()

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", ))
    results = c.fetchone()[0]
    starting_quantity = results

    register_instance.process_return()
    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.state_manager.return_var.set("cash")

    c.execute('SELECT item_quantity FROM inventory WHERE item_barcode = ?', ("Test", ))
    results = c.fetchone()[0]
    end_quantity = results

    assert end_quantity == Decimal(starting_quantity) + Decimal('1')
    assert register_instance.state_manager.trans.returning == False

def test_inventory_decrement(register_instance, db):

    c = db.cursor()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    starting_quantity = c.fetchall()[0][0]

    c.execute("SELECT MAX(sale_id) FROM sales")
    starting_sale_id = c.fetchall()[0][0]

    
    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()
    register_instance.complete_decrement()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    ending_quantity = c.fetchall()[0][0]


    c.execute("SELECT MAX(sale_id) FROM sales")
    ending_sale_id = c.fetchall()[0][0]

    assert ending_quantity == starting_quantity - Decimal('1')
    assert starting_sale_id == ending_sale_id
    assert register_instance.ui.user_entry.get() == '$0.00'
    assert register_instance.ui.sale_items_listbox.get(0, tk.END) == ()
    assert register_instance.state_manager.trans.total == Decimal('0')

def test_manual_quantity_input(register_instance):
    
    register_instance.ui.invisible_entry_var.set('Test')
    register_instance.process_sale()

    register_instance.ui.sale_items_listbox.selection_set(0)
    register_instance.ui.invisible_entry_var.set('1.2345')
    register_instance.process_sale_multiples()

    assert register_instance.state_manager.trans.items_sold == Decimal('1.2345')

def test_decimal_sale(register_instance, db):

    c = db.cursor()
    
    c.execute("SELECT item_quantity FROm inventory WHERE item_barcode = 'Test'")
    starting_quantity = c.fetchall()[0][0]

    register_instance.ui.invisible_entry_var.set('Test')
    register_instance.process_sale()

    register_instance.ui.sale_items_listbox.selection_set(0)
    register_instance.ui.invisible_entry_var.set('1.2345')
    register_instance.process_sale_multiples()
    register_instance.on_cash()

    c.execute('''SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) from sales)''')
    results = c.fetchall()[0]

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    ending_quantity = c.fetchall()[0][0]


    assert ending_quantity == starting_quantity - Decimal('1.2345')
    assert results[1] == Decimal('1.52')
    assert results[2] == Decimal('0')
    assert results[3] == Decimal('0')
    assert results[4] == Decimal('1.52')
    assert results[5] == Dec4('1.2345')
    assert results[8] == Decimal('1.52')
    assert results[9] == Decimal('0')

def test_tax_sale(register_instance):


    register_instance.ui.invisible_entry_var.set('Test1')
    register_instance.process_sale()

    assert register_instance.state_manager.trans.tax == Decimal('1.23') * Decimal(register_instance.config.data['tax_amount'])

@pytest.mark.parametrize("item_name", [
    ("Test"),
    ("Test1")
])
def test_cancel_entire_single_item_sale(register_instance, item_name):

    register_instance.ui.invisible_entry_var.set(item_name)
    register_instance.process_sale()

    register_instance.cancel_sale()

    assert_sale_empty(register_instance)

@pytest.mark.parametrize(
        "listbox_index,balance_entry,user_entry,nontax,pretax,tax," \
        "total,items_sold,listbox_first_item,listbox_second_item", [
            (1, "$1.23", "$0.00", Decimal('1.23'), Decimal('0'),
            Decimal('0'), Decimal('1.23'), Decimal('1'), (), ('Test (1.0) $1.23 NT', )),
            (0, "$1.31", "$0.00", Decimal('0'), Decimal('1.23'),
              Decimal('0.08'), Decimal('1.31'), Decimal('1'), (), ('Test1 (1.0) $1.23 TX', ))
        ])
def test_cancel_single_item(
    register_instance, listbox_index, balance_entry, user_entry, nontax,
    pretax, tax, total, items_sold, listbox_first_item, listbox_second_item):

    register_instance.ui.invisible_entry_var.set('Test')
    register_instance.process_sale()

    register_instance.ui.invisible_entry_var.set('Test1')
    register_instance.process_sale()

    register_instance.ui.sale_items_listbox.selection_set(listbox_index)
    register_instance.cancel_sale()

    assert register_instance.ui.balance_entry.get() == balance_entry
    assert register_instance.ui.user_entry.get() == user_entry
    assert register_instance.state_manager.trans.nontax == nontax
    assert register_instance.state_manager.trans.pretax == pretax
    assert register_instance.state_manager.trans.tax.quantize(Decimal('0.01')) == tax
    assert register_instance.state_manager.trans.total.quantize(Decimal('0.01')) == total
    assert register_instance.state_manager.trans.items_sold == items_sold
    assert register_instance.ui.sale_items_listbox.get(1, tk.END) == listbox_first_item
    assert register_instance.ui.sale_items_listbox.get(0, 1) == listbox_second_item

def test_cancel_entire_multiple_item_sale(register_instance):

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()

    register_instance.ui.invisible_entry_var.set("Test1")
    register_instance.process_sale()

    register_instance.cancel_sale()

    assert_sale_empty(register_instance)

def test_cancel_entire_multiple_item_sale_taxable_decimal(register_instance):

    register_instance.ui.invisible_entry_var.set("Test")
    register_instance.process_sale()

    register_instance.ui.invisible_entry_var.set("Test1")
    register_instance.process_sale()

    register_instance.ui.sale_items_listbox.selection_set(1)
    register_instance.ui.invisible_entry_var.set(1.2345)
    register_instance.process_sale_multiples()

    register_instance.cancel_sale()

    assert_sale_empty(register_instance)


