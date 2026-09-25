import json
import os
from pathlib import Path


def create_config_json():
    default_data = {
        "printing_width": 42,
        "backup_interval": 5,
        "tax_amount": "0.06625",
        "backup_removal_cutoff": 14,
        "manual_time_last_boot": True,
        "database_name": "RegisterDatabase",
        "backup_path": "~/Desktop/",
        "printer_vendor_id": "0x0000",
        "printer_product_id": "0x0000",
        "email_address": "johnsmith123@gmail.com",
    }
    try:
        with open(
            Path(__file__).parent / "../python_register/config.json", "x"
        ) as file:
            json.dump(default_data, file)
            return True
    except FileExistsError:
        return False
