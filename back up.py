import tkinter as tk
import mysql.connector 
from tkinter import font
from tkinter import PhotoImage
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

root = tk.Tk()
root.title("KeepSafe")
root.geometry("800x500")
root.resizable(False, False)
#user database connection if related or inside the database
def login():
    global current_user
    username = inputuser.get()
    pin = inputpin.get()
    
    if not username or not pin:
        messagebox.showwarning("Input Error", "Please enter both username and PIN")
        return
    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()
        user_query = """SELECT UserID FROM users WHERE BINARY Username = %s AND BINARY PIN = %s"""
        cursor.execute(user_query, (username, pin))
        user_result = cursor.fetchone()

        if user_result:
            current_user = user_result[0]  # Set the current user as the UserID
            messagebox.showinfo("Login Success", f"Welcome, {username}")
            show_user_dashboard()  # Show the user dashboard
        else:
            admin_query = """SELECT EmployeeID FROM admin WHERE BINARY EmplUser = %s AND BINARY EmplPIN = %s"""
            cursor.execute(admin_query, (username, pin))
            admin_result = cursor.fetchone()

            if admin_result:
                messagebox.showinfo("Login Success", f"Welcome, Admin {username}")
                show_admin_dashboard()  # Redirect to the admin dashboard
            else:
                messagebox.showerror("Login Failed", "Incorrect username or PIN")
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def clear_login_inputs():
    inputuser.delete(0, tk.END)
    inputpin.delete(0, tk.END)
