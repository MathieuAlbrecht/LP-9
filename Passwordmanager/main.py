import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
import subprocess
from cryptography.fernet import Fernet, InvalidToken

# Load or generate a key for encryption and decryption
try:
    with open("key.key", "rb") as key_file:
        key = key_file.read()
except FileNotFoundError:
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

cipher_suite = Fernet(key)

# Function to save password
def save_password(original_username=None, original_password=None):
    website = website_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    if website and username and password:
        encrypted_data = cipher_suite.encrypt(f"{website} | {username} | {password}".encode())
        if original_username and original_password:
            with open("passwords.txt", "rb") as file:
                encrypted_passwords = file.readlines()

            with open("passwords.txt", "wb") as file:
                for encrypted_line in encrypted_passwords:
                    decrypted_line = cipher_suite.decrypt(encrypted_line.strip()).decode()
                    website, u, p = decrypted_line.split(" | ")
                    if u == original_username and p == original_password:
                        file.write(encrypted_data + b'\n')
                    else:
                        file.write(encrypted_line)
        else:
            with open("passwords.txt", "ab") as file:
                file.write(encrypted_data + b'\n')
        website_entry.delete(0, tk.END)
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        messagebox.showinfo("Success", "Password saved successfully!")
    else:
        messagebox.showwarning("Warning", "Please fill out all fields")

# Function to show add password page
def show_add_password_page():
    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text="Website:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    global website_entry
    website_entry = ttk.Entry(root, width=35)
    website_entry.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    global username_entry
    username_entry = ttk.Entry(root, width=35)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    global password_entry
    password_entry = ttk.Entry(root, width=35, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    save_button = ttk.Button(root, text="Save Password", command=save_password)
    save_button.grid(row=3, column=1, pady=10, sticky="e")

    back_button = ttk.Button(root, text="Back", command=show_start_page)
    back_button.grid(row=4, column=1, pady=10, sticky="e")

# Function to show list passwords page
def show_list_passwords_page():
    for widget in root.winfo_children():
        widget.destroy()

    try:
        with open("passwords.txt", "rb") as file:
            encrypted_passwords = file.readlines()
    except FileNotFoundError:
        encrypted_passwords = []

    for i, encrypted_line in enumerate(encrypted_passwords):
        try:
            decrypted_line = cipher_suite.decrypt(encrypted_line.strip()).decode()
            website, username, password = decrypted_line.split(" | ")
            ttk.Label(root, text=f"Website: {website}").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            show_password_button = ttk.Button(root, text="Show",
                                              command=lambda u=username, p=password: show_password_details_page(u, p))
            show_password_button.grid(row=i, column=1, pady=5, sticky="e")
        except (InvalidToken, ValueError):
            ttk.Label(root, text="Error decrypting data").grid(row=i, column=0, padx=10, pady=5, sticky="w")

    back_button = ttk.Button(root, text="Back", command=show_start_page)
    back_button.grid(row=len(encrypted_passwords), column=1, pady=10, sticky="e")

# Function to show password details page
def show_password_details_page(username, password):
    for widget in root.winfo_children():
        widget.destroy()

    copy_username_button = ttk.Button(root, text=f"Username: {username}", command=lambda: copy_username(username))
    copy_username_button.pack(pady=10)
    copy_password_button = ttk.Button(root, text=f"Password: {password}", command=lambda: copy_password(password))
    copy_password_button.pack(pady=10)

    delete_password_button = ttk.Button(root, text="Delete Password", command=lambda: delete_password(username, password))
    delete_password_button.pack(pady=10)

    edit_password_button = ttk.Button(root, text="Edit Password", command=lambda: show_edit_password_page(username, password))
    edit_password_button.pack(pady=10)

    back_button = ttk.Button(root, text="Back", command=show_list_passwords_page)
    back_button.pack(pady=10)

# Function to copy username
def copy_username(username):
    subprocess.run("pbcopy", text=True, input=username.strip())
    messagebox.showinfo("Copied", "Username copied to clipboard!")

# Function to copy password
def copy_password(password):
    subprocess.run("pbcopy", text=True, input=password.strip())
    messagebox.showinfo("Copied", "Password copied to clipboard!")

# Function to delete password
def delete_password(username, password):
    with open("passwords.txt", "rb") as file:
        encrypted_passwords = file.readlines()

    with open("passwords.txt", "wb") as file:
        for encrypted_line in encrypted_passwords:
            decrypted_line = cipher_suite.decrypt(encrypted_line.strip()).decode()
            website, u, p = decrypted_line.split(" | ")
            if u != username or p != password:
                encrypted_data = cipher_suite.encrypt(f"{website} | {u} | {p}".encode())
                file.write(encrypted_data + b'\n')

    show_list_passwords_page()

# Function to show edit password page
def show_edit_password_page(original_username, original_password):
    for widget in root.winfo_children():
        widget.destroy()

    ttk.Label(root, text="Website:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
    global website_entry
    website_entry = ttk.Entry(root, width=35)
    website_entry.grid(row=0, column=1, padx=10, pady=10)

    ttk.Label(root, text="Username:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
    global username_entry
    username_entry = ttk.Entry(root, width=35)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    ttk.Label(root, text="Password:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
    global password_entry
    password_entry = ttk.Entry(root, width=35, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    save_button = ttk.Button(root, text="Save Password", command=lambda: save_password(original_username, original_password))
    save_button.grid(row=3, column=1, pady=10, sticky="e")

    back_button = ttk.Button(root, text="Back", command=show_list_passwords_page)
    back_button.grid(row=4, column=1, pady=10, sticky="e")

# Function to show start page
def show_start_page():
    for widget in root.winfo_children():
        widget.destroy()

    welcome_label = ttk.Label(root, text="Welcome to Password Manager", font=("Helvetica", 16))
    welcome_label.pack(pady=10)

    add_password_button = ttk.Button(root, text="Add Password", command=show_add_password_page)
    add_password_button.pack(pady=10)

    list_passwords_button = ttk.Button(root, text="List Passwords", command=show_list_passwords_page)
    list_passwords_button.pack(pady=10)

# Create the main window
root = ThemedTk(theme="breeze")
root.title("Password Manager")
root.geometry("600x400")

# Show the start page
show_start_page()

# Run the application
root.mainloop()