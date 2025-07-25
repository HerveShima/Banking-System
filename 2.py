import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

# Timestamp function
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# BankAccount Class
class BankAccount:
    account_number_counter = 1000

    def __init__(self, name, pin, acc_number=None, balance=0.0, transactions=None):
        self.account_holder = name
        self.balance = balance
        self.pin = pin
        self.trans = transactions if transactions is not None else []
        if acc_number:
            self.account_number = acc_number
        else:
            self.account_number = BankAccount.account_number_counter
            BankAccount.account_number_counter += 1

    def to_dict(self):
        return {
            'name': self.account_holder,
            'pin': self.pin,
            'balance': self.balance,
            'account_number': self.account_number,
            'transactions': self.trans
        }

    def createAccount(self):
        self.account_number = BankAccount.account_number_counter
        self.account_holder = input('Enter your names: ')
        self.pin = int(input('Enter your pin: '))
        pin = int(input('Confirm your pin: '))
        if self.pin == pin:
            return f'You have successfully created account.'

    @staticmethod
    def from_dict(data):
        return BankAccount(
            name=data['name'],
            pin=data['pin'],
            balance=data['balance'],
            acc_number=data['account_number'],
            transactions=data.get('transactions', [])
        )

    def deposit(self, amount):
        if amount < 0:
            return '❌ Deposit cannot be negative.'
        self.balance += amount
        self.trans.append(f'[{get_timestamp()}] You deposited ${amount}')
        save_accounts()
        return f'✅ You deposited ${amount}.'

    def withdraw(self, amount, pin):
        if amount < 0:
            return '❌ Withdraw cannot be negative.'
        if amount > self.balance:
            return '❌ Insufficient funds.'
        if pin != self.pin:
            return '❌ Incorrect PIN.'
        self.balance -= amount
        self.trans.append(f'[{get_timestamp()}] You withdrew ${amount}')
        save_accounts()
        return f'✅ You withdrew ${amount}.'

    def display_balance(self):
        return f'💰 Your balance is: ${self.balance}'

    def __str__(self):
        return f'👤 Account holder: {self.account_holder}\n🏦 Account number: {self.account_number}\n💰 Balance: ${self.balance}'

# Account handling
accounts = {}

def save_accounts():
    try:
        with open("accounts.json", "w") as f:
            data = {acc_num: acc.to_dict() for acc_num, acc in accounts.items()}
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving accounts: {e}")

def load_accounts():
    global accounts
    if os.path.exists("accounts.json"):
        with open("accounts.json", "r") as f:
            data = json.load(f)
            accounts = {int(acc_num): BankAccount.from_dict(acc_data) for acc_num, acc_data in data.items()}
        if accounts:
            BankAccount.account_number_counter = max(accounts.keys()) + 1

# GUI setup
root = tk.Tk()
root.title("Simple Bank System")
root.geometry("800x800")
current_account = None

load_accounts()

def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()

def main_menu():
    clear_screen()
    tk.Label(root, text="Banking System", font=('Helvetica', 16)).pack(pady=20)
    tk.Button(root, text="Login", command=show_login).pack(pady=10)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=10)

def show_login():
    clear_screen()
    tk.Label(root, text="Login", font=('Helvetica', 16)).pack(pady=10)
    tk.Label(root, text="Account Number").pack()
    acc_entry = tk.Entry(root)
    acc_entry.pack()

    tk.Label(root, text="PIN").pack()
    pin_entry = tk.Entry(root, show="*")
    pin_entry.pack()

    def login_action():
        acc = acc_entry.get()
        pin = pin_entry.get()
        if not acc.isdigit():
            messagebox.showerror("Error", "Invalid account number.")
            return
        acc = int(acc)
        global current_account
        user = accounts.get(acc)
        if user and user.pin == pin:
            current_account = user
            messagebox.showinfo("Success", f"Welcome {user.account_holder}!")
            show_dashboard()
        else:
            messagebox.showerror("Error", "Login failed.")

    tk.Button(root, text="Login", command=login_action).pack(pady=10)
    tk.Button(root, text="Back", command=main_menu).pack()

def show_dashboard():
    clear_screen()
    tk.Label(root, text=f"Welcome {current_account.account_holder}", font=('Helvetica', 14)).pack(pady=10)
    tk.Button(root, text="Deposit", command=deposit_screen).pack(fill='x')
    tk.Button(root, text="Withdraw", command=withdraw_screen).pack(fill='x')
    tk.Button(root, text="Balance", command=lambda: messagebox.showinfo("Balance", current_account.display_balance())).pack(fill='x')
    tk.Button(root, text="Transactions", command=show_transactions).pack(fill='x')
    tk.Button(root, text="Logout", command=main_menu).pack(pady=10)

def deposit_screen():
    clear_screen()
    tk.Label(root, text="Deposit Amount").pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    def deposit_action():
        try:
            amount = float(amount_entry.get())
            message = current_account.deposit(amount)
            messagebox.showinfo("Deposit", message)
            show_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid amount.")

    tk.Button(root, text="Submit", command=deposit_action).pack(pady=10)
    tk.Button(root, text="Back", command=show_dashboard).pack()

def withdraw_screen():
    clear_screen()
    tk.Label(root, text="Withdraw Amount").pack()
    amount_entry = tk.Entry(root)
    amount_entry.pack()

    tk.Label(root, text="PIN").pack()
    pin_entry = tk.Entry(root, show="*")
    pin_entry.pack()

    def withdraw_action():
        try:
            amount = float(amount_entry.get())
            pin = pin_entry.get()
            message = current_account.withdraw(amount, pin)
            messagebox.showinfo("Withdraw", message)
            show_dashboard()
        except ValueError:
            messagebox.showerror("Error", "Invalid input.")

    tk.Button(root, text="Submit", command=withdraw_action).pack(pady=10)
    tk.Button(root, text="Back", command=show_dashboard).pack()

def show_transactions():
    clear_screen()
    tk.Label(root, text="Transactions").pack()
    for tx in current_account.trans:
        tk.Label(root, text=tx).pack(anchor='w')
    tk.Button(root, text="Back", command=show_dashboard).pack(pady=10)

main_menu()
root.mainloop()
