import sqlite3
import tkinter as tk
from decimal import Decimal
from pathlib import Path

import pygame
import pytest

from python_register.Register import Register


def convert_twdecint(b):
    print(repr(b))
    return Decimal(b.decode()) / Decimal("100")


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(
        Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100"))
    )
    sqlite3.register_converter("TWODECINT", convert_twdecint)
    sqlite3.register_adapter(
        Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000"))
    )
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
            item_reconciled BOOLEAN,
            item_date_last_reconciled TEXT,
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
        INSERT INTO inventory VALUES(NULL, 'Test', 123, 0, 'Test', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test1', 123, 1, 'Test1', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test2', 123, 0, 'Test2', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test3', 123, 1, 'Test3', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test4', 123, 0, 'Test4', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test5', 123, 1, 'Test5', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test6', 123, 0, 'Test6', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test7', 123, 1, 'Test7', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test8', 123, 0, 'Test8', 1000000, 0, 0, 0, 0, NULL);
        INSERT INTO inventory VALUES(NULL, 'Test9', 123, 1, 'Test9', 1000000, 0, 0, 0, 0, NULL);
    """)


@pytest.fixture(scope="function")
def register_instance(db):
    root = tk.Tk()
    register = Register(root, db)
    pygame.mixer.init()
    root.withdraw()
    register.ui.show_frame("register")
    root.update()
    yield register
    root.destroy()


class Dec4(Decimal):
    pass


sqlite3.register_adapter(
    Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100"))
)
sqlite3.register_converter("TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100"))

sqlite3.register_adapter(
    Dec4, lambda d: int(d.quantize(Decimal("0.0001")) * Decimal("10000"))
)
sqlite3.register_converter("FOURDECINT", lambda b: Dec4(b.decode()) / Dec4("10000"))


def _sell_test_item(register_instance):
    """Helper function, sell one item 'Test'"""
    register_instance.ui.frames["register"].invisible_entry_var.set("Test")
    register_instance.ui.frames["register"].process_sale()


def _assert_sale_empty(register: Register) -> None:
    """Helper function for checking that current transaction is empty"""
    assert register.ui.frames["register"].user_entry.get() == "$0.00"
    assert register.ui.frames["register"].balance_entry.get() == "$0.00"
    assert register.state_mgr.trans.items_sold == Decimal("0")
    assert register.state_mgr.trans.nontax == Decimal("0")
    assert register.state_mgr.trans.pretax == Decimal("0")
    assert register.state_mgr.trans.tax == Decimal("0")
    assert register.state_mgr.trans.total == Decimal("0")
    assert register.ui.frames["register"].sale_items_listbox.get(0, tk.END) == ()


def _assert_sale_state(
    register: Register, items_sold, nontax, pretax, tax, total
) -> None:
    assert (
        register.ui.frames["register"].user_entry.get()
        == f"${Decimal(items_sold * nontax * pretax).quantize(Decimal('0.01'))}"
    )
    assert (
        register.ui.frames["register"].balance_entry.get()
        == f"${Decimal(items_sold * nontax * pretax).quantize(Decimal('0.01'))}"
    )
    assert register.state_mgr.trans.items_sold == items_sold
    assert register.state_mgr.trans.nontax == nontax
    assert register.state_mgr.trans.pretax == pretax
    assert register.state_mgr.trans.tax == tax
    assert register.state_mgr.trans.total == total


@pytest.mark.parametrize(
    "payment_method,cash_used,cc_used",
    [
        ("cash", Decimal("1.23"), Decimal("0")),
        ("cc", Decimal("0"), Decimal("1.23")),
    ],
)
def test_basic_sale_(register_instance, payment_method, cash_used, cc_used, db):
    """Sale of one item, no specified cash amount"""

    c = db.cursor()

    num_sales_beginning = c.execute("SELECT MAX(sale_id) FROM sales").fetchone()[0]
    if num_sales_beginning == None:
        num_sales_beginning = 0

    _sell_test_item(register_instance)
    getattr(register_instance.ui.frames["register"], f"on_{payment_method}")()

    num_entries_ending = c.execute("SELECT MAX(sale_id) FROM sales").fetchone()[0]

    assert num_sales_beginning == num_entries_ending - 1

    row = c.execute(
        "SELECT * FROM sales WHERE sale_id = ?", (num_entries_ending,)
    ).fetchone()

    assert row["cash_used"] == cash_used
    assert row["cc_used"] == cc_used
    assert row["is_voided"] == 0


def test_basic_sale_item_not_found(register_instance, db):
    """Sale of an item that is not in the inventory."""
    register_instance.ui.frames["register"].invisible_entry_var.set("NOTFOUNDITEM")
    register_instance.ui.frames["register"].process_sale()
    _assert_sale_empty(register_instance)
    register_instance.ui.frames[
        "register_add_item_prompt"
    ].register_add_item_yes_button.invoke()
    assert register_instance.state_mgr.add_item_dict.barcode == "NOTFOUNDITEM"


def test_basic_sale_cc(register_instance, db):
    """Sale of one item, no specified cc amount"""

    c = db.cursor()

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].on_cc()

    c.execute("SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)")
    results = c.fetchall()
    row = results[0]
    assert row[1] == Decimal("1.23")
    assert row[2] == Decimal("0")
    assert row[3] == Decimal("0")
    assert row[4] == Decimal("1.23")
    assert row[5] == Decimal("1")
    assert row[8] == Decimal("0")
    assert row[9] == Decimal("1.23")
    assert row[10] == 0


def test_sale_cash_cc(register_instance, db):
    """Sale of one item. $1.00 is paid in cash, and the rest CC"""

    c = db.cursor()

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].invisible_entry_var.set("100")
    register_instance.ui.frames["register"].on_cash()
    register_instance.ui.frames["register"].on_cc()

    c.execute(
        "SELECT non_tax, cash_used, cc_used FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)"
    )
    results = c.fetchall()
    row = results[0]
    assert row[0] == Decimal("1.23")
    assert row[1] == Decimal("1.00")
    assert row[2] == Decimal("0.23")


def test_sale_cc_cash(register_instance, db):
    """Sale of one item. $1.00 is paid in CC, and the rest Cash"""
    c = db.cursor()

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].invisible_entry_var.set("100+")
    register_instance.ui.frames["register"].on_cc()
    register_instance.ui.frames["register"].on_cash()

    c.execute(
        "SELECT non_tax, cash_used, cc_used FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)"
    )
    results = c.fetchall()
    row = results[0]
    assert row[0] == Decimal("1.23")
    assert row[1] == Decimal("0.23")
    assert row[2] == Decimal("1.00")


def test_cc_invalid(register_instance, db):
    """Sale of one item. The user enters an amount to be paid in CC that
    exceeds the balance. Register should pause the sale and print to the
    user that this is invalid. Sales ending in a CC amount should not
    result in any change needing to be given."""

    c = db.cursor()

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].invisible_entry_var.set("124+")
    register_instance.ui.frames["register"].on_cc()

    result = register_instance.ui.popup_description_label_var.get()
    assert result == "CC Amount Entered\nExceeds Balance!"
    assert register_instance.state_mgr.trans.total == Decimal("1.23")


def test_quantity_decrement_single(register_instance, db):

    c = db.cursor()

    quantity = c.execute(
        "SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",)
    ).fetchone()["item_quantity"]

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].on_cash()

    new_quantity = c.execute(
        "SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",)
    ).fetchone()["item_quantity"]

    assert new_quantity == Decimal(quantity) - Decimal("1")


def test_quantity_decrement_double(register_instance, db):

    c = db.cursor()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",))
    results = c.fetchall()
    row = results[0]

    item_one_starting_quantity = row[0]

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test1",))
    results = c.fetchall()
    row = results[0]

    item_two_starting_quantity = row[0]

    _sell_test_item(register_instance)
    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].invisible_entry_var.set("Test1")
    register_instance.ui.frames["register"].process_sale()
    register_instance.ui.frames["register"].on_cash()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",))
    results = c.fetchall()
    row = results[0]

    item_one_final_quantity = row[0]

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test1",))
    results = c.fetchall()
    row = results[0]
    item_two_final_quantity = row[0]

    assert item_one_final_quantity == Decimal(item_one_starting_quantity) - Decimal("2")
    assert item_two_final_quantity == Decimal(item_two_starting_quantity) - Decimal("1")


def test_basic_return(register_instance, db):

    c = db.cursor()

    starting_quantity = c.execute(
        "SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",)
    ).fetchone()["item_quantity"]

    register_instance.ui.frames["register"].process_return()
    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].return_var.set("cash")

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", ("Test",))
    results = c.fetchone()["item_quantity"]
    end_quantity = results

    assert end_quantity == Decimal(starting_quantity) + Decimal("1")
    assert register_instance.state_mgr.trans.returning == False


def test_inventory_decrement(register_instance, db):

    c = db.cursor()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    starting_quantity = c.fetchall()[0][0]

    c.execute("SELECT MAX(sale_id) FROM sales")
    starting_sale_id = c.fetchall()[0][0]

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].complete_decrement()

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    ending_quantity = c.fetchall()[0][0]

    c.execute("SELECT MAX(sale_id) FROM sales")
    ending_sale_id = c.fetchall()[0][0]

    assert ending_quantity == starting_quantity - Decimal("1")
    assert starting_sale_id == ending_sale_id
    assert register_instance.ui.frames["register"].user_entry.get() == "$0.00"
    assert (
        register_instance.ui.frames["register"].sale_items_listbox.get(0, tk.END) == ()
    )
    assert register_instance.state_mgr.trans.total == Decimal("0")


def test_empty_decrement(register_instance, db):
    """Empty decrement should do nothing"""
    c = db.cursor()

    expected_max_decrement_id = c.execute(
        "SELECT MAX(decrement_id) FROM inventory_decrements"
    ).fetchone()[0]

    register_instance.ui.frames["register"].complete_decrement()

    actual_max_decrement_id = c.execute(
        "SELECT MAX(decrement_id) FROM inventory_decrements"
    ).fetchone()[0]

    actual_max_decrement_items_id = c.execute(
        "SELECT MAX(decrement_id) FROM inventory_decrements_items"
    ).fetchone()[0]

    assert (
        expected_max_decrement_id
        == actual_max_decrement_id
        == actual_max_decrement_items_id
    )


def test_manual_quantity_input(register_instance):

    _sell_test_item(register_instance)

    register_instance.ui.frames["register"].sale_items_listbox.selection_set(0)
    register_instance.ui.frames["register"].invisible_entry_var.set("1.2345")
    register_instance.ui.frames["register"].process_sale_multiples()

    assert register_instance.state_mgr.trans.items_sold == Decimal("1.2345")


def test_decimal_sale(register_instance, db):

    c = db.cursor()

    c.execute("SELECT item_quantity FROm inventory WHERE item_barcode = 'Test'")
    starting_quantity = c.fetchall()[0][0]

    _sell_test_item(register_instance)

    register_instance.ui.frames["register"].sale_items_listbox.selection_set(0)
    register_instance.ui.frames["register"].invisible_entry_var.set("1.2345")
    register_instance.ui.frames["register"].process_sale_multiples()
    register_instance.ui.frames["register"].on_cash()

    c.execute(
        """SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) from sales)"""
    )
    results = c.fetchall()[0]

    c.execute("SELECT item_quantity FROM inventory WHERE item_barcode = 'Test'")
    ending_quantity = c.fetchall()[0][0]

    assert ending_quantity == starting_quantity - Decimal("1.2345")
    assert results[1] == Decimal("1.52")
    assert results[2] == Decimal("0")
    assert results[3] == Decimal("0")
    assert results[4] == Decimal("1.52")
    assert results[5] == Dec4("1.2345")
    assert results[8] == Decimal("1.52")
    assert results[9] == Decimal("0")


def test_tax_sale(register_instance):

    register_instance.ui.frames["register"].invisible_entry_var.set("Test1")
    register_instance.ui.frames["register"].process_sale()

    assert register_instance.state_mgr.trans.tax == Decimal("1.23") * Decimal(
        register_instance.config.data["tax_amount"]
    )


@pytest.mark.parametrize("item_name", [("Test"), ("Test1")])
def test_cancel_entire_single_item_sale(register_instance, item_name):

    register_instance.ui.frames["register"].invisible_entry_var.set(item_name)
    register_instance.ui.frames["register"].process_sale()

    register_instance.ui.frames["register"].cancel_sale()

    _assert_sale_empty(register_instance)


@pytest.mark.parametrize(
    "listbox_index,balance_entry,user_entry,nontax,pretax,tax,"
    "total,items_sold,listbox_first_item,listbox_second_item",
    [
        (
            1,
            "$1.23",
            "$0.00",
            Decimal("1.23"),
            Decimal("0"),
            Decimal("0"),
            Decimal("1.23"),
            Decimal("1"),
            (),
            ("Test (1) $1.23 NT",),
        ),
        (
            0,
            "$1.31",
            "$0.00",
            Decimal("0"),
            Decimal("1.23"),
            Decimal("0.08"),
            Decimal("1.31"),
            Decimal("1"),
            (),
            ("Test1 (1) $1.23 TX",),
        ),
    ],
)
def test_cancel_single_item(
    register_instance,
    listbox_index,
    balance_entry,
    user_entry,
    nontax,
    pretax,
    tax,
    total,
    items_sold,
    listbox_first_item,
    listbox_second_item,
):

    _sell_test_item(register_instance)

    register_instance.ui.frames["register"].invisible_entry_var.set("Test1")
    register_instance.ui.frames["register"].process_sale()

    register_instance.ui.frames["register"].sale_items_listbox_var.set(listbox_index)
    register_instance.ui.frames["register"].cancel_sale()

    assert register_instance.ui.frames["register"].balance_entry.get() == balance_entry
    assert register_instance.ui.frames["register"].user_entry.get() == user_entry
    assert register_instance.state_mgr.trans.nontax == nontax
    assert register_instance.state_mgr.trans.pretax == pretax
    assert register_instance.state_mgr.trans.tax.quantize(Decimal("0.01")) == tax
    assert register_instance.state_mgr.trans.total.quantize(Decimal("0.01")) == total
    assert register_instance.state_mgr.trans.items_sold == items_sold
    assert (
        register_instance.ui.frames["register"].sale_items_listbox.get(1, tk.END)
        == listbox_first_item
    )
    assert (
        register_instance.ui.frames["register"].sale_items_listbox.get(0, 1)
        == listbox_second_item
    )


def test_cancel_entire_multiple_item_sale(register_instance):

    _sell_test_item(register_instance)

    register_instance.ui.frames["register"].invisible_entry_var.set("Test1")
    register_instance.ui.frames["register"].process_sale()

    register_instance.ui.frames["register"].cancel_sale()

    _assert_sale_empty(register_instance)


def test_cancel_entire_multiple_item_sale_taxable_decimal(register_instance):

    _sell_test_item(register_instance)

    register_instance.ui.frames["register"].invisible_entry_var.set("Test1")
    register_instance.ui.frames["register"].process_sale()

    register_instance.ui.frames["register"].sale_items_listbox.selection_set(1)
    register_instance.ui.frames["register"].invisible_entry_var.set(1.2345)
    register_instance.ui.frames["register"].process_sale_multiples()

    register_instance.ui.frames["register"].cancel_sale()

    _assert_sale_empty(register_instance)


def test_void_sale(register_instance, db):
    """Test that a voided sale is marked correctly"""
    c = db.cursor()

    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].complete_sale()

    is_voided = c.execute(
        "SELECT is_voided FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)"
    ).fetchone()[0]

    assert is_voided == 0

    register_instance.ui.show_frame("browse_transactions", browse_mode="void")

    register_instance.ui.frames["browse_transactions"].void_print_button.invoke()

    is_voided = c.execute(
        "SELECT is_voided FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)"
    ).fetchone()[0]

    assert is_voided == 1


@pytest.mark.parametrize(
    "error_expected,listbox_selected,item_looked_up,entered_quantity,expected_quantity",
    [
        (1, 1, " ", "1", ""),
        (1, 0, " ", "", ""),
        (1, 1, " ", "", ""),
        (1, 1, "Test", "-1", ""),
        (1, 1, "Test", "0", ""),
        (0, 1, "Test", "1", Decimal("1")),
        (0, 1, "Test", "1.23", Decimal("1.23")),
    ],
)
def test_lookup_item_register(
    register_instance,
    error_expected,
    listbox_selected,
    item_looked_up,
    entered_quantity,
    expected_quantity,
):
    """Ensure that valid entries for item lookup fields
    ring up a transaction, while proper ones are disallowed."""
    register_instance.ui.show_frame("lookup_items")
    register_instance.ui.frames["lookup_items"].item_lookup_var.set(item_looked_up)
    if listbox_selected:
        register_instance.ui.frames["lookup_items"].lookup_items_listbox.selection_set(
            0
        )
    register_instance.ui.frames["lookup_items"].lookup_items_quantity_spinbox.delete(
        0, tk.END
    )
    register_instance.ui.frames["lookup_items"].lookup_items_quantity_spinbox.insert(
        tk.END, entered_quantity
    )

    register_instance.ui.frames["lookup_items"].confirm_lookup_items()

    if error_expected:
        _assert_sale_empty(register_instance)
    else:
        assert register_instance.state_mgr.trans.items_sold == expected_quantity


def test_browse_transaction_go_past_max(register_instance, db):
    """Entering a transaction id greater than the highest in
    sales table should set output to the max transaction id"""
    c = db.cursor()

    for i in range(0, 4):
        _sell_test_item(register_instance)
        register_instance.ui.frames["register"].complete_sale()

    register_instance.ui.show_frame("browse_transactions", browse_mode="browse")
    register_instance.ui.frames["browse_transactions"].browse_index.set(1)

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    assert current_trans_id == "1"

    register_instance.ui.frames["browse_transactions"].browse_index.set(9999)

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    max_transaction_id = c.execute("SELECT MAX(sale_id) FROM sales").fetchone()[0]

    assert current_trans_id == str(max_transaction_id)


def test_browse_transaction_go_past_min(register_instance, db):
    """Entering a transaction id less than the lowest in
    sales table should set output to the min transaction id"""
    c = db.cursor()

    for i in range(0, 4):
        _sell_test_item(register_instance)
        register_instance.ui.frames["register"].complete_sale()

    register_instance.ui.show_frame("browse_transactions", browse_mode="browse")
    register_instance.ui.frames["browse_transactions"].browse_index.set(9999)

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    max_transaction_id = c.execute("SELECT MAX(sale_id) FROM sales").fetchone()[0]

    assert current_trans_id == str(max_transaction_id)
    assert int(current_trans_id) > 1

    register_instance.ui.frames["browse_transactions"].browse_index.set(-1)

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    min_transaction_id = c.execute("SELECT MIN(sale_id) FROM sales").fetchone()[0]

    assert current_trans_id == str(min_transaction_id)


def test_browse_transaction_scroll_left(register_instance):
    """Scrolling left should move to one less than the current
    transaction being displayed."""
    for i in range(0, 4):
        _sell_test_item(register_instance)
        register_instance.ui.frames["register"].complete_sale()

    register_instance.ui.show_frame("browse_transactions", browse_mode="browse")

    prev_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    register_instance.ui.frames["browse_transactions"].prev_button.invoke()

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    assert int(current_trans_id) == int(prev_trans_id) - 1


def test_browse_transaction_scroll_right(register_instance):
    """Scrolling right should move to one more than the current
    transaction being displayed."""
    for i in range(0, 4):
        _sell_test_item(register_instance)
        register_instance.ui.frames["register"].complete_sale()

    register_instance.ui.show_frame("browse_transactions", browse_mode="browse")
    register_instance.ui.frames["browse_transactions"].browse_index.set(-1)

    prev_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    register_instance.ui.frames["browse_transactions"].next_button.invoke()

    current_trans_id = (
        register_instance.ui.frames["browse_transactions"]
        .text.get("1.0", "end-1c")
        .split("Trans ID: ", 1)[1]
        .split(" |", 1)[0]
    )

    assert int(current_trans_id) == int(prev_trans_id) + 1


def test_browse_transaction_text_formatting(register_instance, db):
    """Test that the formatted text in the text widget
    matches that of the output from print_transaction_info"""
    c = db.cursor()
    _sell_test_item(register_instance)
    register_instance.ui.frames["register"].complete_sale()

    register_instance.ui.show_frame("browse_transactions", browse_mode="browse")

    text_widget_value = register_instance.ui.frames["browse_transactions"].text.get(
        "1.0", "end-1c"
    )

    function_output_value = register_instance.ui.frames[
        "browse_transactions"
    ].print_transaction_info(
        c.execute(
            "SELECT * FROM sales WHERE sale_id = (SELECT MAX(sale_id) FROM sales)"
        ).fetchone()
    )

    assert text_widget_value == function_output_value
