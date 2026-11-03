import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import services
import reports

class CampusHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CampusHub: Resource Borrowing and Inventory Management")
        self.root.geometry("900x600")
        

        # Setup Tabbed Interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.tab_inventory = ttk.Frame(self.notebook)
        self.tab_borrowers = ttk.Frame(self.notebook)
        self.tab_checkout = ttk.Frame(self.notebook)
        self.tab_monitoring = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_inventory, text="Inventory")
        self.notebook.add(self.tab_borrowers, text="Borrowers")
        self.notebook.add(self.tab_checkout, text="Checkout")
        self.notebook.add(self.tab_monitoring, text="Monitoring & Returns")

        self.setup_inventory_tab()
        self.setup_borrowers_tab()
        self.setup_checkout_tab()
        self.setup_monitoring_tab()
        
        #-- Custom Report --#
    def run_custom_report(self):
        selection = self.combo_report.get()
        columns, data = reports.generate_custom_report(selection)
        
        # Open a new window to display the generated report
        report_win = tk.Toplevel(self.root)
        report_win.title(f"Report: {selection}")
        report_win.geometry("500x300")
        
        tree = ttk.Treeview(report_win, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Populate the table handling both sqlite3.Row objects and dictionaries (from the default case)
        for row in data:
            if isinstance(row, dict):
                tree.insert("", tk.END, values=list(row.values()))
            else:
                tree.insert("", tk.END, values=tuple(row))


    #--inventory tab--#
    def setup_inventory_tab(self):
        # Header
        title = tk.Label(self.tab_inventory, text="Asset Inventory", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Tabular Data Display (Treeview)
        columns = ("Code", "Name", "Category", "Condition", "Status")
        self.tree = ttk.Treeview(self.tab_inventory, columns=columns, show="headings")
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        self.tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Action Buttons
        btn_frame = tk.Frame(self.tab_inventory)
        btn_frame.pack(pady=10)

        add_btn = tk.Button(btn_frame, text="Add New Asset", width=15, command=self.show_add_asset_dialog)
        add_btn.pack(side=tk.LEFT, padx=10)
        
        refresh_btn = tk.Button(btn_frame, text="Refresh List", width=15)
        refresh_btn.pack(side=tk.LEFT, padx=10)
        
        export_btn = tk.Button(btn_frame, text="Export CSV", width=15, command=self.export_inventory)
        export_btn.pack(side=tk.LEFT, padx=10)
        
        self.load_inventory_data()
        
    def load_inventory_data(self):
        """Fetches data from the database and updates the Treeview."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        records = services.get_all_assets()
        for row in records:
            self.tree.insert("", tk.END, values=(row['asset_code'], row['name'], row['category'], row['condition'], row['status']))



    def show_add_asset_dialog(self):
        """Opens a Toplevel form to capture new asset details."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Asset")
        dialog.geometry("350x300")
        dialog.grab_set()  # Focuses the dialog window

        # Form Inputs
        tk.Label(dialog, text="Asset Code:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        entry_code = tk.Entry(dialog)
        entry_code.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        entry_name = tk.Entry(dialog)
        entry_name.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Category:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        entry_category = tk.Entry(dialog)
        entry_category.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Location:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        entry_location = tk.Entry(dialog)
        entry_location.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Condition:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        entry_condition = ttk.Combobox(dialog, values=["New", "Good", "Fair", "Poor"], state="readonly")
        entry_condition.grid(row=4, column=1, padx=10, pady=5)
        entry_condition.current(0)

        def save_asset():
            code = entry_code.get().strip()
            name = entry_name.get().strip()
            category = entry_category.get().strip()
            location = entry_location.get().strip()
            condition = entry_condition.get()

            success, message = services.add_new_asset(code, name, category, location, condition)
            
            if success:
                messagebox.showinfo("Success", message, parent=dialog)
                self.load_inventory_data()  # Refresh the table immediately
                dialog.destroy()
            else:
                messagebox.showerror("Validation Error", message, parent=dialog)

        tk.Button(dialog, text="Save Asset", command=save_asset).grid(row=5, column=0, columnspan=2, pady=20)
        
        
        
        #--Borrower Tab --#             
    def setup_borrowers_tab(self):
        # Header
        title = tk.Label(self.tab_borrowers, text="Borrower Management", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Tabular Data Display
        columns = ("Code", "Name", "Dept/Program", "Active Status")
        self.borrower_tree = ttk.Treeview(self.tab_borrowers, columns=columns, show="headings")
        for col in columns:
            self.borrower_tree.heading(col, text=col)
            self.borrower_tree.column(col, width=150)
        self.borrower_tree.pack(fill='both', expand=True, padx=20, pady=10)

        # Action Buttons
        btn_frame = tk.Frame(self.tab_borrowers)
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Add Borrower", width=15, command=self.show_add_borrower_dialog).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Refresh List", width=15, command=self.load_borrower_data).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Toggle Status", width=15, command=self.toggle_borrower).pack(side=tk.LEFT, padx=10)
        
        self.load_borrower_data()

    def load_borrower_data(self):
        for item in self.borrower_tree.get_children():
            self.borrower_tree.delete(item)
        for row in services.get_all_borrowers():
            status = "Yes" if row['active'] else "No"
            self.borrower_tree.insert("", tk.END, values=(row['borrower_code'], row['display_name'], row['department_or_program'], status))

    def show_add_borrower_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Borrower")
        dialog.geometry("350x250")
        dialog.grab_set()

        tk.Label(dialog, text="Borrower Code:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        entry_code = tk.Entry(dialog)
        entry_code.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Display Name:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        entry_name = tk.Entry(dialog)
        entry_name.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(dialog, text="Dept/Program:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        entry_dept = tk.Entry(dialog)
        entry_dept.grid(row=2, column=1, padx=10, pady=5)

        def save_borrower():
            success, msg = services.add_new_borrower(entry_code.get().strip(), entry_name.get().strip(), entry_dept.get().strip())
            if success:
                messagebox.showinfo("Success", msg, parent=dialog)
                self.load_borrower_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", msg, parent=dialog)

        tk.Button(dialog, text="Save", command=save_borrower).grid(row=3, column=0, columnspan=2, pady=20)

    def toggle_borrower(self):
        """Changes the active status of the selected borrower."""
        selected = self.borrower_tree.focus()
        if not selected:
            messagebox.showerror("Selection Error", "Please select a borrower from the list first.")
            return
            
        # Get the data from the selected row
        values = self.borrower_tree.item(selected, 'values')
        borrower_code = values[0]
        current_status_str = values[3] # "Yes" or "No"
        
        # Convert "Yes"/"No" back to 1 or 0
        current_status_int = 1 if current_status_str == "Yes" else 0
        
        success, msg = services.toggle_borrower_status(borrower_code, current_status_int)
        
        if success:
            messagebox.showinfo("Status Updated", msg)
            self.load_borrower_data() # Refresh the borrower table
            
            # If you are on the Checkout tab, this ensures the dropdown updates too
            if hasattr(self, 'refresh_checkout_dropdowns'):
                self.refresh_checkout_dropdowns() 
        else:
            messagebox.showerror("Update Failed", msg)


        #--checkout tab--#
    def setup_checkout_tab(self):
        title = tk.Label(self.tab_checkout, text="Checkout Asset", font=("Arial", 16, "bold"))
        title.pack(pady=20)

        form_frame = tk.Frame(self.tab_checkout)
        form_frame.pack(pady=10)

        # Asset Selection
        tk.Label(form_frame, text="Select Asset:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.combo_asset = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_asset.grid(row=0, column=1, padx=10, pady=10)

        # Borrower Selection
        tk.Label(form_frame, text="Select Borrower:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.combo_borrower = ttk.Combobox(form_frame, state="readonly", width=30)
        self.combo_borrower.grid(row=1, column=1, padx=10, pady=10)

        from datetime import datetime
        today_str = datetime.today().strftime('%Y-%m-%d')

        tk.Label(form_frame, text="Borrow Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=10, sticky='e')
        self.entry_borrow_date = tk.Entry(form_frame, width=33)
        self.entry_borrow_date.insert(0, today_str)
        self.entry_borrow_date.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, padx=10, pady=10, sticky='e')
        self.entry_due_date = tk.Entry(form_frame, width=33)
        self.entry_due_date.grid(row=3, column=1, padx=10, pady=10)

        # Buttons
        btn_frame = tk.Frame(self.tab_checkout)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Refresh Lists", command=self.refresh_checkout_dropdowns).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Process Checkout", command=self.process_checkout).pack(side=tk.LEFT, padx=10)
        
        self.refresh_checkout_dropdowns()


    def refresh_checkout_dropdowns(self):
        assets = services.get_available_assets()
        self.combo_asset['values'] = [f"{a['asset_code']} - {a['name']}" for a in assets]
        if assets: self.combo_asset.current(0)
        else: self.combo_asset.set('')

        borrowers = services.get_active_borrowers()
        self.combo_borrower['values'] = [f"{b['borrower_code']} - {b['display_name']}" for b in borrowers]
        if borrowers: self.combo_borrower.current(0)
        else: self.combo_borrower.set('')


    def process_checkout(self):
        asset_val = self.combo_asset.get()
        borrower_val = self.combo_borrower.get()
        
        if not asset_val or not borrower_val:
            messagebox.showerror("Error", "Please select both an asset and a borrower.")
            return
            
        asset_code = asset_val.split(" - ")[0]
        borrower_code = borrower_val.split(" - ")[0]
        
        success, msg = services.checkout_asset(
            asset_code, 
            borrower_code, 
            self.entry_borrow_date.get(), 
            self.entry_due_date.get()
        )
        
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_checkout_dropdowns()
            self.load_inventory_data() # Update inventory tab to show 'Borrowed' status
        else:
            messagebox.showerror("Checkout Failed", msg)
            

                
        #-- reports tab--#
    def setup_monitoring_tab(self):
        title = tk.Label(self.tab_monitoring, text="Monitoring & Returns", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Asset Search Section
        search_frame = tk.Frame(self.tab_monitoring)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search Assets:").pack(side=tk.LEFT)
        self.entry_search = tk.Entry(search_frame, width=30)
        self.entry_search.pack(side=tk.LEFT, padx=10)
        tk.Button(search_frame, text="Search", command=self.execute_search).pack(side=tk.LEFT)

        # Active Loans Display
        tk.Label(self.tab_monitoring, text="Active & Overdue Loans (Select to Return)", font=("Arial", 12, "bold")).pack(pady=10)
        
        columns = ("Loan ID", "Asset Code", "Asset Name", "Borrower", "Due Date", "Status")
        self.loan_tree = ttk.Treeview(self.tab_monitoring, columns=columns, show="headings")
        for col in columns:
            self.loan_tree.heading(col, text=col)
            self.loan_tree.column(col, width=120)
        self.loan_tree.pack(fill='both', expand=True, padx=20, pady=5)

        # Return Controls
        return_frame = tk.Frame(self.tab_monitoring)
        return_frame.pack(pady=10)
        
        from datetime import datetime
        today_str = datetime.today().strftime('%Y-%m-%d')
        
        tk.Label(return_frame, text="Return Date:").pack(side=tk.LEFT, padx=5)
        self.entry_return_date = tk.Entry(return_frame, width=15)
        self.entry_return_date.insert(0, today_str)
        self.entry_return_date.pack(side=tk.LEFT, padx=5)
        
        tk.Button(return_frame, text="Process Return", command=self.process_return).pack(side=tk.LEFT, padx=15)
        tk.Button(return_frame, text="Refresh Loans", command=self.load_loan_data).pack(side=tk.LEFT)

        self.load_loan_data()
        
        #Custom/Specific Report
        report_frame = tk.Frame(self.tab_monitoring)
        report_frame.pack(pady=20)
        
        tk.Label(report_frame, text="Generate Custom Report:").pack(side=tk.LEFT, padx=5)
        
        self.combo_report = ttk.Combobox(report_frame, state="readonly", width=25)
        self.combo_report['values'] = ["All Assets", "Available Assets Only", "Active Borrowers", "Invalid Option (Test Default)"]
        self.combo_report.current(0)
        self.combo_report.pack(side=tk.LEFT, padx=5)
        
        tk.Button(report_frame, text="Run Report", command=self.run_custom_report).pack(side=tk.LEFT, padx=5)



    def execute_search(self):
        term = self.entry_search.get().strip()
        results = reports.search_assets(term)
        
        # Display results in a new popup or temporary messagebox for monitoring
        result_text = "\n".join([f"{r['asset_code']} - {r['name']} ({r['status']})" for r in results])
        if not result_text: result_text = "No assets found."
        messagebox.showinfo("Search Results", result_text)



    def load_loan_data(self):
        for item in self.loan_tree.get_children():
            self.loan_tree.delete(item)
            
        loans = reports.get_active_and_overdue_loans()
        for loan in loans:
            self.loan_tree.insert("", tk.END, values=(
                loan['loan_id'], loan['asset_code'], loan['asset_name'], 
                loan['borrower'], loan['due_on'], loan['status']
            ))



    def process_return(self):
        selected = self.loan_tree.focus()
        if not selected:
            messagebox.showerror("Error", "Please select a loan from the table to return.")
            return
            
        values = self.loan_tree.item(selected, 'values')
        loan_id = values[0]
        return_date = self.entry_return_date.get()
        
        success, msg = services.return_asset(loan_id, return_date)
        if success:
            messagebox.showinfo("Success", msg)
            self.load_loan_data()
            self.load_inventory_data() # Refresh main inventory tab
        else:
            messagebox.showerror("Return Failed", msg)
            
            
            #--export csv file--#
    def export_inventory(self):
        """Opens a save dialog and triggers the CSV export."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Inventory Report",
            initialfile="inventory_report.csv"
        )
        
        # Check if the user cancelled the dialog
        if not filepath:
            return 
            
        success, msg = reports.export_inventory_to_csv(filepath)
        if success:
            messagebox.showinfo("Export Successful", f"{msg}\nSaved to: {filepath}")
        else:
            messagebox.showerror("Export Failed", msg)