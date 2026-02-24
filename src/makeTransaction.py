import sqlite3
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')

class Transaction:
	def __init__(self, db_conn, db_cursor):
		self.db_conn = db_conn
		self.db_cursor = db_cursor
		self.nontax = self.pretax = self.tax = self.total = 0
		self.items_sold = self.cash_used = self.cc_used = 0
		self.cash_tendered = self.cc_tendered = 0
		self.items_list = []
		self.ret_or_void = False
		
		
	def complete_transaction(self):
		global date
		self.db_cursor.execute("INSERT INTO SALES VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.nontax, self.pretax, self.tax, self.total, self.items_sold, date, datetime.now().strftime("%H:%M"), self.cash_used, self.cc_used, 0))
		self.db_cursor.execute('''SELECT MAX("Transaction ID") FROM Sales''')
		results = self.db_cursor.fetchall()[0]
		for item in self.items_list:
			self.db_cursor.execute("INSERT OR IGNORE INTO SALEITEMS VALUES(?, ?, ?, ?, ?, ?)",
				(results[0], item[0], item[1], item[2], item[3], item[4]))
			if not self.ret_or_void:
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = Quantity - ? WHERE barcode = ?",
					(item[4], item[3]))
			else:
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = Quantity + ? WHERE barcode = ?",
					(item[4], item[3]))
		self.db_conn.commit()
		
			

	def sell_item(self, entered_barcode):
	
		self.db_cursor.execute('''SELECT "Name", "Price", "Taxable" FROM INVENTORY WHERE BARCODE = ?''', (entered_barcode,))
		results = self.db_cursor.fetchone()
		if not results:
			return "item_not_found", None, None, None
		
		results = list(results)
		if results[2] == 1:
			self.tax += round(results[1] * 0.06625, 2)
			self.pretax += results[1]
		else:
			self.nontax += results[1]
		self.total = round(self.nontax + self.pretax + self.tax, 2)
			
		if not any(entered_barcode in sublist for sublist in self.items_list):
			self.items_list.append([results[0], results[1], results[2], entered_barcode, 1])
			quantity_sold = 1
		else:
			for sublist in self.items_list:
				if entered_barcode in sublist:
					sublist[-1] += 1
					quantity_sold = sublist[-1]
					break

		self.items_sold += 1	
				
		return self.total, results[0], results[1], results[2]
		
	
