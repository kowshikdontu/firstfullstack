import datetime
import os
from tkinter import *

class bill:
    @staticmethod
    def today_sales():
        try:
            a = str(datetime.datetime.now()).split()
            with open(f'{a[0]}.txt', 'w') as f:
                f.write(f"{a} today's sales\n")
        except Exception:
            print("file not created")

    @staticmethod
    def append_sale(b):
        try:
            a = str(datetime.datetime.now()).split()
            with open(f'{a[0]}.txt', 'a') as f:
                f.write(f'{a[1]} {b.name} {b.items} {b.amount}\n')
        except Exception:
            print("not appended retry")

    def __init__(self, n, i, p):
        self.name = n
        self.items = i
        self.prices = p
        self.amount = 0

    def amount_cal(self):
        self.amount = sum(self.prices[item] for item in self.items)

    def printer(self):
        bill.append_sale(self)
        print(f"Bill for {self.name}:")
        print(f"Items: {', '.join(self.items)}")
        print(f"Total Amount: {self.amount}")

# Create the main window
w = Tk()
w.title("Sales Entry")

# Define price dictionary globally
price_dict = {"premium": 20, "normal": 10}

# Define and place the labels and entry widgets
Label(w, text="Name").grid(row=0, column=0)
e1 = Entry(w)
e1.grid(row=0, column=1)

Label(w, text="Items").grid(row=1, column=0)
e2 = Entry(w)
e2.grid(row=1, column=1)

def submit():
    name = e1.get()
    items = e2.get().split()
    b = bill(name, items, price_dict)
    b.amount_cal()
    b.printer()

# Create and place the submit button
Button(w, text='Submit', command=submit).grid(row=2, column=0, columnspan=2)

# Start the Tkinter main loop
w.mainloop()
