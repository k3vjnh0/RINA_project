import tkinter as tk
from tkinter import filedialog, messagebox

import pandas as pd


class SiloAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SILO Summarizer")

        self.df = None
        self.selected_params = []
        self.selected_years = []

        self.load_button = tk.Button(
            root, text="Load CSV or Excel File", command=self.load_file
        )
        self.load_button.pack(pady=10)

        # selectors frame
        frame = tk.Frame(root)
        frame.pack(pady=10)

        # parameters
        param_frame = tk.LabelFrame(frame, text="Select Parameters")
        param_frame.pack(side="left", padx=10)
        self.param_listbox = tk.Listbox(
            param_frame,
            selectmode=tk.MULTIPLE,
            width=30,
            height=15,
            exportselection=False,
        )
        self.param_listbox.pack(padx=5, pady=5)
        self.param_listbox.bind("<<ListboxSelect>>", self.save_param_selection)
        self.select_all_params_var = tk.IntVar()
        self.select_all_params_cb = tk.Checkbutton(
            param_frame,
            text="Select All Parameters",
            variable=self.select_all_params_var,
            command=self.toggle_all_params,
        )
        self.select_all_params_cb.pack(anchor="w", pady=5)

        # months
        month_frame = tk.LabelFrame(frame, text="Select Months")
        month_frame.pack(side="left", padx=10)
        self.month_vars = {}
        for i in range(1, 13):
            var = tk.IntVar()
            cb = tk.Checkbutton(month_frame, text=f"{i:02d}", variable=var)
            cb.pack(anchor="w")
            self.month_vars[i] = var
        self.select_all_months_var = tk.IntVar()
        self.select_all_months_cb = tk.Checkbutton(
            month_frame,
            text="Select All Months",
            variable=self.select_all_months_var,
            command=self.toggle_all_months,
        )
        self.select_all_months_cb.pack(anchor="w", pady=5)

        # years
        year_frame = tk.LabelFrame(frame, text="Select Years")
        year_frame.pack(side="left", padx=10)
        self.year_listbox = tk.Listbox(
            year_frame, selectmode=tk.MULTIPLE, height=15, exportselection=False
        )
        self.year_listbox.pack(padx=5, pady=5)
        self.year_listbox.bind("<<ListboxSelect>>", self.save_year_selection)
        self.select_all_years_var = tk.IntVar()
        self.select_all_years_cb = tk.Checkbutton(
            year_frame,
            text="Select All Years",
            variable=self.select_all_years_var,
            command=self.toggle_all_years,
        )
        self.select_all_years_cb.pack(pady=5)

        # summary options
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
        self.radio_avg.pack()
        self.radio_sum.pack()

        self.separate_sheets_var = tk.IntVar(value=0)
        self.save_mode_cb = tk.Checkbutton(
            root,
            text="Save each parameter to separate sheets",
            variable=self.separate_sheets_var,
        )
        self.save_mode_cb.pack(pady=5)

        self.calc_button = tk.Button(
            root, text="Calculate and Save to Excel", command=self.calculate_summary
        )
        self.calc_button.pack(pady=10)

    def toggle_all_params(self):
        if self.select_all_params_var.get():
            self.param_listbox.select_set(0, tk.END)
        else:
            self.param_listbox.selection_clear(0, tk.END)
        self.selected_params = [
            self.param_listbox.get(i) for i in self.param_listbox.curselection()
        ]

    def toggle_all_months(self):
        state = self.select_all_months_var.get()
        for var in self.month_vars.values():
            var.set(state)

    def toggle_all_years(self):
        if self.select_all_years_var.get():
            self.year_listbox.select_set(0, tk.END)
        else:
            self.year_listbox.selection_clear(0, tk.END)
        self.selected_years = [
            int(self.year_listbox.get(i)) for i in self.year_listbox.curselection()
        ]

    def save_param_selection(self, event):
        self.selected_params = [
            self.param_listbox.get(i) for i in self.param_listbox.curselection()
        ]

    def save_year_selection(self, event):
        self.selected_years = [
            int(self.year_listbox.get(i)) for i in self.year_listbox.curselection()
        ]

    def load_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx *.xls")]
        )
        if not file_path:
            return
        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            self.df.columns = self.df.columns.str.strip()
            if "Date2" not in self.df.columns:
                raise ValueError("Missing 'Date2' column in dataset.")
            self.df["Date2"] = self.df["Date2"].astype(str).str.strip()
            self.df = self.df[~self.df["Date2"].str.contains("ddmmyyyy", case=False)]
            self.df["ParsedDate"] = pd.to_datetime(
                self.df["Date2"], errors="coerce", dayfirst=True
            )
            self.df = self.df.dropna(subset=["ParsedDate"])
            self.df["day"] = self.df["ParsedDate"].dt.day
            self.df["month"] = self.df["ParsedDate"].dt.month
            self.df["year"] = self.df["ParsedDate"].dt.year
            for col in self.df.columns:
                if col not in ["Date2", "ParsedDate"]:
                    self.df[col] = pd.to_numeric(self.df[col], errors="coerce")

            date_keywords = ["date", "day", "month", "year"]
            param_cols = [
                col
                for col in self.df.columns
                if not any(key in col.lower() for key in date_keywords)
            ]
            self.param_listbox.delete(0, tk.END)
            for col in param_cols:
                self.param_listbox.insert(tk.END, col)
            self.selected_params = []
            self.select_all_params_var.set(0)

            years_available = sorted(self.df["year"].dropna().unique())
            self.year_listbox.delete(0, tk.END)
            for y in years_available:
                self.year_listbox.insert(tk.END, str(int(y)))
            self.selected_years = []
            self.select_all_years_var.set(0)

            for var in self.month_vars.values():
                var.set(0)
            self.select_all_months_var.set(0)

        except Exception as e:
            messagebox.showerror("Error", f"File loading failed:\n{e}")

    # split for ruff
    def calculate_summary(self):
        try:
            self._validate_inputs()
            filtered_df = self._filter_data()
            pivot_tables = self._aggregate_data(filtered_df)
            self._save_to_excel(pivot_tables)
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed:\n{e}")

    def _validate_inputs(self):
        if not self.selected_params:
            raise ValueError("Please select at least one parameter.")
        if not any(var.get() for var in self.month_vars.values()):
            raise ValueError("Please select at least one month.")
        if not self.selected_years:
            raise ValueError("Please select at least one year.")

    def _filter_data(self):
        selected_months = [m for m, var in self.month_vars.items() if var.get() == 1]
        filtered = self.df[
            self.df["month"].isin(selected_months)
            & self.df["year"].isin(self.selected_years)
        ]
        if filtered.empty:
            raise ValueError("No data after filtering. Check your selections.")
        return filtered

    def _aggregate_data(self, filtered_df):
        agg_func = "mean" if self.summary_type_var.get() == "average" else "sum"
        grouped = (
            filtered_df.groupby(["year", "month"])[self.selected_params]
            .agg(agg_func)
            .reset_index()
        )
        pivots = {
            param: grouped.pivot(
                index="year", columns="month", values=param
            ).sort_index(ascending=False)
            for param in self.selected_params
        }
        if not any(not tbl.dropna(how="all").empty for tbl in pivots.values()):
            raise ValueError("No data to save after aggregation.")
        return pivots

    def _save_to_excel(self, pivot_tables):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Excel File",
        )
        if not save_path:
            return
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            if self.separate_sheets_var.get():
                for param, tbl in pivot_tables.items():
                    sheet_name = param.replace("/", "_")[:31]
                    tbl.to_excel(writer, sheet_name=sheet_name, index=True)
            else:
                col_offset = 0
                for param, tbl in pivot_tables.items():
                    tbl.insert(0, "Parameter", param)
                    tbl.to_excel(
                        writer, sheet_name="Summary", startcol=col_offset, index=True
                    )
                    col_offset += tbl.shape[1] + 2
        messagebox.showinfo("Success", f"✅ Data saved to: {save_path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SiloAnalyzerGUI(root)
    root.mainloop()
