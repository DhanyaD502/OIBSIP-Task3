import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd


class AdvancedBMICalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced BMI Calculator Pro")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f4f8")


        self.init_database()


        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)


        self.create_calculator_tab()
        self.create_history_tab()
        self.create_stats_tab()

    def init_database(self):
        self.conn = sqlite3.connect('bmi_data.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bmi_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                weight REAL NOT NULL,
                height REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight", "lightcoral"
        elif 18.5 <= bmi < 25:
            return "Normal", "lightgreen"
        elif 25 <= bmi < 30:
            return "Overweight", "orange"
        else:
            return "Obese", "red"

    def calculate_bmi(self):
        try:
            name = self.name_entry.get().strip()
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if not name:
                messagebox.showerror("Error", "Please enter your name!")
                return
            if weight <= 0 or height <= 0:
                messagebox.showerror("Error", "Weight and height must be positive!")
                return

            bmi = weight / (height ** 2)
            category, color = self.get_bmi_category(bmi)

            self.result_label.config(
                text=f"BMI: {bmi:.2f}",
                fg="black",
                bg=color,
                font=("Arial", 32, "bold")
            )
            self.category_label.config(
                text=f"Category: {category}",
                font=("Arial", 18, "bold")
            )


            cursor = self.conn.cursor()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "INSERT INTO bmi_records (name, weight, height, bmi, category, date) VALUES (?, ?, ?, ?, ?, ?)",
                (name, weight, height, bmi, category, date)
            )
            self.conn.commit()

            messagebox.showinfo("Success", "BMI saved successfully!")
            self.refresh_history()

        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")

    def create_calculator_tab(self):

        calc_frame = ttk.Frame(self.notebook)
        self.notebook.add(calc_frame, text="Calculator")


        title = tk.Label(calc_frame, text="🏥 Advanced BMI Calculator",
                         font=("Arial", 28, "bold"),
                         fg="#2c3e50")
        title.grid(row=0, column=0, columnspan=2, pady=30)


        input_frame = ttk.LabelFrame(calc_frame, text="Enter Your Details", padding=20)
        input_frame.grid(row=1, column=0, columnspan=2, pady=20, padx=50, sticky="ew")


        tk.Label(input_frame, text="👤 Name:",
                 font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", pady=15, padx=(20, 10))
        self.name_entry = tk.Entry(input_frame, font=("Arial", 16), width=25)
        self.name_entry.grid(row=0, column=1, padx=10, pady=15, sticky="ew")

        tk.Label(input_frame, text="⚖️ Weight (kg):",
                 font=("Arial", 16, "bold")).grid(row=1, column=0, sticky="w", pady=15, padx=(20, 10))
        self.weight_entry = tk.Entry(input_frame, font=("Arial", 16), width=25)
        self.weight_entry.grid(row=1, column=1, padx=10, pady=15, sticky="ew")

        tk.Label(input_frame, text="📏 Height (m):",
                 font=("Arial", 16, "bold")).grid(row=2, column=0, sticky="w", pady=15, padx=(20, 10))
        self.height_entry = tk.Entry(input_frame, font=("Arial", 16), width=25)
        self.height_entry.grid(row=2, column=1, padx=10, pady=15, sticky="ew")

        input_frame.grid_columnconfigure(1, weight=1)


        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=25)

        tk.Button(btn_frame, text="🧮 Calculate BMI", command=self.calculate_bmi,
                  bg="#27ae60", fg="white", font=("Arial", 16, "bold"),
                  padx=30, pady=12).pack(side="left", padx=15)
        tk.Button(btn_frame, text="🔄 Clear", command=self.clear_inputs,
                  bg="#3498db", fg="white", font=("Arial", 16, "bold"),
                  padx=30, pady=12).pack(side="left", padx=15)


        result_frame = ttk.LabelFrame(calc_frame, text="Your BMI Result", padding=20)
        result_frame.grid(row=2, column=0, columnspan=2, pady=20, padx=50, sticky="ew")

        self.result_label = tk.Label(result_frame,
                                     text="Enter data to calculate BMI",
                                     font=("Arial", 36, "bold"),
                                     width=20, height=2)
        self.result_label.pack(pady=20)

        self.category_label = tk.Label(result_frame, text="",
                                       font=("Arial", 20, "bold"))
        self.category_label.pack()

        calc_frame.grid_columnconfigure(0, weight=1)

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.weight_entry.delete(0, tk.END)
        self.height_entry.delete(0, tk.END)
        self.result_label.config(text="Enter data to calculate BMI", bg="white",
                                 font=("Arial", 36, "bold"))
        self.category_label.config(text="")

    def refresh_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM bmi_records ORDER BY date DESC")
        records = cursor.fetchall()

        for record in records:
            self.history_tree.insert("", "end", values=record)

    def create_history_tab(self):
        history_frame = ttk.Frame(self.notebook)
        self.notebook.add(history_frame, text="History")

        title = tk.Label(history_frame, text="📋 BMI History",
                         font=("Arial", 26, "bold"),
                         fg="#2c3e50")
        title.pack(pady=20)

        columns = ("ID", "Name", "Weight", "Height", "BMI", "Category", "Date")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y", pady=20)

        btn_frame = tk.Frame(history_frame)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_history,
                  bg="#f39c12", fg="white", font=("Arial", 14, "bold"),
                  padx=25, pady=10).pack(side="left", padx=10)
        tk.Button(btn_frame, text="🗑️ Delete Selected", command=self.delete_selected,
                  bg="#e74c3c", fg="white", font=("Arial", 14, "bold"),
                  padx=25, pady=10).pack(side="left", padx=10)

        self.refresh_history()

    def delete_selected(self):
        selected = self.history_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a record to delete!")
            return

        if messagebox.askyesno("Confirm", "Delete selected record?"):
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM bmi_records WHERE id=?", (self.history_tree.item(selected)['values'][0],))
            self.conn.commit()
            self.refresh_history()

    def create_stats_tab(self):
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics & Trends")

        title = tk.Label(stats_frame, text="📊 BMI Analytics",
                         font=("Arial", 26, "bold"),
                         fg="#2c3e50")
        title.pack(pady=20)

        stats_top = tk.Frame(stats_frame)
        stats_top.pack(pady=20, padx=20, fill="x")

        self.stats_label = tk.Label(stats_top, text="Loading statistics...",
                                    font=("Arial", 18, "bold"))
        self.stats_label.pack(pady=20)

        chart_frame = tk.Frame(stats_frame)
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.fig, self.ax = plt.subplots(figsize=(12, 7))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_stats()

    def update_stats(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT name, bmi, date FROM bmi_records ORDER BY date")
        data = cursor.fetchall()

        if not data:
            self.stats_label.config(text="No data available - Calculate your first BMI!")
            self.ax.clear()
            self.ax.text(0.5, 0.5, 'No BMI data to display\nStart tracking your health!',
                         ha='center', va='center', fontsize=20)
            self.canvas.draw()
            return

        df = pd.DataFrame(data, columns=['name', 'bmi', 'date'])
        df['date'] = pd.to_datetime(df['date'])

        total = len(df)
        avg_bmi = df['bmi'].mean()
        self.stats_label.config(text=f"📈 Total Records: {total} | 🎯 Average BMI: {avg_bmi:.2f}",
                                font=("Arial", 18, "bold"))

        self.ax.clear()
        colors = ['#27ae60', 'orange', '#3498db', '#e74c3c']
        for i, name in enumerate(df['name'].unique()):
            user_data = df[df['name'] == name]
            self.ax.plot(user_data['date'], user_data['bmi'], marker='o', linewidth=3,
                         markersize=8, label=name, color=colors[i % len(colors)])

        self.ax.set_title('BMI Trend Analysis', fontsize=20, fontweight='bold')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('BMI')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)
        self.fig.tight_layout()
        self.canvas.draw()

    def __del__(self):
        self.conn.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedBMICalculator(root)
    root.mainloop()
