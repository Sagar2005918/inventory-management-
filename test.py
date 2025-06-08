import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import mysql.connector
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# --- Database Connection ---
def connect_to_database():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='sagar'
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
        return None

# --- Database Initialization ---
def initialize_database(conn):
    """Ensures that the necessary tables exist in the database."""
    if not conn:
        return
    cursor = conn.cursor()
    try:
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
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error initializing database: {err}")
        conn.rollback()
    finally:
        cursor.close()

# --- GUI Setup ---
def setup_gui():
    """Sets up the main graphical user interface."""
    root = tk.Tk()
    root.title("Sales Prediction System")
    root.geometry("700x800")
    return root

# --- Add Zone Section ---
def create_zone_section(root):
    """Creates the GUI section for adding zones."""
    frame_zone = tk.LabelFrame(root, text="Add Zone")
    frame_zone.pack(padx=10, pady=10, fill="x")

    tk.Label(frame_zone, text="Zone Number").grid(row=0, column=0)
    entry_zone_number = tk.Entry(frame_zone)
    entry_zone_number.grid(row=0, column=1)

    tk.Label(frame_zone, text="Zone Name").grid(row=1, column=0)
    entry_zone_name = tk.Entry(frame_zone)
    entry_zone_name.grid(row=1, column=1)

    def add_zone(conn):
        """Adds a new zone to the database."""
        if not conn:
            return
        try:
            zone_number = int(entry_zone_number.get())
            zone_name = entry_zone_name.get()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO zones (zone_number, zone_name) VALUES (%s, %s)",
                           (zone_number, zone_name))
            conn.commit()
            messagebox.showinfo("Done", "Zone added.")
            entry_zone_number.delete(0, tk.END)
            entry_zone_name.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Zone Number must be an integer.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding zone: {err}")
            conn.rollback()
        finally:
            cursor.close()

    add_zone_button = tk.Button(frame_zone, text="Add Zone", command=lambda: add_zone(conn))
    add_zone_button.grid(row=2, columnspan=2, pady=10)
    return frame_zone

# --- Add Product Section ---
def create_product_section(root):
    """Creates the GUI section for adding products."""
    frame_product = tk.LabelFrame(root, text="Add Product")
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

    def add_product(conn):
        """Adds a new product to the database."""
        if not conn:
            return
        try:
            product_id = int(entry_product_id.get())
            name = entry_product_name.get()
            price = float(entry_product_price.get())
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO products (product_id, product_name, product_price) VALUES (%s, %s, %s)",
                (product_id, name, price))
            conn.commit()
            messagebox.showinfo("Done", "Product added.")
            entry_product_id.delete(0, tk.END)
            entry_product_name.delete(0, tk.END)
            entry_product_price.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Product ID and Price must be numbers.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding product: {err}")
            conn.rollback()
        finally:
            cursor.close()

    add_product_button = tk.Button(frame_product, text="Add Product", command=lambda: add_product(conn))
    add_product_button.grid(row=3, columnspan=2, pady=10)
    return frame_product

# --- Add Sales Data Section ---
def create_sales_section(root):
    """Creates the GUI section for adding sales data."""
    frame_sales = tk.LabelFrame(root, text="Add Sales Data")
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

    def add_sale(conn):
        """Adds or updates sales data in the database."""
        if not conn:
            return
        try:
            month = selected_month.get()
            product_id = int(entry_sales_product_id.get())
            quantity = int(entry_quantity_sold.get())
            zone_id = int(entry_sales_zone_id.get())

            cursor = conn.cursor()
            # Check for existing record
            cursor.execute(
                "SELECT quantity FROM sales WHERE month = %s AND product_id = %s AND zone_id = %s",
                (month, product_id, zone_id))
            existing_quantity = cursor.fetchone()

            if existing_quantity:
                new_quantity = existing_quantity[0] + quantity
                cursor.execute(
                    "UPDATE sales SET quantity = %s WHERE month = %s AND product_id = %s AND zone_id = %s",
                    (new_quantity, month, product_id, zone_id))
                conn.commit()
                messagebox.showinfo("Done", "Sale quantity updated.")
            else:
                cursor.execute(
                    "INSERT INTO sales (month, product_id, quantity, zone_id) VALUES (%s, %s, %s, %s)",
                    (month, product_id, quantity, zone_id))
                conn.commit()
                messagebox.showinfo("Done", "Sale added.")
            entry_sales_product_id.delete(0, tk.END)
            entry_quantity_sold.delete(0, tk.END)
            entry_sales_zone_id.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error",
                                 "Product ID, Quantity Sold, and Zone Number must be integers.")
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error adding sale: {err}")
            conn.rollback()
        finally:
            cursor.close()

    add_sale_button = tk.Button(frame_sales, text="Add Sale", command=lambda: add_sale(conn))
    add_sale_button.grid(row=4, columnspan=2, pady=10)
    return frame_sales

