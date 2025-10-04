import sqlite3
from datetime import datetime

date = datetime.today().strftime('%Y-%m-%d')

class Transaction:
	def __init__(self, sql_db="RegisterDatabase"):
		self.conn_inventory = sqlite3.connect(sql_db)
		self.c = self.conn_inventory.cursor()
		self.nontax = 0
		self.pretax = 0
		self.tax = 0
		self.total = 0
		self.items_sold = 0
		self.cash_used = 0
		self.cc_used = 0
		self.items_list = []
		self.quantity_sold_list = []
		self.is_returning = False
		
	def __del__(self):
		self.conn_inventory.commit()
		self.conn_inventory.close()
		
	def complete_transaction(self):
		global date
		self.c.execute("INSERT INTO SALES VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (self.nontax, self.pretax, self.tax, self.total, self.items_sold, date, datetime.now().strftime("%H:%M"), self.cash_used, self.cc_used, 0))
		self.c.execute('''SELECT MAX("Transaction ID") FROM Sales''')
		results = self.c.fetchall()
		row = results[0]
		for i in range(len(self.items_list)):
			self.c.execute("INSERT OR IGNORE INTO SALEITEMS VALUES(?, ?, ?, ?, ?, ?)", (row[0], self.items_list[i][0], self.items_list[i][1], self.items_list[i][2], self.items_list[i][3], self.quantity_sold_list[i][1]))
			if not self.is_returning:
				self.c.execute("UPDATE INVENTORY SET Quantity = Quantity - ? WHERE barcode = ?", (self.quantity_sold_list[i][1], self.quantity_sold_list[i][0]))
		self.conn_inventory.commit()
		
			

	def sell_item(self, entered_barcode):
	
		self.c.execute("SELECT * FROM INVENTORY WHERE BARCODE = ?", (entered_barcode,))
		results = self.c.fetchall()
		if not results:
			return "item_not_found", None, None, None
		row = results[0]
		#Row[1] = item_name, Row[2] = item_price, Row[3] = taxable, Row[5] = quantity
		item_info = [row[1], row[2], row[3], entered_barcode, row[5]]
		if item_info[2] == 1:
			self.tax += item_info[1] * 0.06625
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
		
	
