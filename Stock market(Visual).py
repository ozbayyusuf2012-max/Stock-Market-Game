"""
Stock Market Price Game - Tkinter GUI Edition
Same core game logic as the original console version (buy/sell/check/inventory/roll),
now wrapped in a graphical interface.
"""

import random
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

# ----------------------------------------------------------------------
# Game data (same lists as the original script)
# ----------------------------------------------------------------------
Stocks = ["Meta", "Apple", "Microsoft", "Amazon", "Google", "Tesla", "Nvidia", "Netflix", "Intel"]
Prices = [300, 150, 250, 3500, 2800, 700, 220, 500, 55]


class StockMarketGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Price Game")
        self.root.geometry("780x520")
        self.root.minsize(700, 480)
        self.root.configure(bg="#1e1e2e")

        # ---- game state -------------------------------------------------
        self.money = 1000
        self.inventory = []  # list of stock names owned (duplicates allowed)

        # ---- styling ------------------------------------------------------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                         background="#2a2a3d", fieldbackground="#2a2a3d",
                         foreground="#e6e6e6", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background="#3a3a55", foreground="#ffffff")
        style.map("Treeview", background=[("selected", "#4a7dff")])

        # ---- header ---------------------------------------------------
        header = tk.Frame(root, bg="#1e1e2e")
        header.pack(fill="x", padx=15, pady=(15, 5))

        tk.Label(header, text="📈 Stock Market Price Game", font=("Segoe UI", 18, "bold"),
                 bg="#1e1e2e", fg="#ffffff").pack(side="left")

        self.money_var = tk.StringVar()
        self.money_label = tk.Label(header, textvariable=self.money_var,
                                     font=("Segoe UI", 14, "bold"), bg="#1e1e2e", fg="#5af78e")
        self.money_label.pack(side="right")

        # ---- main body: price table (left) + inventory/log (right) ----
        body = tk.Frame(root, bg="#1e1e2e")
        body.pack(fill="both", expand=True, padx=15, pady=5)

        left = tk.Frame(body, bg="#1e1e2e")
        left.pack(side="left", fill="both", expand=True)

        right = tk.Frame(body, bg="#1e1e2e", width=230)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        # -- price table --
        columns = ("stock", "price", "owned")
        self.tree = ttk.Treeview(left, columns=columns, show="headings", height=12)
        self.tree.heading("stock", text="Stock")
        self.tree.heading("price", text="Price")
        self.tree.heading("owned", text="Owned")
        self.tree.column("stock", width=140, anchor="w")
        self.tree.column("price", width=90, anchor="center")
        self.tree.column("owned", width=70, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # buy/sell buttons under the table
        btn_frame = tk.Frame(left, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=10)

        buy_btn = tk.Button(btn_frame, text="Buy Selected", command=self.buy_selected,
                             bg="#3ddc84", fg="#0b0b0b", font=("Segoe UI", 10, "bold"),
                             relief="flat", padx=12, pady=6, cursor="hand2")
        buy_btn.pack(side="left", padx=(0, 8))

        sell_btn = tk.Button(btn_frame, text="Sell Selected", command=self.sell_selected,
                              bg="#ff5c5c", fg="#0b0b0b", font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=12, pady=6, cursor="hand2")
        sell_btn.pack(side="left", padx=(0, 8))

        roll_btn = tk.Button(btn_frame, text="🎲 Roll Market", command=self.roll_market,
                              bg="#ffd166", fg="#0b0b0b", font=("Segoe UI", 10, "bold"),
                              relief="flat", padx=12, pady=6, cursor="hand2")
        roll_btn.pack(side="left")

        # -- inventory panel --
        tk.Label(right, text="Inventory", font=("Segoe UI", 12, "bold"),
                 bg="#1e1e2e", fg="#ffffff").pack(anchor="w")
        self.inv_list = tk.Listbox(right, bg="#2a2a3d", fg="#e6e6e6",
                                    font=("Segoe UI", 10), height=10,
                                    selectbackground="#4a7dff", relief="flat")
        self.inv_list.pack(fill="both", expand=False, pady=(4, 10))

        # -- status line (shows only the current/latest message) --
        tk.Label(right, text="Status", font=("Segoe UI", 12, "bold"),
                 bg="#1e1e2e", fg="#ffffff").pack(anchor="w")
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(right, textvariable=self.status_var,
                                      bg="#2a2a3d", fg="#c9c9c9", font=("Consolas", 9),
                                      wraplength=210, justify="left", anchor="nw",
                                      padx=8, pady=8)
        self.status_label.pack(fill="both", expand=True, pady=(4, 0))

        # ---- fullscreen toggle ----
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.exit_fullscreen)

        fs_btn = tk.Button(right, text="⛶ Fullscreen (F11)", command=self.toggle_fullscreen,
                            bg="#3a3a55", fg="#ffffff", font=("Segoe UI", 9, "bold"),
                            relief="flat", padx=8, pady=6, cursor="hand2")
        fs_btn.pack(fill="x", pady=(10, 0))

        # ---- initial render ----
        self.refresh_prices()
        self.update_money_label()
        self.log("Welcome! You start with $1000. Buy low, sell high, and watch out for market crashes.")

    # ------------------------------------------------------------------
    # Fullscreen handling
    # ------------------------------------------------------------------
    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def log(self, message):
        """Show only the most recent message (replaces the previous one)."""
        self.status_var.set(message)

    def update_money_label(self):
        self.money_var.set(f"💰 ${self.money}")

    def refresh_prices(self):
        """Repopulate the price table from the Stocks/Prices lists and current inventory."""
        self.tree.delete(*self.tree.get_children())
        owned_counts = Counter(self.inventory)
        for name, price in zip(Stocks, Prices):
            self.tree.insert("", "end", iid=name,
                              values=(name, f"${price}", owned_counts.get(name, 0)))

    def refresh_inventory(self):
        self.inv_list.delete(0, "end")
        for stock in self.inventory:
            self.inv_list.insert("end", stock)

    def get_selected_stock(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select a stock from the table first.")
            return None
        return selection[0]  # iid == stock name

    # ------------------------------------------------------------------
    # Core game actions (same logic as the original console functions)
    # ------------------------------------------------------------------
    def buy_selected(self):
        stock_name = self.get_selected_stock()
        if stock_name is None:
            return
        index = Stocks.index(stock_name)
        price = Prices[index]
        if self.money >= price:
            self.money -= price
            self.inventory.append(stock_name)
            self.log(f"Bought {stock_name} for ${price}. Balance: ${self.money}.")
        else:
            self.log(f"Insufficient funds to buy {stock_name} (${price}). Balance: ${self.money}.")
            messagebox.showwarning("Insufficient funds",
                                    f"You need ${price} to buy {stock_name}, but only have ${self.money}.")
        self.update_money_label()
        self.refresh_prices()
        self.refresh_inventory()

    def sell_selected(self):
        stock_name = self.get_selected_stock()
        if stock_name is None:
            return
        if stock_name not in self.inventory:
            self.log(f"You do not own {stock_name}. Cannot sell it.")
            messagebox.showwarning("Not owned", f"You don't own any {stock_name} to sell.")
            return
        index = Stocks.index(stock_name)
        price = Prices[index]
        self.money += price
        self.inventory.remove(stock_name)
        self.log(f"Sold {stock_name} for ${price}. Balance: ${self.money}.")
        self.update_money_label()
        self.refresh_prices()
        self.refresh_inventory()

    def roll_market(self):
        self.log("Rolling the market...")
        market_roll = random.randint(1, 10)
        if market_roll == 1:
            self.crisis()
        elif 1 < market_roll <= 4:
            self.wild()
        else:
            self.mild()
        self.refresh_prices()

    def crisis(self):
        self.log("💥 The stock market is in CRISIS! Prices are dropping rapidly.")
        for i in range(len(Prices)):
            factor = 0.5 if random.randint(1, 2) == 1 else 0.6
            Prices[i] = int(Prices[i] * factor)

    def mild(self):
        self.log("🙂 The stock market is stable. Prices are changing slightly.")
        for i in range(len(Prices)):
            factor = 1.2 if random.randint(1, 2) == 1 else 0.9
            Prices[i] = int(Prices[i] * factor)

    def wild(self):
        self.log("⚡ The stock market is WILD! Prices are changing significantly.")
        for i in range(len(Prices)):
            factor = 1.5 if random.randint(1, 2) == 1 else 0.7
            Prices[i] = int(Prices[i] * factor)


if __name__ == "__main__":
    root = tk.Tk()
    app = StockMarketGame(root)
    root.mainloop()