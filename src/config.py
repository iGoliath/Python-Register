import json
from pathlib import Path

class Config:

    def __init__(self):

        current_dir = Path(__file__).parent
        file_path = current_dir / "config.json"

        with open(file_path, 'r') as fp:
            data = json.load(fp)
        
        self.printing_width = data['printing_width']
        self.backup_interval = data['backup_interval']
        self.tax_amount = data['tax_amount']
        self.backup_removal_cutoff = data['backup_removal_cutoff']
        self.manual_time_last_boot = data['manual_time_last_boot']
        self.tally_begin_date = data['tally_begin_date']