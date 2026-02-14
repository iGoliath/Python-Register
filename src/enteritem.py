import sqlite3

class AddToInventory:
	
	def __init__(self, db_conn, db_cursor):
		self.name = ""
		self.price = 0.0
		self.barcode = 0
		self.old_barcode = 0
		self.taxable = 0
		self.quantity = 0
		self.category = ""
		self.db_conn = db_conn
		self.db_cursor = db_cursor
		

	def commit_item(self):
		self.db_cursor.execute("INSERT INTO INVENTORY VALUES (NULL, ?, ?, ?, ?, ?, ?)", (self.name, self.price, self.taxable, self.barcode, self.quantity, self.category))
		self.db_conn.commit()		

	def update_item(self, old_barcode):
		self.db_cursor.execute("UPDATE INVENTORY SET Name=?, Price=?, Taxable=?, Barcode=?, Quantity=?, Category=? WHERE Barcode=?", (self.name, self.price, self.taxable, self.barcode, self.quantity, self.category, old_barcode))
		self.db_conn.commit()
		


