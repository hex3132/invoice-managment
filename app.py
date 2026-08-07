import os
import datetime
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from database import DatabaseManager
from updater import AutoUpdater

# -------------------------------------------------------------
# MODERN SAAS DASHBOARD LIGHT THEME
# -------------------------------------------------------------
ctk.set_appearance_mode("Light")

SIDEBAR_BLUE = "#2563EB"       # Royal Blue Sidebar Background
SIDEBAR_HOVER = "#1D4ED8"      # Hover state for sidebar buttons
BG_MAIN = "#F8FAFC"            # Clean Light Slate Gray Background
CARD_BG = "#FFFFFF"            # Crisp White Cards
BORDER_COLOR = "#E2E8F0"       # Light Slate Borders
TEXT_DARK = "#1E293B"          # Main Dark Text
TEXT_MUTED = "#64748B"         # Muted Gray Text
ACCENT_BLUE = "#2563EB"        # Action Buttons Color
ACCENT_GREEN = "#10B981"       # Success/Save Buttons

class HospitalPOSApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.app_name = "UK Dental Clinic POS"
        self.title(self.app_name)
        
        self.geometry("1240x780")
        self.minsize(1050, 700)
        self.configure(fg_color=BG_MAIN)

        # Database and Updater Setup
        self.db = DatabaseManager()
        self.cart = [] 
        self.selected_product_id = None
        self.logo_path = None

        self.updater = AutoUpdater(current_version="v1.0.1", repo="hex3132/invoice-managment")

        # Main Shell Container
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build UI Components
        self._build_sidebar_navigation()
        self._build_main_dashboard_content()
        self._build_floating_suggestion_popup()

    # -------------------------------------------------------------
    # LEFT SIDEBAR NAVIGATION
    # -------------------------------------------------------------
    def _build_sidebar_navigation(self):
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BLUE, corner_radius=0, width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # App Brand Header
        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(fill="x", padx=15, pady=(20, 25))

        self.logo_box = ctk.CTkLabel(
            self.brand_frame, text="🏥", font=("Arial", 22),
            width=40, height=40, fg_color="#3B82F6", corner_radius=10, text_color="white"
        )
        self.logo_box.pack(side="left", padx=(0, 10))

        self.lbl_brand = ctk.CTkLabel(
            self.brand_frame, text="POS Admin", font=("Arial", 16, "bold"), text_color="white"
        )
        self.lbl_brand.pack(side="left", anchor="w")

        # Navigation Links
        self.btn_nav_pos = ctk.CTkButton(
            self.sidebar, text="  📊  Billing / POS", font=("Arial", 13, "bold"),
            fg_color="#3B82F6", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=self.show_pos_view
        )
        self.btn_nav_pos.pack(fill="x", padx=12, pady=4)

        self.btn_nav_products = ctk.CTkButton(
            self.sidebar, text="  📦  Products", font=("Arial", 13),
            fg_color="transparent", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=self.show_product_management_view
        )
        self.btn_nav_products.pack(fill="x", padx=12, pady=4)

        self.btn_nav_old = ctk.CTkButton(
            self.sidebar, text="  📑  Old Files / History", font=("Arial", 13),
            fg_color="transparent", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=self.show_old_files_history
        )
        self.btn_nav_old.pack(fill="x", padx=12, pady=4)

        self.btn_nav_rename = ctk.CTkButton(
            self.sidebar, text="  ✏️  Rename App", font=("Arial", 13),
            fg_color="transparent", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=self.update_application_name
        )
        self.btn_nav_rename.pack(fill="x", padx=12, pady=4)

        self.btn_nav_logo = ctk.CTkButton(
            self.sidebar, text="  🖼️  Change Logo", font=("Arial", 13),
            fg_color="transparent", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=self.change_logo
        )
        self.btn_nav_logo.pack(fill="x", padx=12, pady=4)

        self.btn_nav_update = ctk.CTkButton(
            self.sidebar, text="  🔄  Check Update", font=("Arial", 13),
            fg_color="transparent", text_color="white", hover_color=SIDEBAR_HOVER,
            anchor="w", height=42, corner_radius=10, command=lambda: self.updater.check_for_updates(silent=False)
        )
        self.btn_nav_update.pack(fill="x", padx=12, pady=4)

        # Bottom Status Badge
        self.side_footer_card = ctk.CTkFrame(self.sidebar, fg_color="#3B82F6", corner_radius=12)
        self.side_footer_card.pack(fill="x", padx=12, pady=20, side="bottom")

        ctk.CTkLabel(self.side_footer_card, text="System Status", font=("Arial", 11, "bold"), text_color="white").pack(pady=(10, 2))
        ctk.CTkLabel(self.side_footer_card, text="v1.0.1 (Latest Version)", font=("Arial", 10), text_color="#E0F2FE").pack(pady=(0, 10))

    # -------------------------------------------------------------
    # MAIN DASHBOARD CONTENT
    # -------------------------------------------------------------
    def _build_main_dashboard_content(self):
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=20, pady=15)

        # Header Title
        self.top_header_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.top_header_frame.pack(fill="x", pady=(0, 5))

        title_box = ctk.CTkFrame(self.top_header_frame, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(title_box, text="Dashboard / ", font=("Arial", 18, "bold"), text_color=TEXT_MUTED).pack(side="left")
        self.lbl_main_title = ctk.CTkLabel(title_box, text=self.app_name, font=("Arial", 18, "bold"), text_color=TEXT_DARK)
        self.lbl_main_title.pack(side="left")

        # ------------------- HEADER PATIENT & SEARCH PANEL -------------------
        self.info_card = ctk.CTkFrame(self.main_content, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.info_card.pack(fill="x", pady=(0, 10))

        # Patient Info Entries
        patient_frame = ctk.CTkFrame(self.info_card, fg_color="transparent")
        patient_frame.pack(side="left", fill="y", padx=12, pady=10)

        ctk.CTkLabel(patient_frame, text="Name *", font=("Arial", 10, "bold"), text_color=TEXT_DARK).grid(row=0, column=0, padx=4, pady=2, sticky="w")
        self.ent_name = ctk.CTkEntry(patient_frame, placeholder_text="Mandatory Name", width=130, height=28, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_name.grid(row=0, column=1, padx=(0, 8), pady=2)

        ctk.CTkLabel(patient_frame, text="ID:", font=("Arial", 10, "bold"), text_color=TEXT_DARK).grid(row=0, column=2, padx=4, pady=2, sticky="w")
        self.ent_id = ctk.CTkEntry(patient_frame, placeholder_text="Optional ID", width=90, height=28, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_id.grid(row=0, column=3, padx=(0, 8), pady=2)

        ctk.CTkLabel(patient_frame, text="Mobile:", font=("Arial", 10, "bold"), text_color=TEXT_DARK).grid(row=1, column=0, padx=4, pady=2, sticky="w")
        self.ent_mobile = ctk.CTkEntry(patient_frame, placeholder_text="Optional Mobile", width=130, height=28, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_mobile.grid(row=1, column=1, padx=(0, 8), pady=2)

        ctk.CTkLabel(patient_frame, text="Ref No:", font=("Arial", 10, "bold"), text_color=TEXT_DARK).grid(row=1, column=2, padx=4, pady=2, sticky="w")
        self.ent_ref = ctk.CTkEntry(patient_frame, placeholder_text="Optional Ref", width=90, height=28, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_ref.grid(row=1, column=3, padx=(0, 8), pady=2)

        # Vertical Divider
        divider = ctk.CTkFrame(self.info_card, width=1, fg_color=BORDER_COLOR)
        divider.pack(side="left", fill="y", padx=5, pady=8)

        # Right Column: Product Search Input & Fast-Add Controls
        search_frame = ctk.CTkFrame(self.info_card, fg_color="transparent")
        search_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(search_frame, text="🔍 Search Product:", font=("Arial", 10, "bold"), text_color=TEXT_DARK).pack(anchor="w")
        
        self.ent_search = ctk.CTkEntry(search_frame, placeholder_text="Type product name...", height=30, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_search.pack(fill="x", pady=(2, 4))

        self.ent_search.bind("<KeyRelease>", self.on_search_key_release)
        self.ent_search.bind("<Down>", self.focus_suggestion_list)
        self.ent_search.bind("<Return>", self.on_search_enter_pressed)

        # Inline Quantity & Discount Panel
        param_panel = ctk.CTkFrame(search_frame, fg_color="transparent")
        param_panel.pack(anchor="w")

        ctk.CTkLabel(param_panel, text="Qty:", font=("Arial", 9, "bold"), text_color=TEXT_DARK).grid(row=0, column=0, padx=(0, 4))
        self.ent_add_qty = ctk.CTkEntry(param_panel, width=50, height=26, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_add_qty.insert(0, "1")
        self.ent_add_qty.grid(row=0, column=1, padx=(0, 8))
        self.ent_add_qty.bind("<Return>", self.move_focus_to_disc)

        ctk.CTkLabel(param_panel, text="Disc %:", font=("Arial", 9, "bold"), text_color=TEXT_DARK).grid(row=0, column=2, padx=(0, 4))
        self.ent_add_disc = ctk.CTkEntry(param_panel, width=55, height=26, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_add_disc.insert(0, "0")
        self.ent_add_disc.grid(row=0, column=3, padx=(0, 8))
        self.ent_add_disc.bind("<Return>", lambda e: self.add_product_to_cart())

        self.btn_fast_add = ctk.CTkButton(param_panel, text="+ Add to Cart", command=self.add_product_to_cart, fg_color=ACCENT_BLUE, height=26, width=90, font=("Arial", 10, "bold"))
        self.btn_fast_add.grid(row=0, column=4)

        # View Container
        self.views_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.views_container.pack(fill="both", expand=True, pady=5)

        self._build_main_views()
        self._build_bottom_bar()

    # -------------------------------------------------------------
    # MAIN VIEWS & KEYBOARD DELETE FUNCTIONALITY
    # -------------------------------------------------------------
    def _build_main_views(self):
        self.pos_view = ctk.CTkFrame(self.views_container, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.pos_view.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#F1F5F9", foreground="#334155", rowheight=32, borderwidth=0)
        style.configure("Treeview", font=("Arial", 10), background="#FFFFFF", foreground="#1E293B", fieldbackground="#FFFFFF", rowheight=28, borderwidth=0)
        style.map("Treeview", background=[('selected', '#EFF6FF')], foreground=[('selected', ACCENT_BLUE)])

        columns = ("no", "product", "quantity", "price", "discount", "total")
        self.pos_table = ttk.Treeview(self.pos_view, columns=columns, show="headings")

        self.pos_table.heading("no", text="#")
        self.pos_table.heading("product", text="Product / Service")
        self.pos_table.heading("quantity", text="Quantity (Click to Edit)")
        self.pos_table.heading("price", text="Price")
        self.pos_table.heading("discount", text="Discount % (Click to Edit)")
        self.pos_table.heading("total", text="Total Price")

        self.pos_table.column("no", width=40, anchor="center")
        self.pos_table.column("product", width=250, anchor="w")
        self.pos_table.column("quantity", width=150, anchor="center")
        self.pos_table.column("price", width=100, anchor="center")
        self.pos_table.column("discount", width=160, anchor="center")
        self.pos_table.column("total", width=120, anchor="center")

        self.pos_table.pack(fill="both", expand=True, padx=10, pady=10)

        # Single Click for inline edit
        self.pos_table.bind("<Button-1>", self.on_cell_single_click)

        # BIND DELETE & BACKSPACE KEYS TO REMOVE PRODUCT
        self.pos_table.bind("<Delete>", self.delete_selected_cart_item)
        self.pos_table.bind("<BackSpace>", self.delete_selected_cart_item)

        # Product Management View (Hidden by default)
        self.prod_mgmt_view = ctk.CTkFrame(self.views_container, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)

        input_panel = ctk.CTkFrame(self.prod_mgmt_view, fg_color="transparent")
        input_panel.pack(fill="x", padx=15, pady=12)

        ctk.CTkLabel(input_panel, text="Product Name:", text_color=TEXT_DARK, font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.ent_prod_name = ctk.CTkEntry(input_panel, width=160, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_prod_name.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(input_panel, text="Price ($):", text_color=TEXT_DARK, font=("Arial", 11, "bold")).grid(row=0, column=2, padx=5, pady=5)
        self.ent_prod_price = ctk.CTkEntry(input_panel, width=90, fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_prod_price.grid(row=0, column=3, padx=5, pady=5)

        self.btn_save_prod = ctk.CTkButton(input_panel, text="Save New", command=self.add_new_product, fg_color=ACCENT_GREEN, width=90, font=("Arial", 11, "bold"))
        self.btn_save_prod.grid(row=0, column=4, padx=5, pady=5)

        self.btn_edit_prod = ctk.CTkButton(input_panel, text="Update Selected", command=self.update_selected_product, fg_color="#F59E0B", width=110, font=("Arial", 11, "bold"))
        self.btn_edit_prod.grid(row=0, column=5, padx=5, pady=5)

        self.btn_del_prod = ctk.CTkButton(input_panel, text="Delete", command=self.delete_selected_product, fg_color="#EF4444", width=80, font=("Arial", 11, "bold"))
        self.btn_del_prod.grid(row=0, column=6, padx=5, pady=5)

        self.btn_close_mgmt = ctk.CTkButton(input_panel, text="Back to Billing", command=self.show_pos_view, fg_color="#64748B", width=100)
        self.btn_close_mgmt.grid(row=0, column=7, padx=5, pady=5)

        prod_cols = ("id", "name", "price")
        self.prod_table = ttk.Treeview(self.prod_mgmt_view, columns=prod_cols, show="headings")
        self.prod_table.heading("id", text="ID")
        self.prod_table.heading("name", text="Product Name")
        self.prod_table.heading("price", text="Price ($)")

        self.prod_table.column("id", width=60, anchor="center")
        self.prod_table.column("name", width=300, anchor="w")
        self.prod_table.column("price", width=120, anchor="center")
        self.prod_table.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        self.prod_table.bind("<<TreeviewSelect>>", self.on_product_select)

    def delete_selected_cart_item(self, event=None):
        selected_item = self.pos_table.selection()
        if not selected_item:
            return

        item_id = selected_item[0]
        item_index = self.pos_table.index(item_id)

        # Remove from local cart list and reindex
        if 0 <= item_index < len(self.cart):
            del self.cart[item_index]
            for idx, item in enumerate(self.cart):
                item['no'] = f"{idx + 1:02d}"

            self.refresh_pos_table_display()

    # -------------------------------------------------------------
    # FLOATING AUTOCOMPLETE SUGGESTION POPUP
    # -------------------------------------------------------------
    def _build_floating_suggestion_popup(self):
        self.popup_frame = tk.Frame(self, bg=BORDER_COLOR, bd=1, relief="solid")
        self.suggestion_listbox = tk.Listbox(
            self.popup_frame, 
            font=("Arial", 10), 
            bg="#FFFFFF", 
            fg="#1E293B", 
            selectbackground=ACCENT_BLUE, 
            selectforeground="white",
            bd=0, 
            highlightthickness=0,
            activestyle="none"
        )
        self.suggestion_listbox.pack(fill="both", expand=True, padx=1, pady=1)

        self.suggestion_listbox.bind("<ButtonRelease-1>", self.on_suggestion_clicked)
        self.suggestion_listbox.bind("<Return>", self.on_suggestion_selected_by_enter)

        self.popup_visible = False

    def show_suggestion_popup(self, items):
        self.suggestion_listbox.delete(0, tk.END)
        for item in items:
            self.suggestion_listbox.insert(tk.END, f"🔍  {item[1]}   —   ${item[2]:,.2f}")

        if not self.popup_visible:
            self.popup_frame.place(relx=0.55, rely=0.15, width=320, height=130)
            self.popup_frame.lift()
            self.popup_visible = True

    def hide_suggestion_popup(self):
        if self.popup_visible:
            self.popup_frame.place_forget()
            self.popup_visible = False

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
                f"The product '{selected_text}' is not available in the list!\n\nPlease add this product first via Products Menu."
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
        cell_entry = tk.Entry(self.pos_table, textvariable=entry_var, bg="#2563EB", fg="white", insertbackground="white")
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
    # BOTTOM BAR & SUMMARY PANEL
    # -------------------------------------------------------------
    def _build_bottom_bar(self):
        self.bottom_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.bottom_frame.pack(fill="x", pady=(8, 0), side="bottom")

        # Print Invoice Button (Left)
        self.btn_print = ctk.CTkButton(self.bottom_frame, text="Generate Invoice", command=self.print_a4_invoice, width=190, height=40, fg_color=ACCENT_BLUE, hover_color=SIDEBAR_HOVER, text_color="white", corner_radius=10, font=("Arial", 12, "bold"))
        self.btn_print.pack(side="left", anchor="s")

        # Right Summary Panel
        self.right_summary = ctk.CTkFrame(self.bottom_frame, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        self.right_summary.pack(side="right", anchor="e", padx=5, pady=2, ipadx=18, ipady=6)

        self.lbl_subtotal = ctk.CTkLabel(self.right_summary, text="Total Amount : $0.00", font=("Arial", 11, "bold"), text_color=TEXT_MUTED)
        self.lbl_subtotal.pack(anchor="e", pady=1)

        self.lbl_discount = ctk.CTkLabel(self.right_summary, text="Discount Amount : $0.00", font=("Arial", 11, "bold"), text_color=TEXT_MUTED)
        self.lbl_discount.pack(anchor="e", pady=1)

        self.line = ctk.CTkFrame(self.right_summary, height=1, width=220, fg_color=BORDER_COLOR)
        self.line.pack(anchor="e", pady=4)

        self.lbl_payable = ctk.CTkLabel(self.right_summary, text="Total Payable : $0.00", font=("Arial", 15, "bold"), text_color=ACCENT_BLUE)
        self.lbl_payable.pack(anchor="e", pady=1)

        self.load_all_products()

    # -------------------------------------------------------------
    # OLD FILE EDITOR, SINGLE-CLICK LOGS & DOUBLE-CLICK OPEN
    # -------------------------------------------------------------
    def show_old_files_history(self):
        self.hist_win = ctk.CTkToplevel(self)
        self.hist_win.title("Old Files / Invoice History Logs")
        self.hist_win.geometry("820x520")
        self.hist_win.configure(fg_color=BG_MAIN)
        self.hist_win.grab_set()

        left_p = ctk.CTkFrame(self.hist_win, width=350, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        left_p.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        right_p = ctk.CTkFrame(self.hist_win, width=420, fg_color=CARD_BG, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
        right_p.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(left_p, text="Select Old Invoice File:", font=("Arial", 12, "bold"), text_color=TEXT_DARK).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(left_p, text="(Single click = view logs | Double click = open in POS)", font=("Arial", 9), text_color=TEXT_MUTED).pack(anchor="w", padx=10, pady=(0, 5))

        cols = ("file_name", "total")
        self.rec_table = ttk.Treeview(left_p, columns=cols, show="headings", height=15)
        self.rec_table.heading("file_name", text="Invoice - Client Name")
        self.rec_table.heading("total", text="Payable ($)")
        self.rec_table.column("file_name", width=220, anchor="w")
        self.rec_table.column("total", width=80, anchor="center")
        self.rec_table.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(right_p, text="Edit Logs & Audit Details", font=("Arial", 14, "bold"), text_color=TEXT_DARK).pack(pady=5)

        self.ent_e_name = ctk.CTkEntry(right_p, placeholder_text="Patient Name", fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_e_name.pack(fill="x", padx=15, pady=4)

        self.ent_e_mobile = ctk.CTkEntry(right_p, placeholder_text="Mobile No", fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_e_mobile.pack(fill="x", padx=15, pady=4)

        self.ent_e_payable = ctk.CTkEntry(right_p, placeholder_text="Payable Balance", fg_color="#F8FAFC", border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.ent_e_payable.pack(fill="x", padx=15, pady=4)

        self.log_box = ctk.CTkTextbox(right_p, height=140, fg_color="#F8FAFC", text_color=TEXT_DARK, border_color=BORDER_COLOR, border_width=1)
        self.log_box.pack(fill="both", expand=True, padx=15, pady=5)

        self.selected_rec = {"id": None, "data": None}

        # Single Click: View Audit Log
        self.rec_table.bind("<ButtonRelease-1>", self.on_old_file_single_click)
        # Double Click: Direct Open to Dashboard
        self.rec_table.bind("<Double-Button-1>", self.on_old_file_double_click)

        btn_save = ctk.CTkButton(right_p, text="Save Edits & Append Log", command=self.save_invoice_edits, fg_color=ACCENT_BLUE)
        btn_save.pack(pady=8)

        self.load_receipts_list()

    def load_receipts_list(self):
        for row in self.rec_table.get_children():
            self.rec_table.delete(row)
        for r in self.db.get_all_receipts():
            file_title = f"#{r[0]:03d} - {r[1]}"
            self.rec_table.insert("", "end", iid=str(r[0]), values=(file_title, f"${r[8]:,.2f}"))

    def on_old_file_single_click(self, event=None):
        sel = self.rec_table.selection()
        if sel:
            rid = int(sel[0])
            data = self.db.get_receipt_by_id(rid)
            if data:
                self.selected_rec["id"] = rid
                self.selected_rec["data"] = data

                self.ent_e_name.delete(0, 'end')
                self.ent_e_name.insert(0, data[1])
                self.ent_e_mobile.delete(0, 'end')
                self.ent_e_mobile.insert(0, data[2] or '')
                self.ent_e_payable.delete(0, 'end')
                self.ent_e_payable.insert(0, str(data[8]))

                self.log_box.delete("1.0", "end")
                logs = self.db.get_receipt_history(rid)
                self.log_box.insert("end", f"=== Audit History for Invoice #{rid:03d} ===\n")
                if logs:
                    for l in logs:
                        self.log_box.insert("end", f"[{l[3]}] Edited {l[0]}: '{l[1]}' -> '{l[2]}'\n")
                else:
                    self.log_box.insert("end", "No previous edits logged for this file.\n")

    def on_old_file_double_click(self, event=None):
        sel = self.rec_table.selection()
        if sel:
            rid = int(sel[0])
            data = self.db.get_receipt_by_id(rid)
            if data:
                self.ent_name.delete(0, tk.END)
                self.ent_name.insert(0, data[1])

                self.ent_mobile.delete(0, tk.END)
                self.ent_mobile.insert(0, data[2] or '')

                self.ent_ref.delete(0, tk.END)
                self.ent_ref.insert(0, data[3] or '')

                self.ent_id.delete(0, tk.END)
                self.ent_id.insert(0, data[4] or '')

                self.hist_win.destroy()
                self.show_pos_view()
                messagebox.showinfo("File Opened", f"Opened Old Invoice #{rid:03d} - {data[1]} directly on POS Dashboard!")

    def save_invoice_edits(self):
        rid = self.selected_rec["id"]
        old = self.selected_rec["data"]
        if not rid or not old:
            messagebox.showerror("Error", "Select an invoice file first.")
            return

        new_name = self.ent_e_name.get().strip()
        new_mobile = self.ent_e_mobile.get().strip()
        new_payable = float(self.ent_e_payable.get().strip() or 0.0)

        if new_name != old[1]:
            self.db.log_edit(rid, "patient_name", old[1], new_name)
        if new_mobile != old[2]:
            self.db.log_edit(rid, "mobile", old[2], new_mobile)
        if new_payable != old[8]:
            self.db.log_edit(rid, "payable_balance", old[8], new_payable)

        self.db.update_receipt(rid, new_name, new_mobile, old[3], old[4], old[6], old[7], new_payable)
        messagebox.showinfo("Saved", "Invoice updated and edit history logged!")
        self.load_receipts_list()

    # -------------------------------------------------------------
    # VIEWS SWITCHING & UTILITIES
    # -------------------------------------------------------------
    def load_all_products(self):
        self.all_products = self.db.get_all_products()

    def show_product_management_view(self):
        self.lbl_main_title.configure(text="Products Catalog")
        self.pos_view.pack_forget()
        self.prod_mgmt_view.pack(fill="both", expand=True)
        self.refresh_product_management_table()

    def show_pos_view(self):
        self.lbl_main_title.configure(text=self.app_name)
        self.prod_mgmt_view.pack_forget()
        self.pos_view.pack(fill="both", expand=True)
        self.load_all_products()

    def update_application_name(self):
        dialog = ctk.CTkInputDialog(text="Enter new Application Name:", title="Rename App")
        new_name = dialog.get_input()
        
        if new_name and new_name.strip():
            self.app_name = new_name.strip()
            self.title(self.app_name)
            self.lbl_main_title.configure(text=self.app_name)
            messagebox.showinfo("Success", f"Application name updated to:\n'{self.app_name}'")

    def change_logo(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if path:
            self.logo_path = path
            img = Image.open(path)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(40, 40))
            self.logo_box.configure(image=ctk_img, text="")

    # -------------------------------------------------------------
    # PRODUCT CATALOG MANAGEMENT
    # -------------------------------------------------------------
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
    # COMPUTATIONS & AUTO-PRINTING WITH LOGO
    # -------------------------------------------------------------
    def recalculate_totals(self):
        subtotal = sum(i['price'] * i['qty'] for i in self.cart)
        total_discount_amt = sum(i['discount_amount'] for i in self.cart)
        payable = subtotal - total_discount_amt

        self.lbl_subtotal.configure(text=f"Total Amount : ${subtotal:,.2f}")
        self.lbl_discount.configure(text=f"Discount Amount : ${total_discount_amt:,.2f}")
        self.lbl_payable.configure(text=f"Total Payable : ${payable:,.2f}")

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
                .header {{ border-bottom: 2px solid #2563EB; padding-bottom: 12px; margin-bottom: 15px; overflow: hidden; }}
                .header-text {{ text-align: center; }}
                .header h1 {{ margin: 0; font-size: 22px; color: #2563EB; text-transform: uppercase; }}
                .header p {{ margin: 3px 0 0; font-size: 12px; color: #555; }}
                .info-card {{ width: 100%; border: 1px solid #ddd; border-radius: 6px; padding: 10px 12px; margin-bottom: 15px; font-size: 13px; }}
                .info-table {{ width: 100%; border-collapse: collapse; }}
                .info-table td {{ padding: 4px 0; vertical-align: top; }}
                .items-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }}
                .items-table th {{ background-color: #2563EB; color: white; padding: 8px 6px; font-weight: bold; border: 1px solid #2563EB; }}
                .items-table td {{ border: 1px solid #ccc; padding: 7px 6px; }}
                .summary-wrapper {{ width: 100%; margin-top: 20px; display: table; }}
                .totals-box {{ display: table-cell; text-align: right; float: right; width: 50%; font-size: 13px; line-height: 1.8; }}
                .totals-row {{ display: flex; justify-content: space-between; padding: 2px 0; }}
                .payable-row {{ font-size: 16px; font-weight: bold; color: #2563EB; margin-top: 6px; border-top: 2px solid #2563EB; padding-top: 6px; display: flex; justify-content: space-between; }}
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