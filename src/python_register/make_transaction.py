import sqlite3
from datetime import datetime
from decimal import Decimal
from .enter_item import Dec4

class Transaction:
	def __init__(self, db_conn, db_cursor, tax_rate):
		self.db_conn = db_conn
		self.db_cursor = db_cursor
		self.tax_rate = tax_rate
		self.nontax = self.pretax = self.tax = Decimal('0.0')
		self.total = self.cash_used = self.cc_used = Decimal('0.0')
		self.cash_tendered = self.cc_tendered = Decimal('0.0')
		self.items_sold = Dec4('0.0')
		self.items_list = {}
		self.listbox_indices= []
		self.returning = False
		
		
	def complete_transaction(self, coupon_info = None):

		try:
			self.db_cursor.execute("INSERT INTO sales VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
				(self.nontax, self.pretax, self.tax, self.total, Dec4(self.items_sold), datetime.today().strftime('%Y-%m-%d'),
				datetime.now().strftime("%H:%M"), self.cash_used, self.cc_used, 0))
			self.db_cursor.execute('''SELECT MAX(sale_id) FROM sales''')
			max_sale_id = self.db_cursor.fetchone()[0]
			for key in self.items_list.keys():
				self.db_cursor.execute("INSERT OR IGNORE INTO sale_items VALUES(?, ?, ?, ?)",
					(max_sale_id, self.items_list[key]['item_price'], Dec4(self.items_list[key]['quantity_sold']), self.items_list[key]['item_id']))
				self.db_cursor.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", (key,))
				current_quantity = self.db_cursor.fetchone()[0]
				if not self.returning:
					self.db_cursor.execute("UPDATE inventory SET item_quantity = ? WHERE item_barcode = ?",
						(Dec4(current_quantity - self.items_list[key]['quantity_sold']), key))
				else:
					self.db_cursor.execute("UPDATE inventory SET item_quantity = ? WHERE item_barcode = ?",
						(Dec4(current_quantity + self.items_list[key]['quantity_sold']), key))
			self.db_conn.commit()
		except sqlite3.Error as e:
			print(f"Error when completing transaction: {e}")
			self.db_conn.rollback()
		#if seasonal_id is not None:
			#self.db_cursor.execute('''INSERT INTO seasonal_sales VALUES (NULL, ?, ?)''', (seasonal_id, max_sale_id))

		if coupon_info:
			self.db_cursor.execute("INSERT INTO coupons VALUES (NULL, ?, ?, ?)", (max_sale_id, coupon_info[0], coupon_info[1]))

	def complete_as_decrement(self):
		global datetime
		try:
			self.db_cursor.execute('''INSERT INTO inventory_decrements VALUES (NULL, ?)''', (datetime.now().strftime('%Y-%m-%d_%H-%M-%S'), ))
			max_decrement_id = self.db_cursor.execute('''SELECT MAX(decrement_id) FROM inventory_decrements''').fetchone()[0]
			for key in self.items_list.keys():
				self.db_cursor.execute("INSERT OR IGNORE INTO inventory_decrements_items VALUES (?, ?, ?)",
				(max_decrement_id, self.items_list[key]['item_id'], Dec4(self.items_list[key]['quantity_sold'])))
				self.db_cursor.execute("SELECT item_quantity FROM inventory WHERE item_barcode = ?", (key,))
				current_quantity = self.db_cursor.fetchall()[0][0]
				self.db_cursor.execute("UPDATE inventory SET item_quantity = ? WHERE item_barcode = ?",
					(Dec4(current_quantity - self.items_list[key]['quantity_sold']), key))
			self.db_conn.commit()
		except sqlite3.IntegrityError as e:
			print(e)
			self.db_conn.rollback()
	
		
	def update_seasonal_info(self, seasonal_id):

		self.db_cursor.execute('''INSERT INTO seasonals ''')

	def sell_item(self, entered_barcode, decimal_amount = Decimal('1')):
	
		results = self.db_cursor.execute('''SELECT item_name, item_price, item_taxable, item_id FROM inventory WHERE item_barcode = ?''',
			(entered_barcode,)).fetchone()

		if results == [] or not results:
			return "item_not_found", None, None, None
		
		if results['item_taxable'] == 1:
			self.tax += Decimal((results['item_price'])) * self.tax_rate * Decimal(decimal_amount)
			self.pretax += (results['item_price']) * Decimal(decimal_amount)
		else:
			self.nontax += Decimal(results['item_price']) * Decimal(decimal_amount)
		self.total = self.nontax + self.pretax + self.tax
		if entered_barcode not in self.items_list:
			self.items_list[entered_barcode] = {
				"item_name": results['item_name'], 
				"item_price": Decimal(results['item_price']), 
				"item_taxable": results['item_taxable'],
				"quantity_sold": decimal_amount,
				"item_id": results['item_id']}
			self.listbox_indices.append(entered_barcode)
		else:
			self.items_list[entered_barcode]["quantity_sold"] += Decimal(decimal_amount)

		self.items_sold += Decimal(decimal_amount)	
				
		return self.total, self.items_list[entered_barcode]['item_name'], self.items_list[entered_barcode]['item_price'] / Decimal(100), self.items_list[entered_barcode]['item_taxable']



		
	
