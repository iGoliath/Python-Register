from datetime import datetime, timedelta, time
from escpos.printer import Usb, File
from decimal import Decimal
import calendar

class Printer:

	def __init__(self, state_manager, config):
		self.state_manager = state_manager
		self.config = config
		#self.printer = Usb(0x0fe6, 0x811e, 0) 
		self.printer = File("/tmp/output.bin")

	def print_receipt(
			self, receipt_type,
			items, sale_info, cash_tend = None, cc_tend = None):
		"""Print receipt based on what type of transaction occured."""
		self.print_receipt_header(receipt_type, sale_info['sale_id'])
		if receipt_type == "return":
			for category in ("non_tax", "pre_tax", "tax", "total"):
				sale_info[category] *= -1

		for sublist in items:
			self.state_manager.cursor.execute('''SELECT item_name FROM inventory WHERE item_id = ?''', (sublist[3], ))
			self.printer.textln(self.state_manager.cursor.fetchall()[0][0])
			if sublist[3] == 1:
				self.printer.text("TX ")
			else:
				self.printer.text("NT ")
			self.printer.textln(f"${sublist[1]} QTY {sublist[2]}")
		
		self.printer.ln(1)

		if sale_info['tax'] != 0:
			self.printer.ln(1)
			self.printer.textln(self._line(
				"Subtotal:",
				f"${(sale_info['non_tax'] + sale_info['pre_tax']):.2f}", 
				self.config.data['printing_width']))
			
			self.printer.textln(self._line(
				"Tax:", 
				f"${sale_info['tax']:.2f}", 
				self.config.data['printing_width']))
			
		self.printer.textln(self._line(
			"Total:", 
			f"${sale_info['total']:.2f}", 
			self.config.data['printing_width']))

		if cash_tend != 0 and cash_tend is not None:
			rounded = f"{cash_tend:.2f}"
			spaces = self.config.data['printing_width'] - 16 - len(rounded)
			self.printer.textln(f"Cash Tendered: {' ' * spaces}${rounded}")
		if cc_tend != 0 and cc_tend is not None:
			rounded = f"{cc_tend:.2f}"
			spaces = self.config.data['printing_width'] - 14 - len(rounded)
			self.printer.textln(f"CC Tendered: {' ' * spaces}${rounded}")
		if cash_tend != 0 and cc_tend != 0:
			change = f"{abs(sale_info['total'] - (cash_tend if cash_tend is not None else 0) - (cc_tend if cc_tend is not None else 0)):.2f}"
			spaces = self.config.data['printing_width'] - 13 - len(change)
			self.printer.textln(f"Change Due: {' ' * spaces}${change}")
			self.printer.ln(2)
			self.printer.cut()

	
	def run_x(self, starting_date = datetime.today(), ending_date = datetime.combine(datetime.today(), time.max), event=None):
			"""Sum daily totals and print them to a receipt."""
			ending_date = datetime.combine(ending_date, time.max)
			self.print_receipt_header("x", None, ending_date, starting_date)
		
			gross_total = 0
			gross_total_wo_tax = 0
		
			for key, category in {"Cash": "cash_used", "CC": "cc_used", "Non-Tax": "non_tax", "Pre-Tax": "pre_tax", "Tax": "tax"}.items():
				self.state_manager.cursor.execute('''SELECT "%s" FROM sales WHERE sale_date >= ? AND sale_date <= ? AND is_voided != 1''' % (category), (starting_date, ending_date, ))
				sum_in_question = sum(Decimal(row[0]) for row in self.state_manager.cursor.fetchall())
				if category in ("non_tax", "pre_tax", "tax"):
					gross_total += sum_in_question
				if category in ("non_tax", "pre_tax"):
					gross_total_wo_tax += sum_in_question

				self.printer.textln(self._line(f"{key.split()[0]} Collected:", f"${sum_in_question:.2f}", self.config.data['printing_width']))
			
			propane_results = self.state_manager.cursor.execute('''SELECT price_at_sale, quantity FROM sale_items JOIN sales ON sale_items.sale_id = sales.sale_id WHERE sale_items.item_id IN (78, 79, 92, 692, 693, 1274) AND sales.sale_date >= ? AND sales.sale_date <= ?''', (starting_date, ending_date, )).fetchall()
			propane_sold = sum(row[0] * row[1] for row in propane_results).quantize(Decimal("0.01")) if propane_results else Decimal('0.00')
			self.printer.textln(self._line("Propane sold:", f"${propane_sold}", self.config.data['printing_width']))

			self.printer.textln(self._line("Gross Total", f"${gross_total:.2f}", self.config.data['printing_width']))

			self.printer.textln(self._line("Gross Total w/o Tax", f"${gross_total_wo_tax:.2f}", self.config.data['printing_width']))

			self.state_manager.cursor.execute('''SELECT total FROM sales WHERE total < 0 AND sale_date BETWEEN ? AND ?''', (starting_date, ending_date))
			results = self.state_manager.cursor.fetchall()
			if results == []:
				self.printer.textln(self._line("Total Returns:", f"${abs(0):.2f}", self.config.data['printing_width']))
			else:
				total_returns = sum(row[0] for row in results).quantize(Decimal("0.01"))
				self.printer.textln(self._line("Total Returns:", f"${total_returns}", self.config.data['printing_width']))

			times_pressed = self.state_manager.cursor.execute('''SELECT SUM(times_pressed) FROM no_sale WHERE date >= ? AND date <= ?''', (starting_date, ending_date, )).fetchone()[0]
			self.printer.textln(self._line("# Times No Sale:", f"{str(times_pressed)}", self.config.data['printing_width']))
			self.printer.cut()


	def print_receipt_header(self, receipt_type, transaction_id, ending_date=datetime.today(), starting_date = datetime.today()):
			if receipt_type == "void":
				self.printer.textln(("-" * self.config.data['printing_width']))
				self.printer.textln(f'{"Void Transaction":-^{self.config.data["printing_width"]}}')
				self.printer.textln(("-" * self.config.data['printing_width']))
				self.printer.textln(self._line("Original Transaction ID:", str(transaction_id), self.config.data['printing_width']))
			elif receipt_type == "sale":
				self.printer.textln(f'{"Sale":-^{self.config.data["printing_width"]}}')
				self.printer.textln(self._line("Transaction ID", str(transaction_id), self.config.data['printing_width']))
			elif receipt_type == "return":
				self.printer.textln(f"{'Return':-^{self.config.data['printing_width']}}\n")
			elif receipt_type == "x":
				if self.is_month_range(starting_date, ending_date):
					self.printer.textln(f"{'-' * 13} Monthly Report {'-' * 13}")
				else:
					self.printer.textln(f"{'-' * 14} Daily Report {'-' * 14}")

				self.printer.textln(f"{'-' * 12} {datetime.now().strftime('%Y-%m-%d-%H:%M')} {'-' * 12}")
				self.printer.textln("-" * 42)
				self.printer.textln(f"{'-' * 10}From: {starting_date.strftime('%Y-%m-%d-%H:%M')}{'-' * 10}")
				self.printer.textln(f"{'-' * 11}To: {ending_date.strftime('%Y-%m-%d-%H:%M')}{'-' * 11}")
				self.printer.textln("-" * 42)
				self.printer.ln(2)
				

	def kick_drawer(self):
		self.printer.cashdraw(pin=2)

	def print_no_sale_receipt(self):
		self.printer.textln(("-" * 22) + " NS " + ("-" * 22))
		self.printer.textln(datetime.today().strftime('%Y-%m-%d') + (" " * 33) + datetime.now().strftime("%H:%M"))
		self.printer.ln(2)
		self.printer.cut()

	def is_month_range(self, start_date: datetime, end_date: datetime):

		if (start_date.year != end_date.year) or (start_date.month != end_date.month):
			return False

		if start_date.day != 1:
			return False
		
		_, last_day = calendar.monthrange(start_date.year, start_date.month)

		return end_date.day == last_day

	def _line(self, label: str, value: str, width: int) -> str:
		return f"{label}{value:>{width-len(label)}}\n"

