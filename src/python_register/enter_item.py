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
		try:
			self.db_cursor.execute("INSERT INTO inventory VALUES (NULL, ?, ?, ?, ?, ?, (SELECT category_id FROM categories WHERE category_name  = ?), (SELECT category_id FROM categories WHERE category_name = ?), (SELECT vendor_id FROM vendors WHERE vendor_name = ?))", (self.name, self.price, self.taxable, self.barcode, Dec4(self.quantity), self.category, self.subcategory, self.vendor))
			self.db_conn.commit()	
		except sqlite3.Error as e:
			print(f"Error when committing item. enter_item Line 23. Error: {e} ")
			

	def update_item(self, old_barcode):
		try:
			self.db_cursor.execute("UPDATE inventory SET item_name = ?, item_price = ?, item_taxable = ?, item_barcode = ?, item_quantity = ?, category_id = (SELECT category_id from categories where category_name = ?), subcategory_id = (SELECT category_id FROM categories WHERE category_name = ?), vendor_id = (SELECT vendor_id FROM vendors WHERE vendor_name = ?) WHERE item_barcode = ?", (self.name, self.price, self.taxable, self.barcode, Dec4(self.quantity), self.category, self.subcategory, self.vendor, old_barcode))
			self.db_conn.commit()
		except sqlite3.Error as e:
			print(f"Error when updating item. enter_item line 34. Error: {e}")
			print(
				f"Errored item's info: Name:  {self.name}\n"
				f"Price: {self.price}\n"
				f"Taxable: {self.taxable}\n"
				f"New Barcode: {self.barcode}\n"
				f"Quantity: {Dec4(self.quantity)}\n"
				f"Category: {self.category}\n"
				f"Subcategory: {self.subcategory}\n"
				f"Vendor: {self.vendor}\n"
				f"Old Barcode: {old_barcode}")
			
		


