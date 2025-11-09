"""
Food Ordering App - Full (Menu, Cart, Orders, Admin)
- Single-file runnable app
- SQLite DB (projects.db) created in same folder
- Light theme GUI, improved layout, and admin controls
"""

import sqlite3
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

DB_FILE = 'projects.db'

# --------------------------
# Database helpers
# --------------------------

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.execute('PRAGMA foreign_keys = ON;')
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Create tables (ensure customer simplified schema)
    cur.executescript(r"""
    CREATE TABLE IF NOT EXISTS customer (
        custid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT
    );

    CREATE TABLE IF NOT EXISTS cuisine(
        cuisineid INTEGER PRIMARY KEY,
        cuisinename TEXT
    );

    CREATE TABLE IF NOT EXISTS employee(
        empid INTEGER PRIMARY KEY,
        fname TEXT,
        lname TEXT,
        dob TEXT,
        emailid TEXT,
        pwd TEXT,
        address TEXT,
        phoneno TEXT,
        gender TEXT,
        salary INTEGER
    );

    CREATE TABLE IF NOT EXISTS chef(
        chefid INTEGER PRIMARY KEY,
        chefname TEXT,
        address TEXT,
        street TEXT,
        phoneno TEXT,
        cuisineid INTEGER,
        empid INTEGER,
        emailid TEXT,
        pwd TEXT,
        salary INTEGER,
        FOREIGN KEY(cuisineid) REFERENCES cuisine(cuisineid) ON DELETE CASCADE,
        FOREIGN KEY(empid) REFERENCES employee(empid) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS ingredient(
        ingid INTEGER PRIMARY KEY,
        ingname TEXT
    );

    CREATE TABLE IF NOT EXISTS food(
        foodid INTEGER PRIMARY KEY,
        foodname TEXT,
        price INTEGER,
        quantity INTEGER,
        foodavail TEXT,
        cuisineid INTEGER,
        ingid INTEGER,
        chefid INTEGER,
        FOREIGN KEY(cuisineid) REFERENCES cuisine(cuisineid) ON DELETE CASCADE,
        FOREIGN KEY(ingid) REFERENCES ingredient(ingid) ON DELETE CASCADE,
        FOREIGN KEY(chefid) REFERENCES chef(chefid) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS drink(
        drinkid INTEGER PRIMARY KEY,
        drinkname TEXT,
        price INTEGER,
        quantity TEXT,
        drinkavail TEXT
    );

    CREATE TABLE IF NOT EXISTS delivery(
        delid INTEGER PRIMARY KEY,
        delname TEXT,
        vehicleno TEXT,
        delcharge INTEGER,
        deldate TEXT,
        deltime TEXT,
        custid INTEGER,
        empid INTEGER,
        FOREIGN KEY(custid) REFERENCES customer(custid) ON DELETE CASCADE,
        FOREIGN KEY(empid) REFERENCES employee(empid) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS orders(
        ordid INTEGER PRIMARY KEY AUTOINCREMENT,
        totalcost INTEGER,
        foodid INTEGER,
        drinkid INTEGER,
        delid INTEGER,
        FOREIGN KEY(foodid) REFERENCES food(foodid) ON DELETE CASCADE,
        FOREIGN KEY(drinkid) REFERENCES drink(drinkid) ON DELETE CASCADE,
        FOREIGN KEY(delid) REFERENCES delivery(delid) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS payment(
        payid INTEGER PRIMARY KEY AUTOINCREMENT,
        paymethod TEXT,
        custid INTEGER,
        ordid INTEGER,
        FOREIGN KEY(custid) REFERENCES customer(custid) ON DELETE CASCADE,
        FOREIGN KEY(ordid) REFERENCES orders(ordid) ON DELETE CASCADE
    );
    """)
    conn.commit()

    # helper to check if table empty
    def empty(table):
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        return cur.fetchone()[0] == 0

    # populate sample data only if empty, and match schema
    if empty('cuisine'):
        cur.executemany('INSERT INTO cuisine VALUES (?,?)', [(1,'Italian'),(2,'Chinese'),(3,'Mexican'),(4,'Indian'),(5,'Japanese')])

    if empty('employee'):
        employees = [
            (1, 'Michael', 'Johnson', '1990-05-15', 'mike@email.com', 'emp_pass1', '789 Oak St', '5558765', 'Male', 50000),
            (2, 'Emily', 'Wilson', '1985-02-20', 'emily@email.com', 'emp_pass2', '567 Pine St', '5554321', 'Female', 45000),
            (3, 'David', 'Lee', '1988-09-10', 'david@email.com', 'emp_pass3', '654 Elm St', '5557890', 'Male', 48000),
            (4, 'Anna', 'Garcia', '1993-03-25', 'anna@email.com', 'emp_pass4', '789 Oak St', '5551234', 'Female', 52000),
            (5, 'Robert', 'Brown', '1987-12-12', 'robert@email.com', 'emp_pass5', '101 Oak St', '5553456', 'Male', 55000)
        ]
        cur.executemany('INSERT INTO employee VALUES (?,?,?,?,?,?,?,?,?,?)', employees)

    if empty('chef'):
        chefs = [
            (1, 'Chef Mario', '123 Chef Way', 'Apt 2C', '555-9876', 1, 1, 'mario@email.com', 'chef_pass1', 55000),
            (2, 'Chef Lily', '456 Chef Lane', 'Unit 5D', '555-2345', 2, 2, 'lily@email.com', 'chef_pass2', 52000),
            (3, 'Chef Carlos', '789 Chef St', 'Suite 1B', '555-7890', 3, 3, 'carlos@email.com', 'chef_pass3', 53000),
            (4, 'Chef Priya', '101 Chef Rd', 'Apt 3A', '555-4321', 4, 4, 'priya@email.com', 'chef_pass4', 51000),
            (5, 'Chef Kenji', '456 Chef Ave', 'Unit 4C', '555-3456', 5, 5, 'kenji@email.com', 'chef_pass5', 54000)
        ]
        cur.executemany('INSERT INTO chef VALUES (?,?,?,?,?,?,?,?,?,?)', chefs)

    if empty('ingredient'):
        cur.executemany('INSERT INTO ingredient VALUES (?,?)', [(1,'Tomato'),(2,'Chicken'),(3,'Beef'),(4,'Rice'),(5,'Noodles')])

    if empty('food'):
        foods = [
            (1, 'Margherita Pizza', 12, 20, 'Available', 1, 1, 1),
            (2, 'Kung Pao Chicken', 15, 15, 'Available', 2, 2, 2),
            (3, 'Taco', 10, 30, 'Available', 3, 3, 3),
            (4, 'Chicken Biryani', 14, 25, 'Available', 4, 4, 4),
            (5, 'Sushi Rolls', 18, 20, 'Available', 5, 5, 5)
        ]
        cur.executemany('INSERT INTO food VALUES (?,?,?,?,?,?,?,?)', foods)

    if empty('drink'):
        drinks = [
            (1, 'Coca-Cola', 2, 'In Stock', 'Available'),
            (2, 'Sprite', 2, 'In Stock', 'Available'),
            (3, 'Lemonade', 2, 'In Stock', 'Available'),
            (4, 'Iced Tea', 2, 'In Stock', 'Available'),
            (5, 'Orange Juice', 3, 'In Stock', 'Available')
        ]
        cur.executemany('INSERT INTO drink VALUES (?,?,?,?,?)', drinks)

    if empty('delivery'):
        deliveries = [
            (1, 'Fast Delivery', 'DEL123', 5, '2023-10-13', '12:00 PM', None, None),
            (2, 'Express Delivery', 'DEL456', 7, '2023-10-14', '2:30 PM', None, None),
            (3, 'Standard Delivery', 'DEL789', 6, '2023-10-15', '3:45 PM', None, None),
            (4, 'Late Night Delivery', 'DEL987', 8, '2023-10-16', '9:00 PM', None, None),
            (5, 'Weekend Delivery', 'DEL654', 7, '2023-10-17', '10:30 AM', None, None)
        ]
        cur.executemany('INSERT INTO delivery VALUES (?,?,?,?,?,?,?,?)', deliveries)

    # Ensure customer sample rows match new schema (name, phone, address)
    if empty('customer'):
        sample_customers = [
            ('John Doe', '5551234', '123 Main St'),
            ('Alice Smith', '5555678', '456 Elm St'),
            ('Bob Johnson', '5559876', '789 Oak St'),
            ('Sarah Williams', '5554321', '567 Pine St'),
            ('Mike Brown', '5558765', '101 Oak St')
        ]
        cur.executemany('INSERT INTO customer (name,phone,address) VALUES (?,?,?)', sample_customers)

    conn.commit()
    conn.close()

