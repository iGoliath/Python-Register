import csv
import smtplib
import ssl
import threading
import tkinter as tk
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path

import keyring

from .base_frame import BaseFrame


class RunReportsFrame(BaseFrame):

    def build_widgets(self):

        tk.Button(
            self,
            font=("Arial", 58),
            text="Drinks",
            command=lambda: threading.Thread(
                target=self.send_drinks_report,
                args=(self.controller.state_mgr.get_drink_quantities(),),
            ).start(),
        ).grid(column=1, row=0, sticky="nsew")

        tk.Button(
            self,
            font=("Arial", 58),
            text="Back",
            command=lambda: self.wm.show_frame("admin_menu"),
        ).grid(column=1, row=1, sticky="nsew", pady=50)

    def send_drinks_report(self, query_results):
        """Create an SMTP server, setup an email, and send it"""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            context=context,
        ) as server:
            server.login(
                self.controller.config.data["email_address"],
                keyring.get_password(
                    "PythonPOSSystem", self.controller.config.data["email_address"]
                ),
            )
            msg = EmailMessage()
            msg["to"] = """Recipient address"""
            msg["from"] = """sender_address"""
            msg["subject"] = f"POS System Report | {datetime.today()}"
            msg.set_content(
                "Hello,\nThis email is being sent from the POS System. "
                "It contains a csv file detailing drink inventory information."
            )

            with open("temp.csv", "w", newline="", encoding="utf-8") as file:

                writer = csv.writer(file)
                query_results = self.controller.state_mgr.get_drink_quantities()
                writer.writerow(
                    [
                        "Item ID",
                        "Name",
                        "Price",
                        "Stock",
                        "Number Sold",
                        "Number Decremented",
                    ]
                )
                for row in query_results:
                    writer.writerow(
                        [
                            row["item_id"],
                            row["item_name"],
                            f'${row["item_price"]:.2f}',
                            row["item_quantity"],
                            row["total_sold"],
                            row["total_decremented"],
                        ]
                    )

            attachment_file = Path("temp.csv")
            with open(attachment_file, "rb") as attachment:
                msg.add_attachment(
                    attachment.read(),
                    maintype="text",
                    subtype="csv",
                    filename=attachment_file.name,
                )

            server.send_message(msg)