#admin
def open_delete_user_window():
    delete_window = tk.Toplevel(manage_window)
    delete_window.title("Delete a User")
    delete_window.geometry("400x250")
    delete_window.configure(bg="#1c1f2f")
    delete_window.resizable(False, False)
    screen_width = delete_window.winfo_screenwidth()
    screen_height = delete_window.winfo_screenheight()
    x = (screen_width // 2) - (400 // 2)
    y = (screen_height // 2) - (250 // 2)
    delete_window.geometry(f"400x250+{x}+{y}")
    
    title_font = font.Font(family="Helvetica", size=14, weight="bold")
    title_label = tk.Label(delete_window, text="Delete a User", font=title_font, bg="#1c1f2f", fg = "white")
    title_label.pack(pady=10)
    
    entry_label = tk.Label(delete_window, text="Enter Username:", bg="#1c1f2f", fg = "white")
    entry_label.pack(pady=5)
    
    username_entry = tk.Entry(delete_window, width=20)
    username_entry.pack(pady=5)
    
    def delete_user():
        username = username_entry.get().strip()
    
        if not username:
            messagebox.showerror("Input Error", "Please enter a valid Username.")
            return
        try:
            db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE Username = %s", (username,))
            user = cursor.fetchone()
    
            if not user:
                messagebox.showerror("Error", "User with the specified Username does not exist.")
                db.close()
                return
            insert_query = """INSERT INTO deleted_user(UserID, Firstname, Lastname, Age, Username, PIN) VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(insert_query, user[:6])
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            delete_query = "DELETE FROM users WHERE Username = %s"
            cursor.execute(delete_query, (username,))
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            db.commit()
            
            messagebox.showinfo("Success", "User deleted successfully, re-open window to refresh.")
            db.close()
            delete_window.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error: {err}")
            if db.is_connected():
                db.close()
    
    delete_button = tk.Button(delete_window, text="Delete", command=delete_user, bg="#ff4d4d", fg="white", cursor='hand2')
    delete_button.pack(pady=10)

    close_button = tk.Button(delete_window, text="Close", command=delete_window.destroy, bg="#545454", fg="white", cursor='hand2')
    close_button.pack(pady=8)

def manage_users_window():
    global manage_window
    manage_window = tk.Toplevel(admin_dashboard)
    manage_window.title("Manage Users")
    manage_window.geometry("1000x600")
    manage_window.configure(bg="#1c1f2f")
    screen_width = manage_window.winfo_screenwidth()
    screen_height = manage_window.winfo_screenheight()
    x = (screen_width // 2) - (1000 // 2)
    y = (screen_height // 2) - (600 // 2)
    manage_window.geometry(f"1000x600+{x}+{y}")

    manage_title_font = font.Font(family="Helvetica World", size=20, weight="bold")
    table_font = font.Font(family="Helvetica World", size=10)

    title_label = tk.Label(manage_window, text="Manage Users", font=manage_title_font, bg="#1c1f2f", fg="white")
    title_label.pack(pady=10)
    # columns for my treeview to view all existing users
    tree = ttk.Treeview(manage_window, columns=("UserID", "Firstname", "Lastname", "Age", "Username", "PIN", 
                                       "Address", "ContactNo","Email", "Occupation", "DateofCreation", "Bank1_bal", "Bank2_bal"), show="headings")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    #column size
    columns = [("UserID", 60), ("Firstname", 120), ("Lastname", 120), ("Age", 50), ("Username", 100), ("PIN", 50), ("Address", 150), ("ContactNo", 100),
               ("Email", 150), ("Occupation", 120), ("DateofCreation", 150), ("Bank1_bal", 100), ("Bank2_bal", 100)]

    for col, width in columns:
        tree.heading(col, text=col)
        tree.column(col, width=width, anchor="center")

    scroll_y = ttk.Scrollbar(manage_window, orient=tk.VERTICAL, command=tree.yview)
    scroll_x = ttk.Scrollbar(manage_window, orient=tk.HORIZONTAL, command=tree.xview)
    tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()
        query = "SELECT * FROM users" #inserting the values from database, users table to treeview manage_users window
        cursor.execute(query)
        users = cursor.fetchall()
        for user in users:
            tree.insert("", tk.END, values=user)
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
    close_button = tk.Button(manage_window, text="Close", command=manage_window.destroy, font=table_font, bg="#ff4d4d", fg="white", border=1)
    close_button.pack(pady=10)

    delete_userbutton = tk.Button(manage_window, text="Delete a User", command = open_delete_user_window, font=table_font, bg="#ff4d4d", fg="white", border=1)
    delete_userbutton.place(relx=0.01, rely= 0.90, width = 100, height = 40)

def view_transaction_logs_window():
    transaction_window = tk.Toplevel(admin_dashboard)
    transaction_window.title("Transaction Logs")
    transaction_window.geometry("800x400")
    transaction_window.configure(bg="#1c1f2f")
    
    screen_width = transaction_window.winfo_screenwidth()
    screen_height = transaction_window.winfo_screenheight()
    x = (screen_width // 2) - (800 // 2)
    y = (screen_height // 2) - (400 // 2)
    transaction_window.geometry(f"800x400+{x}+{y}")

    title_font = font.Font(family="Helvetica", size=16, weight="bold")
    title_label = tk.Label(transaction_window, text="All Users Transaction Logs", font=title_font, bg="#1c1f2f", fg="white")
    title_label.pack(pady=10)

    treeview = ttk.Treeview(transaction_window, columns=("TransactionID", "UserID", "TransactionDate", "Amount", "Sender", "Reciever"), show="headings")
    treeview.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
    treeview.heading("TransactionID", text="Transaction ID")
    treeview.heading("UserID", text="User ID")
    treeview.heading("TransactionDate", text="Date")
    treeview.heading("Amount", text="Amount")
    treeview.heading("Sender", text = "Sender")
    treeview.heading("Reciever", text= "Reciever")

    treeview.column("TransactionID", width=50, anchor="center")
    treeview.column("UserID", width=50, anchor="center")
    treeview.column("TransactionDate", width=150, anchor="center")
    treeview.column("Amount", width=100, anchor="center")
    treeview.column("Sender", width=100, anchor="center")
    treeview.column("Reciever", width=100, anchor="center")

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()
        cursor.execute("SELECT TransactionID, UserID, TransactionDate, Amount, FromBank, ToBank FROM transaction") # again inserting the values of the database created for transaction history
        transactions = cursor.fetchall()
        for transaction in transactions:
            treeview.insert("", tk.END, values=transaction)
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        if db.is_connected():
            db.close()
    close_button = tk.Button(transaction_window, text="Close", command=transaction_window.destroy, font=("Helvetica", 12), bg="#545454", fg="white", border=1, cursor='hand2')
    close_button.pack(pady=10)

def show_admin_dashboard():
    root.withdraw()
    global admin_dashboard
    admin_dashboard = tk.Toplevel(root)
    admin_dashboard.title("KeepSafe-AdminInterface")
    admin_dashboard.geometry("800x500")
    admin_dashboard.configure(bg="#1c1f2f")
    admin_dashboard.resizable(False, False)
    admin_dashboard_screenalign_width = admin_dashboard.winfo_screenwidth()
    admin_dashboard_screenalign_height = admin_dashboard.winfo_screenheight()
    x = (admin_dashboard_screenalign_width // 2) - (800 // 2)
    y = (admin_dashboard_screenalign_height // 2) - (500 // 2)
    admin_dashboard.geometry(f"800x500+{x}+{y}")

    admindash_title = font.Font(family="Helvetica World", size=25, weight="bold")
    admindash_button = font.Font(family="Helvetica World", size=12)

    label = tk.Label(admin_dashboard, text="Admin Interface", font=admindash_title, bg="#1c1f2f", fg="white")
    label.place(relx=0.5, rely=0.05, anchor="n")

    logout_button = tk.Button(admin_dashboard, text="Logout", command=admin_back_to_login, font=admindash_button, bg="#ff4d4d", fg="white", border= 1, cursor='hand2')
    logout_button.place(relx=0.455, rely=0.6)

    manage_users_button = tk.Button(admin_dashboard, text="Manage Users", command=manage_users_window, font=admindash_button, bg="#545454", fg="white", cursor='hand2')
    manage_users_button.place(relx=0.5, rely=0.3, anchor="n", width=200, height=50)
    # Button to view transaction logs
    view_transactions_button = tk.Button(admin_dashboard, text="Transaction Logs", command=view_transaction_logs_window, font=admindash_button, bg="#545454", fg="white", cursor='hand2')
    view_transactions_button.place(relx=0.5, rely=0.45, anchor="n", width=200, height=50)

def admin_back_to_login():
    admin_dashboard.destroy()
    clear_login_inputs()
    root.deiconify()
# users dashboard 
def open_bank1_window():
    global current_user

    if current_user is None:
        messagebox.showerror("Login Required", "Please log in first.")
        return
    
    user_dashboard.withdraw()
    global bank1_window
    bank1_window = tk.Toplevel(user_dashboard)
    bank1_window.title("Bank 1 - Personal Use Account")
    bank1_window.geometry("800x500")
    bank1_window.configure(bg="#101745")
    bank1_window.resizable(False, False)
    bank1_window_screenalign_width = bank1_window.winfo_screenwidth()
    bank1_window_screenalign_height = bank1_window.winfo_screenheight()
    x = (bank1_window_screenalign_width // 2) - (800 // 2)
    y = (bank1_window_screenalign_height // 2) - (500 // 2)
    bank1_window.geometry(f"800x500+{x}+{y}")

    bank1_title = font.Font(family="Helvetica World", size=25, weight="bold")
    bank1_button_font = font.Font(family="Helvetica World", size=12)
    bank1_label_font = font.Font(family="Helvetica World", size=16)

    label = tk.Label(bank1_window, text="Bank 1 - Personal Use Account", font=bank1_title, bg="#101745", fg="white")
    label.place(relx=0.5, rely=0.05, anchor="n")

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()

        cursor.execute("SELECT Bank1_bal FROM users WHERE UserID = %s", (current_user,)) #fetch bank1 bal
        result = cursor.fetchone()
        if result:
            current_balance = tk.DoubleVar()
            current_balance.set(result[0])  # Set the balance from the database
        else:
            messagebox.showerror("Error", "Unable to fetch balance for the current user.")
            bank1_window.destroy()
            user_dashboard.deiconify()
            return
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while accessing the database: {e}")
        return

    balance_label = tk.Label(bank1_window, text="Current Balance:", font=bank1_label_font, bg="#101745", fg="white")
    balance_label.place(relx=0.3, rely=0.2, anchor="n")

    balance_value_label = tk.Label(bank1_window, textvariable=current_balance, font=bank1_label_font, bg="#101745", fg="white")
    balance_value_label.place(relx=0.6, rely=0.2, anchor="n")

    entry_label = tk.Label(bank1_window, text="Enter Amount:", font=bank1_label_font, bg="#101745", fg="white")
    entry_label.place(relx=0.3, rely=0.35, anchor="n")

    entry_amount = tk.Entry(bank1_window, font=bank1_label_font)
    entry_amount.place(relx=0.6, rely=0.35, anchor="n")
    # deposit
    def deposit():
        amount_str = entry_amount.get().strip()  
        if not amount_str:  # Check if the input is empty
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)  # Try to convert the input to a float
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Enter a positive amount.")
                return
            # Process the deposit logic
            new_balance = current_balance.get() + amount
            try:
                cursor.execute("UPDATE users SET Bank1_bal = %s WHERE UserID = %s", (new_balance, current_user))
                db.commit()
                current_balance.set(new_balance)
                messagebox.showinfo("Deposit Successful", f"{amount} has been added to your balance.")
                entry_amount.delete(0, tk.END)  # Clear the input field after successful deposit
            except mysql.connector.Error as e:
                messagebox.showerror("Database Error", f"An error occurred while updating the balance: {e}")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    # withdrawal
    def withdraw():
        amount_str = entry_amount.get().strip()  
        if not amount_str:  # Check if the input is empty
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)  
            if 0 < amount <= current_balance.get():
                new_balance = current_balance.get() - amount
                try:
                    cursor.execute("UPDATE users SET Bank1_bal = %s WHERE UserID = %s", (new_balance, current_user))
                    db.commit()
                    current_balance.set(new_balance)
                    messagebox.showinfo("Withdrawal Successful", f"{amount} has been withdrawn from your balance.")
                    entry_amount.delete(0, tk.END)
                except mysql.connector.Error as e:
                    messagebox.showerror("Database Error", f"An error occurred while updating the balance: {e}")
            elif amount > current_balance.get():
                messagebox.showwarning("Insufficient Balance", "You don't have enough balance.")
            else:
                messagebox.showwarning("Invalid Amount", "Enter a valid amount.")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    #transfer to bank 2 process
    def transfer_to_bank2():
        amount_str = entry_amount.get().strip()
        if not amount_str:
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)
            if 0 < amount <= current_balance.get():
                new_balance = current_balance.get() - amount
                try:
                    cursor.execute("UPDATE users SET Bank1_bal = %s WHERE UserID = %s", (new_balance, current_user))
                    cursor.execute("UPDATE users SET Bank2_bal = Bank2_bal + %s WHERE UserID = %s", (amount, current_user))
                    cursor.execute("INSERT INTO transaction (UserID, Amount, FromBank, ToBank, TransactionDate, Status) VALUES (%s, %s, %s, %s, NOW(), %s)",
                                  (current_user, amount, "Bank 1", "Bank 2", "Success"))
                    db.commit()                                        # Commit all changes
                    current_balance.set(new_balance)
                    messagebox.showinfo("Transfer Successful", f"{amount} has been transferred to Bank 2 - Savings.")
                    entry_amount.delete(0, tk.END)
                except mysql.connector.Error as e:
                    db.rollback()                                      # Rollback changes in case error occur
                    messagebox.showerror("Database Error", f"An error occurred while updating balances: {e}")
            elif amount > current_balance.get():
                messagebox.showwarning("Insufficient Balance", "You don't have enough balance.")
            else:
                messagebox.showwarning("Invalid Amount", "Enter a valid amount.")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    # Deposit button
    deposit_button = tk.Button(bank1_window, text="Deposit", command=deposit, font=bank1_button_font, bg="#202c82", fg="white", cursor='hand2')
    deposit_button.place(relx=0.3, rely=0.5, anchor="n", width=150, height=50)
    # Withdraw button
    withdraw_button = tk.Button(bank1_window, text="Withdraw", command=withdraw, font=bank1_button_font, bg="#202c82", fg="white", cursor='hand2')
    withdraw_button.place(relx=0.5, rely=0.5, anchor="n", width=150, height=50)
    # Transfer button
    transfer_button = tk.Button(bank1_window, text="Transfer to Savings", command=transfer_to_bank2, font=bank1_button_font, bg="#202c82", fg="white", cursor='hand2')
    transfer_button.place(relx=0.7, rely=0.5, anchor="n", width=150, height=50)
    # Exit button
    exit_button = tk.Button(bank1_window, text="Exit", command=lambda: [bank1_window.destroy(), user_dashboard.deiconify()], font=bank1_button_font, bg="#ff4d4d", fg="white", cursor='hand2')
    exit_button.place(relx=0.5, rely=0.7, anchor="n", width=150, height=50)

def open_bank2_window():
    global current_user

    if current_user is None:
        messagebox.showerror("Login Required", "Please log in first.")
        return
    
    user_dashboard.withdraw()

    global bank2_window
    bank2_window = tk.Toplevel(user_dashboard)
    bank2_window.title("Bank 2 - Savings Account")
    bank2_window.geometry("800x500")
    bank2_window.configure(bg="#101745")
    bank2_window.resizable(False, False)
    bank2_window_screenalign_width = bank2_window.winfo_screenwidth()
    bank2_window_screenalign_height = bank2_window.winfo_screenheight()
    x = (bank2_window_screenalign_width // 2) - (800 // 2)
    y = (bank2_window_screenalign_height // 2) - (500 // 2)
    bank2_window.geometry(f"800x500+{x}+{y}")

    bank2_title = font.Font(family="Helvetica World", size=25, weight="bold")
    bank2_button_font = font.Font(family="Helvetica World", size=12)
    bank2_label_font = font.Font(family="Helvetica World", size=16)

    label = tk.Label(bank2_window, text="Bank 2 - Savings Account", font=bank2_title, bg="#101745", fg="white")
    label.place(relx=0.5, rely=0.05, anchor="n")

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()
        cursor.execute("SELECT Bank2_bal FROM users WHERE UserID = %s", (current_user,))
        result = cursor.fetchone()
        if result:
            current_balance = tk.DoubleVar()
            current_balance.set(result[0])  # Set the balance from the database
        else:
            messagebox.showerror("Error", "Unable to fetch balance for the current user.")
            bank2_window.destroy()
            user_dashboard.deiconify()
            return
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while accessing the database: {e}")
        return

    balance_label = tk.Label(bank2_window, text="Current Balance:", font=bank2_label_font, bg="#101745", fg="white")
    balance_label.place(relx=0.3, rely=0.2, anchor="n")
    balance_value_label = tk.Label(bank2_window, textvariable=current_balance, font=bank2_label_font, bg="#101745", fg="white")
    balance_value_label.place(relx=0.6, rely=0.2, anchor="n")

    entry_label = tk.Label(bank2_window, text="Enter Amount:", font=bank2_label_font, bg="#101745", fg="white")
    entry_label.place(relx=0.3, rely=0.35, anchor="n")
    entry_amount = tk.Entry(bank2_window, font=bank2_label_font)
    entry_amount.place(relx=0.6, rely=0.35, anchor="n")
    # deposit
    def deposit():
        amount_str = entry_amount.get().strip()
        if not amount_str:
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Invalid Amount", "Enter a positive amount.")
                return
            new_balance = current_balance.get() + amount
            if new_balance > 100000000:
                messagebox.showwarning("Exceeds Limit", "The balance cannot exceed 100,000,000.")
                return
            cursor.execute("UPDATE users SET Bank2_bal = %s WHERE UserID = %s", (new_balance, current_user))
            db.commit()
            current_balance.set(new_balance)
            messagebox.showinfo("Deposit Successful", f"{amount} has been added to your balance.")
            entry_amount.delete(0, tk.END)
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    # withdrawal
    def withdraw():
        amount_str = entry_amount.get().strip()
        if not amount_str:
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)
            if 0 < amount <= current_balance.get():
                new_balance = current_balance.get() - amount
                cursor.execute("UPDATE users SET Bank2_bal = %s WHERE UserID = %s", (new_balance, current_user))
                db.commit()
                current_balance.set(new_balance)
                messagebox.showinfo("Withdrawal Successful", f"{amount} has been withdrawn from your balance.")
                entry_amount.delete(0, tk.END)
            elif amount > current_balance.get():
                messagebox.showwarning("Insufficient Balance", "You don't have enough balance.")
            else:
                messagebox.showwarning("Invalid Amount", "Enter a valid amount.")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    # transfer to Bank 1
    def transfer_to_bank1():
        amount_str = entry_amount.get().strip()
        if not amount_str:
            messagebox.showwarning("Invalid Amount", "Please enter an amount.")
            return
        try:
            amount = float(amount_str)
            if 0 < amount <= current_balance.get():
                new_balance = current_balance.get() - amount
                try:
                    cursor.execute("UPDATE users SET Bank2_bal = %s WHERE UserID = %s", (new_balance, current_user))
                    cursor.execute("UPDATE users SET Bank1_bal = Bank1_bal + %s WHERE UserID = %s", (amount, current_user))
                    cursor.execute("INSERT INTO transaction (UserID, Amount, FromBank, ToBank, TransactionDate, Status) VALUES (%s, %s, %s, %s, NOW(), %s)",
                                  (current_user, amount, "Bank 2", "Bank 1", "Success"))
                    db.commit()                     
                    current_balance.set(new_balance)
                    messagebox.showinfo("Transfer Successful", f"{amount} has been transferred to Bank 1.")
                    entry_amount.delete(0, tk.END)
                except mysql.connector.Error as e:
                    db.rollback()  # Rollback changes in case of error
                    messagebox.showerror("Database Error", f"An error occurred while updating balances: {e}")
            elif amount > current_balance.get():
                messagebox.showwarning("Insufficient Balance", "You don't have enough balance.")
            else:
                messagebox.showwarning("Invalid Amount", "Enter a valid amount.")
        except ValueError:
            messagebox.showwarning("Invalid Amount", "Please enter a valid number.")
    # Deposit button
    deposit_button = tk.Button(bank2_window, text="Deposit", command=deposit, font=bank2_button_font, bg="#202c82", fg="white", cursor='hand2')
    deposit_button.place(relx=0.2, rely=0.5, anchor="n", width=150, height=50)
    # Withdraw button
    withdraw_button = tk.Button(bank2_window, text="Withdraw", command=withdraw, font=bank2_button_font, bg="#202c82", fg="white", cursor='hand2')
    withdraw_button.place(relx=0.4, rely=0.5, anchor="n", width=150, height=50)
    # Transfer button
    transfer_button = tk.Button(bank2_window, text="Transfer to Personal Use", command=transfer_to_bank1, font=bank2_button_font, bg="#202c82", fg="white", cursor='hand2')
    transfer_button.place(relx=0.7, rely=0.5, anchor="n", width=250, height=50)
    # Exit button
    exit_button = tk.Button(bank2_window, text="Exit", command=lambda: [bank2_window.destroy(), user_dashboard.deiconify()], font=bank2_button_font, bg="#ff4d4d", fg="white", cursor='hand2')
    exit_button.place(relx=0.5, rely=0.7, anchor="n", width=150, height=50)

def show_transactions():
    global current_user
    if current_user is None:
        messagebox.showerror("Login Required", "Please log in first.")
        return
    
    transaction_window = tk.Toplevel(user_dashboard)
    transaction_window.title("Transaction History")
    transaction_window.geometry("900x500") 
    transaction_window.configure(bg="#101745")
    transaction_windows_creenalign_width = transaction_window.winfo_screenwidth()
    transaction_window_screenalign_height = transaction_window.winfo_screenheight()
    x = (transaction_windows_creenalign_width // 2) - (900 // 2)
    y = (transaction_window_screenalign_height // 2) - (500 // 2)
    transaction_window.geometry(f"900x500+{x}+{y}")

    title_font = font.Font(family="Helvetica World", size=20, weight="bold")
    label_font = font.Font(family="Helvetica World", size=12)
    label = tk.Label(transaction_window, text="Transaction History", font=title_font, bg="#101745", fg="white")
    label.pack(pady=10)

    def go_back_to_dashboard():
        transaction_window.destroy()  # Close the current window
        user_dashboard.deiconify()  # Show the user dashboard again

    back_button = tk.Button(transaction_window, text="Back", font=label_font, bg="#ff4d4d", fg="white", command=go_back_to_dashboard, cursor='hand2')
    back_button.pack(pady=10)

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
        cursor = db.cursor()

        cursor.execute("SELECT TransactionID, Amount, FromBank, ToBank, TransactionDate, Status FROM transaction WHERE UserID = %s ORDER BY TransactionDate DESC", (current_user,))
        transactions = cursor.fetchall()

        if transactions:
            treeview = ttk.Treeview(transaction_window, columns=("TransactionID", "Amount", "Sender", "Reciever", "Date", "Status"), show="headings")
            treeview.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

            treeview.heading("TransactionID", text="Transaction ID")
            treeview.heading("Amount", text="Amount")
            treeview.heading("Sender", text="Sender")
            treeview.heading("Reciever", text="Reciever")
            treeview.heading("Date", text="Date")
            treeview.heading("Status", text="Status")

            treeview.column("TransactionID", width=150, anchor="center")
            treeview.column("Amount", width=100, anchor="center")
            treeview.column("Sender", width=150, anchor="center")
            treeview.column("Reciever", width=150, anchor="center")
            treeview.column("Date", width=150, anchor="center")
            treeview.column("Status", width=100, anchor="center")

            for trans in transactions:
                treeview.insert("", tk.END, values=trans)
            treeview.config(selectmode="none")
        else:
            tk.Label(transaction_window, text="No transactions found.", font=label_font, bg="#101745", fg="white").pack(pady=20)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

def update_userinfo():
    update_window = tk.Toplevel(user_dashboard)
    update_window.title("Update Information")
    update_window.geometry("500x700")
    update_window.configure(bg="#101745")
    update_window.resizable(False, False)
    update_window_screenalign_width = update_window.winfo_screenwidth()
    update_window_screenalign_height = update_window.winfo_screenheight()
    x = (update_window_screenalign_width // 2) - (500 // 2)
    y = (update_window_screenalign_height // 2) - (700 // 2)
    update_window.geometry(f"500x700+{x}+{y}")

    title_font = font.Font(family="Helvetica World", size=16, weight="bold")
    label_font = font.Font(family="Helvetica World", size=12)

    update_window_label = tk.Label(update_window, text="Update User Information", font=title_font, bg="#101745", fg="white")
    update_window_label.pack(pady=10)

    fields = ["FirstName", "LastName", "Age", "New PIN", "Address", "ContactNo", "Email", "Occupation"]
    entries = {}

    for field in fields:
        tk.Label(update_window, text=f"{field}:", font=label_font, bg="#101745", fg="white").pack(pady=5)
        entry = tk.Entry(update_window, font=label_font)
        entry.pack(pady=5)
        entries[field] = entry

    def submit_update():
        try:
            db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db")
            cursor = db.cursor()
            # Verify if the current user exists
            cursor.execute("SELECT UserID FROM users WHERE UserID = %s", (current_user,))
            user_id = cursor.fetchone()
            if not user_id:
                messagebox.showerror("Error", "Current user not found in the database.")
                return
            user_id = user_id[0]

            changes_made = False  # Flag to track changes

            for field, entry in entries.items():
                new_value = entry.get().strip()
                if new_value:  # Check if a new value was entered
                    cursor.execute(f"SELECT {field} FROM users WHERE UserID = %s", (user_id,))
                    old_value = cursor.fetchone()[0]

                    # Compare old and new values
                    if str(new_value) != str(old_value):
                        cursor.execute(f"UPDATE users SET {field} = %s WHERE UserID = %s", (new_value, user_id))
                        cursor.execute(
                            """
                            INSERT INTO user_updates (UserID, UpdatedField, OldValue, NewValue)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (user_id, field, old_value, new_value)
                        )
                        changes_made = True  # A change was applied

            if changes_made:
                db.commit()
                messagebox.showinfo("Success", "Information updated successfully!")
            else:
                messagebox.showinfo("No Changes", "No change applied.")
            
            update_window.destroy()  # Close the update window
        except Exception as e:
            db.rollback()
            messagebox.showerror("Error", f"Failed to update information: {e}")
        finally:
            if db.is_connected():
                db.close()

    update_button = tk.Button(update_window, text="Submit", command=submit_update, font=label_font, bg="#4CAF50", fg="white", cursor='hand2') # confirm changes
    update_button.pack(pady=20)

    def return_to_dashboard():
        update_window.destroy()
    return_button = tk.Button(update_window, text="Return to Dashboard", command=return_to_dashboard, font=label_font, bg="#ff4d4d", fg="white", cursor='hand2')
    return_button.pack(pady=10)

def show_user_dashboard():
    root.withdraw()
    global user_dashboard
    user_dashboard = tk.Toplevel(root)
    user_dashboard.title("KeepSafe-UserInterface")
    user_dashboard.geometry("800x500")
    user_dashboard.configure(bg="#101745")
    user_dashboard.resizable(False, False)
    user_dashboard_screenalign_width = user_dashboard.winfo_screenwidth()
    user_dashboard_screenalign_height = user_dashboard.winfo_screenheight()
    x = (user_dashboard_screenalign_width // 2) - (800 // 2)
    y = (user_dashboard_screenalign_height // 2) - (500 // 2)
    user_dashboard.geometry(f"800x500+{x}+{y}")

    userdash_title = font.Font(family="Helvetica World", size=25, weight="bold")
    userdash_button = font.Font(family="Helvetica World", size=12)

    label = tk.Label(user_dashboard, text="User Interface", font = userdash_title, bg="#101745", fg="white")
    label.place(relx=0.5, rely=0.05, anchor="n")
    #Logout bttn
    logout_button = tk.Button(user_dashboard, text="Logout", command=user_back_to_login, font=userdash_button, bg="#ff4d4d", fg="white", border=1, cursor='hand2')
    logout_button.place(relx = 0.46, rely = 0.72)
    # personal use account (Bank1) button
    Bank_1_button = tk.Button(user_dashboard, text="Personal Use Account", command=open_bank1_window, font=userdash_button, bg="#202c82", fg="white", cursor='hand2')
    Bank_1_button.place(relx=0.5, rely=0.23, anchor="n", width=200, height=50)
    # savings account (Bank2) button
    Bank_2_button = tk.Button(user_dashboard, text="Savings Account", command=open_bank2_window, font=userdash_button, bg="#202c82", fg="white", cursor='hand2')
    Bank_2_button.place(relx=0.5, rely=0.35, anchor="n", width=200, height=50)
    # show transac history button
    Transaction_button = tk.Button(user_dashboard, text="Show Transactions", command=show_transactions, font=userdash_button, bg="#202c82", fg="white", cursor='hand2')
    Transaction_button.place(relx=0.5, rely=0.47, anchor="n", width=200, height=50)
    # update inf bttn
    Update_button = tk.Button(user_dashboard, text="Update Informations", command=update_userinfo, font=userdash_button, bg="#202c82", fg="white", cursor='hand2')
    Update_button.place(relx=0.5, rely=0.59, anchor="n", width=200, height=50)
    
def user_back_to_login():
    user_dashboard.destroy()
    clear_login_inputs()
    root.deiconify()
# Pin validation
def validate_pin_input(P):
    if P.isdigit() and len(P) <= 4:
        return True
    elif P == "":
        return True
    return False
# Error handling for registration
def register_user():
    first_name = enter_first_name.get()
    last_name = enter_last_name.get()
    age = enter_age.get()
    username = enter_username.get()
    pin = enter_pin.get()
    confirm_pin = confirm_pin_entry.get()
    address = enter_address.get()
    contact_no = enter_contact_no.get()
    email = enter_email.get()
    occupation = enter_occupation.get()
    selected_bank = bank_selection.get()  # The bank selected by the user
    entered_amount = amount_entry.get()  # The amount entered by the user

    if not all([first_name, last_name, age, username, pin, confirm_pin, address, contact_no, email, occupation, selected_bank, entered_amount]):
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return
    try:
        initial_amount = float(entered_amount)
        if initial_amount < 1:
            raise ValueError("Negative amount")
        if initial_amount > 50000:
            messagebox.showwarning("Amount Limit Error", "The starting amount cannot exceed 50,000.")
            return
    except ValueError:
        messagebox.showwarning("Amount Error", "Please enter a valid, non-negative amount up to 50,000.")
        return

    if pin != confirm_pin:
        messagebox.showwarning("PIN Error", "The PINs do not match.")
        return
    if len(pin) != 4 or not pin.isdigit():
        messagebox.showwarning("PIN Error", "PIN must be a 4-digit number.")
        return

    if not age.isdigit():
        messagebox.showwarning("Age Error", "Please enter a valid age (numeric).")
        return
                                                    # 11 po for ph based contact number
    if not contact_no.isdigit() or len(contact_no) != 11 or not contact_no.startswith("09"):
        messagebox.showwarning("Contact Number Error", "Contact number must be an 11-digit number starting with '09'.")
        return

    bank1_amount = 0.0 #initializer para ma set bank acc to zero(0)
    bank2_amount = 0.0

    if selected_bank == "Bank 1":
        bank1_amount = initial_amount
    elif selected_bank == "Bank 2":
        bank2_amount = initial_amount
    else:
        messagebox.showwarning("Bank Selection Error", "Please select a valid bank.")
        return

    try:
        db = mysql.connector.connect(host="localhost", user="root", password="", database="keepsafe.db"  )
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE Username = %s", (username,)) # checks if the username exists in the database
        if cursor.fetchone():
            messagebox.showerror("Username Error", "This username is already taken. Please choose another one.")
            return

        cursor.execute("SELECT * FROM users WHERE Email = %s", (email,))
        if cursor.fetchone():
            messagebox.showerror("Email Error", "This email is already registered. Please use a different email.")
            return

        cursor.execute("SELECT * FROM users WHERE ContactNo = %s", (contact_no,))
        if cursor.fetchone():
            messagebox.showerror("Contact Number Error", "This contact number is already in use. Please use a different contact number.")
            return

        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Format as 'YYYY-MM-DD HH:MM:SS'

        cursor.execute('''INSERT INTO users (Firstname, Lastname, Age, Username, PIN, Address, ContactNo, Email, Occupation, DateofCreation, Bank1_bal, Bank2_bal) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                      (first_name, last_name, int(age), username, pin, address, contact_no, email, occupation, created_at, bank1_amount, bank2_amount))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Registration successful!")
        clear_fields()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"An error occurred while accessing the database: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def clear_fields():
    enter_first_name.delete(0, tk.END)
    enter_last_name.delete(0, tk.END)
    enter_age.delete(0, tk.END)
    enter_username.delete(0, tk.END)
    enter_pin.delete(0, tk.END)
    confirm_pin_entry.delete(0, tk.END)
    enter_address.delete(0, tk.END)
    enter_contact_no.delete(0, tk.END)
    enter_email.delete(0, tk.END)
    enter_occupation.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    bank_selection.set("Select a bank")
# Function for registration window
def open_register_window():
    root.withdraw()
    global register_window
    register_window = tk.Toplevel(root)
    register_window.title("User Registration")
    register_window.geometry("800x500")
    register_window.configure(bg="#101745")
    register_window.resizable(False, False)
    register_window_screenalign_width = register_window.winfo_screenwidth()
    register_window_screenalign_height = register_window.winfo_screenheight()
    x = (register_window_screenalign_width // 2) - (800 // 2)
    y = (register_window_screenalign_height // 2) - (500 // 2)
    register_window.geometry(f"800x500+{x}+{y}")

    rtitle = font.Font(family="Helvetica World", size=25, weight="bold")
    rtitle1 = font.Font(family="Helvetica World", size=12)
    rtitle2 = font.Font(family="Helvetica World", size=11, weight="bold")
    rbutton = font.Font(family="Helvetica World", size=12)
    bank_button = font.Font(family = "Helvetica World", size = 11)

    Main_label = tk.Label(register_window, text="Create Your New Account!", font=rtitle, bg="#101745", fg="white")
    Main_label.place(relx=0.5, rely=0.05, anchor="n")

    validate_cmd = register_window.register(validate_pin_input)
    # Fname
    global enter_first_name
    enter_first_name_label = tk.Label(register_window, text="First Name", font=rtitle2, bg="#101745", fg="white")
    enter_first_name_label.place(relx=0.14, rely=0.15, anchor="n")
    enter_first_name = tk.Entry(register_window, font=rtitle1)
    enter_first_name.place(relx=0.20, rely=0.20, anchor="n")
    # Lname
    global enter_last_name
    enter_last_name_label = tk.Label(register_window, text="Last Name", font=rtitle2, bg="#101745", fg="white")
    enter_last_name_label.place(relx=0.44, rely=0.15, anchor="n")
    enter_last_name = tk.Entry(register_window, font=rtitle1)
    enter_last_name.place(relx=0.50, rely=0.20, anchor="n")
    # Age
    global enter_age
    enter_age_label = tk.Label(register_window, text="Age", font=rtitle2, bg="#101745", fg="white")
    enter_age_label.place(relx=0.715, rely=0.15, anchor="n")
    enter_age = tk.Entry(register_window, font=rtitle1)
    enter_age.place(relx=0.80, rely=0.20, anchor="n")
    # Addr
    global enter_address
    enter_address_label = tk.Label(register_window, text="Address", font=rtitle2, bg="#101745", fg="white")
    enter_address_label.place(relx=0.13, rely=0.25, anchor="n")
    enter_address = tk.Entry(register_window, font=rtitle1)
    enter_address.place(relx=0.20, rely=0.30, anchor="n")
    # CntactNo
    global enter_contact_no
    enter_contact_no_label = tk.Label(register_window, text="Contact No.", font=rtitle2, bg="#101745", fg="white")
    enter_contact_no_label.place(relx=0.445, rely=0.25, anchor="n")
    enter_contact_no = tk.Entry(register_window, font=rtitle1)
    enter_contact_no.place(relx=0.50, rely=0.30, anchor="n")
    # Email
    global enter_email
    enter_email = tk.Label(register_window, text="Email", font=rtitle2, bg="#101745", fg="white")
    enter_email.place(relx=0.72, rely=0.25, anchor="n")
    enter_email = tk.Entry(register_window, font=rtitle1)
    enter_email.place(relx=0.80, rely=0.30, anchor='n')
    # PIN
    global enter_pin
    enter_pin_label = tk.Label(register_window, text="PIN (a 4 digit number)", font=rtitle2, bg="#101745", fg="white")
    enter_pin_label.place(relx=0.19, rely=0.35, anchor="n")
    enter_pin = tk.Entry(register_window, font=rtitle1, validate="key", validatecommand=(validate_cmd, '%P'))
    enter_pin.place(relx=0.20, rely=0.40, anchor="n")
    # CnfPIN
    global confirm_pin_entry
    confirm_pin_label = tk.Label(register_window, text="Re-enter PIN", font=rtitle2, bg="#101745", fg="white")
    confirm_pin_label.place(relx=0.45, rely=0.35, anchor="n")
    confirm_pin_entry = tk.Entry(register_window, font=rtitle1)
    confirm_pin_entry.place(relx=0.50, rely=0.40, anchor="n")
    # UserN
    global enter_username
    enter_username_label = tk.Label(register_window, text="Username", font=rtitle2, bg="#101745", fg="white")
    enter_username_label.place(relx=0.14, rely=0.45, anchor="n")
    enter_username = tk.Entry(register_window, font=rtitle1)
    enter_username.place(relx=0.20, rely=0.50, anchor="n")
    # Occupation
    global enter_occupation 
    enter_occupation = tk.Label(register_window, text="Occupation", font=rtitle2, bg="#101745", fg="white")
    enter_occupation.place(relx=0.44, rely=0.45, anchor="n")
    enter_occupation = tk.Entry(register_window, font=rtitle1)
    enter_occupation.place(relx=0.50, rely=0.50, anchor="n")
    # Amount
    global amount_entry
    amount_label = tk.Label(register_window, text="Initial Amount", font=rtitle2, bg="#101745", fg="white")
    amount_label.place(relx=0.75, rely=0.35, anchor="n")
    amount_entry = tk.Entry(register_window, font=rtitle1)
    amount_entry.place(relx=0.80, rely=0.40, anchor="n")
    # Bank selection
    global bank_selection
    bank_selection = ttk.Combobox(register_window, values=["Personal Use", "Savings"], font= bank_button, cursor='hand2')
    bank_selection.set("Select a bank")
    bank_selection.place(relx=0.80, rely=0.445, anchor="n")
    # Register Button
    register_button = tk.Button(register_window, text="Register", font=rbutton, bg='#202c82', fg="white", command=register_user, border=1, cursor='hand2')
    register_button.place(relx=0.41, rely=0.70, anchor="w", width = 150, height = 50)
    # Back to Login Button
    back_button = tk.Button(register_window, text="Back to Login", font=rbutton, bg="#ff4d4d", fg="white", command=reg_back_to_login, border=1, cursor='hand2')
    back_button.place(relx=0.41, rely=0.85, anchor="w", width = 150, height = 50)

def reg_back_to_login():
    register_window.destroy()
    inputuser.delete(0, tk.END)
    inputpin.delete(0, tk.END)
    root.deiconify()

# Log in interface window setup
screenalign_width = root.winfo_screenwidth()           # screensize and screen pop up loc
screenalign_height = root.winfo_screenheight()
x = (screenalign_width // 2) - (800 // 2)
y = (screenalign_height // 2) - (500 // 2)
root.geometry(f"800x500+{x}+{y}")

bg_path = PhotoImage(file=r"C:\Users\Kier Alvaira\Downloads\KeepSafeLog.png")
bg_main = tk.Label(root, image=bg_path)
bg_main.place(relheight=1, relwidth=1)

title = font.Font(family="Arial", size=25, weight="bold")
title1 = font.Font(family="Helvetica World", size=13, weight="bold")
title2 = font.Font(family="Helvetica World", size=12)
button = font.Font(family="Helvetica World", size=12)
Rgstrtxt = font.Font(family="Helvetica World", size=9)
Rgstrbutton = ("Helvetica World", 9, "underline")

label = tk.Label(root, text="WELCOME!", font=title, bg='#202c82', fg="white")
label.place(anchor='w', relx=0.1, rely=0.1)

userlabel = tk.Label(root, text="Username", font=title2, bg='#202c82', fg="white")
userlabel.place( anchor='w', relx=0.1, rely=0.25)
inputuser = tk.Entry(root, width=20, font=title1, border=0)
inputuser.place(anchor='w', relx=0.1, rely=0.3)

def validate_pin_input(PIN):
    if len(PIN) > 4:
        messagebox.showwarning("Input Error", "PIN cannot exceed 4 digits.")
        return False  # Reject further input
    if not PIN.isdigit() and PIN != "":
        messagebox.showwarning("Input Error", "PIN must only contain numbers.")
        return False  # Reject further input
    return True
validate_pin = root.register(validate_pin_input)

pinlabel = tk.Label(root, text="PIN", font=title2, bg='#202c82', fg="white")
pinlabel.place(anchor='w', relx=0.19, rely=0.40)
inputpin = tk.Entry(root, width=20, font=title1, show="*", border=0, validate="key", validatecommand=(validate_pin, '%P'))
inputpin.place(anchor='w', relx=0.19, rely=0.45, width=35)

loginbutt = tk.Button(root, text="Login", font=button, width=15, bg="#545454", fg="white", border=1, cursor='hand2', command=login)
loginbutt.place(anchor='w', relx=0.15, rely=0.60, width=100, height=50)

signinlabel = tk.Label(root, text="Don't have an account yet?", font=Rgstrtxt, fg="white",  bg='#202c82')
signinlabel.place(anchor='w', relx=0.115, rely=0.70)
signinbutt = tk.Button(root, text="Click here to sign up", font=Rgstrbutton, width=15,  bg='#202c82', fg="white", border=0, cursor='hand2', command=open_register_window)
signinbutt.place(anchor='w', relx=0.085, rely=0.75, width=200)

root.mainloop()