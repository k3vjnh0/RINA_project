import tkinter as tk
from tkinter import filedialog, messagebox

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class SiloAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SILO Summarizer and Plotter")

        self.df = None
        self.selected_params = []
        self.selected_years = []

        # File loading
        tk.Button(root, text="Load CSV or Excel File", command=self.load_file).pack(
            pady=10
        )

        summary_frame = tk.Frame(root)
        summary_frame.pack()

        # Parameters
        param_frame = tk.LabelFrame(summary_frame, text="Select Parameters")
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
        tk.Checkbutton(
            param_frame,
            text="Select All Parameters",
            variable=self.select_all_params_var,
            command=self.toggle_all_params,
        ).pack(anchor="w")

        # Months
        month_frame = tk.LabelFrame(summary_frame, text="Select Months")
        month_frame.pack(side="left", padx=10)
        self.month_vars = {}
        for i in range(1, 13):
            var = tk.IntVar()
            tk.Checkbutton(month_frame, text=f"{i:02d}", variable=var).pack(anchor="w")
            self.month_vars[i] = var
        self.select_all_months_var = tk.IntVar()
        tk.Checkbutton(
            month_frame,
            text="Select All Months",
            variable=self.select_all_months_var,
            command=self.toggle_all_months,
        ).pack(anchor="w", pady=5)

        # Years
        year_frame = tk.LabelFrame(summary_frame, text="Select Years")
        year_frame.pack(side="left", padx=10)
        self.year_listbox = tk.Listbox(
            year_frame, selectmode=tk.MULTIPLE, height=15, exportselection=False
        )
        self.year_listbox.pack(padx=5, pady=5)
        self.year_listbox.bind("<<ListboxSelect>>", self.save_year_selection)
        self.select_all_years_var = tk.IntVar()
        tk.Checkbutton(
            year_frame,
            text="Select All Years",
            variable=self.select_all_years_var,
            command=self.toggle_all_years,
        ).pack(pady=5)

        # --- Options Layout ---
        options_frame = tk.Frame(root)
        options_frame.pack(pady=10, expand=True, anchor="center")

        # Summarize Options
        summary_options = tk.LabelFrame(
            options_frame, text="Summarize Options", padx=10, pady=10
        )
        summary_options.pack(side="left", padx=10, pady=5, fill="y")
        self.summary_type_var = tk.StringVar(value="average")
        tk.Radiobutton(
            summary_options,
            text="Monthly Averages",
            variable=self.summary_type_var,
            value="average",
        ).pack(anchor="w")
        tk.Radiobutton(
            summary_options,
            text="Monthly Totals",
            variable=self.summary_type_var,
            value="sum",
        ).pack(anchor="w")
        self.separate_sheets_var = tk.IntVar(value=0)
        tk.Checkbutton(
            summary_options,
            text="Save each parameter to separate sheets",
            variable=self.separate_sheets_var,
        ).pack(anchor="w", pady=5)
        tk.Button(
            summary_options,
            text="Calculate and Save to Excel",
            command=self.calculate_summary,
        ).pack(pady=5)

        # Plotting Options
        plot_options = tk.LabelFrame(
            options_frame, text="Plotting Options", padx=10, pady=10
        )
        plot_options.pack(side="left", padx=10, pady=5, fill="y")
        plot_frame = tk.Frame(plot_options)
        plot_frame.pack()

        self.plot_tdiff_var = tk.IntVar()
        self.plot_separate_var = tk.IntVar()
        tk.Checkbutton(
            plot_frame,
            text="Plot Tmax - Tmin",
            variable=self.plot_tdiff_var,
        ).pack(anchor="w")
        tk.Checkbutton(
            plot_frame,
            text="Plot each parameter separately",
            variable=self.plot_separate_var,
        ).pack(anchor="w")

        self.enable_stack_var = tk.IntVar(value=1)
        tk.Checkbutton(
            plot_frame,
            text="Stack Graphs",
            variable=self.enable_stack_var,
            command=self.toggle_stack_options,
        ).pack(anchor="w")

        self.stack_direction_var = tk.StringVar(value="vertical")
        self.stack_layout_frame = tk.Frame(plot_frame)
        self.stack_layout_frame.pack(anchor="w")
        tk.Radiobutton(
            self.stack_layout_frame,
            text="Stack Vertically",
            variable=self.stack_direction_var,
            value="vertical",
        ).pack(anchor="w")
        tk.Radiobutton(
            self.stack_layout_frame,
            text="Stack Side-by-Side",
            variable=self.stack_direction_var,
            value="horizontal",
        ).pack(anchor="w")

        tk.Button(
            plot_options, text="Visualize Selected Parameters", command=self.plot_data
        ).pack(pady=10)

    def toggle_stack_options(self):
        if self.enable_stack_var.get():
            self.stack_layout_frame.pack(anchor="w")
        else:
            self.stack_layout_frame.pack_forget()

    def toggle_all_params(self):
        if self.select_all_params_var.get():
            self.param_listbox.select_set(0, tk.END)
        else:
            self.param_listbox.selection_clear(0, tk.END)
        self.save_param_selection(None)

    def toggle_all_months(self):
        state = self.select_all_months_var.get()
        for var in self.month_vars.values():
            var.set(state)

    def toggle_all_years(self):
        if self.select_all_years_var.get():
            self.year_listbox.select_set(0, tk.END)
        else:
            self.year_listbox.selection_clear(0, tk.END)
        self.save_year_selection(None)

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
        return self.df[
            self.df["month"].isin(selected_months)
            & self.df["year"].isin(self.selected_years)
        ]

    def _aggregate_data(self, filtered_df):
        agg_func = "mean" if self.summary_type_var.get() == "average" else "sum"
        grouped = (
            filtered_df.groupby(["year", "month"])[self.selected_params]
            .agg(agg_func)
            .reset_index()
        )
        return {
            param: grouped.pivot(
                index="year", columns="month", values=param
            ).sort_index(ascending=False)
            for param in self.selected_params
        }

    def _save_to_excel(self, pivot_tables):
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")]
        )
        if not save_path:
            return
        with pd.ExcelWriter(save_path, engine="openpyxl") as writer:
            if self.separate_sheets_var.get():
                for param, tbl in pivot_tables.items():
                    tbl.to_excel(writer, sheet_name=param.replace("/", "_")[:31])
            else:
                col_offset = 0
                for param, tbl in pivot_tables.items():
                    tbl.insert(0, "Parameter", param)
                    tbl.to_excel(writer, sheet_name="Summary", startcol=col_offset)
                    col_offset += tbl.shape[1] + 2
        messagebox.showinfo("Success", f"✅ Data saved to: {save_path}")

    def plot_data(self):
        try:
            self._validate_inputs()
            df_filtered = self._filter_data()
            plot_params = self.selected_params.copy()

            if (
                self.plot_tdiff_var.get()
                and "T.Max" in self.df.columns
                and "T.Min" in self.df.columns
            ):
                self.df["Tmax-Tmin"] = self.df["T.Max"] - self.df["T.Min"]
                df_filtered["Tmax-Tmin"] = df_filtered["T.Max"] - df_filtered["T.Min"]
                plot_params.append("Tmax-Tmin")

            if not plot_params:
                messagebox.showwarning(
                    "No Parameters", "No parameters selected for plotting."
                )
                return

            if self.plot_separate_var.get():
                self._plot_separate(df_filtered, plot_params)
            elif self.enable_stack_var.get():
                self._plot_stacked(df_filtered, plot_params)
            else:
                self._plot_combined(df_filtered, plot_params)

        except Exception as e:
            messagebox.showerror("Plot Error", f"Could not generate plot:\n{e}")

    def _plot_separate(self, df_filtered, plot_params):
        for param in plot_params:
            fig, ax = plt.subplots(figsize=(10, 4))
            grouped = (
                df_filtered.groupby(["year", "month"])[param]
                .mean()
                .unstack()
                .sort_index()
            )
            for year in grouped.index:
                ax.plot(
                    grouped.columns,
                    grouped.loc[year],
                    label=f"{param} - {int(year)}",
                    marker="o",
                )
            ax.set_title(f"{param} - Monthly Trend")
            ax.set_xlabel("Month")
            ax.set_ylabel("Value")
            ax.legend(fontsize=8)
            ax.grid(True)
            plt.tight_layout()
            plt.show()

    def _plot_stacked(self, df_filtered, plot_params):
        n_params = len(plot_params)
        if self.stack_direction_var.get() == "horizontal":
            fig, axes = plt.subplots(
                1, n_params, figsize=(5 * n_params, 4), sharey=True
            )
        else:
            fig, axes = plt.subplots(
                n_params, 1, figsize=(12, 4 * n_params), sharex=True
            )

        axes = np.array(axes).flatten()

        for idx, param in enumerate(plot_params):
            ax = axes[idx]
            grouped = (
                df_filtered.groupby(["year", "month"])[param]
                .mean()
                .unstack()
                .sort_index()
            )
            for year in grouped.index:
                ax.plot(
                    grouped.columns,
                    grouped.loc[year],
                    label=f"{param} - {int(year)}",
                    marker="o",
                )
            ax.set_title(f"{param} - Monthly Trends")
            ax.set_ylabel("Value")
            ax.legend(fontsize=8)
            ax.grid(True)

        axes[-1].set_xlabel("Month")
        plt.tight_layout()
        plt.show()

    def _plot_combined(self, df_filtered, plot_params):
        fig, ax = plt.subplots(figsize=(12, 6))
        for param in plot_params:
            grouped = (
                df_filtered.groupby(["year", "month"])[param]
                .mean()
                .unstack()
                .sort_index()
            )
            for year in grouped.index:
                ax.plot(
                    grouped.columns,
                    grouped.loc[year],
                    label=f"{param} - {int(year)}",
                    marker="o",
                )
        ax.set_title("Combined Parameter Plot")
        ax.set_xlabel("Month")
        ax.set_ylabel("Value")
        ax.legend(fontsize=8)
        ax.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = SiloAnalyzerGUI(root)
    root.mainloop()
