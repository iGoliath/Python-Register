import sqlite3
from datetime import datetime
from decimal import Decimal
from enteritem import Dec4

class Transaction:
	def __init__(self, db_conn, db_cursor):
		self.db_conn = db_conn
		self.db_cursor = db_cursor
		self.nontax = self.pretax = self.tax = Decimal('0.0')
		self.total = self.cash_used = self.cc_used = Decimal('0.0')
		self.cash_tendered = self.cc_tendered = Decimal('0.0')
		self.items_sold = Dec4('0.0')
		self.items_list = []
		self.returning = False
		
		
	def complete_transaction(self, coupon_info = None):
		self.db_cursor.execute("INSERT INTO SALES VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
			(self.nontax, self.pretax, self.tax, self.total, Dec4(self.items_sold), datetime.today().strftime('%Y-%m-%d'),
			datetime.now().strftime("%H:%M"), self.cash_used, self.cc_used, 0))
		self.db_cursor.execute('''SELECT MAX(sale_id) FROM Sales''')
		max_sale_id = (self.db_cursor.fetchall()[0])[0]
		for item in self.items_list:
			self.db_cursor.execute("INSERT OR IGNORE INTO SALEITEMS VALUES(?, ?, ?, ?)",
				(max_sale_id, item[1], Dec4(item[4]), item[5]))
			self.db_cursor.execute("SELECT Quantity FROM Inventory where Barcode = ?", (item[3],))
			current_quantity = self.db_cursor.fetchall()[0][0]
			if not self.returning:
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = ? WHERE barcode = ?",
					(Dec4(current_quantity - item[4]), item[3]))
			else:
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = ? WHERE barcode = ?",
					(Dec4(current_quantity + item[4]), item[3]))
		
		#if seasonal_id is not None:
			#self.db_cursor.execute('''INSERT INTO seasonal_sales VALUES (NULL, ?, ?)''', (seasonal_id, max_sale_id))

		if coupon_info:
			self.db_cursor.execute("INSERT INTO coupons VALUES(NULL, ?, ?, ?)", (max_sale_id, coupon_info[0], coupon_info[1]))


		self.db_conn.commit()

	def complete_as_decrement(self):
		global datetime
		self.db_cursor.execute('''INSERT INTO inventory_decrements VALUES (NULL, ?)''', (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ))
		self.db_cursor.execute('''SELECT MAX(decrement_id) FROM inventory_decrements''')
		max_decrement_id = (self.db_cursor.fetchall()[0])[0]
		for item in self.items_list:
			self.db_cursor.execute("INSERT OR IGNORE INTO inventory_decrements_items VALUES (?, ?, ?)",
				(max_decrement_id, item[5], item[4]))
			self.db_cursor.execute("SELECT Quantity FROM Inventory where Barcode = ?", (item[3],))
			current_quantity = self.db_cursor.fetchall()[0][0]
			self.db_cursor.execute("UPDATE Inventory SET Quantity = ? WHERE barcode = ?",
					(Dec4(current_quantity - item[4]), item[3]))
		self.db_conn.commit()

		
	def update_seasonal_info(self, seasonal_id):

		self.db_cursor.execute('''INSERT INTO seasonals ''')

	def sell_item(self, entered_barcode, decimal_amount = Decimal('1')):
	
		self.db_cursor.execute('''SELECT "Name", "Price", "Taxable", item_id FROM Inventory WHERE Barcode = ?''',
			(entered_barcode,))
		results = self.db_cursor.fetchone()
		if not results:
			return "item_not_found", None, None, None
		
		results = list(results)
		if results[2] == 1:
			self.tax += Decimal((results[1])) * Decimal('0.06625') * Decimal(decimal_amount)
			self.pretax += (results[1]) * Decimal(decimal_amount)
		else:
			self.nontax += Decimal(results[1]) * Decimal(decimal_amount)
		self.total = self.nontax + self.pretax + self.tax
		if not any(entered_barcode in sublist for sublist in self.items_list):
			self.items_list.append([results[0], Decimal(results[1]), results[2], entered_barcode, Decimal('1.0'), results[3]])
			quantity_sold = Decimal('1.0')
		else:
			for sublist in self.items_list:
				if entered_barcode in sublist:
					sublist[-2] += Decimal(decimal_amount)
					quantity_sold = sublist[-2]
					break

		
		self.items_sold += Decimal(decimal_amount)	
				
		return self.total, results[0], Decimal(results[1]) / Decimal(100), results[2]



		
	
