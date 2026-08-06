import os
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from database import DatabaseManager
from updater import AutoUpdater

# Hospital Minimalist Color Palette (Water Transparent Glassmorphism)
ctk.set_appearance_mode("Light")
PRIMARY_TEAL = "#00809D"      # Base Background
GLASS_CARD = "#00667E"        # Semi-transparent dark teal card

class HospitalPOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.app_name = "UK Dental Clinic POS"
        self.title(self.app_name)
        
        # Window Geometry
        self.geometry("1100x760")
        self.minsize(980, 680)
        self.configure(fg_color=PRIMARY_TEAL)

        # Database and Updater Setup
        self.db = DatabaseManager()
        self.cart = [] 
        self.selected_product_id = None
        self.logo_path = None

        self.updater = AutoUpdater(current_version="v1.0.0", repo="your-username/your-repo-name")

        # Main Shell Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True)

        # Build UI Sections
        self._build_top_header()
        self._build_main_views()
        self._build_bottom_bar()

        # Build Floating Components
        self._build_floating_suggestion_popup()
        self._build_settings_dropdown_menu()

        # Check updates non-blockingly
        self.after(2000, lambda: self.updater.check_for_updates(silent=True))

    # -------------------------------------------------------------
    # TOP HEADER: Logo, Single-Line Patient Card & Settings Gear
    # -------------------------------------------------------------
    def _build_top_header(self):
        self.top_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=20, pady=(10, 5))

        # Transparent Logo Badge
        self.logo_box = ctk.CTkLabel(
            self.top_frame, text="LOGO", font=("Arial", 14, "bold"),
            width=70, height=42, fg_color="transparent", corner_radius=8,
            border_width=2, border_color="white", text_color="white"
        )
        self.logo_box.pack(side="left", padx=(0, 10))

        # Single-Line Patient Info Card
        self.info_card = ctk.CTkFrame(self.top_frame, fg_color=GLASS_CARD, corner_radius=12, border_width=1, border_color="#0097B2")
        self.info_card.pack(side="left", fill="x", expand=True, padx=5)

        # Single Horizontal Row Layout (row=0 for all fields)
        ctk.CTkLabel(self.info_card, text="Name *", font=("Arial", 11, "bold"), text_color="white").grid(row=0, column=0, padx=(10, 2), pady=8, sticky="w")
        self.ent_name = ctk.CTkEntry(self.info_card, placeholder_text="Mandatory Name", width=140, height=28)
        self.ent_name.grid(row=0, column=1, padx=(0, 10), pady=8)

        ctk.CTkLabel(self.info_card, text="ID:", font=("Arial", 11, "bold"), text_color="white").grid(row=0, column=2, padx=(5, 2), pady=8, sticky="w")
        self.ent_id = ctk.CTkEntry(self.info_card, placeholder_text="Optional ID", width=95, height=28)
        self.ent_id.grid(row=0, column=3, padx=(0, 10), pady=8)

        ctk.CTkLabel(self.info_card, text="mobile :", font=("Arial", 11, "bold"), text_color="white").grid(row=0, column=4, padx=(5, 2), pady=8, sticky="w")
        self.ent_mobile = ctk.CTkEntry(self.info_card, placeholder_text="Optional Mobile", width=130, height=28)
        self.ent_mobile.grid(row=0, column=5, padx=(0, 10), pady=8)

        ctk.CTkLabel(self.info_card, text="Ref No:", font=("Arial", 11, "bold"), text_color="white").grid(row=0, column=6, padx=(5, 2), pady=8, sticky="w")
        self.ent_ref = ctk.CTkEntry(self.info_card, placeholder_text="Optional Ref", width=95, height=28)
        self.ent_ref.grid(row=0, column=7, padx=(0, 10), pady=8)

        # Single Settings Gear Icon Button
        self.btn_gear = ctk.CTkButton(
            self.top_frame, text="⚙", font=("Arial", 26), width=40, height=40,
            fg_color="transparent", hover_color="#005B6E", text_color="white", command=self.toggle_settings_dropdown
        )
        self.btn_gear.pack(side="right", padx=(5, 0))

    # -------------------------------------------------------------
    # MAIN VIEWS: Water-Transparent Billing Dashboard & Management
    # -------------------------------------------------------------
    def _build_main_views(self):
        self.views_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.views_container.pack(fill="both", expand=True, padx=20, pady=5)

        # POS Billing Table Panel (Glassmorphism Styled)
        self.pos_view = ctk.CTkFrame(self.views_container, fg_color=GLASS_CARD, corner_radius=12, border_width=1, border_color="#0097B2")
        self.pos_view.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), rowheight=28)
        style.configure("Treeview", font=("Arial", 10), rowheight=24)

        columns = ("no", "product", "quantity", "price", "discount", "total")
        self.pos_table = ttk.Treeview(self.pos_view, columns=columns, show="headings")

        self.pos_table.heading("no", text="#")
        self.pos_table.heading("product", text="Product")
        self.pos_table.heading("quantity", text="quantity (Click to Edit)")
        self.pos_table.heading("price", text="price")
        self.pos_table.heading("discount", text="Discount % (Click to Edit)")
        self.pos_table.heading("total", text="total price")

        self.pos_table.column("no", width=40, anchor="center")
        self.pos_table.column("product", width=230, anchor="w")
        self.pos_table.column("quantity", width=150, anchor="center")
        self.pos_table.column("price", width=100, anchor="center")
        self.pos_table.column("discount", width=160, anchor="center")
        self.pos_table.column("total", width=120, anchor="center")

        self.pos_table.pack(fill="both", expand=True, padx=10, pady=10)
        self.pos_table.bind("<Button-1>", self.on_cell_single_click)

        # Product Management View (Hidden by default)
        self.prod_mgmt_view = ctk.CTkFrame(self.views_container, fg_color=GLASS_CARD, corner_radius=12, border_width=1, border_color="#0097B2")

        input_panel = ctk.CTkFrame(self.prod_mgmt_view, fg_color="transparent")
        input_panel.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(input_panel, text="Product Name:", text_color="white").grid(row=0, column=0, padx=5, pady=5)
        self.ent_prod_name = ctk.CTkEntry(input_panel, width=160)
        self.ent_prod_name.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_panel, text="Price ($):", text_color="white").grid(row=0, column=2, padx=5, pady=5)
        self.ent_prod_price = ctk.CTkEntry(input_panel, width=90)
        self.ent_prod_price.grid(row=0, column=3, padx=5, pady=5)

        self.btn_save_prod = ctk.CTkButton(input_panel, text="Save New", command=self.add_new_product, fg_color="#276749", width=85)
        self.btn_save_prod.grid(row=0, column=4, padx=5, pady=5)

        self.btn_edit_prod = ctk.CTkButton(input_panel, text="Update Selected", command=self.update_selected_product, fg_color="#D69E2E", width=100)
        self.btn_edit_prod.grid(row=0, column=5, padx=5, pady=5)

        self.btn_del_prod = ctk.CTkButton(input_panel, text="Delete", command=self.delete_selected_product, fg_color="#E53E3E", width=75)
        self.btn_del_prod.grid(row=0, column=6, padx=5, pady=5)

        self.btn_close_mgmt = ctk.CTkButton(input_panel, text="Back to Billing", command=self.show_pos_view, fg_color="#4A5568", width=100)
        self.btn_close_mgmt.grid(row=0, column=7, padx=5, pady=5)

        prod_cols = ("id", "name", "price")
        self.prod_table = ttk.Treeview(self.prod_mgmt_view, columns=prod_cols, show="headings")
        self.prod_table.heading("id", text="ID")
        self.prod_table.heading("name", text="Product Name")
        self.prod_table.heading("price", text="Price ($)")

        self.prod_table.column("id", width=60, anchor="center")
        self.prod_table.column("name", width=300, anchor="w")
        self.prod_table.column("price", width=120, anchor="center")
        self.prod_table.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        self.prod_table.bind("<<TreeviewSelect>>", self.on_product_select)

    # -------------------------------------------------------------
    # ONE-CLICK IN-PLACE EDITING LOGIC
    # -------------------------------------------------------------
    def on_cell_single_click(self, event):
        region = self.pos_table.identify_region(event.x, event.y)
        if region != "cell":
            return

        column = self.pos_table.identify_column(event.x)
        item_id = self.pos_table.identify_row(event.y)
        if not item_id:
            return

        item_index = self.pos_table.index(item_id)
        if column not in ("#3", "#5"):
            return

        x, y, w, h = self.pos_table.bbox(item_id, column)

        entry_var = tk.StringVar()
        cell_entry = tk.Entry(self.pos_table, textvariable=entry_var)
        cell_entry.place(x=x, y=y, width=w, height=h)
        cell_entry.focus_set()

        current_item = self.cart[item_index]
        if column == "#3":
            entry_var.set(str(current_item['qty']))
        elif column == "#5":
            entry_var.set(str(int(current_item['disc_pct'])))

        def save_cell_value(e=None):
            val = entry_var.get().strip()
            cell_entry.destroy()

            if column == "#3":
                if val.isdigit() and int(val) > 0:
                    self.cart[item_index]['qty'] = int(val)
                    self.recalculate_cart_item(item_index)
            elif column == "#5":
                try:
                    disc_val = float(val.replace("%", ""))
                    self.cart[item_index]['disc_pct'] = max(0.0, disc_val)
                    self.recalculate_cart_item(item_index)
                except ValueError:
                    pass

        cell_entry.bind("<Return>", save_cell_value)
        cell_entry.bind("<FocusOut>", save_cell_value)

    def recalculate_cart_item(self, index):
        item = self.cart[index]
        base_price = item['price'] * item['qty']
        discount_amount = base_price * (item['disc_pct'] / 100.0)
        
        item['discount_amount'] = discount_amount
        item['total'] = max(0.0, base_price - discount_amount)

        self.refresh_pos_table_display()

    def refresh_pos_table_display(self):
        for row in self.pos_table.get_children():
            self.pos_table.delete(row)

        for item in self.cart:
            self.pos_table.insert(
                "", "end", 
                values=(
                    item['no'], 
                    item['product'], 
                    f"{item['qty']:02d}", 
                    f"{item['price']:,.0f}", 
                    f"{int(item['disc_pct'])}%", 
                    f"{item['total']:,.0f}"
                )
            )
        self.recalculate_totals()

    # -------------------------------------------------------------
    # BOTTOM BAR & SEARCH INPUT
    # -------------------------------------------------------------
    def _build_bottom_bar(self):
        self.bottom_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=(2, 10), side="bottom")

        # Left Column
        self.left_actions = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.left_actions.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(self.left_actions, text="🔍 Search Product:", font=("Arial", 11, "bold"), text_color="white").pack(anchor="w")

        self.ent_search = ctk.CTkEntry(self.left_actions, placeholder_text="Type product name...", width=280, height=28)
        self.ent_search.pack(anchor="w", pady=(2, 5))

        self.ent_search.bind("<KeyRelease>", self.on_search_key_release)
        self.ent_search.bind("<Down>", self.focus_suggestion_list)
        self.ent_search.bind("<Return>", self.on_search_enter_pressed)

        # Quantity & Discount Panel
        param_panel = ctk.CTkFrame(self.left_actions, fg_color="transparent")
        param_panel.pack(anchor="w", pady=(0, 5))

        ctk.CTkLabel(param_panel, text="Qty:", font=("Arial", 10, "bold"), text_color="white").grid(row=0, column=0, padx=(0, 4))
        self.ent_add_qty = ctk.CTkEntry(param_panel, width=50, height=25)
        self.ent_add_qty.insert(0, "1")
        self.ent_add_qty.grid(row=0, column=1, padx=(0, 10))
        self.ent_add_qty.bind("<Return>", self.move_focus_to_disc)

        ctk.CTkLabel(param_panel, text="Disc %:", font=("Arial", 10, "bold"), text_color="white").grid(row=0, column=2, padx=(0, 4))
        self.ent_add_disc = ctk.CTkEntry(param_panel, width=60, height=25)
        self.ent_add_disc.insert(0, "0")
        self.ent_add_disc.grid(row=0, column=3)
        self.ent_add_disc.bind("<Return>", lambda e: self.add_product_to_cart())

        # Print Button
        self.btn_print = ctk.CTkButton(self.left_actions, text="print", command=self.print_a4_invoice, width=160, height=36, fg_color="white", text_color="black", corner_radius=12, font=("Arial", 12, "bold"))
        self.btn_print.pack(anchor="w")

        # Right Column
        self.right_summary = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.right_summary.pack(side="right", anchor="e")

        self.lbl_subtotal = ctk.CTkLabel(self.right_summary, text="total Amount :0.00", font=("Arial", 14, "bold"), text_color="white")
        self.lbl_subtotal.pack(anchor="e", pady=1)

        self.lbl_discount = ctk.CTkLabel(self.right_summary, text="Discount Amount :0.00", font=("Arial", 14, "bold"), text_color="white")
        self.lbl_discount.pack(anchor="e", pady=1)

        self.line = ctk.CTkFrame(self.right_summary, height=2, width=240, fg_color="white")
        self.line.pack(anchor="e", pady=2)

        self.lbl_payable = ctk.CTkLabel(self.right_summary, text="Total payable :0.00", font=("Arial", 16, "bold"), text_color="white")
        self.lbl_payable.pack(anchor="e", pady=1)

        self.load_all_products()

    # -------------------------------------------------------------
    # FLOATING DROPDOWN OVERLAY
    # -------------------------------------------------------------
    def _build_floating_suggestion_popup(self):
        self.popup_frame = tk.Frame(self, bg="#2D3748", bd=1, relief="solid")
        self.suggestion_listbox = tk.Listbox(
            self.popup_frame, 
            font=("Arial", 10), 
            bg="#303A4A", 
            fg="white", 
            selectbackground="#00809D", 
            selectforeground="white",
            bd=0, 
            highlightthickness=0,
            activestyle="none"
        )
        self.suggestion_listbox.pack(fill="both", expand=True, padx=2, pady=2)

        self.suggestion_listbox.bind("<ButtonRelease-1>", self.on_suggestion_clicked)
        self.suggestion_listbox.bind("<Return>", self.on_suggestion_selected_by_enter)

        self.popup_visible = False

    def show_suggestion_popup(self, items):
        self.suggestion_listbox.delete(0, tk.END)
        for item in items:
            self.suggestion_listbox.insert(tk.END, f"🔍  {item[1]}   —   ${item[2]:,.2f}")

        if not self.popup_visible:
            self.popup_frame.place(relx=0.038, rely=0.72, width=280, height=110)
            self.popup_frame.lift()
            self.popup_visible = True

    def hide_suggestion_popup(self):
        if self.popup_visible:
            self.popup_frame.place_forget()
            self.popup_visible = False

    # -------------------------------------------------------------
    # SEARCH & CART UTILITIES
    # -------------------------------------------------------------
    def load_all_products(self):
        self.all_products = self.db.get_all_products()

    def on_search_key_release(self, event):
        if event.keysym in ("Down", "Up", "Return", "Escape"):
            return

        query = self.ent_search.get().lower().strip()
        if not query:
            self.hide_suggestion_popup()
            return

        matches = [p for p in self.all_products if query in p[1].lower()]
        if matches:
            self.show_suggestion_popup(matches)
        else:
            self.hide_suggestion_popup()

    def focus_suggestion_list(self, event=None):
        if self.popup_visible and self.suggestion_listbox.size() > 0:
            self.suggestion_listbox.focus_set()
            self.suggestion_listbox.selection_set(0)

    def on_search_enter_pressed(self, event=None):
        query = self.ent_search.get().strip()

        if self.popup_visible and self.suggestion_listbox.size() > 0:
            selected_text = self.suggestion_listbox.get(0)
            self.apply_selected_product_text(selected_text)
        elif query:
            self.move_focus_to_qty()

    def on_suggestion_clicked(self, event=None):
        selection = self.suggestion_listbox.curselection()
        if selection:
            selected_text = self.suggestion_listbox.get(selection[0])
            self.apply_selected_product_text(selected_text)

    def on_suggestion_selected_by_enter(self, event=None):
        selection = self.suggestion_listbox.curselection()
        if selection:
            selected_text = self.suggestion_listbox.get(selection[0])
            self.apply_selected_product_text(selected_text)

    def apply_selected_product_text(self, raw_text):
        clean_text = raw_text.replace("🔍  ", "").strip()
        name, price = clean_text.split("   —   $")

        formatted_val = f"{name} - ${price}"
        self.ent_search.delete(0, tk.END)
        self.ent_search.insert(0, formatted_val)

        self.hide_suggestion_popup()
        self.move_focus_to_qty()

    def move_focus_to_qty(self, event=None):
        self.ent_add_qty.focus()
        self.ent_add_qty.select_range(0, tk.END)

    def move_focus_to_disc(self, event=None):
        self.ent_add_disc.focus()
        self.ent_add_disc.select_range(0, tk.END)

    def add_product_to_cart(self):
        selected_text = self.ent_search.get().strip()

        if not selected_text:
            return

        if " - $" not in selected_text:
            messagebox.showwarning(
                "Product Not Available", 
                f"The product '{selected_text}' is not available in the list!\n\nPlease add this product first via Settings (⚙) -> add product."
            )
            self.ent_search.delete(0, tk.END)
            self.hide_suggestion_popup()
            return

        name, price_str = selected_text.split(" - $")
        
        db_product_names = [p[1].strip().lower() for p in self.all_products]
        if name.strip().lower() not in db_product_names:
            messagebox.showwarning(
                "Product Not Available", 
                f"The product '{name}' is not in your product list!\n\nPlease add it to the database first."
            )
            self.ent_search.delete(0, tk.END)
            self.hide_suggestion_popup()
            return

        unit_price = float(price_str.replace(",", ""))

        try:
            qty = int(self.ent_add_qty.get().strip() or 1)
            disc_pct = float(self.ent_add_disc.get().strip() or 0.0)
        except ValueError:
            qty = 1
            disc_pct = 0.0

        base_total = unit_price * qty
        discount_amt = base_total * (disc_pct / 100.0)
        net_total = max(0.0, base_total - discount_amt)

        item_num = f"{len(self.cart) + 1:02d}"
        item = {
            'no': item_num,
            'product': name,
            'qty': qty,
            'price': unit_price,
            'disc_pct': disc_pct,
            'discount_amount': discount_amt,
            'total': net_total
        }

        self.cart.append(item)
        self.refresh_pos_table_display()

        self.ent_search.delete(0, tk.END)
        self.ent_add_qty.delete(0, tk.END)
        self.ent_add_qty.insert(0, "1")
        self.ent_add_disc.delete(0, tk.END)
        self.ent_add_disc.insert(0, "0")

        self.hide_suggestion_popup()
        self.ent_search.focus()

    # -------------------------------------------------------------
    # SETTINGS DROPDOWN & LOGO UPLOAD
    # -------------------------------------------------------------
    def _build_settings_dropdown_menu(self):
        self.settings_dropdown = ctk.CTkFrame(self, fg_color="white", corner_radius=10, border_width=2, border_color="black", width=220, height=350)
        self.settings_dropdown_visible = False

        ctk.CTkLabel(self.settings_dropdown, text="⚙ Settings", font=("Arial", 14, "bold"), text_color="black").pack(pady=(10, 5))

        ctk.CTkLabel(self.settings_dropdown, text="App Name:", font=("Arial", 10, "bold"), text_color="black").pack(anchor="w", padx=15)
        self.ent_app_name = ctk.CTkEntry(self.settings_dropdown, width=180, height=25)
        self.ent_app_name.insert(0, self.app_name)
        self.ent_app_name.pack(padx=15, pady=2)

        btn_save_name = ctk.CTkButton(self.settings_dropdown, text="Update Name", command=self.update_application_name, fg_color="#2B6CB0", height=22, width=120)
        btn_save_name.pack(pady=(0, 10))

        ctk.CTkFrame(self.settings_dropdown, height=1, fg_color="#CBD5E0").pack(fill="x", padx=10, pady=2)

        btn_mode = ctk.CTkButton(self.settings_dropdown, text="mode", text_color="black", fg_color="transparent", hover_color="#E2E8F0", anchor="center", command=self.toggle_mode)
        btn_mode.pack(fill="x", padx=5, pady=2)

        btn_add_prod = ctk.CTkButton(self.settings_dropdown, text="add product", text_color="black", fg_color="transparent", hover_color="#E2E8F0", anchor="center", command=self.show_product_management_view)
        btn_add_prod.pack(fill="x", padx=5, pady=2)

        btn_old_file = ctk.CTkButton(self.settings_dropdown, text="old file", text_color="black", fg_color="transparent", hover_color="#E2E8F0", anchor="center", command=self.show_old_files_history)
        btn_old_file.pack(fill="x", padx=5, pady=2)

        btn_logo = ctk.CTkButton(self.settings_dropdown, text="change logo", text_color="black", fg_color="transparent", hover_color="#E2E8F0", anchor="center", command=self.change_logo)
        btn_logo.pack(fill="x", padx=5, pady=2)

        btn_update = ctk.CTkButton(self.settings_dropdown, text="check update", text_color="black", fg_color="transparent", hover_color="#E2E8F0", anchor="center", command=lambda: self.updater.check_for_updates(silent=False))
        btn_update.pack(fill="x", padx=5, pady=2)

    def toggle_settings_dropdown(self):
        if self.settings_dropdown_visible:
            self.settings_dropdown.place_forget()
            self.settings_dropdown_visible = False
        else:
            self.settings_dropdown.place(relx=0.98, rely=0.08, anchor="ne")
            self.settings_dropdown.lift()
            self.settings_dropdown_visible = True

    def update_application_name(self):
        new_name = self.ent_app_name.get().strip()
        if new_name:
            self.app_name = new_name
            self.title(self.app_name)
            messagebox.showinfo("Updated", f"App Name changed to: {self.app_name}")

    def toggle_mode(self):
        current = ctk.get_appearance_mode()
        new_mode = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)

    def change_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path = path
            img = Image.open(path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(65, 45))
            self.logo_box.configure(image=ctk_img, text="")

    # -------------------------------------------------------------
    # OLD FILE EDITOR & AUDIT LOG HISTORY (Requirement 8)
    # -------------------------------------------------------------
    def show_old_files_history(self):
        self.toggle_settings_dropdown()
        
        hist_win = ctk.CTkToplevel(self)
        hist_win.title("Old File - Invoice Manager & Audit Logs")
        hist_win.geometry("750x500")
        hist_win.grab_set()

        left_p = ctk.CTkFrame(hist_win, width=300)
        left_p.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_p = ctk.CTkFrame(hist_win, width=420)
        right_p.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_p, text="Select Old Invoice:", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)

        cols = ("id", "name", "total")
        rec_table = ttk.Treeview(left_p, columns=cols, show="headings", height=15)
        rec_table.heading("id", text="ID")
        rec_table.heading("name", text="Patient Name")
        rec_table.heading("total", text="Payable ($)")
        rec_table.column("id", width=40, anchor="center")
        rec_table.column("name", width=150, anchor="w")
        rec_table.column("total", width=80, anchor="center")
        rec_table.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(right_p, text="Edit Invoice Details", font=("Arial", 14, "bold")).pack(pady=5)

        ent_e_name = ctk.CTkEntry(right_p, placeholder_text="Patient Name")
        ent_e_name.pack(fill="x", padx=15, pady=4)

        ent_e_mobile = ctk.CTkEntry(right_p, placeholder_text="Mobile No")
        ent_e_mobile.pack(fill="x", padx=15, pady=4)

        ent_e_payable = ctk.CTkEntry(right_p, placeholder_text="Payable Balance")
        ent_e_payable.pack(fill="x", padx=15, pady=4)

        log_box = ctk.CTkTextbox(right_p, height=120)
        log_box.pack(fill="both", expand=True, padx=15, pady=5)

        selected_rec = {"id": None, "data": None}

        def load_receipts():
            for row in rec_table.get_children():
                rec_table.delete(row)
            for r in self.db.get_all_receipts():
                rec_table.insert("", "end", values=(r[0], r[1], f"${r[8]:,.2f}"))

        def on_rec_select(event):
            sel = rec_table.selection()
            if sel:
                rid = rec_table.item(sel[0])['values'][0]
                data = self.db.get_receipt_by_id(rid)
                if data:
                    selected_rec["id"] = rid
                    selected_rec["data"] = data

                    ent_e_name.delete(0, 'end')
                    ent_e_name.insert(0, data[1])
                    ent_e_mobile.delete(0, 'end')
                    ent_e_mobile.insert(0, data[2] or '')
                    ent_e_payable.delete(0, 'end')
                    ent_e_payable.insert(0, str(data[8]))

                    log_box.delete("1.0", "end")
                    logs = self.db.get_receipt_history(rid)
                    log_box.insert("end", f"=== Edit Log History for Invoice #{rid} ===\n")
                    if logs:
                        for l in logs:
                            log_box.insert("end", f"[{l[3]}] Edited {l[0]}: '{l[1]}' -> '{l[2]}'\n")
                    else:
                        log_box.insert("end", "No previous edits logged.\n")

        rec_table.bind("<<TreeviewSelect>>", on_rec_select)

        def save_invoice_edits():
            rid = selected_rec["id"]
            old = selected_rec["data"]
            if not rid or not old:
                messagebox.showerror("Error", "Select an invoice first.")
                return

            new_name = ent_e_name.get().strip()
            new_mobile = ent_e_mobile.get().strip()
            new_payable = float(ent_e_payable.get().strip() or 0.0)

            if new_name != old[1]:
                self.db.log_edit(rid, "patient_name", old[1], new_name)
            if new_mobile != old[2]:
                self.db.log_edit(rid, "mobile", old[2], new_mobile)
            if new_payable != old[8]:
                self.db.log_edit(rid, "payable_balance", old[8], new_payable)

            self.db.update_receipt(rid, new_name, new_mobile, old[3], old[4], old[6], old[7], new_payable)
            messagebox.showinfo("Saved", "Invoice updated and edit history logged!")
            load_receipts()

        btn_save = ctk.CTkButton(right_p, text="Save Edits & Log History", command=save_invoice_edits, fg_color="#276749")
        btn_save.pack(pady=8)

        load_receipts()

    # -------------------------------------------------------------
    # PRODUCT CATALOG MANAGEMENT
    # -------------------------------------------------------------
    def show_product_management_view(self):
        self.toggle_settings_dropdown()
        self.pos_view.pack_forget()
        self.prod_mgmt_view.pack(fill="both", expand=True)
        self.refresh_product_management_table()

    def show_pos_view(self):
        self.prod_mgmt_view.pack_forget()
        self.pos_view.pack(fill="both", expand=True)
        self.load_all_products()

    def refresh_product_management_table(self):
        for item in self.prod_table.get_children():
            self.prod_table.delete(item)
        products = self.db.get_all_products()
        for p in products:
            self.prod_table.insert("", "end", values=(p[0], p[1], f"${p[2]:,.2f}"))

    def add_new_product(self):
        name = self.ent_prod_name.get().strip()
        price_str = self.ent_prod_price.get().strip()

        if name and price_str:
            try:
                price = float(price_str)
                self.db.add_product(name, price)
                self.ent_prod_name.delete(0, 'end')
                self.ent_prod_price.delete(0, 'end')
                self.refresh_product_management_table()
                messagebox.showinfo("Success", f"Product '{name}' added!")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid numeric price.")

    def on_product_select(self, event):
        selected = self.prod_table.selection()
        if selected:
            item = self.prod_table.item(selected[0])
            vals = item['values']
            self.selected_product_id = vals[0]
            self.ent_prod_name.delete(0, 'end')
            self.ent_prod_name.insert(0, vals[1])
            self.ent_prod_price.delete(0, 'end')
            self.ent_prod_price.insert(0, str(vals[2]).replace('$', '').replace(',', ''))

    def update_selected_product(self):
        if not self.selected_product_id:
            messagebox.showerror("Error", "Select a product from table to update.")
            return

        name = self.ent_prod_name.get().strip()
        price_str = self.ent_prod_price.get().strip()

        if name and price_str:
            try:
                price = float(price_str)
                self.db.update_product(self.selected_product_id, name, price)
                self.refresh_product_management_table()
                messagebox.showinfo("Success", "Product updated successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric price.")

    def delete_selected_product(self):
        if not self.selected_product_id:
            messagebox.showerror("Error", "Select a product from table to delete.")
            return

        if messagebox.askyesno("Confirm", "Delete selected product?"):
            self.db.delete_product(self.selected_product_id)
            self.ent_prod_name.delete(0, 'end')
            self.ent_prod_price.delete(0, 'end')
            self.selected_product_id = None
            self.refresh_product_management_table()

    # -------------------------------------------------------------
    # COMPUTATIONS & RELIABLE AUTO-PRINTING WITH LOGO
    # -------------------------------------------------------------
    def recalculate_totals(self):
        subtotal = sum(i['price'] * i['qty'] for i in self.cart)
        total_discount_amt = sum(i['discount_amount'] for i in self.cart)
        payable = subtotal - total_discount_amt

        self.lbl_subtotal.configure(text=f"total Amount :{subtotal:,.0f}")
        self.lbl_discount.configure(text=f"Discount Amount :{total_discount_amt:,.0f}")
        self.lbl_payable.configure(text=f"Total payable :{payable:,.0f}")

    def print_a4_invoice(self):
        patient_name = self.ent_name.get().strip()
        if not patient_name:
            messagebox.showerror("Error", "Patient Name is mandatory!")
            return

        if not self.cart:
            messagebox.showerror("Error", "Billing cart is empty! Add products first.")
            return

        subtotal = sum(i['price'] * i['qty'] for i in self.cart)
        total_discount = sum(i['discount_amount'] for i in self.cart)
        payable = subtotal - total_discount
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")

        self.db.save_receipt(
            patient_name, self.ent_mobile.get().strip(), self.ent_ref.get().strip(),
            self.ent_id.get().strip(), now_str, subtotal, total_discount, payable
        )

        logo_html = ""
        if self.logo_path and os.path.exists(self.logo_path):
            logo_uri = f"file:///{os.path.abspath(self.logo_path).replace('\\', '/')}"
            logo_html = f'<img src="{logo_uri}" style="max-height: 50px; max-width: 150px; float: left;" />'

        table_rows_html = ""
        for item in self.cart:
            table_rows_html += f"""
            <tr>
                <td style="width: 8%; text-align: center;">{item['no']}</td>
                <td style="width: 42%; text-align: left;">{item['product']}</td>
                <td style="width: 12%; text-align: center;">{item['qty']:02d}</td>
                <td style="width: 13%; text-align: right;">${item['price']:,.2f}</td>
                <td style="width: 10%; text-align: center;">{int(item['disc_pct'])}%</td>
                <td style="width: 15%; text-align: right;">${item['total']:,.2f}</td>
            </tr>
            """

        html_doc = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Invoice - {patient_name}</title>
            <style>
                @page {{ size: A4; margin: 12mm; }}
                * {{ box-sizing: border-box; }}
                body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #111; margin: 0; padding: 0; background-color: #fff; }}
                .invoice-container {{ width: 100%; max-width: 100%; padding: 10px; }}
                .header {{ border-bottom: 2px solid #00809D; padding-bottom: 12px; margin-bottom: 15px; overflow: hidden; }}
                .header-text {{ text-align: center; }}
                .header h1 {{ margin: 0; font-size: 22px; color: #00809D; text-transform: uppercase; }}
                .header p {{ margin: 3px 0 0; font-size: 12px; color: #555; }}
                .info-card {{ width: 100%; border: 1px solid #ddd; border-radius: 6px; padding: 10px 12px; margin-bottom: 15px; font-size: 13px; }}
                .info-table {{ width: 100%; border-collapse: collapse; }}
                .info-table td {{ padding: 4px 0; vertical-align: top; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }}
                .items-table th {{ background-color: #00809D; color: white; padding: 8px 6px; font-weight: bold; border: 1px solid #00809D; }}
                .items-table td {{ border: 1px solid #ccc; padding: 7px 6px; }}
                .summary-wrapper {{ width: 100%; margin-top: 20px; display: table; }}
                .totals-box {{ display: table-cell; text-align: right; float: right; width: 50%; font-size: 13px; line-height: 1.8; }}
                .totals-row {{ display: flex; justify-content: space-between; padding: 2px 0; }}
                .payable-row {{ font-size: 16px; font-weight: bold; color: #00809D; margin-top: 6px; border-top: 2px solid #00809D; padding-top: 6px; display: flex; justify-content: space-between; }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <div class="header">
                    {logo_html}
                    <div class="header-text">
                        <h1>{self.app_name}</h1>
                        <p>Date: {now_str}</p>
                    </div>
                </div>

                <div class="info-card">
                    <table class="info-table">
                        <tr>
                            <td style="width: 50%;"><strong>Patient Name:</strong> {patient_name}</td>
                            <td style="width: 50%;"><strong>Patient ID:</strong> {self.ent_id.get() or 'N/A'}</td>
                        </tr>
                        <tr>
                            <td><strong>Mobile:</strong> {self.ent_mobile.get() or 'N/A'}</td>
                            <td><strong>Ref No:</strong> {self.ent_ref.get() or 'N/A'}</td>
                        </tr>
                    </table>
                </div>

                <table class="items-table">
                    <thead>
                        <tr>
                            <th style="width: 8%;">#</th>
                            <th style="width: 42%; text-align: left;">Product / Service</th>
                            <th style="width: 12%;">Qty</th>
                            <th style="width: 13%; text-align: right;">Unit Price</th>
                            <th style="width: 10%;">Discount</th>
                            <th style="width: 15%; text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows_html}
                    </tbody>
                </table>

                <div class="summary-wrapper">
                    <div class="totals-box">
                        <div class="totals-row">
                            <span>Subtotal:</span>
                            <span>${subtotal:,.2f}</span>
                        </div>
                        <div class="totals-row">
                            <span>Discount Amount:</span>
                            <span>${total_discount:,.2f}</span>
                        </div>
                        <div class="payable-row">
                            <span>Total Payable:</span>
                            <span>${payable:,.2f}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Auto Print Trigger -->
            <script type="text/javascript">
                window.onload = function() {{
                    window.print();
                }};
            </script>
        </body>
        </html>
        """

        temp_path = os.path.abspath("print_invoice.html")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(html_doc)

        webbrowser.open(f"file:///{temp_path}")

if __name__ == "__main__":
    app = HospitalPOSApp()
    app.mainloop()