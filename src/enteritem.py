import sqlite3
from decimal import Decimal

class Dec4(Decimal): pass

class AddToInventory:
	
	def __init__(self, db_conn, db_cursor):
		self.name = ""
		self.price = Decimal('0.0')
		self.barcode = 0
		self.old_barcode = 0
		self.taxable = 0
		self.quantity = Dec4('0.0')
		self.category = ""
		self.subcategory = ""
		self.vendor = ""
		self.db_conn = db_conn
		self.db_cursor = db_cursor
		
	def commit_item(self):
		self.db_cursor.execute("INSERT INTO INVENTORY VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)", (self.name, self.price, self.taxable, self.barcode, Dec4(self.quantity), self.category, self.subcategory, self.vendor))
		self.db_conn.commit()		

	def update_item(self, old_barcode):
		self.db_cursor.execute("UPDATE INVENTORY SET Name=?, Price=?, Taxable=?, Barcode=?, Quantity=?, Category=?, Subcategory=?, Vendor=? WHERE Barcode=?", (self.name, self.price, self.taxable, self.barcode, Dec4(self.quantity), self.category, self.subcategory, self.vendor, old_barcode))
		self.db_conn.commit()
		


