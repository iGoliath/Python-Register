import sqlite3
import tkinter as tk
from decimal import Decimal

import pytest

import python_register.inventory_functions as invf
from python_register.Register import Register


class Dec4(Decimal):
    pass


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:", detect_types=sqlite3.PARSE_DECLTYPES)
    sqlite3.register_adapter(
        Decimal, lambda d: int(d.quantize(Decimal("0.01")) * Decimal("100"))
    )
    sqlite3.register_converter(
        "TWODECINT", lambda b: Decimal(b.decode()) / Decimal("100")
    )
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

    assert register_instance.state_mgr.add_item_object.barcode == "Test Item"

    register_instance.ui.name_var.set("Test Item")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.name == "Test Item"

    register_instance.ui.price_var.set("123")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.price == Decimal("1.23")

    register_instance.ui.tax_var.set("0")

    assert register_instance.state_mgr.add_item_object.taxable == 0

    register_instance.ui.category_var.set("Camping")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.category == "Camping"

    register_instance.ui.subcategory_var.set("BBQ Supplies")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.subcategory == "BBQ Supplies"

    register_instance.ui.vendor_var.set("ABC 123")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.vendor == "ABC 123"

    register_instance.ui.quantity_var.set("100")
    register_instance.on_add_item_enter()

    assert register_instance.state_mgr.add_item_object.quantity == Decimal("100")

    register_instance.state_mgr.yes_no_var.set("yes")

    item_info = c.execute(
        "SELECT * FROM inventory WHERE item_barcode = 'Test Item'"
    ).fetchall()[0]

    assert item_info["item_id"] == 11
    assert item_info["item_name"] == "Test Item"
    assert item_info["item_price"] == Decimal("1.23")
    assert item_info["item_taxable"] == 0
    assert item_info["item_barcode"] == "Test Item"
    assert item_info["item_quantity"] == Dec4("100")
    assert item_info["category_id"] == 0
    assert item_info["subcategory_id"] == 1
    assert item_info["vendor_id"] == 0


def _enter_full_item(
    register_instance,
    barcode="Test Item",
    name="Test Item",
    price="123",
    taxable="1",
    category="Camping",
    subcategory="BBQ Supplies",
    vendor="ABC 123",
    quantity=Decimal("100"),
    skipping_barcode=False,
):
    """Walk through the add item wizard using the same values as
    test_enter_item, leaving the process at the confirmation step."""

    if not skipping_barcode:
        register_instance.enter_add_item_frame()
        register_instance.ui.barcode_var.set(barcode)
        register_instance.on_add_item_enter()

    register_instance.ui.name_var.set(name)
    register_instance.on_add_item_enter()

    register_instance.ui.price_var.set(price)
    register_instance.on_add_item_enter()

    register_instance.ui.tax_var.set(taxable)

    register_instance.ui.category_var.set(category)
    register_instance.on_add_item_enter()

    register_instance.ui.subcategory_var.set(subcategory)
    register_instance.on_add_item_enter()

    register_instance.ui.vendor_var.set(vendor)
    register_instance.on_add_item_enter()

    register_instance.ui.quantity_var.set(quantity)
    register_instance.on_add_item_enter()


def _assert_item_attributes(
    add_item_object,
    barcode="Test Item",
    name="Test Item",
    price=Decimal("1.23"),
    taxable=1,
    category="Camping",
    subcategory="BBQ Supplies",
    vendor="ABC 123",
    quantity=Decimal("100"),
):
    """Assert add_item_object against the given expected values, which
    default to the same values _enter_full_item enters. Used to confirm
    that reentering a single field doesn't disturb the others."""

    assert add_item_object.barcode == barcode
    assert add_item_object.name == name
    assert add_item_object.price == price
    assert add_item_object.taxable == taxable
    assert add_item_object.category == category
    assert add_item_object.subcategory == subcategory
    assert add_item_object.vendor == vendor
    assert add_item_object.quantity == quantity


def test_reenter_barcode(register_instance):
    """Reentering barcode updates only the barcode."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("barcode")
    register_instance.ui.barcode_var.set("Reentered Item")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, barcode="Reentered Item"
    )


def test_reenter_name(register_instance):
    """Reentering name updates only the name."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("name")
    register_instance.ui.name_var.set("Reentered Name")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, name="Reentered Name"
    )


def test_reenter_price(register_instance):
    """Reentering price updates only the price."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("price")
    register_instance.ui.price_var.set("456")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, price=Decimal("4.56")
    )


def test_reenter_taxable(register_instance):
    """Reentering taxable updates only whether the item is taxable."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("taxable")
    register_instance.ui.tax_var.set("0")

    _assert_item_attributes(register_instance.state_mgr.add_item_object, taxable=0)


def test_reenter_category(register_instance):
    """Reentering category updates only the category."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("category")
    register_instance.ui.category_var.set("Reentered Category")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, category="Reentered Category"
    )


def test_reenter_subcategory(register_instance):
    """Reentering subcategory updates only the subcategory."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("subcategory")
    register_instance.ui.subcategory_var.set("Reentered Subcategory")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, subcategory="Reentered Subcategory"
    )


def test_reenter_vendor(register_instance):
    """Reentering vendor updates only the vendor."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("vendor")
    register_instance.ui.vendor_var.set("Reentered Vendor")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, vendor="Reentered Vendor"
    )


def test_reenter_quantity(register_instance):
    """Reentering quantity updates only the quantity."""
    _enter_full_item(register_instance)

    register_instance.reenter_button_pressed("quantity")
    register_instance.ui.quantity_var.set("50")
    register_instance.on_add_item_enter()

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, quantity=Decimal("50")
    )


def test_add_item_coming_from_register(register_instance, db):
    """Enter an item when coming from the register. Ensure that
    only one item was entered, and that state is reset as expected."""
    c = db.cursor()
    register_instance.ui.invisible_entry_var.set("UNKNOWN BARCODE")
    register_instance.process_sale()
    register_instance.state_mgr.register_yes_no_var.set("yes")
    _enter_full_item(register_instance, skipping_barcode=True)
    register_instance.state_mgr.yes_no_var.set("yes")

    assert register_instance.state_mgr.coming_from_register == False

    _assert_item_attributes(
        register_instance.state_mgr.add_item_object, barcode="UNKNOWN BARCODE"
    )

    database_version = c.execute(
        "SELECT * FROM inventory WHERE item_id = (SELECT MAX(item_id) FROM inventory)"
    ).fetchall()[0]

    # _assert_item_attributes once enter item is made into a dictionary
