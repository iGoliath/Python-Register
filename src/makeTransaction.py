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
		self.quantity_sold_list = []
		self.ret_or_void = False
		
		
	def complete_transaction(self):
		global date
		self.db_cursor.execute("INSERT INTO SALES VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.nontax, self.pretax, self.tax, self.total, self.items_sold, date, datetime.now().strftime("%H:%M"), self.cash_used, self.cc_used, 0))
		self.db_cursor.execute('''SELECT MAX("Transaction ID") FROM Sales''')
		results = self.db_cursor.fetchall()
		row = results[0]
		for i in range(len(self.items_list)):
			self.db_cursor.execute("INSERT OR IGNORE INTO SALEITEMS VALUES(?, ?, ?, ?, ?, ?)", (row[0], self.items_list[i][0], self.items_list[i][1], self.items_list[i][2], self.items_list[i][3], self.quantity_sold_list[i][1]))
			if not self.ret_or_void:
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = Quantity - ? WHERE barcode = ?", (self.quantity_sold_list[i][1], self.quantity_sold_list[i][0]))
			else:
				print("In else block")
				self.db_cursor.execute("UPDATE INVENTORY SET Quantity = Quantity + ? WHERE barcode = ?", (self.quantity_sold_list[i][1], self.quantity_sold_list[i][0]))
		self.db_conn.commit()
		
			

	def sell_item(self, entered_barcode):
	
		self.db_cursor.execute("SELECT * FROM INVENTORY WHERE BARCODE = ?", (entered_barcode,))
		results = self.db_cursor.fetchall()
		if not results:
			return "item_not_found", None, None, None
		row = results[0]
		#Row[1] = item_name, Row[2] = item_price, Row[3] = taxable, Row[5] = quantity
		item_info = [row[1], row[2], row[3], entered_barcode, row[5]]
		if item_info[2] == 1:
			self.tax += round(item_info[1] * 0.06625, 2)
			self.pretax += item_info[1]
		else:
			self.nontax += item_info[1]
		self.total = round(self.nontax + self.pretax + self.tax, 2)
		
		# If no items have been sold, start the list
		# Otherwise, make sure item doesn't already exist within the list
		if len(self.items_list) == 0:
			self.items_list.append(item_info)
		elif len(self.items_list) >= 1:
			if not any(entered_barcode in sublist for sublist in self.items_list):
				self.items_list.append(item_info)
		self.items_sold += 1
		
		# Update list of barcodes for items sold and how many for 
		# later use in transaction sales table and updating item's quantity
		if len(self.quantity_sold_list) == 0:
			self.quantity_sold_list.append([entered_barcode, 1])
		elif len(self.quantity_sold_list) >= 1:
			for sublist in self.quantity_sold_list:
				if sublist[0] == entered_barcode:
					sublist[1] += 1
					break
			else:
				self.quantity_sold_list.append([entered_barcode, 1])
				
				
		return self.total, item_info[0], item_info[1], item_info[2]
		
	
