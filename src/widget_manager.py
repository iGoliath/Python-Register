import tkinter as tk
from tkinter import ttk
import widget_functions as wf
from datetime import datetime
import subprocess

class WidgetManager:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        """Initialize all frames necessary for the program"""

        self.admin_menu_frame = tk.Frame(self.root)
        self.register_menu_frame = tk.Frame(self.root)
        self.add_item_listbox_frame = tk.Frame(self.root)
        self.add_item_frame = tk.Frame(self.root)
        self.register_frame = tk.Frame(self.root, bg='black')
        self.main_menu_frame = tk.Frame(self.root)
        self.menu_buttons_frame=tk.Frame(self.main_menu_frame)
        self.reenter_frame = tk.Frame(self.add_item_frame)
        self.add_item_yes_no = tk.Frame(self.add_item_frame)
        self.register_add_item_prompt_frame = tk.Frame(self.root)
        self.browse_transactions_frame = tk.Frame(self.root)
        self.errors_frame = tk.Frame(self.root, width = 400, height = 300, borderwidth=20, relief="ridge", bg="black")
        self.seasonal_id_entry_frame = tk.Frame(self.root, width=400, height=300, borderwidth=20, relief='ridge', bg="black")
        self.datetime_frame = tk.Frame(self.root)

        # Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
        # Widgets in column 1 will determine the width of the rest of the widgets
        for frame in (self.register_frame, self.add_item_frame, 
            self.main_menu_frame, self.add_item_listbox_frame,
            self.register_add_item_prompt_frame, self.browse_transactions_frame):
            frame.grid(row=0, column=0, sticky='nsew')
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=0)
            frame.grid_columnconfigure(2, weight=1)   

        """These frames only need 2 columns of widgets, so
        configure them as such."""
        for frame in (
            self.reenter_frame, self.add_item_yes_no, self.admin_menu_frame,
            self.menu_buttons_frame, self.admin_menu_frame, self.register_menu_frame):
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        self.register_menu_frame.grid(column = 0, row = 0, sticky='nsew')
        self.admin_menu_frame.grid(column = 0, row = 0, sticky='nsew')

        self.errors_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.errors_frame.grid_columnconfigure(0, weight=1)
        self.errors_frame.grid_columnconfigure(1, weight=0)
        self.errors_frame.grid_columnconfigure(2, weight=1)

        self.seasonal_id_entry_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.seasonal_id_entry_frame.grid_columnconfigure(0, weight=1)
        self.seasonal_id_entry_frame.grid_columnconfigure(1, weight=0)
        self.seasonal_id_entry_frame.grid_columnconfigure(2, weight=1)


        # ===============================
        # Widgets for Register Mode frame
        # ===============================

        self.register_frame.config(bg="black")

        self.new_frame = tk.Frame(self.register_frame, bg="black")
        self.new_frame.columnconfigure(0, weight=1)
        self.new_frame.columnconfigure(1, weight=1)

        self.register_label = tk.Label(
            self.new_frame, font=("Arial", 30), text="Mode: Register", fg="#68FF00", bg="black"
        )
        self.register_label.grid(column=0, row=0, sticky='sw', pady=5)
        #Entry box where numbers user is typing are being displayed 
        self.usr_entry = tk.Entry(
            self.new_frame, font=("Arial", 91),
            bg="black", fg="#68FF00", justify="right", width=9)
        self.usr_entry.insert(tk.END, "$0.00")
        self.usr_entry.grid(column=1, row=0, sticky='e', padx=2)
        self.usr_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        # Invisible entry where user input actually occurs. Allows user entry to be untampered so 
        # same entry box can be used for barcodes and numberic values alike
        self.invisible_entry = tk.Entry(self.register_frame)
        self.invisible_entry.place(x=0, y=-50)
        self.invisible_entry.bind("<Return>", controller.process_sale)
        self.bind_invisible_entry_keys()

        # Box where program outputs current running total
        self.total_entry = tk.Entry(
            self.new_frame, font=("Arial", 35), width=10, bg="black",
            fg="#68FF00")
        self.total_entry.insert(tk.END, "$0.00")
        self.total_entry.grid(column = 0, row = 0, sticky='nw')
        self.total_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        self.new_frame.grid(column = 1, row = 0, sticky='nsew')
        self.sale_items_listbox = tk.Listbox(
            self.register_frame, width=34, bg="black",
            height=8, font=("Courier New", 37), fg="white"
        )
        self.sale_items_listbox.grid(column = 1, row = 2, sticky='nsw')
        self.sale_items_listbox.bind("<FocusIn>", controller.return_invisible_entry_focus)
        self.sale_items_scrollbar = tk.Scrollbar(
            self.register_frame, bg="white",
            orient=tk.VERTICAL, width=40
        )
        self.sale_items_scrollbar.grid(column = 1, row = 2, sticky='nse')
        self.sale_items_listbox.config(yscrollcommand= self.sale_items_scrollbar.set)
        self.sale_items_scrollbar.config(command = self.sale_items_listbox.yview)

        self.register_add_item_prompt_label=tk.Label(
            self.register_add_item_prompt_frame, text="Item not found\nAdd it?", font=("Arial", 50))
        self.register_add_item_prompt_label.grid(row=0, column=1, sticky='ew')

        self.register_add_item_yes_no_frame=tk.Frame(self.register_add_item_prompt_frame)
        self.register_add_item_yes_no_frame.grid_columnconfigure(0, weight=1)
        self.register_add_item_yes_no_frame.grid_columnconfigure(1, weight=1)
        self.register_add_item_yes_no_frame.grid(row=1, column=1, sticky='nsew')

        self.register_add_item_yes_button=tk.Button(
            self.register_add_item_yes_no_frame, text="Yes", font=("Arial", 90),
            command = lambda: self.controller.state_manager.yes_no_var.set("yes"))
        self.register_add_item_yes_button.grid(row=0, column=0, sticky='nsew')

        self.register_add_item_no_button=tk.Button(
            self.register_add_item_yes_no_frame, text="No",
            font=("Arial", 90), command = lambda: self.controller.state_manager.yes_no_var.set("no"))
        self.register_add_item_no_button.grid(row=0, column=1, sticky='nsew')


        # ==========================
        # Widgets for Add Item frame
        # ==========================

        self.add_item_label = tk.Label(
            self.add_item_frame, text="Please enter the item's barcode:",
              font=("Arial", 50), width=27)

        self.add_item_button = tk.Button(
            self.add_item_frame, text="Next", font=("Arial", 50),
              command=lambda: controller.on_add_item_enter())

        self.back_button = tk.Button(
            self.add_item_frame, text="Back", font=("Arial", 50),
              command=lambda: controller.go_back())

        self.quit_button = tk.Button(
            self.add_item_frame, text="Quit", font=("Arial", 50),
              command = lambda: self.main_menu_frame.tkraise())

        self.add_item_entry = tk.Entry(
            self.add_item_frame, font=("Arial", 50),
            width=15, justify="right")
        self.add_item_entry.bind("<Return>", controller.on_add_item_enter)

        self.add_item_invisible_entry = tk.Entry(
            self.add_item_frame, font=("Arial", 50), width=15, justify="right")
        self.add_item_invisible_entry.place(x=-10, y=-10)
        self.add_item_invisible_entry.bind("<Return>", controller.on_add_item_enter)
        self.add_item_invisible_entry.bind("<KeyRelease-KP_Enter>", controller.on_add_item_enter)
        for key in ("Left", "Right", "Up", "Down"):
            self.add_item_invisible_entry.bind(f"<{key}>", wf.disable_arrow_keys)


        self.item_info_confirmation = tk.Text(
            self.add_item_frame, font=("Arial", 40),
            width=6, height=3)
        self.item_info_confirmation.tag_configure("justify_right", justify = "right")
        self.yes_button = tk.Button(
            self.add_item_yes_no, text="Yes", font=("Arial", 150),
            command= lambda: controller.on_yes_no("yes"))

        self.no_button = tk.Button(
            self.add_item_yes_no, text="No", font=("Arial", 150),
            command=lambda: controller.on_yes_no("no"))

        self.yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
        self.no_button.grid(column=1, row=0, sticky='nsew', padx=10)

        # =========================
        # Widgets for Listbox Frame
        # =========================

        self.add_item_listbox = tk.Listbox(
            self.add_item_listbox_frame, width=20,
            height=5, font=("Arial", 50))
        self.add_item_scrollbar = tk.Scrollbar(
            self.add_item_listbox_frame,
            orient=tk.VERTICAL, width=40)

        self.add_item_listbox.grid(row=1, column=1, sticky='nw')
        self.add_item_scrollbar.grid(row=1, column=1, sticky='nse')

        self.add_item_scrollbar_label = tk.Label(
            self.add_item_listbox_frame,
            text="Please select category:", font=("Arial", 50))
        self.add_item_scrollbar_label.grid(column=1, row=0, sticky='nsew')

        self.add_item_scrollbar_next = tk.Button(
            self.add_item_listbox_frame, text="Next", font=("Arial", 50),
              command=lambda: controller.on_add_item_scrollbar_next())
        self.add_item_scrollbar_next.grid(row=2, column=1, sticky='nsew')

        self.add_item_scrollbar_back = tk.Button(
            self.add_item_listbox_frame, text="Back",
            font=("Arial", 50), command=lambda: controller.go_back())
        self.add_item_scrollbar_back.grid(column=1, row=3, sticky='nsew')

        self.add_item_scrollbar_quit = tk.Button(
            self.add_item_listbox_frame, text="Quit", font=("Arial", 50),
            command=lambda: self.admin_frame.tkraise())
        self.add_item_scrollbar_quit.grid(column=1, row=4, sticky='nsew')

        for values in (
            "Camping", "Candy", "Cleaning", "Clothes",
            "Cookies/Chips", "Drinks", "Dry Goods", "Fishing",
            "Gifts", "Ice Cream", "Kitchenware", "Medicinal",
            "Paper Products", "Pool", "Propane", "Refrigerated",
            "RV", "Toiletries", "Toys"):
            self.add_item_listbox.insert(tk.END, values)

        self.add_item_listbox.config(yscrollcommand= self.add_item_scrollbar.set)
        self.add_item_scrollbar.config(command = self.add_item_listbox.yview)

        # Buttons for options when user wants to correct one of their inputs

        self.add_name_button = tk.Button(
            self.reenter_frame, text="Name", font=("Arial", 75),
            command = lambda: controller.reenter_button_pressed("name"))
        self.add_name_button.grid(row=0, column=0, sticky='nsew')

        self.add_price_button = tk.Button(
            self.reenter_frame, text="Price", font=("Arial", 75),
            command = lambda: controller.reenter_button_pressed("price"))
        self.add_price_button.grid(row=0, column=1, sticky='nsew')

        self.add_barcode_button = tk.Button(
            self.reenter_frame, text="Barcode", font=("Arial", 75),
            command = lambda: controller.reenter_button_pressed("barcode"))
        self.add_barcode_button.grid(row=1, column=0, sticky='nsew')

        self.add_taxable_button = tk.Button(
            self.reenter_frame, text="Taxable", font=("Arial", 75),
            command = lambda: controller.reenter_button_pressed("taxable"))
        self.add_taxable_button.grid(row=1, column=1, sticky='nsew')

        self.add_quantity_button = tk.Button(
            self.reenter_frame, text="Quantity", font=("Arial", 75),
            command = lambda: controller.reenter_button_pressed("quantity"))
        self.add_quantity_button.grid(row=2, column=0, sticky='nsew')

        self.add_category_button = tk.Button(
            self.reenter_frame, text="Category", font=("Arial", 75),
            command = lambda: self.reenter_button_pressed("category"))
        self.add_category_button.grid(row=2, column=1, sticky='nsew')

        # ==========================================
        # Widgets for Additional Register Functions 
        # ==========================================

        self.menu_label = tk.Label(
            self.main_menu_frame, text="Menu", font=("Arial", 50))
        self.menu_label.grid(column = 1, row = 0, sticky='ew')

        
        self.menu_buttons_frame.grid(row=1, column=1, sticky='nsew')

        self.register_functions_button = tk.Button(
            self.menu_buttons_frame, text="Register\nFunctions", font=("Arial", 60),
            command = lambda: self.register_menu_frame.tkraise()
        )
        self.register_functions_button.grid(column = 0, row = 0, sticky='nsew',pady=5)

        self.admin_functions_button = tk.Button(
            self.menu_buttons_frame, text="Administrator\nFunctions", font=("Arial", 60),
            command = lambda: self.admin_menu_frame.tkraise()
        )
        self.admin_functions_button.grid(column = 0, row = 1, sticky='nsew', pady=5)

        self.main_menu_back_button = tk.Button(
            self.menu_buttons_frame, text="Back", font=("Arial", 60),
            command = lambda: controller.enter_register_frame()
        )
        self.main_menu_back_button.grid(column = 0, row = 2, sticky='nsew', pady=5)



        self.void_button = tk.Button(
            self.register_menu_frame, text="Void Trans",
            font=("Arial", 58), command = lambda: controller.void_transaction())
        
        self.print_receipt_button = tk.Button(
            self.register_menu_frame, text="Print Receipt", font=("Arial", 58))

        self.make_return_button = tk.Button(
            self.register_menu_frame, text="Make Return",
            font=("Arial", 58), command = lambda: controller.process_return())
         
        self.back_to_register_button = tk.Button(
            self.register_menu_frame, text="Back",
            font=("Arial", 58), command = lambda: self.main_menu_frame.tkraise())
        
        self.seasonal_button = tk.Button(
            self.register_menu_frame, text="Seasonal Sale",
            font=("Arial", 58), command = lambda: self.setup_seasonal_sale())
        
        self.void_button.grid(column = 0, row = 0, sticky='nsew', pady=2)
        self.print_receipt_button.grid(column = 1, row = 0, sticky='nsew', pady=2)
        self.make_return_button.grid(column = 0, row = 1, sticky='nsew', pady=2)
        self.back_to_register_button.grid(column = 1, row = 1, sticky='nsew', pady=2)
        self.seasonal_button.grid(column = 0, row = 2, sticky='nsew', pady=2)

        self.run_x_button = tk.Button(
            self.admin_menu_frame, text = "Run X", font=("Arial", 58),
            height = 1, command = lambda: controller.run_x())

        self.new_item_button = tk.Button(
            self.admin_menu_frame, text = "Manage Inv", font=("Arial", 58),
            height = 1, command = lambda: controller.enter_add_item_frame())

        self.fullscreen_button = tk.Button(
            self.admin_menu_frame, text="Fullscreen",
            font=("Arial", 58), command = lambda: self.datetime_frame.tkraise())

        self.browse_transactions_button = tk.Button(
            self.admin_menu_frame, text="Browse Trans", 
            font=("Arial", 58), command = lambda: self.controller.enter_browse_transactions_frame(0, 0))
        
        self.quit_program_button = tk.Button(
            self.admin_menu_frame, text="Quit Program",
            font=("Arial", 58), command = lambda: self.quit_program())
        
        self.manage_seasonals_button = tk.Button(
            self.admin_menu_frame, text="Manage\nSeasonals", font=("Arial", 58),
            command = lambda: controller.enter_browse_transactions_frame(0, 1)
        )
        
        self.run_x_button.grid(column = 0, row = 0, sticky='nsew', pady=2)
        self.new_item_button.grid(column = 1, row = 0, sticky='nsew', pady=2)
        self.fullscreen_button.grid(column = 0, row = 1, sticky='nsew', pady=2)
        self.browse_transactions_button.grid(column = 1, row = 1, sticky='nsew', pady=2)
        self.quit_program_button.grid(column = 0, row = 2, sticky='nsew', pady=2)
        self.manage_seasonals_button.grid(column = 1, row = 2, sticky='nsew', pady=2)
       
        
        
      
        # ===========================================
        # Widgets for browsing / voiding transactions
        # ===========================================

        self.browse_label = tk.Label(
            self.browse_transactions_frame, text="Browsing Transactions", font=("Arial", 40))
        self.browse_label.grid(column = 1, row = 0, sticky='ew', pady=10)

        self.browse_prev_button = tk.Button(
            self.browse_transactions_frame, text="<<", font=("Arial", 55),
            command = lambda: self.controller.state_manager.browse_index.set(self.controller.state_manager.browse_index.get() - 1)
        )
        self.browse_prev_button.grid(column = 0, row = 1, sticky='nsw')

        self.browse_next_button = tk.Button(
            self.browse_transactions_frame, text=">>", font=("Arial", 55),
            command = lambda: self.controller.state_manager.browse_index.set(self.controller.state_manager.browse_index.get() + 1)
        )
        self.browse_next_button.grid(column = 2, row = 1, sticky='nse')

        self.browse_text = tk.Text(
            self.browse_transactions_frame, width=28, height=4,
            font=("Arial", 39)
        )
        self.browse_text.tag_configure("bold", font=("Arial", 40, "bold"))
        self.browse_text.grid(column = 1, row = 1, sticky='ew', pady=10)
        self.browse_text.bind("<FocusIn>", self.controller.return_browse_entry_focus)

        self.browse_second_label = tk.Label(
            self.browse_transactions_frame, text="Press continue when satisfied", font=("Arial", 50)
        )

        self.browse_entry_frame = tk.Frame(self.browse_transactions_frame)
        self.browse_entry_frame.grid_columnconfigure(1, weight=1)
        self.browse_entry_frame.grid_columnconfigure(0, weight=1)

       
        self.browse_entry = tk.Entry(
            self.browse_entry_frame, font=("Arial", 35),
            width = 10, validate='key', vcmd=self.controller.vcmd)
        self.browse_entry.bind("<Return>", lambda event: self.controller.state_manager.browse_index.set(int(self.browse_entry.get())))
        self.browse_entry.grid(column = 0, row = 0, sticky='nsew')
        self.browse_entry_frame.grid(column = 1, row = 2, sticky='ew', pady=30)


        self.browse_go_button = tk.Button(self.browse_entry_frame, font=("Arial", 40),
            text = "-> GO", command = lambda: self.controller.state_manager.browse_index.set(int(self.browse_entry.get())))
        self.browse_go_button.grid(column = 1 , row = 0, sticky='nsew')

        self.browse_confirm_button = tk.Button(self.browse_transactions_frame, text="Confirm",
            font=("Arial", 50), command = lambda: self.controller.state_manager.void_var.set("")
        )

        self.add_seasonal_button = tk.Button(
            self.browse_entry_frame, font=("Arial", 35), text="Add"
        )

        self.remove_seasonal_button = tk.Button(
            self.browse_entry_frame, font=("Arial", 35), text="Remove"
        )

        self.edit_seasonal_button = tk.Button(
            self.browse_transactions_frame, font=("Arial", 35), text="Edit"
        )

        self.seasonal_buttons_frame = tk.Frame(self.browse_transactions_frame)
        self.seasonal_buttons_frame.grid_columnconfigure(0, weight = 1, uniform="equal")
        self.seasonal_buttons_frame.grid_columnconfigure(1, weight = 1, uniform="equal")
        self.seasonal_buttons_frame.grid_columnconfigure(2, weight = 1, uniform="equal")

        self.seasonal_buttons_frame.grid(column = 1, row = 3, sticky='ew')

        self.add_seasonal_button.grid(column = 0, row = 0, sticky='nsew')
        self.remove_seasonal_button.grid(column = 1, row = 0, sticky='nsew')
        self.edit_seasonal_button.grid(column = 2, row = 0, sticky='nsew')

        self.browse_back_button = tk.Button(
            self.browse_transactions_frame, text="Back",
            font=("Arial", 35), command = lambda: controller.menu_back()
        )
        #self.browse_back_button.grid(column = 1, row = 4, sticky='nsew')

        self.error_label = tk.Label(self.errors_frame, text="ERROR:", font=("Arial", 50), fg="red", justify="center")
        self.error_label.grid(column=1, row=0, sticky='ew')

        self.error_description_label = tk.Label(self.errors_frame, text="", font=("Arial", 50))
        self.error_description_label.grid(column = 1, row = 1, sticky='ew')

        self.error_ok_button = tk.Button(self.errors_frame, text="Ok", font=("Arial", 50),
            command = lambda: self.errors_frame.lower())
        self.error_ok_button.grid(column = 1, row = 2, sticky='ew')

        # =============================
        # Widgets for Seasonal ID Entry
        # =============================

        self.seasonal_id_label = tk.Label(
            self.seasonal_id_entry_frame, font=("Arial", 50),
            text="Please enter\nSeasonal's ID"
        )
        self.seasonal_id_label.grid(column = 1, row = 0, sticky='nsew')

        self.seasonal_id_entry = tk.Entry(
            self.seasonal_id_entry_frame, font=("Arial", 50),
            validate='key', vcmd=self.controller.vcmd)
        self.seasonal_id_entry.grid(column = 1, row = 1, sticky='nsew')

        self.seasonal_id_button = tk.Button(
            self.seasonal_id_entry_frame, font=("Arial", 50),
            text="Confirm", command = lambda: self.controller.state_manager.seasonal_id_var.set(self.seasonal_id_entry.get()))
        self.seasonal_id_button.grid(column = 1, row = 2, sticky='nsew')
        
        # =============================
        # Widgets for Manual Time Entry
        # =============================

        self.datetime_frame.columnconfigure(0, weight=0)
        self.datetime_frame.columnconfigure(1, weight=1)
        self.datetime_frame.columnconfigure(2, weight=0)

        self.datetime_frame.grid(column=0, row=0, sticky='nsew')

        self.date_widgets_frame = tk.Frame(self.datetime_frame)

        self.date_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(1, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(2, weight=1, uniform="equal")


        self.datetime_label = tk.Label(
            self.datetime_frame, font=("Arial", 35),
            text="Current time could not be synced. Please\nenter the current time below, or exit the \nprogram and check for an internet connection."
        )
        self.datetime_label.grid(column = 1, row = 0, sticky='nsew', pady=15)

        self.year_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Year"
        )

        self.month_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Month"
        )

        self.day_label = tk.Label(
            self.date_widgets_frame, font=("Arial", 35), text="Day"
        )
        
        self.date_widgets_frame.grid(column = 1, row = 1, sticky='nsew')
        self.year_label.grid(column = 0, row = 0, sticky='nsew')
        self.month_label.grid(column = 1, row = 0, sticky='nsew')
        self.day_label.grid(column = 2, row = 0, sticky='nsew')

        
        self.year_spinbox = tk.Spinbox(
            self.date_widgets_frame, from_=2026, to=2100, font=("Arial", 50), width = 5
        )
        self.year_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.month_spinbox = tk.Spinbox(
            self.date_widgets_frame, from_=1, to=12, font=("Arial", 50), width=5, wrap=True
        )
        self.month_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())
        
        self.date_spinbox = tk.Spinbox(
            self.date_widgets_frame, from_=1, to=31, font=("Arial", 50), width=5, wrap=True
        )
        self.date_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.year_spinbox.grid(column=0,row=1,sticky='nsew')
        self.month_spinbox.grid(column = 1, row = 1, sticky='nsew')
        self.date_spinbox.grid(column = 2, row = 1, sticky='nsew')

        self.time_widgets_frame = tk.Frame(self.datetime_frame)

        self.time_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.time_widgets_frame.columnconfigure(1, weight=1, uniform="equal")

        self.time_widgets_frame.grid(column = 1, row = 2, sticky='nsew')
        self.hours_label = tk.Label(
            self.time_widgets_frame, font=("Arial", 35), text=("Hour")
        )

        self.minutes_label = tk.Label(
            self.time_widgets_frame, font=("Arial", 35), text=("Minute")
        )

        self.hours_spinbox = tk.Spinbox(
            self.time_widgets_frame, from_=0, to=23, font=("Arial", 50), width=5, wrap=True
        )
        self.hours_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.minute_spinbox = tk.Spinbox(
            self.time_widgets_frame, from_=0, to=59, font=("Arial", 50), width=5, wrap=True
        )
        self.minute_spinbox.bind("<FocusIn>", lambda event: self.lose_spinbox_focus())

        self.hours_label.grid(column = 0, row=0, sticky='nsew', pady=5)
        self.minutes_label.grid(column = 1, row = 0, sticky='nsew', pady=5)

        self.hours_spinbox.grid(column = 0, row = 1, sticky='nsew', pady=15)
        self.minute_spinbox.grid(column = 1, row = 1, sticky='nsew', pady=15)

        self.datetime_confirm_button = tk.Button(
            self.datetime_frame, font=("Arial, 50"), text="Confirm",
            command = lambda: self.set_system_time())
        
        self.datetime_confirm_button.grid(column = 1, row = 3, sticky='nsew')


    def enter_add_item_frame(self):
        self.add_item_label.grid(column=1, row=0, sticky='ew')
        self.add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
        self.add_item_button.grid(column=1, row=2, sticky='ew')
        self.back_button.grid(column=1, row=4, sticky='ew')
        self.quit_button.grid(column=1, row=5, sticky='ew')
        self.add_item_yes_no.grid_forget()
        self.item_info_confirmation.grid_forget()
        self.reenter_frame.grid_forget()
        self.add_item_frame.tkraise()
        self.add_item_entry.focus_set()

    def enter_register_frame(self):
        self.invisible_entry.delete(0, tk.END)
        self.sale_items_listbox.delete(0, tk.END)
        self.update_entry(self.total_entry, "$0.00")
        self.update_entry(self.usr_entry, "$0.00")
        self.register_label.config(text="Mode: Register", fg="#68FF00")
        self.register_frame.tkraise()
        self.invisible_entry.focus_force()

    def setup_seasonal_sale(self):
        self.register_label.config(text="Mode: Seasonal Sale", fg="red")
        self.unbind_invisible_entry_keys()
        self.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.controller.make_seasonal_sale())
        self.invisible_entry.delete(0, tk.END)
        # Finish later->> self.invisible_entry.bind("<KeyRelease-KP_Decimal>", lambda event: self.return_register_widgets())
        self.register_frame.tkraise()
        self.invisible_entry.focus_set()
   
    def setup_browse_seasonals(self):
        self.browse_label.grid_forget()
        self.browse_transactions_frame.tkraise()
        self.error_description_label.config(font=("Arial", 35))	
        self.error_description_label.config(text='You are now browsing seasonals. ' \
        'Enter a\nseasonal ID in the entry box and select "GO"\nto jump to one. ' \
        'Press one of the buttons\nto delete, add, or edit that seasonal.')
        self.browse_entry_frame.grid(column = 1, row = 2, sticky='ew', pady=30)
        self.errors_frame.tkraise()

    def bind_invisible_entry_keys(self):
        for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
            self.invisible_entry.bind(f"<KeyRelease-KP_{key}>", self.controller.number_pressed)
        self.invisible_entry.bind("<KeyRelease-BackSpace>", self.controller.clear)
        self.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.controller.on_cash())
        self.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: self.controller.on_cc())
        self.invisible_entry.bind("<KeyRelease-KP_Multiply>", lambda event: self.main_menu_frame.tkraise())
        self.invisible_entry.bind("<KeyRelease-KP_Divide>", lambda event: self.controller.enter_register_frame())
        self.invisible_entry.bind("<KeyRelease-KP_Subtract>", self.controller.no_sale)

    def unbind_invisible_entry_keys(self):
        for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
            self.invisible_entry.unbind(f"<KeyRelease-KP_{key}>")
        self.invisible_entry.unbind("<KeyRelease-BackSpace>")
        self.invisible_entry.unbind("<KeyRelease-KP_Enter>")
        self.invisible_entry.unbind("<KeyRelease-KP_Add>")
        self.invisible_entry.unbind("<KeyRelease-KP_Multiply>")
        self.invisible_entry.unbind("<KeyRelease-KP_Divide>")
        self.invisible_entry.unbind("<KeyRelease-KP_Subtract>")

    def setup_void_widgets(self):
        self.browse_label.config(text="Browse or enter the Transaction ID")
        self.browse_confirm_button.config(text = "Print")
        #self.browse_second_label.grid(column = 1, row = 2, sticky='ew')
        self.browse_confirm_button.grid(column = 1, row = 3, sticky='sew')
        self.browse_entry.focus_set()

    def remove_void_widgets(self):
        self.browse_label.config(text="Browsing Transactions")
        self.browse_second_label.grid_forget()
        self.browse_entry_frame.grid_forget()
        self.browse_confirm_button.grid_forget()

    def update_entry(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)

    def quit_program(self):
        self.controller.state_manager.conn.commit()
        self.controller.state_manager.conn.close()
        self.root.destroy()

    def lose_spinbox_focus(self):
        self.datetime_label.focus_set()
        return "break"
    
    def set_system_time(self):
        time_string = ""
        
        time_string += f'{self.year_spinbox.get()}-'
        time_string += f'{self.month_spinbox.get()}-' if len(self.month_spinbox.get()) == 2 else f"0{self.month_spinbox.get()}-"
        time_string += f'{self.date_spinbox.get()} ' if len(self.date_spinbox.get()) == 2 else f"0{self.date_spinbox.get()}"
        time_string += f' {self.hours_spinbox.get()}:' if len(self.hours_spinbox.get()) == 2 else f' 0{self.hours_spinbox.get()}:'
        time_string += f'{self.minute_spinbox.get()}:00'if len(self.minute_spinbox.get()) == 2 else f"0{self.minute_spinbox.get()}:00"

        #date_time = datetime.strptime(time_string, "%Y%m%d %H%M")
        
        subprocess.run(['sudo', 'date', '-s', time_string])
        self.quit_program()



    