# --- Search Section ---
def create_search_section(root):
    """Creates the GUI section for searching products and zones."""
    frame_search = tk.LabelFrame(root, text="Search")
    frame_search.pack(padx=10, pady=10, fill="x")

    # Product Search
    tk.Label(frame_search, text="Product Name:").grid(row=0, column=0)
    entry_search_name = tk.Entry(frame_search)
    entry_search_name.grid(row=0, column=1)
    product_result_label = tk.Label(frame_search, text="Product ID: ")
    product_result_label.grid(row=1, column=0, columnspan=2)

    # Zone Search
    tk.Label(frame_search, text="Zone Name:").grid(row=0, column=2)
    entry_search_zone_name = tk.Entry(frame_search)
    entry_search_zone_name.grid(row=0, column=3)
    zone_result_label = tk.Label(frame_search, text="Zone Number: ")
    zone_result_label.grid(row=1, column=2, columnspan=2)

    def search_product(conn):
        """Searches for a product by name and displays its ID."""
        if not conn:
            return
        product_name = entry_search_name.get()
        try:
            cursor = conn.cursor()
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
        finally:
            cursor.close()

    def search_zone(conn):
        """Searches for a zone by name and displays its ID."""
        if not conn:
            return
        zone_name = entry_search_zone_name.get()
        try:
            cursor = conn.cursor()
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
        finally:
            cursor.close()

    search_product_button = tk.Button(frame_search, text="Search Product", command=lambda: search_product(conn))
    search_product_button.grid(row=2, column=0, columnspan=2, pady=10)
    search_zone_button = tk.Button(frame_search, text="Search Zone", command=lambda: search_zone(conn))
    search_zone_button.grid(row=2, column=2, columnspan=2, pady=10)
    return frame_search

# --- Chart and Prediction Section ---
def create_chart_prediction_section(root, conn):
    """Creates the GUI section for displaying sales charts and predictions."""
    def show_chart_and_prediction():
        """
        Displays a sales chart and future predictions based on user input.
        """
        if not conn:
            return
        # Get product id for selection
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

        try:
            cursor = conn.cursor()
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
                plt.figure(figsize=(8, 5))
                plt.title("Insufficient Data for Prediction", fontdict={'fontsize': 12, 'fontweight': 'bold'})
                plt.xlabel("Month", fontsize=10)
                plt.ylabel("Quantity", fontsize=10)
                plt.xticks(months)
                plt.plot(months, quantities, marker='o', linestyle='-', color="#3498db")
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
            plt.xlabel("Month", fontsize=12)
            plt.ylabel("Total Quantity Sold", fontsize=12)
            plt.title(
                f"Sales Trend + Future Prediction for Product ID {product_id_for_prediction} "
                f"{'(Zone ' + str(zone_filter) + ')' if zone_filter else '(All Zones)'}",
                fontdict={'fontsize': 14, 'fontweight': 'bold'}
            )
            plt.xticks(months + list(future_months.flatten()), fontsize=10)
            plt.yticks(fontsize=10)
            plt.legend(fontsize=10)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
            plt.show()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error during chart/prediction: {err}")
        finally:
            cursor.close()

    def show_product_sales_pie_chart():
        """
        Displays a pie chart of product sales for a selected zone.
        """
        if not conn:
            return

        zone_number = simpledialog.askinteger("Zone Selection", "Enter Zone Number to analyze product sales:")
        if zone_number is None:
            messagebox.showwarning("No Zone Selected", "Please enter a Zone Number.")
            return

        try:
            cursor = conn.cursor()
            query = """
                SELECT p.product_name, SUM(s.quantity)
                FROM sales s
                JOIN products p ON s.product_id = p.product_id
                WHERE s.zone_id = %s
                GROUP BY s.product_id
                ORDER BY SUM(s.quantity) DESC
            """
            cursor.execute(query, (zone_number,))
            data = cursor.fetchall()

            if not data:
                messagebox.showwarning("No Data", f"No sales data available for Zone Number {zone_number}.")
                return

            product_names = [row[0] for row in data]
            quantities = [row[1] for row in data]

            if len(product_names) > 0:
                plt.figure(figsize=(8, 6))
                plt.pie(quantities, labels=product_names, autopct='%1.1f%%', startangle=140)
                plt.title(f"Product Sales Distribution in Zone {zone_number}", fontdict={'fontsize': 14, 'fontweight': 'bold'})
                plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                plt.tight_layout()
                plt.show()
            else:
                messagebox.showinfo("Info", "No products sold in the selected zone.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error fetching sales data: {err}")
        finally:
            cursor.close()

    chart_button = tk.Button(root, text="Show Chart + Predict", command=show_chart_and_prediction)
    chart_button.pack(pady=10)

    pie_chart_button = tk.Button(root, text="Show Product Sales Pie Chart", command=show_product_sales_pie_chart)
    pie_chart_button.pack(pady=10)

    return chart_button, pie_chart_button

# --- Main Function ---
def main():
    """Main function to run the application."""
    conn = connect_to_database()
    if conn:
        initialize_database(conn)
        root = setup_gui()
        create_zone_section(root)
        create_product_section(root)
        create_sales_section(root)
        create_search_section(root)
        create_chart_prediction_section(root, conn)
        root.mainloop()
        conn.close()

if __name__ == "__main__":
    main()