# --------------------------
# GUI Application
# --------------------------

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Food Ordering App')
        self.root.geometry('1024x700')
        self.cart = []  # (type, id, name, price, qty)

        self.setup_style()
        self.create_widgets()
        self.load_menu()

    def setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        # Light theme basics
        style.configure('TFrame', background='#f7f7f7')
        style.configure('TLabel', background='#f7f7f7', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), background='#f7f7f7')
        style.configure('TButton', padding=6)
        style.configure('Treeview', rowheight=28, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.tab_menu = ttk.Frame(self.notebook, padding=6)
        self.tab_cart = ttk.Frame(self.notebook, padding=6)
        self.tab_admin = ttk.Frame(self.notebook, padding=6)

        self.notebook.add(self.tab_menu, text='Menu')
        self.notebook.add(self.tab_cart, text='Cart')
        self.notebook.add(self.tab_admin, text='Admin')
        self.notebook.pack(expand=1, fill='both')

        self.build_menu_tab()
        self.build_cart_tab()
        self.build_admin_tab()

    # Menu tab
    def build_menu_tab(self):
        f = self.tab_menu
        left = ttk.Frame(f)
        right = ttk.Frame(f)
        left.pack(side='left', fill='both', expand=True, padx=6, pady=6)
        right.pack(side='right', fill='both', expand=True, padx=6, pady=6)

        ttk.Label(left, text='Foods', style='Header.TLabel').pack(anchor='w', pady=(0,6))
        self.food_tree = ttk.Treeview(left, columns=('name','price','qty','avail'), show='headings', height=18)
        for col,width in (('name',300),('price',90),('qty',90),('avail',140)):
            self.food_tree.heading(col, text=col.capitalize())
            self.food_tree.column(col, width=width, anchor='center' if col!='name' else 'w')
        self.food_tree.pack(fill='both', expand=True)

        ttk.Label(right, text='Drinks', style='Header.TLabel').pack(anchor='w', pady=(0,6))
        self.drink_tree = ttk.Treeview(right, columns=('name','price','qty','avail'), show='headings', height=18)
        for col,width in (('name',300),('price',90),('qty',90),('avail',140)):
            self.drink_tree.heading(col, text=col.capitalize())
            self.drink_tree.column(col, width=width, anchor='center' if col!='name' else 'w')
        self.drink_tree.pack(fill='both', expand=True)

        # alternate coloring tags
        for tv in (self.food_tree, self.drink_tree):
            tv.tag_configure('odd', background='#ffffff')
            tv.tag_configure('even', background='#f2f2f2')

        ctrl = ttk.Frame(f)
        ctrl.pack(fill='x', pady=(8,0))
        ttk.Button(ctrl, text='Refresh Menu', command=self.load_menu).pack(side='left', padx=6)
        ttk.Label(ctrl, text='Tip: double-click an item to add to cart', font=('Segoe UI', 9, 'italic')).pack(side='left', padx=12)

        self.food_tree.bind('<Double-1>', self.on_food_add)
        self.drink_tree.bind('<Double-1>', self.on_drink_add)

    def load_menu(self):
        # clear
        for tv in (self.food_tree, self.drink_tree):
            for r in tv.get_children():
                tv.delete(r)

        conn = get_conn()
        cur = conn.cursor()

        cur.execute('SELECT foodid, foodname, price, quantity, foodavail FROM food')
        for i, (fid, name, price, qty, avail) in enumerate(cur.fetchall(), start=1):
            tag = 'even' if i%2==0 else 'odd'
            self.food_tree.insert('', 'end', iid=f'food_{fid}', values=(name, f"{price}", qty, avail), tags=(tag,))

        cur.execute('SELECT drinkid, drinkname, price, quantity, drinkavail FROM drink')
        for i, (did, name, price, qty, avail) in enumerate(cur.fetchall(), start=1):
            tag = 'even' if i%2==0 else 'odd'
            self.drink_tree.insert('', 'end', iid=f'drink_{did}', values=(name, f"{price}", qty, avail), tags=(tag,))

        conn.close()

    def on_food_add(self, event):
        iid = self.food_tree.focus()
        if not iid:
            return
        try:
            fid = int(iid.split('_')[1])
        except Exception:
            fid = None
        vals = self.food_tree.item(iid, 'values')
        if not vals:
            return
        name, price, qty_avail, avail = vals
        try:
            max_q = int(qty_avail)
        except Exception:
            max_q = 50
        q = simpledialog.askinteger('Quantity', f'Quantity for {name} (available {qty_avail})', minvalue=1, maxvalue=max_q)
        if q:
            self.cart.append(('food', fid, name, float(price), int(q)))
            messagebox.showinfo('Added', f'Added {q} x {name} to cart')
            self.update_cart_view()

    def on_drink_add(self, event):
        iid = self.drink_tree.focus()
        if not iid:
            return
        try:
            did = int(iid.split('_')[1])
        except Exception:
            did = None
        vals = self.drink_tree.item(iid, 'values')
        if not vals:
            return
        name, price, qty_avail, avail = vals
        q = simpledialog.askinteger('Quantity', f'Quantity for {name}', minvalue=1, maxvalue=20)
        if q:
            self.cart.append(('drink', did, name, float(price), int(q)))
            messagebox.showinfo('Added', f'Added {q} x {name} to cart')
            self.update_cart_view()

    # ------------------ Cart Tab ------------------
    def build_cart_tab(self):
        f = self.tab_cart
        ttk.Label(f, text='Cart', style='Header.TLabel').pack(anchor='w', pady=(4,6))
        cols = ('Type','Name','Unit Price','Qty','Subtotal')
        self.cart_tree = ttk.Treeview(f, columns=cols, show='headings', height=14)
        for c in cols:
            self.cart_tree.heading(c, text=c)
            self.cart_tree.column(c, anchor='center')
        self.cart_tree.pack(fill='both', expand=True, padx=6, pady=6)
        self.cart_tree.tag_configure('odd', background='#ffffff')
        self.cart_tree.tag_configure('even', background='#f2f2f2')

        ctrl = ttk.Frame(f)
        ctrl.pack(fill='x', padx=6, pady=(0,8))
        ttk.Button(ctrl, text='Remove Selected', command=self.remove_selected_cart).pack(side='left', padx=6)
        ttk.Button(ctrl, text='Clear Cart', command=self.clear_cart).pack(side='left', padx=6)
        ttk.Button(ctrl, text='Place Order', command=self.place_order_flow).pack(side='right', padx=6)

        self.total_var = tk.StringVar(value='Total: Rs 0')
        ttk.Label(f, textvariable=self.total_var, font=('Segoe UI', 11, 'bold')).pack(anchor='e', padx=6)

        self.update_cart_view()

    def update_cart_view(self):
        for r in self.cart_tree.get_children():
            self.cart_tree.delete(r)
        total = 0
        for idx, item in enumerate(self.cart, start=1):
            if len(item) != 5:
                continue
            typ, _id, name, price, qty = item
            subtotal = price * qty
            total += subtotal
            tag = 'even' if idx%2==0 else 'odd'
            self.cart_tree.insert('', 'end', iid=str(idx), values=(typ.capitalize(), name, f"{price}", qty, f"{subtotal}"), tags=(tag,))
        self.total_var.set(f'Total: Rs {total}')

    def remove_selected_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        try:
            idx = int(sel[0]) - 1
        except Exception:
            messagebox.showwarning('Remove', 'Could not determine selected item.')
            return
        if 0 <= idx < len(self.cart):
            removed = self.cart.pop(idx)
            messagebox.showinfo('Removed', f'Removed {removed[2]} from cart')
            self.update_cart_view()

    def clear_cart(self):
        self.cart = []
        self.update_cart_view()

    # ------------------ Checkout / Orders ------------------
    def place_order_flow(self):
        if not self.cart:
            messagebox.showwarning('Empty', 'Cart is empty')
            return

        conn = get_conn()
        cur = conn.cursor()

        # Ask for customer id or create new
        custid = simpledialog.askinteger('Customer ID', 'Enter customer ID (leave blank to create new):', minvalue=1)
        if not custid:
            create = messagebox.askyesno('New customer', 'Create a new customer now?')
            if not create:
                conn.close()
                return
            fname = simpledialog.askstring('First name', 'First name:')
            lname = simpledialog.askstring('Last name', 'Last name:')
            phone = simpledialog.askstring('Phone', 'Phone:')
            address = simpledialog.askstring('Address', 'Address:')
            if not (fname and lname and phone and address):
                messagebox.showerror('Error', 'All fields required to create customer.')
                conn.close()
                return
            full_name = f"{fname} {lname}"
            cur.execute('INSERT INTO customer (name, phone, address) VALUES (?,?,?)', (full_name, phone, address))
            conn.commit()
            custid = cur.lastrowid
            messagebox.showinfo('Customer Created', f'New customer ID: {custid}')
        else:
            cur.execute('SELECT COUNT(*) FROM customer WHERE custid=?', (custid,))
            if cur.fetchone()[0] == 0:
                messagebox.showerror('Not found', 'Customer ID not found.')
                conn.close()
                return

        # Delivery selection (optional)
        cur.execute('SELECT delid, delname, delcharge FROM delivery')
        deliveries = cur.fetchall()
        delid = None
        if deliveries:
            options = [f'{d[0]}: {d[1]} (Rs {d[2]})' for d in deliveries]
            choice = simpledialog.askinteger('Delivery', 'Choose delivery id:\n' + '\n'.join(options), minvalue=1)
            if choice is None:
                conn.close()
                return
            delid = choice

        # Compute total
        total_cost = sum(item[3] * item[4] for item in self.cart)

        # For simplified orders table, store first food/drink ids if present
        first_food = next((it for it in self.cart if it[0]=='food'), None)
        first_drink = next((it for it in self.cart if it[0]=='drink'), None)
        foodid = first_food[1] if first_food else None
        drinkid = first_drink[1] if first_drink else None

        # Insert into orders
        cur.execute('INSERT INTO orders (totalcost, foodid, drinkid, delid) VALUES (?,?,?,?)',
                    (int(total_cost), foodid, drinkid, delid))
        ordid = cur.lastrowid

        # Payment
        paymethod = simpledialog.askstring('Payment', 'Payment method (Cash/Credit Card/PayPal):') or 'Cash'
        cur.execute('INSERT INTO payment (paymethod, custid, ordid) VALUES (?,?,?)', (paymethod, custid, ordid))

        # Update stock quantities for foods
        for it in self.cart:
            typ, _id, _name, price, qty = it
            if typ == 'food' and _id is not None:
                cur.execute('SELECT quantity FROM food WHERE foodid=?', (_id,))
                row = cur.fetchone()
                if row:
                    current = row[0] if row[0] is not None else 0
                    new_qty = current - qty
                    if new_qty < 0:
                        new_qty = 0
                    cur.execute('UPDATE food SET quantity=? WHERE foodid=?', (new_qty, _id))

        conn.commit()
        conn.close()

        messagebox.showinfo('Order Placed', f'Order {ordid} placed. Total: Rs {total_cost}')
        self.cart = []
        self.update_cart_view()
        self.load_menu()

    # ------------------ Admin Tab ------------------
    def build_admin_tab(self):
        f = self.tab_admin
        ttk.Label(f, text='Admin', style='Header.TLabel').pack(anchor='w', pady=(4,6))
        btns = ttk.Frame(f)
        btns.pack(fill='x', padx=6, pady=(0,8))
        ttk.Button(btns, text='View Customers', command=lambda: self.show_table('customer')).pack(side='left', padx=4)
        ttk.Button(btns, text='View Food', command=lambda: self.show_table('food')).pack(side='left', padx=4)
        ttk.Button(btns, text='View Drink', command=lambda: self.show_table('drink')).pack(side='left', padx=4)
        ttk.Button(btns, text='View Orders', command=lambda: self.show_table('orders')).pack(side='left', padx=4)
        ttk.Button(btns, text='View Payments', command=lambda: self.show_table('payment')).pack(side='left', padx=4)
        ttk.Button(btns, text='Reset All Customers', command=self.reset_customers).pack(side='right', padx=4)
        ttk.Button(btns, text='Add Food Item', command=self.add_food_window).pack(side='right', padx=4)

        self.admin_frame = ttk.Frame(f)
        self.admin_frame.pack(fill='both', expand=True, padx=6, pady=8)

    def show_table(self, table_name):
        for w in self.admin_frame.winfo_children():
            w.destroy()
        conn = get_conn()
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        except Exception as e:
            messagebox.showerror('Error', str(e))
            conn.close()
            return
        conn.close()

        tv = ttk.Treeview(self.admin_frame, columns=list(df.columns), show='headings')
        for c in df.columns:
            tv.heading(c, text=c)
            tv.column(c, width=120, anchor='center')
        for _, row in df.iterrows():
            tv.insert('', 'end', values=list(row.values))
        tv.pack(fill='both', expand=True)

    def reset_customers(self):
        if not messagebox.askyesno('Confirm', 'This will DELETE all customers permanently. Continue?'):
            return
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM customer')
        conn.commit()
        conn.close()
        messagebox.showinfo('Done', 'All customers deleted.')

    def add_food_window(self):
        top = tk.Toplevel(self.root)
        top.title('Add Food Item')
        labels = ['foodid','foodname','price','quantity','foodavail','cuisineid','ingid','chefid']
        entries = {}
        for i, lab in enumerate(labels):
            ttk.Label(top, text=lab).grid(row=i, column=0, sticky='w', padx=6, pady=4)
            ent = ttk.Entry(top)
            ent.grid(row=i, column=1, padx=6, pady=4)
            entries[lab] = ent

        def add_food():
            vals = [entries[l].get() or None for l in labels]
            try:
                conn = get_conn(); cur = conn.cursor()
                cleaned = []
                for idx, v in enumerate(vals):
                    if v in (None, '', 'None'):
                        cleaned.append(None)
                    else:
                        if labels[idx] in ('foodid','price','quantity','cuisineid','ingid','chefid'):
                            try:
                                cleaned.append(int(v))
                            except Exception:
                                cleaned.append(None)
                        else:
                            cleaned.append(v)
                cur.execute('INSERT INTO food (foodid,foodname,price,quantity,foodavail,cuisineid,ingid,chefid) VALUES (?,?,?,?,?,?,?,?)', cleaned)
                conn.commit(); conn.close()
                messagebox.showinfo('Added', 'Food added successfully.')
                top.destroy()
                self.load_menu()
            except Exception as e:
                messagebox.showerror('Error', str(e))

        ttk.Button(top, text='Add', command=add_food).grid(row=len(labels), column=0, columnspan=2, pady=10)

# --------------------------
# Run
# --------------------------
if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = App(root)
    root.mainloop()
