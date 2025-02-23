import flet as ft
import pandas as pd
import qrcode
import os

# Load or create user database
file_path = "bank_database.csv"

try:
    df = pd.read_csv(file_path)
except FileNotFoundError:
    data = {
        'Account Number': [1001, 1002],
        'Name': ['Alice', 'Bob'],
        'Balance': [5000, 3000],
        'PIN': [1234, 5678],
        'Transactions': ['', ''],
        'QR Code': ['', '']
    }
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

# Generate permanent QR codes for each user
def generate_permanent_qr():
    for index, row in df.iterrows():
        qr_data = f"Account:{row['Account Number']}"
        qr = qrcode.make(qr_data)
        qr_path = f"qr_{row['Account Number']}.png"
        qr.save(qr_path)
        df.at[index, 'QR Code'] = qr_path
    df.to_csv(file_path, index=False)

generate_permanent_qr()

# Theme Colors
PRIMARY_COLOR = "#0047AB"
SECONDARY_COLOR = "#FFCF40"
BACKGROUND_COLOR = "#F8F9FA"
TEXT_COLOR = "#333333"

# Login Page
def login_page(page: ft.Page):
    page.clean()
    page.bgcolor = BACKGROUND_COLOR
    page.title = "Secure Bank Login"
    
    logo = ft.Image(src="bank_logo.png", width=150, height=150)
    title = ft.Text("Welcome to Mini Google Pay", size=24, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    
    account_field = ft.TextField(label="Account Number", keyboard_type=ft.KeyboardType.NUMBER)
    pin_field = ft.TextField(label="PIN", password=True, keyboard_type=ft.KeyboardType.NUMBER)
    status_text = ft.Text("", size=16, color=ft.colors.RED)
    
    def login(e):
        try:
            account_number = int(account_field.value)
            pin = int(pin_field.value)
            user = df[(df['Account Number'] == account_number) & (df['PIN'] == pin)]
            if not user.empty:
                main_dashboard(page, account_number)
            else:
                status_text.value = "Invalid account number or PIN!"
                page.update()
        except ValueError:
            status_text.value = "Enter valid details!"
            page.update()
    
    login_button = ft.ElevatedButton("Login", on_click=login, bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR)
    
    page.add(logo, title, account_field, pin_field, login_button, status_text)

# Main Dashboard
def main_dashboard(page: ft.Page, account_number):
    page.clean()
    page.bgcolor = BACKGROUND_COLOR
    
    welcome_text = ft.Text(f"Welcome, {df[df['Account Number'] == account_number]['Name'].values[0]}", size=22, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    
    buttons = [
        ft.ElevatedButton("Send Money", on_click=lambda e: transaction_page(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR),
        ft.ElevatedButton("QR Code Payment", on_click=lambda e: qr_page(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR),
        ft.ElevatedButton("Balance Inquiry", on_click=lambda e: balance_inquiry_page(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR),
        ft.ElevatedButton("Transaction History", on_click=lambda e: transaction_history_page(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR),
        ft.ElevatedButton("Logout", on_click=lambda e: login_page(page), bgcolor="#D32F2F", color="white")
    ]
    
    page.add(welcome_text, *buttons)

# Balance Inquiry Page
def balance_inquiry_page(page: ft.Page, account_number):
    page.clean()
    page.bgcolor = BACKGROUND_COLOR
    user_data = df[df['Account Number'] == account_number].iloc[0]
    
    balance_text = ft.Text(f"Your Balance: ₹{user_data['Balance']}", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR)
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main_dashboard(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR)
    
    page.add(balance_text, back_button)

# Transaction History Page
def transaction_history_page(page: ft.Page, account_number):
    page.clean()
    page.bgcolor = BACKGROUND_COLOR
    user_data = df[df['Account Number'] == account_number].iloc[0]
    transactions = user_data['Transactions'].split(', ') if pd.notna(user_data['Transactions']) else ["No transactions yet."]
    
    transaction_list = ft.Column([ft.Text(transaction, size=16, color=TEXT_COLOR) for transaction in transactions])
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main_dashboard(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR)
    
    page.add(ft.Text("Transaction History", size=20, weight=ft.FontWeight.BOLD, color=PRIMARY_COLOR), transaction_list, back_button)

# Transactions Page
def transaction_page(page: ft.Page, account_number):
    page.clean()
    user_data = df[df['Account Number'] == account_number].iloc[0]
    balance = user_data['Balance']
    transactions = [] if pd.isna(user_data['Transactions']) else user_data['Transactions'].split(', ')

    def send_money(e):
        nonlocal balance
        amount = float(amount_field.value)
        receiver_account = int(receiver_field.value)
        receiver = df[df['Account Number'] == receiver_account]
        
        if not receiver.empty and amount > 0 and amount <= balance:
            balance -= amount
            transactions.append(f"Sent ₹{amount} to {receiver_account}")
            
            df.loc[df['Account Number'] == account_number, 'Balance'] = balance
            df.loc[df['Account Number'] == account_number, 'Transactions'] = ', '.join(transactions)
            
            receiver_index = receiver.index[0]
            receiver_balance = df.at[receiver_index, 'Balance'] + amount
            receiver_transactions = [] if pd.isna(df.at[receiver_index, 'Transactions']) else df.at[receiver_index, 'Transactions'].split(', ')
            receiver_transactions.append(f"Received ₹{amount} from {account_number}")
            
            df.at[receiver_index, 'Balance'] = receiver_balance
            df.at[receiver_index, 'Transactions'] = ', '.join(receiver_transactions)
            df.to_csv(file_path, index=False)
            
            status_text.value = "Transaction Successful!"
        else:
            status_text.value = "Invalid transaction!"
        page.update()
    
    receiver_field = ft.TextField(label="Receiver Account Number")
    amount_field = ft.TextField(label="Amount", keyboard_type=ft.KeyboardType.NUMBER)
    send_button = ft.ElevatedButton("Send Money", on_click=send_money)
    status_text = ft.Text("", size=16, color=ft.colors.RED)
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main_dashboard(page, account_number))
    
    page.add(receiver_field, amount_field, send_button, status_text, back_button)
    
# QR Code Payment Page
def qr_page(page: ft.Page, account_number):
    page.clean()
    page.bgcolor = BACKGROUND_COLOR
    user_data = df[df['Account Number'] == account_number].iloc[0]
    qr_image = ft.Image(src=user_data['QR Code'], width=200, height=200)
    
    receiver_account = ft.TextField(label="Scanned Account Number", disabled=True)
    amount_field = ft.TextField(label="Amount", keyboard_type=ft.KeyboardType.NUMBER)
    status_text = ft.Text("", size=16, color=ft.colors.RED)

    def scan_qr_code(e):
        scanned_data = "Account:1002"  # Simulating scanned data
        scanned_account = int(scanned_data.split(':')[1])
        receiver_account.value = str(scanned_account)
        page.update()
    
    def send_money_qr(e):
        sender_balance = df.loc[df['Account Number'] == account_number, 'Balance'].values[0]
        if float(amount_field.value) > sender_balance:
            status_text.value = "Insufficient balance!"
        else:
            status_text.value = "Transaction Successful!"
        page.update()

    send_button = ft.ElevatedButton("Send Money", on_click=send_money_qr, bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR)
    scan_button = ft.ElevatedButton("Scan QR Code", on_click=scan_qr_code, bgcolor=SECONDARY_COLOR, color=PRIMARY_COLOR)
    back_button = ft.ElevatedButton("Back", on_click=lambda e: main_dashboard(page, account_number), bgcolor=PRIMARY_COLOR, color=SECONDARY_COLOR)
    
    page.add(qr_image, scan_button, receiver_account, amount_field, send_button, status_text, back_button)

ft.app(target=login_page)
