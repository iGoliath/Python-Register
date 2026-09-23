# Python Register
## Point-of-Sale (POS) system developed using Python and SQLite

Welcome! This repo contains a POS system developed using the Python programming language and SQLite database engine.
Python is useful as it is a language rich in third-party packages.
This comes in handy when interfacing with hardware like receipt printers and cash drawers.
SQLite is a light-weight, self-contained SQL database engine.
This allows for ease of local data storage and retrieval, and allows for future uploading of data to a centralized SQL server.

## Who is this for?

At its core, this program was written and is intended for small businesses.
In my case, the cash register I sought to replace was a Casio PCR-T280. Essentially nothing more than a fancy calculator that stored some values.
The vision is to create an easy to use and lightweight but powerful program that can be run on most hardware business owners might have lying around.
Additionally, it brings small businesses into the modern day in terms of their POS system, without needing fancy hardware or subscriptions.


## Features

### Below are the features I would say are "working". I am sure they will change in code, functionality, efficiency, etc. in the future, but for now they work:

1. Storing and retrieving items from inventory.
2. Selling those items, and logging the information in SQLite.
3. Voiding or returning sales/items.
4. Canceling sales or individual items in a sale.
5. Logging with Python's Decimal module. Monetary values are stored as integer with two points of precision, and quantity values are stored as integers with four points of precision.
6. Manual changing of quantity on register screen, removing the need to scan barcodes repeatedly.
7. Printing an X, which gives some X-to-date totals.
8. Ability to look-up items both when ringing them up in the register and when altering their information in inventory.
9. Full database backups performed on a specified schedule, and removal of old backups from a specified date range.

### Below is a list of features that are either currently being worked on or are planed in future updates. They appear in no particular order:

1. Major refactor of tkinter widgets. Each main "screen frame" is being moved to its own module, and program will load these as needed. Currently, all frames and widgets are initialized upon program's launch.
2. Changing of tkinter widgets to something more appealing, like ttk or ctk.
3. Ability to upload database files to cloud services using something like Rclone.
4. Either in-program or helper program tools to retrieve database information. I.E. sales of chocolate bars from date X to Y, perhaps displayed in a graph.
5. Ease of changing inventory. This could look like the ability to upload your tables to excel and edit them, or perhaps tools that call SQL.
6. Settings are currently handled through a manually edited JSON file. I'd like to add a settings page.
7. To go along with settings, eventually I'd like to add a "welcome mode" or "tutorial mode" upon first program boot to help user set up their environment and understand the program.
8. Outward facing screen to display totals to customer. Currently I am working on using a max7219 and the luma module.
9. I'd like to eventually write a proper instruction/user manual. For now that makes no sense with how much will definitely change.

## How to Use

### For now, this will be sort of janky. Bear with me as I make the program easier to get up and running.

```bash
# !!!Please note that this installation guide was written and worked on in Linux only. I will work on getting it up and running on Windows and MacOS in the future.

# Download and install Python for your specific operating system. (https://www.python.org/downloads/) I would recommend at least version 3.13.

# Ensure git is installed. https://git-scm.com/install/

# Clone this repository
git clone https://github.com/iGoliath/Python-Register

# Install as a package
pip install -e .

# Navigate to main directory
cd Python-Register/src/python_register

# Run the first time setup script
python3 first_time_checks.py

# Run the program
python3 -m python_register.Register

```

By default, backups will be disabled and the printer will be set to a file output. Additionally, the config.json file is setup for my personal environment. You can edit these as follows:
### Backups:
1. Open Python-Register/src/python_register/Register.py in your editor of choice.
2. Uncomment lines 771-779.
3. Replace the directory in the connect statement in the function perform_backup() with your desired location for backups.

### Printer:
1. Open Python-Register/src/python_register/printing_manager.py in your editor of choice.
2. Comment the line 'self.printer = File("/tmp/output.bin")'
3. Open Terminal
4. Run lsusb and find the vendor ID and product ID of your esc-pos compatible receipt printer. They are the numbers in the format XXXX:XXXX
5. Replace these sections in the 'self.printer = Usb' line above the one you commented out. For example, my printer is 0FE6:811E. The line would then be 'self.printer = Usb(0x0f36, 0x811e, 0)

### Config:

Edit config.json located in Python-Register/src/python_register
The fields are as follows:
printing_width: Width in characters of receipt printer. Most are 42 or 48.
backup_interval: Time, in seconds, to perform each scheduled backup.
tax_amount: Amount of tax to be applied to sold items.
backup_removal_cutoff: Time, in days, back in history that backups will be removed by remove_old_backups()
manual_time_last_boot: Flag whether or not the last boot could not establish the time. This is less used for right now.
tally_begin_date: Date that run_x() will sum back from.
database_name: Name of the database. Only RegisterDatabase is accepted for now.

### Default keybinds are as follows:
Backspace - Clear  
NumPad Enter - Sell as Cash  
NumPad Add - Sell as Credit Card  
NumPad Multiply - Main Menu  
NumPad Divide - Cancel Sale  
NumPad Subtract - No Sale  
Backslash - Decrement currently rang up items from inventory without sale  

## Feedback / Critique

Any help with this project would be much appreciated.
This is my first ever real program that I've written to serve a purpose.
As such, I am sure there are an infinite number of things I am forgetting or have done wrong.
Feedback would be great to help me out. 
For now, please leave anything you'd like on the Feedback discussion.