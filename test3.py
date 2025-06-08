import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# MySQL connection
conn = mysql.connector.connect(host='localhost', user='root', password='root',
                              database='sagar')
cursor = conn.cursor()

# Ensure tables exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        product_id INT PRIMARY KEY,
        product_name VARCHAR(100),
        product_price FLOAT
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS zones (
        zone_number INT PRIMARY KEY,
        zone_name VARCHAR(100)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INT AUTO_INCREMENT PRIMARY KEY,
        month INT,
        product_id INT,
        quantity INT,
        zone_id INT,
        FOREIGN KEY (product_id) REFERENCES products(product_id),
        FOREIGN KEY (zone_id) REFERENCES zones(zone_number)
    )
""")
conn.commit()

# GUI setup
root = tk.Tk()
root.title("Inventory Management System")
root.geometry("700x800")

# --- Add Zone Section ---
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

# --- Add Product Section ---
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
        cursor.execute(
            "INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s, %s)",
            (product_id, name, price))
        conn.commit()
        messagebox.showinfo("Done", "Product added.")
    except ValueError:
        messagebox.showerror("Error", "Product ID and Price must be numbers.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding product: {err}")


tk.Button(frame_product, text="Add Product", command=add_product).grid(row=3,
                                                                    columnspan=2)

# --- Add Sales Data Section ---
frame_sales = tk.LabelFrame(root, text="Add Sales Data", padx=10, pady=10)
frame_sales.pack(padx=10, pady=10, fill="x")

tk.Label(frame_sales, text="Month").grid(row=0, column=0)
month_options = list(range(1, 13))
selected_month = tk.IntVar()
month_dropdown = ttk.Combobox(frame_sales, textvariable=selected_month,
                              values=month_options, state="readonly")
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

        # Check if a record with the same month, product_id, and zone_id exists
        cursor.execute(
            "SELECT quantity FROM sales WHERE month = %s AND product_id = %s AND zone_id = %s",
            (month, product_id, zone_id))
        existing_quantity = cursor.fetchone()

        if existing_quantity:
            # Update the existing record
            new_quantity = existing_quantity[0] + quantity
            cursor.execute(
                "UPDATE sales SET quantity = %s WHERE month = %s AND product_id = %s AND zone_id = %s",
                (new_quantity, month, product_id, zone_id))
            conn.commit()
            messagebox.showinfo("Done", "Sale quantity updated.")
        else:
            # Insert a new record
            cursor.execute(
                "INSERT INTO sales (month, product_id, quantity, zone_id) VALUES (%s, %s, %s, %s)",
                (month, product_id, quantity, zone_id))
            conn.commit()
            messagebox.showinfo("Done", "Sale added.")

    except ValueError:
        messagebox.showerror("Error",
                             "Product ID, Quantity Sold, and Zone Number must be integers.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error adding sale: {err}")


tk.Button(frame_sales, text="Add Sale", command=add_sale).grid(row=4,
                                                              columnspan=2)

# --- Search Section ---
frame_search = tk.LabelFrame(root, text="Search", padx=10,
                            pady=10)
frame_search.pack(padx=10, pady=10, fill="x")

# Product Search
tk.Label(frame_search, text="Product Name:").grid(row=0, column=0)
entry_search_name = tk.Entry(frame_search)
entry_search_name.grid(row=0, column=1)
product_result_label = tk.Label(frame_search, text="Product ID: ", wraplength=250)
product_result_label.grid(row=1, column=0, columnspan=2)

# Zone Search
tk.Label(frame_search, text="Zone Name:").grid(row=0, column=2)  # Changed column
entry_search_zone_name = tk.Entry(frame_search)
entry_search_zone_name.grid(row=0, column=3)  # Changed column
zone_result_label = tk.Label(frame_search, text="Zone Number: ", wraplength=250)
zone_result_label.grid(row=1, column=2, columnspan=2)  # Changed column



def search_product():
    product_name = entry_search_name.get()
    try:
        cursor.execute("SELECT product_id FROM products WHERE product_name = %s",
                       (product_name,))
        result = cursor.fetchone()
        if result:
            product_result_label.config(
                text=f"Product ID: {result[0]}")
        else:
            product_result_label.config(text="Product not found.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error searching: {err}")
        product_result_label.config(text="Error")



def search_zone():
    zone_name = entry_search_zone_name.get()
    try:
        cursor.execute("SELECT zone_number FROM zones WHERE zone_name = %s",
                       (zone_name,))
        result = cursor.fetchone()
        if result:
            zone_result_label.config(text=f"Zone Number: {result[0]}")
        else:
            zone_result_label.config(text="Zone not found.")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error searching: {err}")
        zone_result_label.config(text="Error")



tk.Button(frame_search, text="Search Product", command=search_product).grid(row=2, column=0, columnspan=2) # Changed row
tk.Button(frame_search, text="Search Zone", command=search_zone).grid(row=2, column=2, columnspan=2)  # Changed row and column

# --- Chart + Prediction Section ---
def show_chart_and_prediction():
    # Get product id for  selection
    product_id_for_prediction = simpledialog.askinteger("Product Selection",
                                           "Enter Product ID to predict sales:")
    if product_id_for_prediction is None:
        messagebox.showwarning("No Product Selected", "Please enter a Product ID.")
        return

    # Get zone selection
    zone_filter = None
    zone_input = simpledialog.askinteger("Zone Filter",
                                           "Enter Zone Number to filter (leave blank for all):")
    if zone_input is not None:
        zone_filter = zone_input

    query = "SELECT month, SUM(quantity) FROM sales WHERE product_id = %s"
    query_params = (product_id_for_prediction,)

    if zone_filter is not None:
        query += f" AND zone_id = %s"
        query_params = (product_id_for_prediction, zone_filter)
    query += " GROUP BY month ORDER BY month"
    cursor.execute(query, query_params)
    data = cursor.fetchall()

    if not data:
        messagebox.showwarning("No Data",
                               f"No sales data available for Product ID {product_id_for_prediction} "
                               f"{'and the selected zone' if zone_filter else 'overall'}.")
        return

    months = [row[0] for row in data]
    quantities = [row[1] for row in data]

    if len(months) < 2:
        messagebox.showwarning("Insufficient Data",
                               "Not enough data points to perform prediction.")
        plt.figure()
        plt.title("Insufficient Data for Prediction")
        plt.xlabel("Month")
        plt.ylabel("Quantity")
        plt.xticks(months)
        plt.plot(months, quantities, marker='o', linestyle='-')
        plt.show()
        return

    # Linear Regression Prediction
    X = np.array(months).reshape(-1, 1)
    y = np.array(quantities)
    model = LinearRegression()
    model.fit(X, y)

    future_months = np.array([max(months) + i for i in range(1, 4)]).reshape(-1, 1)
    future_preds = model.predict(future_months)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(months, quantities, label="Actual Sales", marker='o', linestyle='-')
    plt.plot(future_months, future_preds, label="Prediction", linestyle="--",
             marker='x')
    plt.xlabel("Month")
    plt.ylabel("Total Quantity Sold")
    plt.title(
        f"Sales Trend + Future Prediction for Product ID {product_id_for_prediction} "
        f"{'(Zone ' + str(zone_filter) + ')' if zone_filter else '(All Zones)'}")
    plt.xticks(months + list(future_months.flatten()))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


tk.Button(root, text="Show Chart + Predict", bg="lightblue",
          command=show_chart_and_prediction).pack(pady=10)

root.mainloop()
conn.close()
