import json

class Config:

    def __init__(self):

        with open('/home/tbc/Desktop/Pullable/Python-Register/src/config.json', 'r') as fp:
            data = json.load(fp)
        
        self.printing_width = data['printing_width']
        self.backup_interval = data['backup_interval']
        self.tax_amount = data['tax_amount']
        self.backup_removal_cutoff = data['backup_removal_cutoff']
        self.manual_time_last_boot = data['manual_time_last_boot']
        self.tally_begin_date = data['tally_begin_date']