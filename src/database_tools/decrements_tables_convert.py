import sqlite3
from decimal import Decimal

conn = sqlite3.connect('RegisterDatabase')
c = conn.cursor()

c.row_factory = sqlite3.Row
sqlite3.register_adapter(Decimal, lambda d: int(d * Decimal("10000")))


results = c.execute('''SELECT * from inventory_decrements_items''').fetchall()

for row in results:
    if row[0] >= 337:
        c.execute('''UPDATE inventory_decrements_items SET decrement_quantity = ? where item_id = ? and decrement_id = ?''', (Decimal(row[2]) / Decimal('100'), row[1], row[0]) )
    else:
        c.execute('''UPDATE inventory_decrements_items SET decrement_quantity = ? where item_id = ? and decrement_id = ?''', (Decimal(row[2]), row[1], row[0]))

c.execute('''ALTER TABLE inventory_decrements_items RENAME TO old_inventory_decrements_items''')
c.execute('''CREATE TABLE inventory_decrements_items(decrement_id INTEGER, item_id INTEGER, decrement_quantity FOURDECINT, FOREIGN KEY(decrement_id) REFERENCES inventory_decrements(decrement_id), FOREIGN KEY(item_id) REFERENCES inventory(item_id))''')

c.execute('''INSERT INTO inventory_decrements_items SELECT * FROM old_inventory_decrements_items''')


conn.commit()
    
