import tkinter as tk
from tkinter import messagebox, scrolledtext
import mysql.connector
import matplotlib.pyplot as plt

# ----- MySQL Connection -----
connection = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='sagar'
)
cursor = connection.cursor()

# ----- Ensure Tables -----
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (          
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(50)
    )
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS people (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        age INT
    )
""")
connection.commit()

# ----- Insert Sample User -----
cursor.execute("SELECT * FROM users WHERE username='admin'")
if not cursor.fetchone():
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'admin')")
    connection.commit()

# ----- Main App -----
def open_main_app():
    login_window.destroy()
    root = tk.Tk()
    root.title("MySQL GUI With Pie Chart")
    root.geometry("500x600")
    root.configure(bg="#e0f7fa")

    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    tk.Label(root, text="Name:", bg="#e0f7fa").pack(pady=5, anchor="w", padx=10)
    entry_name = tk.Entry(root, width=30)
    entry_name.pack(pady=5, anchor="w", padx=10)

    tk.Label(root, text="Price:", bg="#e0f7fa").pack(pady=5, anchor="w", padx=10)
    entry_age = tk.Entry(root, width=30)
    entry_age.pack(pady=5, anchor="w", padx=10)

    def submit_data():
        name = entry_name.get()
        age = entry_age.get()
        if not name or not age:
            messagebox.showwarning("Missing Info", "Please fill all fields")
        else:
            try:
                cursor.execute("INSERT INTO people (name, age) VALUES (%s, %s)", (name, int(age)))
                connection.commit()
                messagebox.showinfo("Success", "Data successfully inserted!")
                entry_name.delete(0, tk.END)
                entry_age.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def show_data():
        cursor.execute("SELECT * FROM people")
        output_box.delete("1.0", tk.END)
        for row in cursor.fetchall():
            output_box.insert(tk.END, f"ID: {row[0]} | Name: {row[1]} | Age: {row[2]}\n")

    def show_pie_chart():
        cursor.execute("SELECT name, COUNT(*) FROM people GROUP BY name")
        results = cursor.fetchall()
        if not results:
            messagebox.showinfo("No Data", "No data to display in pie chart.")
            return
        labels = [row[0] for row in results]
        sizes = [row[1] for row in results]

        plt.figure(figsize=(6, 6))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("People Distribution by Name")
        plt.axis('equal')
        plt.show()

    tk.Button(root, text="Submit", bg="yellow", command=submit_data).pack(pady=10, anchor="w", padx=10)
    tk.Button(root, text="Show All Data", bg="yellow", command=show_data).pack(pady=5, anchor="w", padx=10)
    tk.Button(root, text="Show Pie Chart", bg="lightgreen", command=show_pie_chart).pack(pady=5, anchor="w", padx=10)

    output_box = scrolledtext.ScrolledText(root, width=60, height=15, bg="#ffffff")
    output_box.pack(pady=15, anchor="w", padx=10)

    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(label="Insert Data", command=submit_data)
    file_menu.add_command(label="Retrieve Data", command=show_data)
    file_menu.add_command(label="Show Pie Chart", command=show_pie_chart)
    file_menu.add_command(label="Clear Output", command=lambda: output_box.delete("1.0", tk.END))
    file_menu.add_command(label="Exit", command=root.quit)
    menu_bar.add_cascade(label="Menu", menu=file_menu)

    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "MySQL GUI With Pie Chart"))
    menu_bar.add_cascade(label="Help", menu=help_menu)

    root.mainloop()

# ----- Login Page -----
def check_login():
    username = entry_user.get()
    password = entry_pass.get()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    if cursor.fetchone():
        open_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x200")
login_window.configure(bg="#f0f0f0")

tk.Label(login_window, text="Username:").pack(pady=5)
entry_user = tk.Entry(login_window)
entry_user.pack(pady=5)

tk.Label(login_window, text="Password:").pack(pady=5)
entry_pass = tk.Entry(login_window, show="*")
entry_pass.pack(pady=5)

tk.Button(login_window, text="Login", command=check_login).pack(pady=20)

login_window.mainloop()
connection.close()
