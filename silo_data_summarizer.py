import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


class SiloAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SILO Summarizer")

        self.df = None

        self.load_button = tk.Button(
            root, text="Load CSV or Excel File", command=self.load_file
        )
        self.load_button.pack(pady=10)

        self.listbox_label = tk.Label(root, text="Select parameters:")
        self.listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=60, height=18)

        self.summary_type_var = tk.StringVar(value="average")
        self.radio_avg = tk.Radiobutton(
            root,
            text="Monthly Averages",
            variable=self.summary_type_var,
            value="average",
        )
        self.radio_sum = tk.Radiobutton(
            root, text="Monthly Totals", variable=self.summary_type_var, value="sum"
        )

        self.calc_button = tk.Button(
            root, text="Calculate and Save to Excel", command=self.calculate_summary
        )

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            # Load CSV or Excel
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)

            self.df.columns = self.df.columns.str.strip()

            if "Date2" not in self.df.columns:
                raise ValueError("Missing 'Date2' column in dataset.")

            # Handle Date2
            self.df["Date2"] = self.df["Date2"].astype(str).str.strip()
            self.df = self.df[~self.df["Date2"].str.contains("ddmmyyyy", case=False)]

            self.df["ParsedDate"] = pd.to_datetime(
                self.df["Date2"], errors="coerce", dayfirst=True
            )
            self.df = self.df.dropna(subset=["ParsedDate"])

            self.df["day"] = self.df["ParsedDate"].dt.day
            self.df["month"] = self.df["ParsedDate"].dt.month
            self.df["year"] = self.df["ParsedDate"].dt.year

            # Convert all values to numeric (safe)
            self.df = self.df.apply(pd.to_numeric, errors="coerce")

            # Clear previous UI
            for widget in self.root.pack_slaves():
                if widget not in [self.load_button]:
                    widget.destroy()

            self.listbox_label.pack()
            self.listbox.delete(0, tk.END)

            date_keywords = ["date", "day", "month", "year"]
            param_cols = [
                col
                for col in self.df.columns
                if not any(key in col.lower() for key in date_keywords)
            ]

            for col in param_cols:
                self.listbox.insert(tk.END, col)

            self.listbox.pack(pady=10)
            self.radio_avg.pack()
            self.radio_sum.pack()
            self.calc_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"File loading failed:\n{e}")

    def calculate_summary(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(
                "No selection", "Please select at least one parameter."
            )
            return

        selected_params = [self.listbox.get(i) for i in selected_indices]
        summary_type = self.summary_type_var.get()

        try:
            agg_func = "mean" if summary_type == "average" else "sum"
            grouped = (
                self.df.groupby(["year", "month"])[selected_params]
                .agg(agg_func)
                .reset_index()
            )

            pivot_tables = {}
            for param in selected_params:
                pivot_df = grouped.pivot(index="year", columns="month", values=param)
                pivot_df = pivot_df.sort_index(ascending=False)
                if not pivot_df.dropna(how="all").empty:
                    pivot_tables[param] = pivot_df

            if not pivot_tables:
                raise ValueError(
                    "No data to save. Please check the file contents or selected fields."
                )

            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Save Excel File",
            )
            if not save_path:
                return

            with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
                for param, table in pivot_tables.items():
                    sheet_name = param.replace("/", "_")[:31]
                    table.to_excel(writer, sheet_name=sheet_name)

            messagebox.showinfo("Success", f"Saved to: {save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SiloAnalyzerGUI(root)
    root.mainloop()
