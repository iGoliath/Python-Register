import sqlite3
from decimal import Decimal
import csv

conn = sqlite3.connect("RegisterDatabase")
cursor = conn.cursor()


cursor.execute("SELECT * FROM inventory")

results = cursor.fetchall()

with open("inventory.csv", "w", newline="", encoding="utf-8") as file:

	writer = csv.writer(file)
	for row in results:
		writer.writerow([row[0], row[1],
		(row[2] / Decimal('100')).quantize(Decimal('0.01')),
		row[3], row[4], (row[5] / Decimal('10000')).quantize(Decimal('0.01')), 
		row[6], row[7], row[8]])

file.close()
