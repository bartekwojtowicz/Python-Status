# Autor: !bartix
# Discord: dc.gold-plugins.pl


import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import json
import requests
import os
import sys

# Plik, w którym będą dane
ORDER_FILE = 'klienci.json'

# Webhook Discorda
DISCORD_WEBHOOK_URL = "" #<------------ Tutaj wklei webhoki Kanału Discorda!

# Ładowanie zamówień
def load_orders():
    try:
        with open(ORDER_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_orders(orders):
    with open(ORDER_FILE, 'w') as file:
        json.dump(orders, file)

# Wysyłanie waidomości na discord
def send_discord_message(status, order):
    message = f"{order['customer_nick']} {order['item_name']} | Płatność: {order['payment_status']} | Realizacja: {status}"
    
    data = {
        "content": message
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code != 204:
        print(f"Problem w wysłaniu wiadomości na Discord | ERROR: {response.status_code}")
    else:
        print("Poprawnie wysłano wiadomość!.")

# Funkcja do dodawania nowego zamówienia
def add_order():
    customer_nick = entry_nick.get()
    item_name = entry_item.get()
    payment_status = entry_payment.get()
    
    if not customer_nick or not item_name or not payment_status:
        message = "Wszystkie pola muszą być wypełnione!"
        send_discord_message("Błąd", {"customer_nick": customer_nick, "item_name": item_name, "payment_status": payment_status})
        messagebox.showwarning("Błąd", message)
        return

    order = {
        'customer_nick': customer_nick,
        'item_name': item_name,
        'payment_status': payment_status,
        'status': 'w trakcie realizacji'  # Domyślny status to 'w trakcie realizacji'
    }

    orders.append(order)
    save_orders(orders)
    refresh_orders()

    entry_nick.delete(0, tk.END)
    entry_item.delete(0, tk.END)
    entry_payment.delete(0, tk.END)

    send_discord_message("Zamówienie dodane", order)  # Wyślij wiadomość na Discorda po dodaniu zamówienia

# Funkcja do zmiany statusu zamówienia
def change_status(index):
    def on_status_change(status):
        orders[index]['status'] = status
        save_orders(orders)
        
        # Wyślij wiadomość na Discorda
        send_discord_message(status, orders[index])
        
        refresh_orders()
    
    # Tworzenie okna wyboru statusu
    status_window = tk.Toplevel(root)
    status_window.title("Zmień status")
    
    label_status = tk.Label(status_window, text="Wybierz nowy status:", font=("Helvetica", 12), bg="#f4f4f4", fg="#333")
    label_status.pack(padx=10, pady=10)
    
    # ComboBox z opcjami
    status_combobox = ttk.Combobox(status_window, values=["zrealizowane", "w trakcie realizacji", "zrezygnowano"], font=("Helvetica", 12))
    status_combobox.set(orders[index]['status'])  # Ustawienie obecnego statusu jako domyślnego
    status_combobox.pack(padx=10, pady=10)
    
    button_ok = tk.Button(status_window, text="Zatwierdź", font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="raised", bd=2, command=lambda: on_status_change(status_combobox.get()))
    button_ok.pack(padx=10, pady=10)

# Funkcja do edytowania zamówienia
def edit_order(index):
    order = orders[index]
    new_nick = simpledialog.askstring("Edytuj nick", "Podaj nowy nick:", initialvalue=order['customer_nick'])
    new_item = simpledialog.askstring("Edytuj przedmiot", "Podaj nowy przedmiot:", initialvalue=order['item_name'])
    new_payment = simpledialog.askstring("Edytuj płatność", "Podaj nowy status płatności:", initialvalue=order['payment_status'])
    
    if new_nick and new_item and new_payment:
        order['customer_nick'] = new_nick
        order['item_name'] = new_item
        order['payment_status'] = new_payment
        save_orders(orders)
        refresh_orders()

        send_discord_message("Zamówienie edytowane", order)  # Wyślij wiadomość na Discorda po edytowaniu zamówienia

# Funkcja do usuwania zamówienia
def delete_order(index):
    order = orders[index]
    del orders[index]
    save_orders(orders)
    refresh_orders()

    send_discord_message("Zamówienie usunięte", order)  # Wyślij wiadomość na Discorda po usunięciu zamówienia

# Funkcja do otwierania menu kontekstowego
def on_right_click(event):
    selected_index = listbox_orders.curselection()
    
    if not selected_index:
        return
    
    index = selected_index[0]
    order = orders[index]

    menu = tk.Menu(root, tearoff=0, bg="#f4f4f4", fg="#333")
    menu.add_command(label="Edytuj", command=lambda: edit_order(index))
    menu.add_command(label="Zmień status", command=lambda: change_status(index))  # Dodanie opcji zmiany statusu
    menu.add_command(label="Usuń", command=lambda: delete_order(index))
    menu.post(event.x_root, event.y_root)

# Funkcja do odświeżania zamówień w oknie
def refresh_orders():
    listbox_orders.delete(0, tk.END)  # Usuwanie wszystkich elementów z listboxa
    
    for order in orders:
        status_color = {
            "zrealizowane": "green",
            "w trakcie realizacji": "red",
            "zrezygnowano": "orange"
        }.get(order['status'], "black")  # Domyślny kolor to czarny

        listbox_orders.insert(tk.END, f"{order['customer_nick']} {order['item_name']} | Płatność: {order['payment_status']} | Realizacja: {order['status']}")
        listbox_orders.itemconfig(tk.END, {'fg': status_color})  # Ustawienie koloru tekstu

# Inicjalizacja GUI
root = tk.Tk()
root.title("Status aktywności Klientów - Gold-Plugins")  # Tytuł okna z logo i nazwą
root.geometry("750x750")
root.config(bg="#f4f4f4")  # Tło okna

orders = load_orders()

# Dodajemy logo i tytuł wewnątrz okna
frame_header = tk.Frame(root, bg="#ffffff", pady=20)
frame_header.pack(fill="x")

# Załaduj obrazek (logo)
try:
    logo_image = Image.open("image/gp.png")
    logo_image = logo_image.resize((50, 50), Image.ANTIALIAS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(frame_header, image=logo_photo, bg="#ffffff")
    logo_label.image = logo_photo  # Zapisz odniesienie do zdjęcia, aby zapobiec usunięciu przez GC
    logo_label.pack(side="left", padx=10)
except Exception as e:
    print(f"Error loading logo: {e}")

# Tytuł aplikacji
title_label = tk.Label(frame_header, text="Status aktywności Klientów - Gold-Plugins", font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#333")
title_label.pack(side="left", padx=10)

# Tworzenie elementów GUI z zaawansowaną stylizacją
frame_input = tk.Frame(root, bg="#ffffff", padx=20, pady=20, relief="solid", bd=2, highlightbackground="#4CAF50", highlightthickness=2)
frame_input.pack(padx=20, pady=20, fill="x")

label_nick = tk.Label(frame_input, text="Nick klienta:", font=("Helvetica", 12), bg="#ffffff", fg="#333")
label_nick.grid(row=0, column=0, sticky="w", pady=10)

entry_nick = tk.Entry(frame_input, width=30, font=("Helvetica", 12), bd=2, relief="solid")
entry_nick.grid(row=0, column=1, pady=10)

label_item = tk.Label(frame_input, text="Nazwa przedmiotu:", font=("Helvetica", 12), bg="#ffffff", fg="#333")
label_item.grid(row=1, column=0, sticky="w", pady=10)

entry_item = tk.Entry(frame_input, width=30, font=("Helvetica", 12), bd=2, relief="solid")
entry_item.grid(row=1, column=1, pady=10)

label_payment = tk.Label(frame_input, text="Płatność:", font=("Helvetica", 12), bg="#ffffff", fg="#333")
label_payment.grid(row=2, column=0, sticky="w", pady=10)

entry_payment = tk.Entry(frame_input, width=30, font=("Helvetica", 12), bd=2, relief="solid")
entry_payment.grid(row=2, column=1, pady=10)

button_add = tk.Button(frame_input, text="Dodaj zamówienie", font=("Helvetica", 12), bg="#4CAF50", fg="white", relief="raised", bd=2, command=add_order)
button_add.grid(row=3, column=0, columnspan=2, pady=10, padx=10, sticky="ew")

# Stylizacja listboxa
listbox_orders = tk.Listbox(root, width=70, height=12, font=("Helvetica", 12), bd=2, relief="solid", selectmode=tk.SINGLE, bg="#ffffff", highlightthickness=1, highlightbackground="#4CAF50")
listbox_orders.pack(padx=20, pady=10)

# Dodanie menu kontekstowego na prawy przycisk myszy
listbox_orders.bind("<Button-3>", on_right_click)

# Odświeżenie widoku zamówień
refresh_orders()

# Uruchomienie aplikacji
root.mainloop()
