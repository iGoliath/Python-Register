import tkinter as tk
import widget_functions as wf

class WidgetManager:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        """Initialize all frames necessary for the program"""

        self.admin_frame = tk.Frame(self.root)
        self.add_item_listbox_frame = tk.Frame(self.root)
        self.add_item_frame = tk.Frame(self.root)
        self.update_inventory_frame = tk.Frame(self.root)
        self.register_frame = tk.Frame(self.root, bg='black')
        self.additional_register_functions_frame = tk.Frame(self.root)
        self.update_buttons_frame = tk.Frame(self.update_inventory_frame)
        self.reenter_frame = tk.Frame(self.add_item_frame)
        self.add_item_yes_no = tk.Frame(self.add_item_frame)
        self.additional_register_functions_yes_no = tk.Frame(self.additional_register_functions_frame)
        self.update_inventory_yes_no = tk.Frame(self.update_inventory_frame)
        self.register_widgets_frame = tk.Frame(self.register_frame)
        self.register_add_item_prompt_frame = tk.Frame(self.root)
        self.mode_select_frame = tk.Frame(self.root)

        # Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
        # Widgets in column 1 will determine the width of the rest of the widgets
        for frame in (self.mode_select_frame, self.register_frame, self.admin_frame, 
			        self.add_item_frame, self.update_inventory_frame, 
			        self.additional_register_functions_frame, 
			        self.add_item_listbox_frame, self.register_add_item_prompt_frame):
            frame.grid(row=0, column=0, sticky='nsew')
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=0)
            frame.grid_columnconfigure(2, weight=1)   

        """These frames only need 2 columns of widgets, so
        configure them as such."""
        for frame in (
            self.update_buttons_frame, self.reenter_frame,
            self.add_item_yes_no, self.additional_register_functions_yes_no,
            self.register_widgets_frame):
            frame.grid_columnconfigure(1, weight=1)
            frame.grid_columnconfigure(0, weight=1)

        # =============================
        # Widgets for Mode select frame
        # =============================

        self.mode_select_label = tk.Label(
            self.mode_select_frame, text="Please select a mode: ", font=("Arial", 50))
        self.mode_select_label.grid(column=1, row=0, sticky='ew', pady=10)
        self.register_mode_button = tk.Button(
            self.mode_select_frame, text="Enter Register Mode",
            font=("Arial", 50), command=lambda: controller.enter_register_frame()).grid(
            column=1, row=1, sticky='ew', pady=10)
        self.admin_mode_button = tk.Button(
            self.mode_select_frame, text="Enter Admin Mode",
            font=("Arial", 50), command=lambda: self.admin_frame.tkraise()).grid(
            column=1, row=2, sticky='ew', pady=10)

        # ===============================
        # Widgets for Register Mode frame
        # ===============================


        #Entry box where numbers user is typing are being displayed 
        self.usr_entry = tk.Entry(
            self.register_frame, font=("Arial", 95),
            bg="black", fg="#68FF00", justify="right", width=15)
        self.usr_entry.insert(tk.END, "$0.00")
        self.usr_entry.grid(column=1, row=0, sticky='ew', padx=2)
        self.usr_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        # Invisible entry where user input actually occurs. Allows user entry to be untampered so 
        # same entry box can be used for barcodes and numberic values alike
        self.invisible_entry = tk.Entry(self.register_frame)
        self.invisible_entry.place(x=-10, y=0)
        self.invisible_entry.bind("<Return>", controller.process_sale)
        for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
            self.invisible_entry.bind(f"<KeyRelease-KP_{key}>", controller.number_pressed)
        self.invisible_entry.bind("<KeyRelease-BackSpace>", controller.clear)
        self.invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: controller.on_cash())
        self.invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: controller.on_cc())
        self.invisible_entry.bind("<KeyRelease-KP_Multiply>", controller.enter_void_frame)
        self.invisible_entry.bind("<KeyRelease-KP_Divide>", lambda event: controller.enter_register_frame())
        self.invisible_entry.bind("<KeyRelease-KP_Subtract>", controller.no_sale)

        self.register_widgets_frame.grid(column=1, row=1, sticky='nsew')



        self.new_frame = tk.Frame(self.register_widgets_frame)
        self.new_frame.grid_columnconfigure(0, weight=1)
        self.new_frame.grid(column=0, row=0, sticky='nsew')
        # Box where program outputs current running total
        self.total_entry = tk.Entry(self.new_frame, font=("Arial", 35), width=9)
        self.total_entry.insert(tk.END, "$0.00")
        self.total_entry.grid(column = 0, row = 0, sticky='nw')
        self.total_entry.bind("<FocusIn>", controller.return_invisible_entry_focus)

        self.register_back_button = tk.Button(
            self.new_frame, text="Back", font=("Arial", 35),
            height=5, command = lambda: self.mode_select_frame.tkraise())
        self.register_back_button.grid(column = 0, row = 1, sticky='nw')

        #Log of what is being sold 
        #self.sale_items = tk.Text(self.register_widgets_frame, width=29, font=("Arial", 35), padx=10)
        #self.sale_items.grid(column = 1, row = 0, sticky='e')
        #self.sale_items.bind("<FocusIn>", controller.return_invisible_entry_focus)

        self.sale_items_listbox = tk.Listbox(
            self.register_widgets_frame, width=29,
            height=8, font=("Arial", 46)
        )
        self.sale_items_listbox.grid(column = 1, row = 0, sticky='nse')

        self.sale_items_scrollbar = tk.Scrollbar(
            self.register_widgets_frame,
            orient=tk.VERTICAL, width=40
        )
        self.sale_items_scrollbar.grid(column = 1, row = 0, sticky='nse')
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
            command = lambda: controller.state_manager.yes_no_var.set("yes"))
        self.register_add_item_yes_button.grid(row=0, column=0, sticky='nsew')

        self.register_add_item_no_button=tk.Button(
            self.register_add_item_yes_no_frame, text="No",
            font=("Arial", 90), command = lambda: controller.state_manager.yes_no_var.set("no"))
        self.register_add_item_no_button.grid(row=0, column=1, sticky='nsew')

        # ============================
        # Widgets for Admin Mode frame 
        # ============================
        self.new_item_button = tk.Button(
            self.admin_frame, text = "Add New Item", font=("Arial", 50),
            height = 5, command = lambda: controller.enter_add_item_frame()) 
        self.new_item_button.grid(
            column = 0, row = 1, sticky='s',
            padx = 5, pady = 5, ipadx=10, ipady=10)

        self.run_x_button = tk.Button(
            self.admin_frame, text = "Run\nX", font=("Arial", 50),
              height = 5, command = lambda: controller.run_x())
        self.run_x_button.grid(
            column=1, row=1, sticky='e', padx=5,
            pady=5, ipadx=10, ipady=10)


        self.admin_back_button = tk.Button(
            self.admin_frame, text="Go Back", font=("Arial", 50),
            command=lambda: self.mode_select_frame.tkraise()).grid(column = 0, row = 0, sticky='nw')

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
              command = lambda: controller.quit_button_handler())

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

        # ==================================
        # Widgets for Update Inventory Frame
        # ==================================

        self.update_inventory_label=tk.Label(
            self.update_inventory_frame, text="What would you\nlike to update?",
            font=("Arial", 50))
        self.update_inventory_label.grid(column=1, row=0, sticky='nsew')

        self.update_inventory_entry=tk.Entry(
            self.update_inventory_frame,
            font=("Arial", 75), width=18)
        self.update_inventory_entry.bind("<Return>", controller.get_update_barcode)

        self.update_buttons_frame.grid(column = 1, row=1, sticky='nsew')

        self.update_yes_button = tk.Button(
            self.update_inventory_yes_no, text="Yes", font=("Arial", 150),
            command= lambda: controller.state_manager.yes_no_var.set("yes"))

        self.update_no_button = tk.Button(
            self.update_inventory_yes_no, text="No", font=("Arial", 150),
            command=lambda: controller.state_manager.yes_no_var.set("no"))


        self.update_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
        self.update_no_button.grid(column=1, row=0, sticky='nsew', padx=10)

        self.update_name_button = tk.Button(
            self.update_buttons_frame, text="Name", font=("Arial", 75),
            command = lambda: controller.update_inventory("Name", None))
        self.update_name_button.grid(row=0, column=0, sticky='nsew')

        self.update_price_button = tk.Button(
            self.update_buttons_frame, text="Price", font=("Arial", 75),
            command = lambda: controller.update_inventory("Price", None))
        self.update_price_button.grid(row=0, column=1, sticky='nsew')

        self.update_barcode_button = tk.Button(
            self.update_buttons_frame, text="Barcode", font=("Arial", 75),
            command = lambda: controller.update_inventory("Barcode", None))
        self.update_barcode_button.grid(row=1, column=0, sticky='nsew')

        self.update_taxable_button = tk.Button(
            self.update_buttons_frame, text="Taxable", font=("Arial", 75),
            command = lambda: controller.update_inventory("Taxable", None))
        self.update_taxable_button.grid(row=1, column=1, sticky='nsew')

        self.update_quantity_button = tk.Button(
            self.update_buttons_frame, text="Quantity", font=("Arial", 75),
            command = lambda: controller.update_inventory("Quantity", None))
        self.update_quantity_button.grid(row=2, column=0, sticky='nsew')

        self.update_category_button = tk.Button(
            self.update_buttons_frame, text="Category", font=("Arial", 75),
            command = lambda: controller.update_inventory("Category", None))
        self.update_category_button.grid(row=2, column=1, sticky='nsew')

        # ==========================================
        # Widgets for Additional Register Functions 
        # ==========================================

        self.additional_register_functions_label = tk.Label(
            self.additional_register_functions_frame, text="Select an Option", font=("Arial", 50))
        self.additional_register_functions_label.grid(column = 1, row = 0, sticky='ew')

        self.register_functions_buttons_frame=tk.Frame(self.additional_register_functions_frame)
        self.register_functions_buttons_frame.grid_columnconfigure(0, weight=1)
        self.register_functions_buttons_frame.grid_columnconfigure(1, weight=1)
        self.register_functions_buttons_frame.grid(row=1, column=1, sticky='nsew')

        self.last_button = tk.Button(
            self.register_functions_buttons_frame, text="Void Last\nTransaction",
            font=("Arial", 70), command = lambda: controller.void_transaction("last"))
        self.last_button.grid(row=0, column=0, sticky='nsew')

        self.number_button = tk.Button(
            self.register_functions_buttons_frame, text="Void by\nReference #", 
            font=("Arial", 70), command = lambda: controller.void_transaction("ref"))
        self.number_button.grid(row=0, column=1, sticky='nsew')

        self.print_receipt_button = tk.Button(
            self.register_functions_buttons_frame, text="Print a Receipt", font=("Arial", 70))
        self.print_receipt_button.grid(row=1, column=0, sticky='nsew')

        self.make_return_button = tk.Button(
            self.register_functions_buttons_frame, text="Process Return",
            font=("Arial", 70), command = lambda: controller.process_return())
        self.make_return_button.grid(row=1, column=1, sticky='nsew')

        self.run_x_button = tk.Button(
            self.register_functions_buttons_frame, text="Run X",
            font=("Arial", 50), command = lambda: controller.run_x())
        self.run_x_button.grid(row=2, column=0, sticky='nsew')

        self.continue_button = tk.Button(
            self.additional_register_functions_frame, text="Continue", font=("Arial", 50),
            command= lambda: controller.state_manager.reference_number_var.set("continue"))

        self.additional_register_functions_entry = tk.Entry(
            self.additional_register_functions_frame,
            font=("Arial", 50), justify="right")
        self.additional_register_functions_entry.bind(
            "<Return>", controller.on_additional_register_functions_entry)

        self.additional_register_functions_text = tk.Text(
            self.additional_register_functions_frame, width=30, height=3, font=("Arial", 40))


        self.additional_register_functions_yes_button = tk.Button(
            self.additional_register_functions_yes_no, text="Yes", font=("Arial", 150),
            command= lambda: controller.state_manager.yes_no_var.set("yes"))
        self.additional_register_functions_no_button = tk.Button(
            self.additional_register_functions_yes_no, text="No", font=("Arial", 150),
            command=lambda: controller.state_manager.yes_no_var.set("no"))


        self.additional_register_functions_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
        self.additional_register_functions_yes_button.grid(column=1, row=0, sticky='nsew', padx=10)


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

    def set_return_start(self):
        self.register_functions_buttons_frame.grid_forget()
        self.additional_register_functions_label.config(text="Please scan the item(s) to return\nWhen done, press continue")
        self.additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')
        self.additional_register_functions_entry.focus_force()
        self.continue_button.grid(row=2, column=1, sticky='nsew')

    def set_return_confirmation(self):
        self.additional_register_functions_label.config(text="Return the following item(s)?")
        self.additional_register_functions_text.grid(row=1, column=1, sticky='nsew')
        self.additional_register_functions_yes_no.grid(row=2, column=1, sticky='nsew')
        self.additional_register_functions_text.delete("1.0", "end")

    def set_return_restart(self):
        self.additional_register_functions_label.config(text="Please scan the item(s) to return\nWhen done, press continue")
        self.additional_register_functions_yes_no.grid_forget()
        self.continue_button.grid(row=2, column=1, sticky='nsew')
        self.additional_register_functions_text.grid_forget()
        self.additional_register_functions_text.delete("1.0", "end")
        self.additional_register_functions_entry.grid(row=1, column=1, sticky='nsew')


    def set_return_options(self):
        self.additional_register_functions_yes_no.grid_forget()
        self.register_functions_buttons_frame.grid(row=1, column=1, sticky='nsew')
        self.additional_register_functions_label.config(text="Select an Option")
        self.additional_register_functions_text.grid_forget()
        self.additional_register_functions_entry.grid_forget()


    

