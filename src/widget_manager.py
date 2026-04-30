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
        self.add_item_frame = tk.Frame(self.root)
        self.add_barcode_frame = tk.Frame(self.root)
        self.add_name_frame = tk.Frame(self.root)
        self.add_price_frame = tk.Frame(self.root)
        self.add_tax_frame = tk.Frame(self.root)
        self.add_category_frame = tk.Frame(self.root)
        self.add_subcategory_frame = tk.Frame(self.root)
        self.add_vendor_frame = tk.Frame(self.root)
        self.add_quantity_frame = tk.Frame(self.root)
        self.register_frame = tk.Frame(self.root, bg='black')
        self.register_info_frame = tk.Frame(self.register_frame, bg="black")
        self.main_menu_frame = tk.Frame(self.root)
        self.menu_buttons_frame = tk.Frame(self.main_menu_frame)
        self.reenter_frame = tk.Frame(self.root)
        self.add_item_yes_no = tk.Frame(self.add_item_frame)
        self.add_item_back_quit_frame = tk.Frame(self.add_item_frame)
        self.register_add_item_prompt_frame = tk.Frame(self.root)
        self.register_add_item_yes_no_frame = tk.Frame(self.register_add_item_prompt_frame)
        self.browse_transactions_frame = tk.Frame(self.root)
        self.browse_entry_frame = tk.Frame(self.browse_transactions_frame)
        self.errors_frame = tk.Frame(self.root, width = 400, height = 300, borderwidth=20, relief="ridge", bg="black")
        self.seasonal_id_entry_frame = tk.Frame(self.root, width=400, height=300, borderwidth=20, relief='ridge', bg="black")
        self.datetime_frame = tk.Frame(self.root)
        self.edit_seasonal_frame = tk.Frame(self.root)
        self.edit_seasonal_buttons_frame = tk.Frame(self.root)
        self.time_widgets_frame = tk.Frame(self.datetime_frame)
        self.date_widgets_frame = tk.Frame(self.datetime_frame)
        self.seasonal_buttons_frame = tk.Frame(self.browse_transactions_frame)
        self.coupon_frame = tk.Frame(self.root)
        self.coupon_buttons_frame = tk.Frame(self.coupon_frame)
        self.register_lookup_items_frame = tk.Frame(self.root)
        self.register_lookup_items_buttons_frame = tk.Frame(self.register_lookup_items_frame)

        
        self._init_add_barcode_frame()
        self._init_add_name_frame()
        self._init_add_price_frame()
        self._init_add_tax_frame()
        self._init_add_category_frame()
        self._init_add_subcategory_frame()
        self._init_add_vendor_frame()
        self._init_add_quantity_frame()


        # Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
        # Widgets in column 1 will determine the width of the rest of the widgets
        for frame in (self.register_frame, self.add_item_frame, self.main_menu_frame,
            self.register_add_item_prompt_frame,
            self.browse_transactions_frame, self.edit_seasonal_frame, self.datetime_frame,
            self.coupon_frame, self.register_lookup_items_frame, self.add_barcode_frame,
            self.add_name_frame, self.add_price_frame, self.add_tax_frame, self.add_category_frame,
            self.add_quantity_frame, self.add_subcategory_frame, self.add_vendor_frame):
            frame.grid(row=0, column=0, sticky='nsew')
            frame.columnconfigure(0, weight=1)
            frame.columnconfigure(1, weight=0)
            frame.columnconfigure(2, weight=1)   

        """These frames only need 2 columns of widgets, so
        configure them as such."""
        for frame in (
            self.reenter_frame, self.add_item_yes_no, self.admin_menu_frame,
            self.menu_buttons_frame, self.admin_menu_frame, self.register_menu_frame,
            self.edit_seasonal_buttons_frame, self.register_info_frame,
            self.register_add_item_yes_no_frame, self.add_item_back_quit_frame,
            self.coupon_buttons_frame, self.register_lookup_items_buttons_frame):
            frame.columnconfigure(1, weight=1)
            frame.columnconfigure(0, weight=1)


        self.reenter_frame.grid(column = 0, row = 0, sticky='nsew')
        self.reenter_frame.columnconfigure(0, uniform="equal")
        self.reenter_frame.columnconfigure(1, uniform="equal")

        self.register_menu_frame.grid(column = 0, row = 0, sticky='nsew')
        self.admin_menu_frame.grid(column = 0, row = 0, sticky='nsew')
        self.admin_menu_frame.columnconfigure(0, uniform="equal")
        self.admin_menu_frame.columnconfigure(1, uniform="equal")

        self.errors_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.errors_frame.columnconfigure(0, weight=1)
        self.errors_frame.columnconfigure(1, weight=0)
        self.errors_frame.columnconfigure(2, weight=1)

        self.seasonal_id_entry_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.seasonal_id_entry_frame.columnconfigure(0, weight=1)
        self.seasonal_id_entry_frame.columnconfigure(1, weight=0)
        self.seasonal_id_entry_frame.columnconfigure(2, weight=1)

        self.time_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.time_widgets_frame.columnconfigure(1, weight=1, uniform="equal")

        self.add_item_yes_no.columnconfigure(0, uniform="equal")
        self.add_item_yes_no.columnconfigure(1, uniform="equal")

        self.add_item_back_quit_frame.columnconfigure(0, uniform="equal")
        self.add_item_back_quit_frame.columnconfigure(1, uniform="equal")

        self.date_widgets_frame.columnconfigure(0, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(1, weight=1, uniform="equal")
        self.date_widgets_frame.columnconfigure(2, weight=1, uniform="equal")

        self.seasonal_buttons_frame.columnconfigure(0, weight = 1, uniform="equal")
        self.seasonal_buttons_frame.columnconfigure(1, weight = 1, uniform="equal")
        self.seasonal_buttons_frame.columnconfigure(2, weight = 1, uniform="equal")

        

        # ===============================
        # Widgets for Register Mode frame
        # ===============================

        self.register_label = tk.Label(
            self.register_info_frame, font=("Arial", 30), text="Mode: Register", fg="#68FF00", bg="black"
        )
        self.register_label.grid(column=0, row=0, sticky='sw', pady=5)


        self.balance_entry = tk.Entry(
            self.register_info_frame, font=("Arial", 91),
            bg="black", fg="#68FF00", justify="right", width=9)
        self.balance_entry.insert(tk.END, "$0.00")
        self.balance_entry.grid(column=1, row=0, sticky='e', padx=2)
        self.balance_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        # Invisible entry where user input actually occurs. Allows user entry to be untampered so 
        # same entry box can be used for barcodes and numberic values alike

        self.invisible_entry = tk.Entry(self.register_frame)
        self.invisible_entry.place(x=-100, y=-100)
        self.invisible_entry.bind("<Return>", controller.process_sale)
        self.bind_invisible_entry_keys()


        self.user_entry = tk.Entry(
            self.register_info_frame, font=("Arial", 35), width=10, bg="black",
            fg="#68FF00")
        self.user_entry.insert(tk.END, "$0.00")
        self.user_entry.grid(column = 0, row = 0, sticky='nw')
        self.user_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        self.register_info_frame.grid(column = 1, row = 0, sticky='nsew')
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

        self.register_add_item_yes_no_frame.grid(row=1, column=1, sticky='nsew')

        self.register_add_item_yes_button=tk.Button(
            self.register_add_item_yes_no_frame, text="Yes", font=("Arial", 90),
            command = lambda: self.controller.state_manager.yes_no_var.set("yes"))
        self.register_add_item_yes_button.grid(row=0, column=0, sticky='nsew')

        self.register_add_item_no_button=tk.Button(
            self.register_add_item_yes_no_frame, text="No",
            font=("Arial", 90), command = lambda: self.controller.state_manager.yes_no_var.set("no"))
        self.register_add_item_no_button.grid(row=0, column=1, sticky='nsew')

        # =====================
        # Widgets for coupons
        # =====================

        self.coupon_label = tk.Label(
            self.coupon_frame, text="Please enter the amount to\nbe couponed.",
            font=("Arial", 50)
        )
        self.coupon_label.grid(column = 1, row = 0, sticky='ew', pady=10)

        self.coupon_entry = tk.Entry(
            self.coupon_frame, font=("Arial", 50)
        )
        self.coupon_entry.grid(column = 1, row = 1, sticky='ew', pady=10)

        self.coupon_reason_label = tk.Label(
            self.coupon_frame, text="If desired, enter a coupon reason.",
            font=("Arial", 50)
        )
        self.coupon_reason_label.grid(column = 1, row = 2, sticky='ew', pady=10)

        self.coupon_reason_entry = tk.Entry(
            self.coupon_frame, font=("Arial", 50)
        )
        self.coupon_reason_entry.grid(column = 1, row = 3, sticky='ew', pady=10)
        
        self.coupon_back_button = tk.Button(
            self.coupon_buttons_frame, text="Back",
            font=("Arial", 50), command = lambda: self.register_frame.tkraise()
        )
        self.coupon_confirm_button = tk.Button(
            self.coupon_buttons_frame, text="Confirm", font=("Arial", 50),
            command = lambda: self.controller.apply_coupon()
        )

        self.coupon_back_button.grid(column = 0, row = 0, sticky='ew')
        self.coupon_confirm_button.grid(column = 1, row = 0, sticky='ew')

        self.coupon_buttons_frame.grid(column = 1, row = 4, sticky='ew')
        # ==========================
        # Widgets for Add Item frame
        # ==========================

        self.add_item_label = tk.Label(
            self.add_item_frame, text="Please confirm item's info:",
              font=("Arial", 50), width=27)

        self.add_item_label.grid(column = 1, row = 0, sticky='ew')

        self.add_item_quit_button = tk.Button(
            self.add_item_back_quit_frame, text="Quit", font=("Arial", 50),
              command = lambda: self.main_menu_frame.tkraise())

        self.add_item_quit_button.grid(column = 0, row = 0, sticky='ew')

        self.item_info_confirmation = tk.Text(
            self.add_item_frame, font=("Arial", 40),
            width=6, height=4)
        self.item_info_confirmation.tag_configure("justify_right", justify = "right")

        self.item_info_confirmation.grid(column = 1, row = 1, sticky='ew')

        self.item_info_scrollbar = tk.Scrollbar(
            self.add_item_frame, bg="white",
            orient = tk.VERTICAL, width=40
        )

        self.item_info_scrollbar.grid(column = 1, row = 1, sticky='nse')
        self.item_info_confirmation.config(yscrollcommand= self.item_info_scrollbar.set)
        self.item_info_scrollbar.config(command = self.item_info_confirmation.yview)

        self.add_item_yes_no.grid(column = 1, row = 2, sticky='ew')

        self.add_item_back_quit_frame.grid(column = 1, row = 4, sticky='ew')

        self.yes_button = tk.Button(
            self.add_item_yes_no, text="Yes", font=("Arial", 100),
            command= lambda: controller.on_yes_no("yes"))

        self.no_button = tk.Button(
            self.add_item_yes_no, text="No", font=("Arial", 100),
            command=lambda: controller.on_yes_no("no"))

        self.yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
        self.no_button.grid(column=1, row=0, sticky='nsew', padx=10)

        # Buttons for options when user wants to correct one of their inputs

        self.add_name_button = tk.Button(
            self.reenter_frame, text="Name", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("name"))
        self.add_name_button.grid(row=0, column=0, sticky='nsew')

        self.add_price_button = tk.Button(
            self.reenter_frame, text="Price", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("price"))
        self.add_price_button.grid(row=0, column=1, sticky='nsew')

        self.add_barcode_button = tk.Button(
            self.reenter_frame, text="Barcode", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("barcode"))
        self.add_barcode_button.grid(row=1, column=0, sticky='nsew')

        self.add_taxable_button = tk.Button(
            self.reenter_frame, text="Taxable", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("taxable"))
        self.add_taxable_button.grid(row=1, column=1, sticky='nsew')

        self.add_quantity_button = tk.Button(
            self.reenter_frame, text="Quantity", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("quantity"))
        self.add_quantity_button.grid(row=2, column=0, sticky='nsew')

        self.add_category_button = tk.Button(
            self.reenter_frame, text="Category", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("category"))
        self.add_category_button.grid(row=2, column=1, sticky='nsew')

        self.add_subcategory_button = tk.Button(
            self.reenter_frame, text="Subcategory", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("subcategory"))
        self.add_subcategory_button.grid(row = 3, column = 0, sticky='nsew')

        self.add_vendor_button = tk.Button(
            self.reenter_frame, text="Vendor", font=("Arial", 50),
            command = lambda: controller.reenter_button_pressed("vendor"))
        self.add_vendor_button.grid(row = 3, column = 1, sticky='nsew')

        tk.Button(
            self.reenter_frame, text="Back", font=("Arial", 50),
            command = lambda: self.add_item_frame.tkraise()
            ).grid(row = 4, column = 0, sticky='nsew', pady=20)
        
        tk.Button(
            self.reenter_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()
            ).grid(row = 4, column = 1, sticky='nsew', pady=20)

        # ==========================
        # Widgets for Menu Functions
        # ==========================

        # ==========================
        

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
            command = lambda: self.return_to_register()
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

        self.coupon_button = tk.Button(
            self.register_menu_frame, text="Apply coupon", 
            font=("Arial", 58), command = lambda: self.coupon_frame.tkraise())

        self.lookup_item_button = tk.Button(
            self.register_menu_frame, text="Lookup Item",
            font=("Arial", 58), command = lambda: self.enter_register_lookup_items_frame())
        
        self.void_button.grid(column = 0, row = 0, sticky='nsew', pady=2)
        self.print_receipt_button.grid(column = 1, row = 0, sticky='nsew', pady=2)
        self.make_return_button.grid(column = 0, row = 1, sticky='nsew', pady=2)
        self.back_to_register_button.grid(column = 1, row = 1, sticky='nsew', pady=2)
        self.seasonal_button.grid(column = 0, row = 2, sticky='nsew', pady=2)
        self.coupon_button.grid(column = 1, row = 2, sticky='nsew', pady=2)
        self.lookup_item_button.grid(column = 0, row = 3, sticky='nsew', pady=2)

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

        self.admin_menu_back_button = tk.Button(
            self.admin_menu_frame, text="Back", font=("Arial", 58),
            command = lambda: self.main_menu_frame.tkraise()
        )

        self.run_z_button = tk.Button(
            self.admin_menu_frame, text="Run Z", font=("Arial", 58),
            command = lambda: self.controller.run_z()
        )
        
        self.run_x_button.grid(column = 0, row = 0, sticky='nsew', pady=2)
        self.new_item_button.grid(column = 1, row = 0, sticky='nsew', pady=2)
        self.fullscreen_button.grid(column = 0, row = 1, sticky='nsew', pady=2)
        self.browse_transactions_button.grid(column = 1, row = 1, sticky='nsew', pady=2)
        self.quit_program_button.grid(column = 0, row = 2, sticky='nsew', pady=2)
        self.manage_seasonals_button.grid(column = 1, row = 2, sticky='nsew', pady=2)
        self.admin_menu_back_button.grid(column = 0, row = 3, sticky='nsew', pady=2)
        self.run_z_button.grid(column = 1, row = 3, sticky='nsew', pady=2)
        
        # ==============================
        # Widgets For Lookup Items Frame
        # ==============================

        self.lookup_items_label = tk.Label(
            self.register_lookup_items_frame, text="Item Lookup", font=("Arial", 50))

        self.lookup_items_text = tk.Text(
            self.register_lookup_items_frame, font=("Courier New", 40), height=4,
            width = 27)

        self.lookup_items_listbox = tk.Listbox(
            self.register_lookup_items_frame, font=("Courier New", 40),
            height = 4, bg="black", fg="white", width=23
        )
        self.lookup_items_scrollbar = tk.Scrollbar(
            self.register_lookup_items_frame, bg="white",
            orient = tk.VERTICAL, width=40
        )
        self.lookup_items_entry = tk.Entry(
            self.register_lookup_items_frame, font=("Arial", 50), textvariable=self.controller.state_manager.item_lookup_var
        )

        self.lookup_items_go_button = tk.Button(
            self.register_lookup_items_frame, font=("Arial", 50), text="GO",
            width = 5
        )

        self.lookup_items_quantity_spinbox = tk.Spinbox(
            self.register_lookup_items_frame, font=("Arial", 50),
            from_=1, to=99, width = 3
        )

        self.lookup_items_back_button = tk.Button(
            self.register_lookup_items_buttons_frame, text="Back", font=("Arial", 50),
            command = lambda: self.return_to_register())

        self.lookup_items_confirm_button = tk.Button(
            self.register_lookup_items_buttons_frame, text="Confirm", font=("Arial", 50),
            command = lambda: self.controller.confirm_lookup_items()
        )

        self.lookup_items_label.grid(column = 1, row = 0, sticky='ew')
        self.lookup_items_listbox.grid(column = 1 , row = 1, sticky='nsw')
        self.lookup_items_scrollbar.grid(column = 1, row = 1, stick='nse')
        self.lookup_items_entry.grid(column = 1, row = 2, sticky='w')
        #self.lookup_items_go_button.grid(column = 1, row = 2, sticky='e')
        self.lookup_items_quantity_spinbox.grid(column = 1, row = 3, sticky='ew')
        self.lookup_items_back_button.grid(column = 0, row = 0, sticky='ew')
        self.lookup_items_confirm_button.grid(column = 1, row = 0, sticky='ew')
        self.register_lookup_items_buttons_frame.grid(column = 1, row = 4, sticky='ew')

        self.lookup_items_listbox.config(yscrollcommand= self.lookup_items_scrollbar.set)
        self.lookup_items_scrollbar.config(command = self.lookup_items_listbox.yview)

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
            self.browse_transactions_frame, width=28, height=3,
            font=("Courier New", 37)
        )
        self.browse_text.tag_configure("bold", font=("Courier New", 40, "bold"))
        self.browse_text.grid(column = 1, row = 1, sticky='ew', pady=10)
        self.browse_text.bind("<FocusIn>", self.controller.return_browse_entry_focus)

        self.browse_second_label = tk.Label(
            self.browse_transactions_frame, text="Press continue when satisfied", font=("Arial", 50)
        )
       
        self.browse_entry = tk.Entry(
            self.browse_entry_frame, font=("Arial", 35),
            width = 10, validate='key', vcmd=self.controller.vcmd)
        self.browse_entry.bind("<Return>", lambda event: self.controller.state_manager.browse_index.set(int(self.browse_entry.get())))
        self.browse_entry.grid(column = 0, row = 0, sticky='nsew')
        self.browse_entry_frame.grid(column = 1, row = 2, sticky='ew', pady=30)


        self.browse_go_button = tk.Button(self.browse_entry_frame, font=("Arial", 40),
            text = "-> GO", command = lambda: self.controller.state_manager.browse_index.set(int(self.browse_entry.get())))
        self.browse_go_button.grid(column = 1 , row = 0, sticky='nsew')

        browse_back_quit_frame = tk.Frame(self.browse_transactions_frame)
        browse_back_quit_frame.columnconfigure(0, weight=1, uniform="equal")
        browse_back_quit_frame.columnconfigure(1, weight=1, uniform="equal")
        browse_back_quit_frame.grid(column=1, row = 3, sticky='nsew')

        self.browse_back_button = tk.Button(
            browse_back_quit_frame, text="Back",
            font=("Arial", 50), command = lambda: controller.menu_back()
        )
        self.browse_back_button.grid(column=0, row=0, sticky='nsew')

        self.browse_confirm_button = tk.Button(browse_back_quit_frame, text="Confirm",
            font=("Arial", 50), command = lambda: self.controller.state_manager.void_var.set("")
        )


        # ================================================
        # Widgets for the seasonal version of browse frame
        # ================================================


        self.add_seasonal_button = tk.Button(
            self.seasonal_buttons_frame, font=("Arial", 35), text="Add"
        )

        self.remove_seasonal_button = tk.Button(
            self.seasonal_buttons_frame, font=("Arial", 35), text="Remove"
        )

        self.edit_seasonal_button = tk.Button(
            self.seasonal_buttons_frame, font=("Arial", 35), text="Edit",
            command = lambda: self.edit_seasonal_frame.tkraise()
        )

        self.seasonal_buttons_frame.grid(column = 1, row = 4, sticky='ew')

        self.add_seasonal_button.grid(column = 0, row = 0, sticky='nsew')
        self.remove_seasonal_button.grid(column = 1, row = 0, sticky='nsew')
        self.edit_seasonal_button.grid(column = 2, row = 0, sticky='nsew')

        

        # =================================
        # Widgets for Editing Seasonal Info
        # =================================

        


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

        # ============================
        # Widgets for the Errors Frame
        # ============================

        self.error_label = tk.Label(self.errors_frame, text="ERROR:", font=("Arial", 50), fg="red", justify="center")
        self.error_label.grid(column=1, row=0, sticky='ew')

        self.error_description_label = tk.Label(self.errors_frame, text="", font=("Arial", 50))
        self.error_description_label.grid(column = 1, row = 1, sticky='ew')

        self.error_ok_button = tk.Button(self.errors_frame, text="Ok", font=("Arial", 50),
            command = lambda: self.errors_frame.lower())
        self.error_ok_button.grid(column = 1, row = 2, sticky='ew')

        self.error_back_confirm_frame = tk.Frame(self.errors_frame)
        self.error_back_confirm_frame.columnconfigure(0, weight=1, uniform="equal")
        self.error_back_confirm_frame.columnconfigure(1, weight=1, uniform="equal")
        self.error_back_confirm_frame.grid(column = 1, row = 2, sticky='ew')
        self.error_back_button = tk.Button(
            self.error_back_confirm_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.state_manager.error_var.set("Back")
        )
        self.error_back_button.grid(column = 0, row = 0, sticky='nsew')

        self.error_confirm_button = tk.Button(
            self.error_back_confirm_frame, text="Confirm", font=("Arial", 50),
            command = lambda: self.controller.state_manager.error_var.set("Confirm")
        )
        
        self.error_confirm_button.grid(column = 1 , row = 0, sticky='nsew')
        
        # =============================
        # Widgets for Manual Time Entry
        # =============================

        self.datetime_frame.grid(column=0, row=0, sticky='nsew')

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

    def return_to_register(self):
        self.register_frame.tkraise()
        self.invisible_entry.focus_set()

    def enter_register_lookup_items_frame(self):
        self.register_lookup_items_frame.tkraise()
        self.lookup_items_quantity_spinbox.delete(0, "end")
        self.lookup_items_quantity_spinbox.insert(0, 1)
        self.lookup_items_listbox.delete(0, tk.END)
        self.lookup_items_entry.delete(0, tk.END)
        self.lookup_items_entry.focus_set()

    def _init_add_barcode_frame(self):
        tk.Label(self.add_barcode_frame, text="Please enter item's barcode:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_barcode_entry = tk.Entry(
            self.add_barcode_frame, font=("Arial", 50), justify="right")
        self.add_barcode_entry.grid(column = 1, row = 1, sticky='ew', pady=15)
        self.add_barcode_entry.bind("<Return>", lambda event: self.controller.on_add_item_enter())
        tk.Button(
            self.add_barcode_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_item_enter()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_barcode_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def _init_add_name_frame(self):
        tk.Label(self.add_name_frame, text="Please enter item's name:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_name_entry = tk.Entry(
            self.add_name_frame, font=("Arial", 50), justify="right")
        self.add_name_entry.grid(column = 1, row = 1, sticky='ew', pady=15)
        self.add_name_entry.bind("<Return>", lambda event: self.controller.on_add_item_enter())
        tk.Button(
            self.add_name_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_item_enter()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_name_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def return_price_invisible_entry_focus(self):
        self.add_price_invisible_entry.focus_set()
        return "break"
    
    def _init_add_price_frame(self):
        tk.Label(self.add_price_frame, text="Please enter item's price:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_price_entry = tk.Entry(
            self.add_price_frame, font=("Arial", 50), justify="right")
        self.add_price_entry.grid(column = 1, row = 1, sticky='ew', pady=15)

        self.add_price_invisible_entry = tk.Entry(
            self.add_price_frame, validate='key', vcmd=self.controller.vcmd,
            textvariable=self.controller.state_manager.add_price_var)
        self.add_price_invisible_entry.place(x=-100, y=-100)
        self.add_price_invisible_entry.bind("<Return>", lambda event: self.controller.on_add_item_enter())
        for key in ("Left", "Right", "Up", "Down"):
            self.add_price_invisible_entry.bind(f"<{key}>", wf.disable_arrow_keys)
        self.add_price_entry.bind("<FocusIn>", lambda e: self.return_price_invisible_entry_focus())
        tk.Button(
            self.add_price_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_item_enter()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_price_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def _init_add_tax_frame(self):
        tk.Label(self.add_tax_frame, text="Is the item taxable?:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')

        yes_no_frame = tk.Frame(self.add_tax_frame)
        yes_no_frame.columnconfigure(0, weight=1)
        yes_no_frame.columnconfigure(1, weight=1)
        yes_no_frame.grid(column = 1, row = 1, sticky='ew')
        
        tk.Button(
            yes_no_frame, text="Yes", font=("Arial", 100),
            command= lambda: self.controller.on_yes_no("yes")).grid(
                column = 0, row = 0, sticky='ew'
            )
        tk.Button(
            yes_no_frame, text="No", font=("Ariak", 100),
            command= lambda: self.controller.on_yes_no("no")).grid(
                column = 1, row = 0, sticky='ew'
            )

        self.add_tax_entry = tk.Entry(self.add_tax_frame)

        back_quit_frame = tk.Frame(self.add_tax_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def _init_add_category_frame(self):
        tk.Label(self.add_category_frame, text="Please enter item's category:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_category_entry = tk.Entry(self.add_category_frame)

        self.add_category_listbox = tk.Listbox(
            self.add_category_frame, width=25,
            height=4, font=("Arial", 50))
        add_category_scrollbar = tk.Scrollbar(
            self.add_category_frame,
            orient=tk.VERTICAL, width=40
        )

        self.add_category_listbox.grid(column = 1, row = 1, sticky='nw')
        add_category_scrollbar.grid(column = 1, row = 1, sticky='nse')

        self.add_category_listbox.config(yscrollcommand= add_category_scrollbar.set)
        add_category_scrollbar.config(command = self.add_category_listbox.yview)

        for values in (
        "Camping", "Gifts", "Fishing", "General Merch",
        "RV", "Summer Fun", "Toys & Hobby", "Candy & Snacks", "Misc.",
        "Foodstuffs", "TBC Merch", "Souvenirs"):
            self.add_category_listbox.insert(tk.END, values)

        tk.Button(
            self.add_category_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_category_listbox_next()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_category_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def _init_add_subcategory_frame(self):
        tk.Label(self.add_subcategory_frame, text="Please enter item's subcategory:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_subcategory_entry = tk.Entry(self.add_subcategory_frame)

        self.add_subcategory_listbox = tk.Listbox(
            self.add_subcategory_frame, width=25,
            height=4, font=("Arial", 50))
        add_subcategory_scrollbar = tk.Scrollbar(
            self.add_subcategory_frame,
            orient=tk.VERTICAL, width=40
        )

        self.add_subcategory_listbox.grid(column = 1, row = 1, sticky='nw')
        add_subcategory_scrollbar.grid(column = 1, row = 1, sticky='nse')

        self.add_subcategory_listbox.config(yscrollcommand= add_subcategory_scrollbar.set)
        add_subcategory_scrollbar.config(command = self.add_subcategory_listbox.yview)

        tk.Button(
            self.add_subcategory_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_subcategory_listbox_next()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_subcategory_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )


    def _init_add_vendor_frame(self):
        tk.Label(self.add_vendor_frame, text="Please enter item's vendor:", 
        font=("Arial", 50), width=25).grid(column = 1, row = 0, sticky='ew')
        self.add_vendor_entry = tk.Entry(self.add_vendor_frame)

        self.add_vendor_listbox = tk.Listbox(
            self.add_vendor_frame, width=25,
            height=3, font=("Arial", 50))
        add_vendor_scrollbar = tk.Scrollbar(
            self.add_vendor_frame,
            orient=tk.VERTICAL, width=40
        )

        self.add_vendor_listbox.grid(column = 1, row = 1, sticky='nw')
        add_vendor_scrollbar.grid(column = 1, row = 1, sticky='nse')

        self.add_vendor_listbox.config(yscrollcommand= add_vendor_scrollbar.set)
        add_vendor_scrollbar.config(command = self.add_vendor_listbox.yview)

        for values in (
        "Wilcor", "Restaurant Depot", "Shoprite", "Sam's Club", "ABC 123", "Zoologee", "Aldi", "Kohl's", "Cheap Carls", "Gib Carson", "D&D Distributing",
        "Puka Creations", "Dollar Tree", "ACME", "Walmart"):
            self.add_vendor_listbox.insert(tk.END, values)

        tk.Button(
            self.add_vendor_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_vendor_listbox_next()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_vendor_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )
        
        tk.Button(
            self.add_vendor_frame, text="Skip", font=("Arial", 50),
            command = lambda: self.controller.skip_vendor_step()).grid(
                column = 1, row = 4, sticky='ew')

        

    def _init_add_quantity_frame(self):
        self.add_quantity_label = tk.Label(self.add_quantity_frame, text="Please enter item's quantity:", 
        font=("Arial", 50), width=25)
        self.add_quantity_label.grid(column = 1, row = 0, sticky='ew')

        self.add_quantity_entry = tk.Entry(
            self.add_quantity_frame, font=("Arial", 50), justify="right",
            validate='key', vcmd=self.controller.vcmd)
        self.add_quantity_entry.grid(column = 1, row = 1, sticky='ew', pady=15)
        self.add_quantity_entry.bind("<Return>", lambda e: self.controller.on_add_item_enter())

        for key in ("Left", "Right", "Up", "Down"):
            self.add_quantity_entry.bind(f"<{key}>", wf.disable_arrow_keys)

        tk.Button(
            self.add_quantity_frame, text="Next", font=("Arial", 50),
            command = lambda: self.controller.on_add_item_enter()).grid(
                column = 1, row = 2, sticky='ew')
        back_quit_frame = tk.Frame(self.add_quantity_frame)
        back_quit_frame.columnconfigure(0, weight=1)
        back_quit_frame.columnconfigure(1, weight=1)
        back_quit_frame.grid(column = 1, row = 3, sticky='ew', pady=(15, 0))
        tk.Button(
            back_quit_frame, text="Back", font=("Arial", 50),
            command = lambda: self.controller.go_back()).grid(
                column = 0, row = 0, sticky='ew', padx=(0, 15)
            )
        tk.Button(
            back_quit_frame, text="Quit", font=("Arial", 50),
            command = lambda: self.main_menu_frame.tkraise()).grid(
                column = 1, row = 0, sticky='ew'
            )

    def populate_subcategory_listbox(self, primary_category):
        self.add_subcategory_listbox.delete(0, tk.END)

        match primary_category:
            case "Camping":
                for values in (
                    "BBQ Supplies", "Blankets, Bajas & Pillows", "Camp Books",
                    "Camp Cookware", "Campfire Cooking", "Campfire Items and Starters",
                    "Camping Accessories", "Camping Bedding", "Camp Tools & Tent Stakes",
                    "Coolers and Thermals", "Flashlights (including head lamps)",
                    "Fuels and Matches", "Hiking Gear", "Insect Control",
                    "Knives", "Furniture & Hammocks", "Packs",
                    "Picnic Products", "Propane Cooking and Lighting",
                    "Raingear", "Ropes, Cords, Tiedowns", "Tarps, Tents, Shelters",
                    "Pet Supplies", "Lanterns", "Decorative & Impulse Lights",
                    "Waterproof Pouches and Bags", "Shopping Bags & Totes",
                    "Ceramics Mugs", "Outdoor Adventure Books", "Nature Guides & Maps",
                    "Cooking & Campfire Books", "Notebooks & Journals"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Gifts":
                for values in(
                    "Antler Look Theme", "Baskets", "Bear Theme",
                    "Birdhouses", "Camping and RV Gifts", "Canoe and Paddle Gifts",
                    "Cute/Fantasy Theme", "Dream Catchers", "Fur Figures",
                    "Lamps", "Magnets", "Moose Theme", "Ornaments",
                    "Other Gifts", "Cabin & Lodge Gifts", "Pens",
                    "Picture Frames", "Seaside Themes", "Signs and Plaques",
                    "Stuffed Animals", "Wildlife Theme", "Wind Chimes and Spinners",
                    "Wood Gifts", "Smore Gifts", "Big Foot"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Fishing":
                for values in(
                    "Fishing Accessories", "Lures", "Nets",
                    "Rod and Reel Combos", "Tackle"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "General Merch":
                for values in(
                    "Brooms Cleaning Supplies", "Hardware Related Products", "Health and Beauty Aids",
                    "Household Electric", "Kitchen Utensils", "Kitchenware",
                    "Laundry Products", "Other Household Items", "Drinkware"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "RV":
                for values in(
                    "Automovite", "Drinking Water Hoses & Acc", "Ground Coverings & Awning Mats",
                    "Leveling Towing", "Patio Lights & Accessories", "RV Accessories",
                    "RV Cleaning Products", "RV Electrical", "RV Parts & Maintenance",
                    "Sewer Products", "Toilet Chemicals and Tissue"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Summer Fun":
                for values in(
                    "Beach Towels", "Flags, Pennants, Yard Spinners", "Footwear",
                    "Inflateable Floats, Tubes, Rafts", "Outdoor Fun & Sport Items",
                    "Ski Tubes, Towables, Life Preserv", "Sunglasses",
                    "Suntan Lotion", "Swim Goggles and Fins"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Toys & Hobby":
                for values in(
                    "Action Figures", "Activity Books", "Arts and Crafts",
                    "Bubbles, Traditional Toys", "Cap Guns, Caps", "Camper Toys",
                    "Games", "Toys", "Gross & Squishy", "Guns, Action Toys", "Sand Toys",
                    "School Supplies", "Vehicles, Die Cast", "Water Guns, Water Bombs", "Fur Figures",
                    "Reptiles & Bugs"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Candy & Snacks":
                for values in(
                    "Jewelry & Novelties", "Candy and Jerky", "Hats & Bandanas",
                    "Jokes and Tricks", "Keychains", "Light Up Fun"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Misc.":
                for values in(
                    "Batteries", "Phone Accessories & Bluetooth",
                    "Merchandising", "Other Items/Notions", "Playing Cards",
                    "Winter Items", "Winter Wear", "Work Gloves", "PPE"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Foodstuffs":
                for values in(
                    "Refrigerated", "Dry Goods", "Chips", "Ice Cream",
                    "Cookies"):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "TBC Merch":
                for values in("N/A"):
                    self.add_subcategory_listbox.insert(tk.END, values)
            case "Souvenirs":
                for values in(
                    "NULL"
                ):
                    self.add_subcategory_listbox.insert(tk.END, values)

        
    def enter_add_item_frame(self):
        self.add_barcode_frame.tkraise()
        self.add_quantity_label.config(text="Please enter item's quantity:")
        self.add_barcode_entry.focus_set()

    def enter_register_frame(self):
        self.invisible_entry.delete(0, tk.END)
        self.sale_items_listbox.delete(0, tk.END)
        self.update_entry(self.user_entry, "$0.00")
        self.update_entry(self.balance_entry, "$0.00")
        self.register_label.config(text="Mode: Register", fg="#68FF00")
        self.register_frame.tkraise()
        self.bind_invisible_entry_keys()
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
        self.errors_frame.tkraise()
        self.browse_entry.focus_set()

    def enter_main_menu(self):
        self.main_menu_frame.tkraise()
        self.invisible_entry.delete(0, tk.END)

    def bind_invisible_entry_keys(self):
        for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
            self.invisible_entry.bind(f"<KeyRelease-KP_{key}>", lambda e: self.controller.number_pressed())
        self.invisible_entry.bind("<KeyRelease-BackSpace>", self.controller.clear)
        self.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: self.controller.on_cash())
        self.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: self.controller.on_cc())
        self.invisible_entry.bind("<KeyRelease-KP_Multiply>", lambda event: self.enter_main_menu())
        self.invisible_entry.bind("<KeyRelease-KP_Divide>", lambda event: self.controller.cancel_sale())
        self.invisible_entry.bind("<KeyRelease-KP_Subtract>", self.controller.no_sale)
        self.invisible_entry.unbind("<KeyRelease-Escape>")

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
        self.browse_label.config(text="Browse or enter the Transaction ID\nPress 'Print' to confirm Void")
        self.browse_confirm_button.config(text = "Print")
        #self.browse_second_label.grid(column = 1, row = 2, sticky='ew')
        self.browse_confirm_button.grid(column = 1, row = 0, sticky='sew')
        self.browse_entry.focus_set()

    def remove_void_widgets(self):
        self.browse_label.config(text="Browsing Transactions")
        self.browse_second_label.grid_forget()
        self.browse_entry_frame.grid_forget()
        self.browse_confirm_button.grid_forget()

    def update_entry(self, entry, text):
        entry.delete(0, tk.END)
        entry.insert(0, text)
    
    def setup_coupon(self):
        self.update_entry(self.coupon_entry, "$0.00")
        self.coupon_reason_entry.delete(0, tk.END)
        self.update_entry(self.balance_entry, f'${self.controller.state_manager.trans.total:.2f}')
        self.register_frame.tkraise()
        self.invisible_entry.focus_set()
        

    def quit_program(self):
        self.controller.state_manager.conn.commit()
        self.controller.state_manager.conn.close()
        del self.controller.state_manager
        del self.controller
        self.root.quit()
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

