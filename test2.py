import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# MySQL connection
conn = mysql.connector.connect(
    host='localhost', user='root', password='root', database='sagar'
)
cursor = conn.cursor()

# ---------------------- LOGIN WINDOW ----------------------
def verify_login(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    return cursor.fetchone() is not None

def show_login_window():
    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x200")
    
    tk.Label(login_window, text="Username").pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack()

    tk.Label(login_window, text="Password").pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack()

    def attempt_login():
        username = entry_username.get()
        password = entry_password.get()
        if verify_login(username, password):
            login_window.destroy()
            run_main_app()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    tk.Button(login_window, text="Login", command=attempt_login).pack(pady=20)
    login_window.mainloop()

# ---------------------- MAIN APPLICATION ----------------------
def run_main_app():
    # Ensure tables exist
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
        product_id INT PRIMARY KEY,
        product_name VARCHAR(100),
        product_price FLOAT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS zones (
        zone_number INT PRIMARY KEY,
        zone_name VARCHAR(100)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        month INT,
        product_id INT,
        quantity INT,
        zone_id INT,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (zone_id) REFERENCES zones(zone_number)
    )""")
    conn.commit()

    root = tk.Tk()
    root.title("Inventory Management System")
    root.geometry("700x800")

    # -------------- ZONE ENTRY --------------
    frame_zone = tk.LabelFrame(root, text="Add Zone", padx=10, pady=10)
    frame_zone.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_zone, text="Zone Number").grid(row=0, column=0)
    entry_zone_number = tk.Entry(frame_zone)
    entry_zone_number.grid(row=0, column=1)

    tk.Label(frame_zone, text="Zone Name").grid(row=1, column=0)
    entry_zone_name = tk.Entry(frame_zone)
    entry_zone_name.grid(row=1, column=1)

    def add_zone():
        try:
            zone_number = int(entry_zone_number.get())
            zone_name = entry_zone_name.get()
            cursor.execute("INSERT INTO zones (zone_number, zone_name) VALUES (%s, %s)",
                        (zone_number, zone_name))
            conn.commit()
            messagebox.showinfo("Done", "Zone added.")
        except ValueError:
            messagebox.showerror("Error", "Zone Number must be an integer.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding zone: {err}")

    tk.Button(frame_zone, text="Add Zone", command=add_zone).grid(row=2, columnspan=2)

    # -------------- PRODUCT ENTRY --------------
    frame_product = tk.LabelFrame(root, text="Add Product", padx=10, pady=10)
    frame_product.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_product, text="Product ID").grid(row=0, column=0)
    entry_product_id = tk.Entry(frame_product)
    entry_product_id.grid(row=0, column=1)

    tk.Label(frame_product, text="Name").grid(row=1, column=0)
    entry_product_name = tk.Entry(frame_product)
    entry_product_name.grid(row=1, column=1)

    tk.Label(frame_product, text="Price").grid(row=2, column=0)
    entry_product_price = tk.Entry(frame_product)
    entry_product_price.grid(row=2, column=1)

    def add_product():
        try:
            product_id = int(entry_product_id.get())
            name = entry_product_name.get()
            price = float(entry_product_price.get())
            cursor.execute("INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s, %s)",
                        (product_id, name, price))
            conn.commit()
            messagebox.showinfo("Done", "Product added.")
        except ValueError:
            messagebox.showerror("Error", "Product ID and Price must be numbers.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding product: {err}")

    tk.Button(frame_product, text="Add Product", command=add_product).grid(row=3, columnspan=2)

    # -------------- SALES ENTRY --------------
    frame_sales = tk.LabelFrame(root, text="Add Sales Data", padx=10, pady=10)
    frame_sales.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_sales, text="Month").grid(row=0, column=0)
    month_options = list(range(1, 13))
    selected_month = tk.IntVar()
    month_dropdown = ttk.Combobox(frame_sales, textvariable=selected_month, values=month_options, state="readonly")
    month_dropdown.grid(row=0, column=1)
    month_dropdown.set(1)

    tk.Label(frame_sales, text="Product ID").grid(row=1, column=0)
    entry_sales_product_id = tk.Entry(frame_sales)
    entry_sales_product_id.grid(row=1, column=1)

    tk.Label(frame_sales, text="Quantity Sold").grid(row=2, column=0)
    entry_quantity_sold = tk.Entry(frame_sales)
    entry_quantity_sold.grid(row=2, column=1)

    tk.Label(frame_sales, text="Zone Number").grid(row=3, column=0)
    entry_sales_zone_id = tk.Entry(frame_sales)
    entry_sales_zone_id.grid(row=3, column=1)

    def add_sale():
        try:
            month = selected_month.get()
            product_id = int(entry_sales_product_id.get())
            quantity = int(entry_quantity_sold.get())
            zone_id = int(entry_sales_zone_id.get())

            cursor.execute("SELECT quantity FROM sales WHERE month = %s AND product_id = %s AND zone_id = %s",
                        (month, product_id, zone_id))
            existing_quantity = cursor.fetchone()

            if existing_quantity:
                new_quantity = existing_quantity[0] + quantity
                cursor.execute("UPDATE sales SET quantity = %s WHERE month = %s AND product_id = %s AND zone_id = %s",
                            (new_quantity, month, product_id, zone_id))
            else:
                cursor.execute("INSERT INTO sales (month, product_id, quantity, zone_id) VALUES (%s, %s, %s, %s)",
                            (month, product_id, quantity, zone_id))
            conn.commit()
            messagebox.showinfo("Done", "Sale recorded.")
        except ValueError:
            messagebox.showerror("Error", "ID and Quantity fields must be integers.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding sale: {err}")

    tk.Button(frame_sales, text="Add Sale", command=add_sale).grid(row=4, columnspan=2)

    # -------------- SEARCH SECTION --------------
    frame_search = tk.LabelFrame(root, text="Search", padx=10, pady=10)
    frame_search.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_search, text="Product Name:").grid(row=0, column=0)
    entry_search_name = tk.Entry(frame_search)
    entry_search_name.grid(row=0, column=1)
    product_result_label = tk.Label(frame_search, text="Product ID: ")
    product_result_label.grid(row=1, column=0, columnspan=2)

    tk.Label(frame_search, text="Zone Name:").grid(row=0, column=2)
    entry_search_zone_name = tk.Entry(frame_search)
    entry_search_zone_name.grid(row=0, column=3)
    zone_result_label = tk.Label(frame_search, text="Zone Number: ")
    zone_result_label.grid(row=1, column=2, columnspan=2)

    def search_product():
        product_name = entry_search_name.get()
        try:
            cursor.execute("SELECT product_id FROM products WHERE product_name = %s", (product_name,))
            result = cursor.fetchone()
            product_result_label.config(text=f"Product ID: {result[0]}" if result else "Not found.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching: {err}")

    def search_zone():
        zone_name = entry_search_zone_name.get()
        try:
            cursor.execute("SELECT zone_number FROM zones WHERE zone_name = %s", (zone_name,))
            result = cursor.fetchone()
            zone_result_label.config(text=f"Zone Number: {result[0]}" if result else "Not found.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error searching: {err}")

    tk.Button(frame_search, text="Search Product", command=search_product).grid(row=2, column=0, columnspan=2)
    tk.Button(frame_search, text="Search Zone", command=search_zone).grid(row=2, column=2, columnspan=2)

    # -------------- CHART + PREDICTION --------------
    def show_chart_and_prediction():
        product_id_for_prediction = simpledialog.askinteger("Product Selection", "Enter Product ID to predict sales:")
        if product_id_for_prediction is None:
            return

        zone_filter = simpledialog.askinteger("Zone Filter", "Enter Zone Number to filter (optional):")

        query = "SELECT month, SUM(quantity) FROM sales WHERE product_id = %s"
        params = [product_id_for_prediction]
        if zone_filter:
            query += " AND zone_id = %s"
            params.append(zone_filter)
        query += " GROUP BY month ORDER BY month"

        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

        if not data:
            messagebox.showwarning("No Data", "No sales data for selected product.")
            return

        months = [row[0] for row in data]
        quantities = [row[1] for row in data]

        if len(months) < 2:
            messagebox.showwarning("Not enough data", "Need at least 2 data points.")
            return

        X = np.array(months).reshape(-1, 1)
        y = np.array(quantities)
        model = LinearRegression()
        model.fit(X, y)

        future_months = np.array([max(months) + i for i in range(1, 4)]).reshape(-1, 1)
        future_preds = model.predict(future_months)

        plt.figure(figsize=(10, 6))
        plt.plot(months, quantities, label="Actual Sales", marker='o')
        plt.plot(future_months, future_preds, label="Predicted Sales", linestyle='--', marker='x')
        plt.title("Sales Trend & Prediction")
        plt.xlabel("Month")
        plt.ylabel("Quantity Sold")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    tk.Button(root, text="Show Chart + Predict", bg="lightblue", command=show_chart_and_prediction).pack(pady=10)
    root.mainloop()

# ---------------------- START ----------------------
show_login_window()
conn.close()
