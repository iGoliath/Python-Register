from datetime import datetime, timedelta, time
from escpos.printer import Usb, File
from decimal import Decimal

class Printer:

	def __init__(self, state_manager, config):
		self.state_manager = state_manager
		self.config = config
		self.printer = Usb(0x0fe6, 0x811e, 0) 
		#self.printer = File("/tmp/output.bin")

	def print_receipt(
			self, receipt_type,
			items, sale_info, cash_tend = None, cc_tend = None):
		"""Print receipt based on what type of transaction occured."""
		self.print_receipt_header(receipt_type, sale_info[0])

		if receipt_type == "return":
			for i in (1, 2, 3, 4):
				sale_info[i] *= -1

		for sublist in items:
			self.state_manager.cursor.execute('''SELECT item_name FROM inventory WHERE item_id = ?''', (sublist[3], ))
			self.printer.textln(self.state_manager.cursor.fetchall()[0][0])
			if sublist[3] == 1:
				self.printer.text("TX ")
			else:
				self.printer.text("NT ")
			self.printer.textln(f"${sublist[1]} QTY {sublist[2]}")
		
		self.printer.ln(1)

		if sale_info[3] != 0:
			self.printer.ln(1)
			rounded = f"{sale_info[1]+sale_info[2]:.2f}"
			spaces = 31 - len(rounded)
			self.printer.textln(f"Subtotal: {' ' * spaces}${rounded}")
			rounded = f"{sale_info[3]:.2f}"
			spaces = 36 - len(rounded)
			self.printer.textln(f"Tax: {' ' * spaces}${rounded}")
		rounded = f"{sale_info[4]:.2f}"
		spaces = 34 - len(rounded)
		self.printer.textln(f"Total: {' '  * spaces}${rounded}")

		if cash_tend != 0 and cash_tend is not None:
			rounded = f"{cash_tend:.2f}"
			spaces = self.config.data['printing_width'] - 16 - len(rounded)
			self.printer.textln(f"Cash Tendered: {' ' * spaces}${rounded}")
		if cc_tend != 0 and cc_tend is not None:
			rounded = f"{cc_tend:.2f}"
			spaces = self.config.data['printing_width'] - 14 - len(rounded)
			self.printer.textln(f"CC Tendered: {' ' * spaces}${rounded}")
		change = f"{abs(sale_info[4] - (cash_tend if cash_tend is not None else 0) - (cc_tend if cc_tend is not None else 0)):.2f}"
		spaces = self.config.data['printing_width'] - 13 - len(change)
		self.printer.textln(f"Change Due: {' ' * spaces}${change}")
		self.printer.ln(2)
		self.printer.cut()

	
	def run_x(self, event=None, running_z = None):
			"""Sum daily totals and print them to a receipt."""
			end_of_day = datetime.combine(datetime.today(), time.max)
			if not running_z:
				self.print_receipt_header("x", None)
			else:
				self.print_receipt_header("z", None)
			gross_total = 0
			gross_total_wo_tax = 0

			for category in ("cash_used", "cc_used", "non_tax", "pre_tax", "Tax"):
				self.state_manager.cursor.execute('''SELECT "%s" FROM sales WHERE sale_date >= ? AND sale_date <= ? AND is_voided != 1''' % (category), (self.config.data['tally_begin_date'], end_of_day, ))
				sum_in_question = sum(Decimal(row[0]) for row in self.state_manager.cursor.fetchall())
				if category in ("non_tax", "pre_tax", "tax"):
					gross_total += sum_in_question
				if category in ("non_tax", "pre_tax"):
					gross_total_wo_tax += sum_in_question
				rounded = f"{sum_in_question:.2f}"
				spaces = 29 - len(category.split()[0]) - len(f"{sum_in_question}")
				self.printer.textln(f"{category.split()[0]} Collected: {' ' * spaces}${sum_in_question}\n")
			
			self.state_manager.cursor.execute('''SELECT price_at_sale, quantity FROM sale_items JOIN sales ON sale_items.sale_id = sales.sale_id WHERE sale_items.item_id IN (78, 79, 92, 692, 693, 1274) AND sales.sale_date >= ? AND sales.sale_date <= ?''', (self.config.data['tally_begin_date'], end_of_day, ))
			propane_sold = sum(row[0] * row[1] for row in self.state_manager.cursor.fetchall()).quantize(Decimal("0.01"))
			spaces = 42 - 15 - len(f"{propane_sold}")
			self.printer.textln(f"Propane Sold: {' ' * spaces}${propane_sold}\n")

			spaces = 42 - 14 - len(f"{gross_total:.2f}")
			self.printer.textln(f"Gross Total: {' ' * spaces}${gross_total:.2f}\n")

			spaces = self.config.data['printing_width'] - 22 - len(f"{gross_total_wo_tax:.2f}")
			self.printer.textln(f"Gross Total w/o Tax: {' ' * spaces}${gross_total_wo_tax:.2f}\n")

			self.state_manager.cursor.execute('''SELECT total FROM sales WHERE total < 0 AND sale_date = ?''', (datetime.today().strftime('%Y-%m-%d'), ))
			results = self.state_manager.cursor.fetchall()
			if results == []:
				total_returns = 0
				spaces = 42 - 16 - len(f"{total_returns:.2f}")
				self.printer.textln(f"Total Returns: {' ' * spaces}${abs(total_returns):.2f}\n")
			else:
				total_returns = sum(row[0] for row in results).quantize(Decimal("0.01"))
				spaces = 42 - 15 - len(f"{total_returns}")
				self.printer.textln(f"Total Returns: {' ' * spaces}${abs(total_returns):.2f}\n")

			self.state_manager.cursor.execute('''SELECT SUM(times_pressed) FROM no_sale WHERE date >= ? AND date <= ?''', (self.config.data['tally_begin_date'], end_of_day, ))
			results = self.state_manager.cursor.fetchall()
			times_pressed = results[0]
			spaces = 28 - len((str(times_pressed)))
			self.printer.textln("# Times No Sale: " + (" " * spaces) + str(times_pressed[0]))
			self.printer.cut()


	def print_receipt_header(self, receipt_type, transaction_id):
			if receipt_type == "void":
				self.printer.textln(("-" * 42))
				self.printer.textln(f"{'-' * 12} Void Transaction {'-' * 12}")
				self.printer.textln(("-" * 42))
				spaces = 17 - len(str(transaction_id))
				self.printer.textln(f"Original Transaction ID: {' ' * spaces}{str(transaction_id)}")
			elif receipt_type == "sale":
				self.printer.textln(f"{'-' * 18} Sale {'-' * 18}")
				spaces = self.config.data['printing_width'] - 16 - len(str(transaction_id))
				self.printer.textln(f"Transaction ID: {' ' * spaces}{str(transaction_id)}")
			elif receipt_type == "return":
				self.printer.textln(f"{'-' * 17} Return {'-' * 17}")
				spaces = 26 - len(str(transaction_id))
				self.printer.textln(f"Transaction ID: {' ' * spaces}{str(transaction_id)}")
			elif receipt_type == "x":
				self.printer.textln(("-" * 42))
				self.printer.textln(f"{'-' * 14} Daily Report {'-' * 14}")
				self.printer.textln(f"{'-' * 12} {datetime.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M')} {'-' * 12}")
				self.printer.textln("-" * 42)
				self.printer.ln(2)
			elif receipt_type == "z":
				self.printer.textln(("-" * 42))
				self.printer.textln(f"{'-' * 13} Monthly Report {'-' * 13}")
				self.printer.textln(f"{'-' * 12} {datetime.today().strftime('%Y-%m-%d')} {datetime.now().strftime('%H:%M')} {'-' * 12}")
				self.printer.textln("-" * 42)
				self.printer.ln(2)

			if receipt_type != "x" and receipt_type != "z":
				self.printer.textln(f"{datetime.today().strftime('%Y-%m-%d')}{' ' * 27}{datetime.now().strftime('%H:%M')}")
				self.printer.ln(2)

	def kick_drawer(self):
		self.printer.cashdraw(pin=2)

	def print_no_sale_receipt(self):
		self.printer.textln(("-" * 22) + " NS " + ("-" * 22))
		self.printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 33) + datetime.now().strftime("%H:%M"))
		self.printer.ln(2)
		self.printer.cut()